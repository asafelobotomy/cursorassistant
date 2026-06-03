"""Pack and profile resolution for cursorAssistant installs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.lifecycle.models import ManagedEntry


def load_pack_registry(package_root: Path) -> dict[str, Any]:
    path = package_root / "template" / "setup" / "pack-registry.json"
    if not path.is_file():
        return {"packs": []}
    return json.loads(path.read_text(encoding="utf-8"))


def load_profile_registry(package_root: Path) -> dict[str, Any]:
    path = package_root / "template" / "setup" / "profile-registry.json"
    if not path.is_file():
        return {"profiles": []}
    return json.loads(path.read_text(encoding="utf-8"))


def active_pack_ids(pack_registry: dict[str, Any]) -> set[str]:
    return {
        pack["id"]
        for pack in pack_registry.get("packs", [])
        if pack.get("status") == "active"
    }


def profile_by_id(profile_registry: dict[str, Any], profile_id: str) -> dict[str, Any] | None:
    for profile in profile_registry.get("profiles", []):
        if profile.get("id") == profile_id:
            return profile
    return None


def resolve_selected_packs(
    package_root: Path,
    answers: dict[str, Any],
    lockfile: dict[str, Any] | None,
) -> list[str]:
    pack_registry = load_pack_registry(package_root)
    profile_registry = load_profile_registry(package_root)
    active = active_pack_ids(pack_registry)

    profile_id = answers.get("profile.selected", "balanced")
    profile = profile_by_id(profile_registry, profile_id)
    default_packs = list(profile.get("defaultPacks", [])) if profile else []

    if "packs.selected" in answers:
        selected = answers["packs.selected"]
    elif lockfile and isinstance(lockfile.get("selectedPacks"), list):
        selected = lockfile["selectedPacks"]
    else:
        selected = default_packs

    if not isinstance(selected, list):
        selected = default_packs

    resolved = [pack_id for pack_id in selected if pack_id in active]
    return sorted(set(resolved))


def pack_skill_entries(package_root: Path, pack_id: str) -> list[ManagedEntry]:
    skills_root = package_root / "packs" / pack_id / "skills"
    if not skills_root.is_dir():
        return []
    entries: list[ManagedEntry] = []
    for skill_dir in sorted(skills_root.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.is_file():
            continue
        skill_name = skill_dir.name
        entries.append(
            ManagedEntry(
                entry_id=f"packs.{pack_id}.{skill_name}",
                source_rel=f"packs/{pack_id}/skills/{skill_name}/SKILL.md",
                target_rel=f".cursor/skills/{skill_name}/SKILL.md",
                layer="pack",
                strategy="replace",
                pack=pack_id,
            )
        )
    return entries


def all_pack_skill_names(package_root: Path, pack_id: str) -> list[str]:
    skills_root = package_root / "packs" / pack_id / "skills"
    if not skills_root.is_dir():
        return []
    return sorted(
        path.name
        for path in skills_root.iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    )
