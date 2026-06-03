"""Shared lifecycle data models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ManagedEntry:
    entry_id: str
    source_rel: str
    target_rel: str
    layer: str
    strategy: str = "replace"
    pack: str | None = None
    required_when: dict[str, bool | str] | None = None
