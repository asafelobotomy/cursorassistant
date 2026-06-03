#!/usr/bin/env python3
"""Regenerate install-manifest.json from install-policy.json and pack skills."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def package_version(package_root: Path) -> str:
    version_file = package_root / "VERSION"
    if not version_file.is_file():
        return "0.0.0"
    return version_file.read_text(encoding="utf-8").strip().splitlines()[0]


def discover_pack_entries(package_root: Path) -> list[dict]:
    entries: list[dict] = []
    packs_root = package_root / "packs"
    if not packs_root.is_dir():
        return entries
    for pack_dir in sorted(packs_root.iterdir()):
        if not pack_dir.is_dir():
            continue
        skills_root = pack_dir / "skills"
        if not skills_root.is_dir():
            continue
        pack_id = pack_dir.name
        for skill_dir in sorted(skills_root.iterdir()):
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.is_file():
                continue
            skill_name = skill_dir.name
            source = f"packs/{pack_id}/skills/{skill_name}/SKILL.md"
            entries.append(
                {
                    "id": f"packs.{pack_id}.{skill_name}",
                    "source": source,
                    "target": f".cursor/skills/{skill_name}/SKILL.md",
                    "layer": "pack",
                    "pack": pack_id,
                    "strategy": "replace",
                    "requiredWhen": [f"packs.selected={pack_id}"],
                    "hash": sha256_file(skill_file),
                }
            )
    return entries


def discover_mcp_entries(package_root: Path) -> list[dict]:
    import sys

    root = str(package_root)
    if root not in sys.path:
        sys.path.insert(0, root)
    from scripts.lifecycle import mcp_scripts

    rows: list[dict] = []
    for entry in mcp_scripts.mcp_script_entries(
        package_root,
        mcp_enabled=True,
        selected_packs=["lean", "secure", "tdd"],
    ):
        source = package_root / entry.source_rel
        if not source.is_file():
            continue
        row = {
            "id": entry.entry_id,
            "source": entry.source_rel,
            "target": entry.target_rel,
            "layer": entry.layer,
            "strategy": entry.strategy,
            "hash": sha256_file(source),
        }
        if entry.pack:
            row["pack"] = entry.pack
        if entry.required_when:
            row["requiredWhen"] = [
                f"{key}={str(value).lower()}" if isinstance(value, bool) else f"{key}={value}"
                for key, value in entry.required_when.items()
            ]
        else:
            row["requiredWhen"] = []
        rows.append(row)
    return rows


def generate_manifest(package_root: Path, policy: dict) -> dict:
    managed_files = []
    for entry in policy.get("entries", []):
        source = package_root / entry["source"]
        if not source.is_file():
            raise FileNotFoundError(f"Missing managed source: {entry['source']}")
        row = {
            "id": entry["id"],
            "source": entry["source"],
            "target": entry["target"],
            "layer": entry.get("layer", "core"),
            "strategy": entry.get("strategy", "replace"),
            "hash": sha256_file(source),
        }
        if entry.get("pack"):
            row["pack"] = entry["pack"]
        managed_files.append(row)
    managed_files.extend(discover_mcp_entries(package_root))
    managed_files.extend(discover_pack_entries(package_root))
    managed_files.sort(key=lambda row: row["target"])
    generation = policy.get("generationSettings", {})
    return {
        "schemaVersion": generation.get("manifestSchemaVersion", policy.get("schemaVersion", "0.4.0")),
        "packageVersion": package_version(package_root),
        "policySchemaVersion": policy.get("schemaVersion", "0.4.0"),
        "managedFiles": managed_files,
    }


def generate_catalog(package_root: Path) -> dict:
    pack_registry = json.loads(
        (package_root / "template/setup/pack-registry.json").read_text(encoding="utf-8")
    )
    profile_registry = json.loads(
        (package_root / "template/setup/profile-registry.json").read_text(encoding="utf-8")
    )
    return {
        "schemaVersion": "0.1.0",
        "commands": [
            "inspect",
            "plan-setup",
            "setup",
            "update",
            "repair",
            "factory-restore",
        ],
        "packs": [pack["id"] for pack in pack_registry.get("packs", []) if pack.get("status") == "active"],
        "agents": [
            "cursorLifecycle",
            "inventory",
            "review",
            "commit",
            "deps",
            "docs",
            "debugger",
            "planner",
            "researcher",
            "triage",
            "organise",
            "cleaner",
        ],
        "mcpServers": {
            "core": ["cursorTools"],
            "extensions": ["git", "devDocs", "memory"],
            "packs": {
                "secure": ["security", "secureOsv"],
                "tdd": ["workspaceTesting", "tddTestRunner"],
                "lean": ["leanContextBudget", "leanTestReporter"],
            },
            "deprecated": ["web", "filesystem", "time"],
        },
        "profiles": [
            profile["id"]
            for profile in profile_registry.get("profiles", [])
            if profile.get("status") == "active"
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate cursorAssistant install manifest.")
    parser.add_argument("--package-root", default=".", help="cursorAssistant package root")
    parser.add_argument(
        "--policy",
        default="template/setup/install-policy.json",
        help="Policy path relative to package root",
    )
    parser.add_argument(
        "--manifest-out",
        default=None,
        help="Manifest output path relative to package root",
    )
    args = parser.parse_args()
    package_root = Path(args.package_root).resolve()
    policy_path = package_root / args.policy
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    manifest = generate_manifest(package_root, policy)
    manifest_out = args.manifest_out or policy.get("generationSettings", {}).get(
        "manifestOutput", "template/setup/install-manifest.json"
    )
    output_path = package_root / manifest_out
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"manifest → {output_path.relative_to(package_root)}")

    catalog_path = package_root / "template/setup/catalog.json"
    catalog_path.write_text(json.dumps(generate_catalog(package_root), indent=2) + "\n", encoding="utf-8")
    print(f"catalog  → {catalog_path.relative_to(package_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
