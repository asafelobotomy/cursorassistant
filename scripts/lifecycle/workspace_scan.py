"""Silent workspace stack detection for install-time tokens."""

from __future__ import annotations

import json
from pathlib import Path


def scan_workspace_stack(workspace: Path) -> dict[str, str]:
    """Return PRIMARY_LANGUAGE, PACKAGE_MANAGER, TEST_COMMAND when detected."""
    results: dict[str, str] = {}
    language = _detect_language(workspace)
    if language:
        results["PRIMARY_LANGUAGE"] = language
    package_manager = _detect_package_manager(workspace)
    if package_manager:
        results["PACKAGE_MANAGER"] = package_manager
    test_command = _detect_test_command(workspace)
    if test_command:
        results["TEST_COMMAND"] = test_command
    return results


_LANGUAGE_CHECKS: list[tuple[str, str]] = [
    ("Cargo.toml", "Rust"),
    ("go.mod", "Go"),
    ("pom.xml", "Java"),
    ("build.gradle", "Java"),
    ("build.gradle.kts", "Java"),
    ("Gemfile", "Ruby"),
]


def _detect_language(workspace: Path) -> str | None:
    for filename in ("pyproject.toml", "setup.py", "requirements.txt", "requirements-dev.txt"):
        if (workspace / filename).exists():
            return "Python"
    if (workspace / "package.json").exists():
        if (workspace / "tsconfig.json").exists():
            return "TypeScript"
        return "JavaScript"
    for filename, language in _LANGUAGE_CHECKS:
        if (workspace / filename).exists():
            return language
    return None


def _detect_package_manager(workspace: Path) -> str | None:
    if (workspace / "yarn.lock").exists():
        return "yarn"
    if (workspace / "pnpm-lock.yaml").exists():
        return "pnpm"
    if (workspace / "package-lock.json").exists():
        return "npm"
    if (workspace / "poetry.lock").exists():
        return "Poetry"
    pyproject = workspace / "pyproject.toml"
    if pyproject.exists():
        try:
            if "[tool.poetry]" in pyproject.read_text(encoding="utf-8"):
                return "Poetry"
        except OSError:
            pass
    if (workspace / "Pipfile").exists():
        return "pipenv"
    if (workspace / "Cargo.toml").exists():
        return "Cargo"
    if (workspace / "go.mod").exists():
        return "go modules"
    if (workspace / "requirements.txt").exists() or (workspace / "requirements-dev.txt").exists():
        return "pip"
    return None


def _detect_test_command(workspace: Path) -> str | None:
    pyproject = workspace / "pyproject.toml"
    if pyproject.exists():
        try:
            text = pyproject.read_text(encoding="utf-8")
            if "pytest" in text or "[tool.pytest" in text:
                return "pytest"
        except OSError:
            pass
    pkg = workspace / "package.json"
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text(encoding="utf-8"))
            test_script = (data.get("scripts") or {}).get("test")
            no_test = 'echo "Error: no test specified"'
            if (
                isinstance(test_script, str)
                and test_script
                and test_script.strip() != no_test
                and not test_script.strip().lower().startswith("echo ")
            ):
                return test_script
        except (OSError, json.JSONDecodeError):
            pass
    if (workspace / "scripts" / "run-tests.sh").exists():
        return "scripts/run-tests.sh"
    if (workspace / "go.mod").exists():
        return "go test ./..."
    if (workspace / "Cargo.toml").exists():
        return "cargo test"
    makefile = workspace / "Makefile"
    if makefile.exists():
        try:
            text = makefile.read_text(encoding="utf-8")
            if "\ntest:" in text or text.startswith("test:"):
                return "make test"
        except OSError:
            pass
    if _detect_language(workspace) == "Python" and (workspace / "tests").is_dir():
        return 'python3 -m unittest discover -s tests -p "test_*.py"'
    return None
