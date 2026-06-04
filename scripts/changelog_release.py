#!/usr/bin/env python3
"""Verify CHANGELOG entries and extract release notes for GitHub Releases."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = ROOT / "CHANGELOG.md"
VERSION_FILE = ROOT / "VERSION"

HEADING_RE = re.compile(
    r"^## \[(?P<version>[^\]]+)\](?:\s+-\s+(?P<date>\d{4}-\d{2}-\d{2}))?\s*$"
)


def read_version(path: Path | None = None) -> str:
    text = (path or VERSION_FILE).read_text(encoding="utf-8").strip()
    line = text.splitlines()[0].strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", line):
        raise ValueError(f"Invalid VERSION: {line!r}")
    return line


def parse_sections(content: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current_version: str | None = None
    lines: list[str] = []

    for line in content.splitlines():
        match = HEADING_RE.match(line)
        if match:
            if current_version is not None:
                sections[current_version] = "\n".join(lines).strip()
            current_version = match.group("version")
            if current_version.lower() == "unreleased":
                current_version = None
                lines = []
                continue
            lines = []
            continue
        if current_version is not None:
            lines.append(line)

    if current_version is not None:
        sections[current_version] = "\n".join(lines).strip()
    return sections


def section_for_version(version: str, changelog_path: Path | None = None) -> str:
    path = changelog_path or CHANGELOG
    if not path.is_file():
        raise FileNotFoundError(f"Missing CHANGELOG: {path}")
    sections = parse_sections(path.read_text(encoding="utf-8"))
    body = sections.get(version, "").strip()
    if not body:
        raise ValueError(
            f"CHANGELOG has no section for version {version}. "
            f"Add '## [{version}] - YYYY-MM-DD' with release notes."
        )
    return body


def cmd_verify(version: str | None, changelog: Path) -> int:
    ver = version or read_version()
    section_for_version(ver, changelog)
    print(f"CHANGELOG ok for {ver}")
    return 0


def cmd_extract(version: str | None, changelog: Path, output: Path | None) -> int:
    ver = version or read_version()
    body = section_for_version(ver, changelog)
    notes = f"## cursorAssistant {ver}\n\n{body}\n"
    if output:
        output.write_text(notes, encoding="utf-8")
        print(f"Wrote {output}")
    else:
        print(notes, end="")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--changelog", type=Path, default=CHANGELOG)
    sub = parser.add_subparsers(dest="command", required=True)

    verify = sub.add_parser("verify", help="Ensure CHANGELOG documents a version")
    verify.add_argument("--version", help="Version to check (default: VERSION file)")

    extract = sub.add_parser("extract", help="Write GitHub release notes markdown")
    extract.add_argument("--version", help="Version to extract (default: VERSION file)")
    extract.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file path (default: stdout)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "verify":
            return cmd_verify(args.version, args.changelog)
        if args.command == "extract":
            return cmd_extract(args.version, args.changelog, args.output)
        parser.error(f"unknown command: {args.command}")
        return 2
    except (OSError, ValueError, FileNotFoundError) as exc:
        print(exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
