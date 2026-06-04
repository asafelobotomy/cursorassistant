"""Install, inspect, update, repair, and plan engine for Cursor-managed surfaces."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.lifecycle import conditions, interview, merge, mcp_config, mcp_scripts, packs
from scripts.lifecycle.models import ManagedEntry

LOCKFILE_REL = Path(".cursor") / "cursorAssistant-lock.json"
BACKUP_ROOT_REL = Path(".cursor") / ".cursorAssistant-backup"
TOKEN_PATTERN = re.compile(r"\{\{([A-Z0-9_]+)\}\}")
LOCKFILE_REQUIRED_KEYS = ("schemaVersion", "package", "fileHashes")


def lockfile_package_root(workspace: Path, package_root: Path) -> str:
    """Store a portable package root: '.' when package_root is the workspace."""
    ws = workspace.resolve()
    pkg = package_root.resolve()
    if pkg == ws:
        return "."
    try:
        return str(pkg.relative_to(ws))
    except ValueError:
        return str(pkg)


def package_version(package_root: Path) -> str:
    version_file = package_root / "VERSION"
    if not version_file.is_file():
        return "0.0.0"
    return version_file.read_text(encoding="utf-8").strip().splitlines()[0]


def load_policy(package_root: Path) -> dict[str, Any]:
    path = package_root / "template" / "setup" / "install-policy.json"
    return json.loads(path.read_text(encoding="utf-8"))


def core_entries(policy: dict[str, Any]) -> list[ManagedEntry]:
    entries: list[ManagedEntry] = []
    for item in policy.get("entries", []):
        if item["id"].startswith("mcp.") and item["id"] != "mcp.config":
            continue
        entries.append(
            ManagedEntry(
                entry_id=item["id"],
                source_rel=item["source"],
                target_rel=item["target"],
                layer=item.get("layer", "core"),
                strategy=item.get("strategy", "replace"),
                required_when=item.get("requiredWhen"),
            )
        )
    return entries


def managed_entries(
    policy: dict[str, Any],
    package_root: Path,
    selected_packs: list[str],
    answers: dict[str, Any],
) -> list[ManagedEntry]:
    entries = core_entries(policy)
    mcp_enabled = conditions.mcp_enabled(answers)
    entries.extend(
        mcp_scripts.mcp_script_entries(
            package_root,
            mcp_enabled=mcp_enabled,
            selected_packs=selected_packs,
        )
    )
    for pack_id in selected_packs:
        entries.extend(packs.pack_skill_entries(package_root, pack_id))
    return [entry for entry in entries if conditions.conditions_match(entry.required_when, answers)]


def _resolve_context(
    package_root: Path,
    answers: dict[str, Any] | None,
    lockfile: dict[str, Any] | None,
) -> tuple[dict[str, Any], list[str]]:
    interview_data = interview.load_interview(package_root)
    resolved_answers = interview.resolve_answers(
        interview_data, answers, lockfile, package_root=package_root
    )
    selected_packs = packs.resolve_selected_packs(package_root, resolved_answers, lockfile)
    return resolved_answers, selected_packs


def _sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _default_tokens(workspace: Path, answers: dict[str, Any] | None = None) -> dict[str, str]:
    tokens = {
        "WORKSPACE_NAME": workspace.name or "workspace",
        "PACKAGE_VERSION": "0.0.0",
    }
    if answers:
        profile = answers.get("profile.selected")
        if profile:
            tokens["PROFILE"] = str(profile)
    return tokens


def render_tokens(text: str, tokens: dict[str, str]) -> str:
    def repl(match: re.Match[str]) -> str:
        key = match.group(1)
        return tokens.get(key, match.group(0))

    return TOKEN_PATTERN.sub(repl, text)


def resolve_entry_source(
    package_root: Path,
    entry: ManagedEntry,
    answers: dict[str, Any],
) -> Path:
    if entry.entry_id == "mcp.config":
        return package_root / mcp_config.CORE_REL
    return package_root / entry.source_rel


def materialize_source(
    package_root: Path,
    entry: ManagedEntry,
    tokens: dict[str, str],
    answers: dict[str, Any],
) -> bytes:
    if entry.entry_id == "mcp.config":
        selected_packs = packs.resolve_selected_packs(package_root, answers, None)
        payload = mcp_config.build_mcp_config(package_root, answers, selected_packs, tokens)
        return merge.serialize_json_object(payload)
    source = resolve_entry_source(package_root, entry, answers)
    if not source.is_file():
        raise FileNotFoundError(f"Missing package source: {source.relative_to(package_root)}")
    raw = source.read_text(encoding="utf-8")
    return render_tokens(raw, tokens).encode("utf-8")


def apply_write_strategy(
    entry: ManagedEntry,
    source_bytes: bytes,
    target: Path,
) -> bytes:
    if not target.is_file() or entry.strategy == "replace":
        return source_bytes

    existing_text = target.read_text(encoding="utf-8")
    source_text = source_bytes.decode("utf-8")

    if entry.strategy == "preserve-marked-markdown-blocks":
        merged = merge.merge_markdown_with_preserved_blocks(existing_text, source_text)
        return merged.encode("utf-8")

    if entry.strategy == "merge-json-object":
        existing_data = merge.parse_json_object(existing_text)
        source_data = merge.parse_json_object(source_text)
        if entry.entry_id == "mcp.config":
            existing_data = mcp_config.sanitize_mcp_config(existing_data)
            source_data = mcp_config.sanitize_mcp_config(source_data)
        merged = merge.merge_json_objects(existing_data, source_data)
        if entry.entry_id == "mcp.config":
            merged = mcp_config.sanitize_mcp_config(merged)
        return merge.serialize_json_object(merged)

    raise ValueError(f"Unsupported write strategy for {entry.entry_id}: {entry.strategy}")


def lockfile_path(workspace: Path) -> Path:
    return workspace / LOCKFILE_REL


def read_lockfile(workspace: Path) -> dict[str, Any] | None:
    path = lockfile_path(workspace)
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"__malformed__": True}
    if not isinstance(payload, dict):
        return {"__malformed__": True}
    return payload


def lockfile_is_malformed(lock: dict[str, Any] | None) -> bool:
    if lock is None:
        return False
    if lock.get("__malformed__"):
        return True
    return any(key not in lock for key in LOCKFILE_REQUIRED_KEYS)


def write_lockfile(
    workspace: Path,
    payload: dict[str, Any],
    *,
    preserve_timestamps: dict[str, str] | None = None,
) -> None:
    path = lockfile_path(workspace)
    path.parent.mkdir(parents=True, exist_ok=True)
    if preserve_timestamps:
        timestamps = dict(preserve_timestamps)
    else:
        timestamps = dict(payload.get("timestamps", {}))
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    timestamps.setdefault("appliedAt", now)
    timestamps["updatedAt"] = now
    payload = dict(payload)
    payload["timestamps"] = timestamps
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _inspect_tokens(workspace: Path, package_root: Path, answers: dict[str, Any] | None) -> dict[str, str]:
    tokens = _default_tokens(workspace, answers)
    tokens["PACKAGE_VERSION"] = package_version(package_root)
    return tokens


def inspect(
    workspace: Path,
    package_root: Path,
    *,
    answers: dict[str, Any] | None = None,
) -> dict[str, Any]:
    policy = load_policy(package_root)
    lock = read_lockfile(workspace)
    resolved_answers, selected_packs = _resolve_context(package_root, answers, lock)
    entries = managed_entries(policy, package_root, selected_packs, resolved_answers)
    installed = lock is not None and not lockfile_is_malformed(lock)
    tokens = _inspect_tokens(workspace, package_root, resolved_answers)
    file_rows: list[dict[str, Any]] = []
    stale = 0
    missing = 0
    for entry in entries:
        target = workspace / entry.target_rel
        source_bytes = materialize_source(package_root, entry, tokens, resolved_answers)
        if target.is_file():
            expected = apply_write_strategy(entry, source_bytes, target)
        else:
            expected = source_bytes
        expected_hash = _sha256_bytes(expected)
        if not target.is_file():
            status = "missing"
            missing += 1
            actual_hash = None
        else:
            actual_hash = _sha256_file(target)
            status = "clean" if actual_hash == expected_hash else "stale"
            if status == "stale":
                stale += 1
        file_rows.append(
            {
                "id": entry.entry_id,
                "target": entry.target_rel,
                "status": status,
                "expectedHash": expected_hash,
                "actualHash": actual_hash,
            }
        )
    install_state = "not-installed" if not installed else "installed"
    if installed and (stale or missing):
        install_state = "needs-update"
    repair_reasons = determine_repair_reasons(
        workspace, package_root, lock, file_rows, selected_packs
    )
    if repair_reasons and install_state == "installed":
        install_state = "needs-repair"
    mcp_path = workspace / ".cursor" / "mcp.json"
    mcp_payload = None
    if mcp_path.is_file():
        try:
            mcp_payload = json.loads(mcp_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            mcp_payload = None
    scripts_dir = workspace / ".cursor" / "mcp" / "scripts"
    warnings = mcp_config.mcp_warnings(mcp_payload)
    for name in mcp_config.deprecated_scripts_on_disk(scripts_dir):
        warnings.append(f"deprecated-mcp-script:{name} — run update to remove")

    mcp_enabled = conditions.mcp_enabled(resolved_answers)
    return {
        "packageName": policy.get("packageName", "cursorAssistant"),
        "packageVersion": package_version(package_root),
        "installState": install_state,
        "lockfilePresent": lock is not None,
        "lockfileMalformed": lockfile_is_malformed(lock),
        "repairReasons": repair_reasons,
        "profile": resolved_answers.get("profile.selected", "balanced"),
        "selectedPacks": selected_packs,
        "mcpEnabled": mcp_enabled,
        "mcpWarnings": warnings,
        "summary": {"managed": len(entries), "stale": stale, "missing": missing},
        "files": file_rows,
        "nextSteps": _install_next_steps(install_state, mcp_enabled),
    }


def _install_next_steps(install_state: str, mcp_enabled: bool) -> list[str]:
    steps: list[str] = []
    if install_state == "not-installed":
        steps.append(
            "Run: python3 cursorAssistant.py configure --workspace . "
            "(or /cursor-assistant:setup-workspace in chat after installing the plugin)"
        )
        steps.append("Reload the Cursor window after setup (Developer: Reload Window).")
    elif install_state in {"needs-update", "needs-repair"}:
        steps.append("Run: python3 cursorAssistant.py update --workspace .")
        steps.append("Or ask the Agent to update cursorAssistant (cursorLifecycle / cursorTools MCP).")
    if mcp_enabled:
        steps.append("Enable MCP servers in Cursor Settings → Features → MCP (cursorTools first).")
    else:
        steps.append(
            "Optional: enable cursorTools in Settings → MCP after setup, or re-run configure with MCP enabled."
        )
    return steps


def determine_repair_reasons(
    workspace: Path,
    package_root: Path,
    lock: dict[str, Any] | None,
    file_rows: list[dict[str, Any]] | None = None,
    selected_packs: list[str] | None = None,
) -> list[str]:
    reasons: list[str] = []
    if lock is None:
        return reasons
    if lockfile_is_malformed(lock):
        reasons.append("malformed-lockfile")
        return reasons
    if file_rows is None:
        file_rows = inspect(workspace, package_root)["files"]
    if any(row["status"] == "missing" for row in file_rows):
        reasons.append("incomplete-install")
    file_hashes = lock.get("fileHashes", {})
    if not isinstance(file_hashes, dict):
        reasons.append("malformed-lockfile")
        return reasons
    policy = load_policy(package_root)
    if selected_packs is None:
        selected_packs = lock.get("selectedPacks", []) if isinstance(lock.get("selectedPacks"), list) else []
    resolved_answers, _ = _resolve_context(package_root, None, lock)
    entries = managed_entries(policy, package_root, selected_packs, resolved_answers)
    expected_ids = {entry.entry_id for entry in entries}
    if set(file_hashes.keys()) != expected_ids:
        reasons.append("lockfile-hash-mismatch")
    package_info = lock.get("package", {})
    if isinstance(package_info, dict):
        if package_info.get("name") not in (None, load_policy(package_root).get("packageName", "cursorAssistant")):
            reasons.append("package-identity-mismatch")
    return reasons


def _backup_file(workspace: Path, target: Path) -> None:
    if not target.is_file():
        return
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_dir = workspace / BACKUP_ROOT_REL / stamp
    dest = backup_dir / target.relative_to(workspace)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(target, dest)


def _prune_deselected_pack_skills(
    workspace: Path,
    package_root: Path,
    previous_packs: list[str],
    new_packs: list[str],
) -> list[str]:
    removed = sorted(set(previous_packs) - set(new_packs))
    pruned: list[str] = []
    for pack_id in removed:
        for skill_name in packs.all_pack_skill_names(package_root, pack_id):
            target = workspace / ".cursor/skills" / skill_name / "SKILL.md"
            if target.is_file():
                _backup_file(workspace, target)
                target.unlink()
                pruned.append(f"packs.{pack_id}.{skill_name}")
                if target.parent.is_dir() and not any(target.parent.iterdir()):
                    target.parent.rmdir()
    return pruned


def _prune_deselected_pack_mcp(
    workspace: Path,
    package_root: Path,
    previous_packs: list[str],
    new_packs: list[str],
) -> list[str]:
    removed = sorted(set(previous_packs) - set(new_packs))
    pruned: list[str] = []
    for pack_id in removed:
        for name in mcp_scripts.PACK_SCRIPTS.get(pack_id, frozenset()):
            target = workspace / ".cursor/mcp/scripts" / name
            if target.is_file():
                _backup_file(workspace, target)
                target.unlink()
                pruned.append(f"packs.{pack_id}.mcp.{Path(name).stem}")
    return pruned


def _prune_orphan_mcp_scripts(
    workspace: Path,
    package_root: Path,
    answers: dict[str, Any],
    selected_packs: list[str],
) -> list[str]:
    scripts_dir = workspace / ".cursor/mcp/scripts"
    if not scripts_dir.is_dir():
        return []
    expected = mcp_scripts.expected_script_names(
        package_root,
        mcp_enabled=conditions.mcp_enabled(answers),
        selected_packs=selected_packs,
    )
    pruned: list[str] = []
    for path in sorted(scripts_dir.glob("*.py")):
        if path.name not in expected:
            _backup_file(workspace, path)
            path.unlink()
            pruned.append(f"mcp.orphan.{path.stem}")
    return pruned


def _build_lockfile_payload(
    workspace: Path,
    package_root: Path,
    entries: list[ManagedEntry],
    tokens: dict[str, str],
    answers: dict[str, Any],
    selected_packs: list[str],
    existing_lock: dict[str, Any] | None,
) -> dict[str, Any]:
    policy = load_policy(package_root)
    lock_fields = interview.answers_to_lockfile_fields(answers, selected_packs)
    hashes = {}
    for entry in entries:
        target = workspace / entry.target_rel
        source_bytes = materialize_source(package_root, entry, tokens, answers)
        payload = apply_write_strategy(entry, source_bytes, target)
        hashes[entry.entry_id] = _sha256_bytes(payload)
    preserve = None
    if existing_lock and not lockfile_is_malformed(existing_lock):
        preserve = existing_lock.get("timestamps")
    payload = {
        "schemaVersion": "0.4.0",
        "package": {
            "name": policy.get("packageName", "cursorAssistant"),
            "version": package_version(package_root),
            "packageRoot": lockfile_package_root(workspace, package_root),
        },
        "profile": lock_fields["profile"],
        "selectedPacks": lock_fields["selectedPacks"],
        "mcpEnabled": lock_fields["mcpEnabled"],
        "setupAnswers": lock_fields["setupAnswers"],
        "fileHashes": hashes,
    }
    write_lockfile(workspace, payload, preserve_timestamps=preserve)
    return payload


def apply_entries(
    workspace: Path,
    package_root: Path,
    *,
    only_stale_or_missing: bool,
    force_all: bool = False,
    answers: dict[str, Any] | None = None,
) -> dict[str, Any]:
    policy = load_policy(package_root)
    existing_lock = read_lockfile(workspace)
    resolved_answers, selected_packs = _resolve_context(package_root, answers, existing_lock)
    previous_packs = (
        existing_lock.get("selectedPacks", [])
        if existing_lock and isinstance(existing_lock.get("selectedPacks"), list)
        else []
    )
    pruned = _prune_deselected_pack_skills(workspace, package_root, previous_packs, selected_packs)
    pruned.extend(_prune_deselected_pack_mcp(workspace, package_root, previous_packs, selected_packs))
    pruned.extend(_prune_orphan_mcp_scripts(workspace, package_root, resolved_answers, selected_packs))
    entries = managed_entries(policy, package_root, selected_packs, resolved_answers)
    tokens = _inspect_tokens(workspace, package_root, resolved_answers)
    report = inspect(workspace, package_root, answers=resolved_answers)
    status_by_id = {row["id"]: row["status"] for row in report["files"]}
    written: list[str] = []
    skipped: list[str] = []
    for entry in entries:
        status = status_by_id.get(entry.entry_id, "missing")
        if only_stale_or_missing and not force_all and status == "clean":
            skipped.append(entry.entry_id)
            continue
        target = workspace / entry.target_rel
        if target.is_file():
            _backup_file(workspace, target)
        source_bytes = materialize_source(package_root, entry, tokens, resolved_answers)
        payload = apply_write_strategy(entry, source_bytes, target)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        written.append(entry.entry_id)
    lock_payload = _build_lockfile_payload(
        workspace,
        package_root,
        entries,
        tokens,
        resolved_answers,
        selected_packs,
        existing_lock,
    )
    return {
        "written": written,
        "skipped": skipped,
        "pruned": pruned,
        "lockfile": str(LOCKFILE_REL),
        "profile": lock_payload.get("profile"),
        "selectedPacks": lock_payload.get("selectedPacks"),
        "setupAnswers": lock_payload.get("setupAnswers"),
    }


def plan_setup(
    workspace: Path,
    package_root: Path,
    answers: dict[str, Any] | None = None,
) -> dict[str, Any]:
    existing_lock = read_lockfile(workspace)
    resolved_answers, selected_packs = _resolve_context(package_root, answers, existing_lock)
    report = inspect(workspace, package_root, answers=resolved_answers)
    to_write = [
        row for row in report["files"] if row["status"] in {"missing", "stale"}
    ]
    return {
        "command": "plan-setup",
        "installState": report["installState"],
        "repairReasons": report["repairReasons"],
        "answers": resolved_answers,
        "wouldWrite": [row["id"] for row in to_write] if existing_lock else [row["id"] for row in report["files"]],
        "files": report["files"],
        "profile": resolved_answers.get("profile.selected", "balanced"),
        "selectedPacks": selected_packs,
    }


def setup(
    workspace: Path,
    package_root: Path,
    *,
    answers: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return apply_entries(
        workspace,
        package_root,
        only_stale_or_missing=False,
        answers=answers,
    )


def update(
    workspace: Path,
    package_root: Path,
    *,
    answers: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return apply_entries(
        workspace,
        package_root,
        only_stale_or_missing=True,
        answers=answers,
    )


def repair(
    workspace: Path,
    package_root: Path,
    *,
    answers: dict[str, Any] | None = None,
) -> dict[str, Any]:
    report = inspect(workspace, package_root, answers=answers)
    reasons = report["repairReasons"]
    if not reasons and report["installState"] == "installed":
        return {
            "command": "repair",
            "written": [],
            "skipped": [row["id"] for row in report["files"]],
            "repairReasons": [],
            "lockfile": str(LOCKFILE_REL),
            "message": "No repair needed",
        }
    result = apply_entries(
        workspace,
        package_root,
        only_stale_or_missing=True,
        force_all=lockfile_is_malformed(read_lockfile(workspace)),
        answers=answers,
    )
    return {"command": "repair", "repairReasons": reasons, **result}


def factory_restore(
    workspace: Path,
    package_root: Path,
    *,
    answers: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result = apply_entries(
        workspace,
        package_root,
        only_stale_or_missing=False,
        force_all=True,
        answers=answers,
    )
    return {"command": "factory-restore", "factoryRestore": True, **result}
