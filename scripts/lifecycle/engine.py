"""Minimal install, inspect, and update engine for Cursor-managed surfaces."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LOCKFILE_REL = Path(".cursor") / "cursorAssistant-lock.json"
BACKUP_ROOT_REL = Path(".cursor") / ".cursorAssistant-backup"
TOKEN_PATTERN = re.compile(r"\{\{([A-Z0-9_]+)\}\}")


@dataclass(frozen=True)
class ManagedEntry:
    entry_id: str
    source_rel: str
    target_rel: str
    layer: str


def package_version(package_root: Path) -> str:
    version_file = package_root / "VERSION"
    if not version_file.is_file():
        return "0.0.0"
    return version_file.read_text(encoding="utf-8").strip().splitlines()[0]


def load_policy(package_root: Path) -> dict[str, Any]:
    path = package_root / "template" / "setup" / "install-policy.json"
    return json.loads(path.read_text(encoding="utf-8"))


def managed_entries(policy: dict[str, Any]) -> list[ManagedEntry]:
    entries: list[ManagedEntry] = []
    for item in policy.get("entries", []):
        entries.append(
            ManagedEntry(
                entry_id=item["id"],
                source_rel=item["source"],
                target_rel=item["target"],
                layer=item.get("layer", "core"),
            )
        )
    return entries


def _sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _default_tokens(workspace: Path) -> dict[str, str]:
    return {
        "WORKSPACE_NAME": workspace.name or "workspace",
        "PACKAGE_VERSION": "0.0.0",
    }


def render_tokens(text: str, tokens: dict[str, str]) -> str:
    def repl(match: re.Match[str]) -> str:
        key = match.group(1)
        return tokens.get(key, match.group(0))

    return TOKEN_PATTERN.sub(repl, text)


def materialize_source(
    package_root: Path,
    entry: ManagedEntry,
    tokens: dict[str, str],
) -> bytes:
    source = package_root / entry.source_rel
    if not source.is_file():
        raise FileNotFoundError(f"Missing package source: {entry.source_rel}")
    raw = source.read_text(encoding="utf-8")
    return render_tokens(raw, tokens).encode("utf-8")


def lockfile_path(workspace: Path) -> Path:
    return workspace / LOCKFILE_REL


def read_lockfile(workspace: Path) -> dict[str, Any] | None:
    path = lockfile_path(workspace)
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_lockfile(workspace: Path, payload: dict[str, Any]) -> None:
    path = lockfile_path(workspace)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def inspect(workspace: Path, package_root: Path) -> dict[str, Any]:
    policy = load_policy(package_root)
    entries = managed_entries(policy)
    lock = read_lockfile(workspace)
    installed = lock is not None
    file_rows: list[dict[str, Any]] = []
    stale = 0
    missing = 0
    for entry in entries:
        target = workspace / entry.target_rel
        expected = materialize_source(package_root, entry, _default_tokens(workspace))
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
    return {
        "packageName": policy.get("packageName", "cursorAssistant"),
        "packageVersion": package_version(package_root),
        "installState": install_state,
        "lockfilePresent": installed,
        "summary": {"managed": len(entries), "stale": stale, "missing": missing},
        "files": file_rows,
    }


def _backup_file(workspace: Path, target: Path) -> None:
    if not target.is_file():
        return
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_dir = workspace / BACKUP_ROOT_REL / stamp
    dest = backup_dir / target.relative_to(workspace)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(target, dest)


def apply_entries(
    workspace: Path,
    package_root: Path,
    *,
    only_stale_or_missing: bool,
) -> dict[str, Any]:
    policy = load_policy(package_root)
    entries = managed_entries(policy)
    tokens = _default_tokens(workspace)
    tokens["PACKAGE_VERSION"] = package_version(package_root)
    report = inspect(workspace, package_root)
    status_by_id = {row["id"]: row["status"] for row in report["files"]}
    written: list[str] = []
    skipped: list[str] = []
    for entry in entries:
        status = status_by_id.get(entry.entry_id, "missing")
        if only_stale_or_missing and status == "clean":
            skipped.append(entry.entry_id)
            continue
        target = workspace / entry.target_rel
        if target.is_file():
            _backup_file(workspace, target)
        payload = materialize_source(package_root, entry, tokens)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        written.append(entry.entry_id)
    hashes = {
        entry.entry_id: _sha256_bytes(
            materialize_source(package_root, entry, tokens)
        )
        for entry in entries
    }
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    write_lockfile(
        workspace,
        {
            "schemaVersion": "0.1.0",
            "package": {
                "name": policy.get("packageName", "cursorAssistant"),
                "version": package_version(package_root),
                "packageRoot": str(package_root.resolve()),
            },
            "timestamps": {"appliedAt": now, "updatedAt": now},
            "profile": "balanced",
            "selectedPacks": [],
            "fileHashes": hashes,
        },
    )
    return {"written": written, "skipped": skipped, "lockfile": str(LOCKFILE_REL)}


def setup(workspace: Path, package_root: Path) -> dict[str, Any]:
    return apply_entries(workspace, package_root, only_stale_or_missing=False)


def update(workspace: Path, package_root: Path) -> dict[str, Any]:
    return apply_entries(workspace, package_root, only_stale_or_missing=True)
