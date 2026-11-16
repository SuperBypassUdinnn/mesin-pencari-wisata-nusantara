#!/usr/bin/env python3
"""Automated 7-gate pre-flight quality pipeline for mesin-pencari-wisata-nusantara.

Usage:
    python3 scripts/verify_pipeline.py
    make verify

Gates:
    1. Directory integrity (required root files exist).
    2. requirements.txt dependency manifest validity.
    3. Makefile target availability (run, test, verify, lint).
    4. Clean Text Policy compliance (no decorative emojis or icons).
    5. No artificial timelines in documents and code comments.
    6. AGENTS.md session protocol presence.
    7. Mock evaluation (deterministic smoke test of project constants).
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "docs/TEAM_WORKFLOW.md",
    "docs/PROGRESS.md",
    "AGENTS.md",
    "requirements.txt",
    "Makefile",
    "scripts/verify_pipeline.py",
    "tests/test_scaffolding.py",
]

REQUIRED_DEPENDENCIES = [
    "fastapi",
    "uvicorn",
    "elasticsearch",
    "PySastrawi",
    "pydantic",
    "pytest",
    "beautifulsoup4",
    "requests",
]

REQUIRED_MAKE_TARGETS = ["run", "test", "verify", "lint"]

# A conservative sample of common decorative emoji/pictograph code points.
EMOJI_PATTERN = re.compile(
    r"[\U0001F600-\U0001F64F"  # emoticons
    r"\U0001F300-\U0001F5FF"  # miscellaneous symbols and pictographs
    r"\U0001F680-\U0001F6FF"  # transport and map symbols
    r"\U0001F1E0-\U0001F1FF"  # regional indicator symbols
    r"\U00002700-\U000027BF"  # dingbats
    r"\U00002600-\U000026FF"  # miscellaneous symbols
    r"\U0001F900-\U0001F9FF"  # supplemental symbols and pictographs
    r"\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-A
    r"\u200d"                # zero-width joiner
    r"\ufe0f"                # variation selector-16
    "]+"
)

TIMELINE_PATTERN = re.compile(
    r"\b(\d+\s*(minggu|hari|bulan|tahun))\b",
    re.IGNORECASE,
)

TEXT_EXTENSIONS = {".md", ".py", ".txt", ".json", ".yaml", ".yml", ".cfg", ".toml", "Makefile"}


def gate_directory_integrity() -> tuple[bool, str]:
    missing = [p for p in REQUIRED_FILES if not (REPO_ROOT / p).exists()]
    if missing:
        return False, "Missing required files: " + ", ".join(missing)
    return True, f"All {len(REQUIRED_FILES)} required files present"


def gate_requirements_manifest() -> tuple[bool, str]:
    path = REPO_ROOT / "requirements.txt"
    if not path.exists():
        return False, "requirements.txt missing"
    content = path.read_text(encoding="utf-8")
    missing = [dep for dep in REQUIRED_DEPENDENCIES if dep.lower() not in content.lower()]
    if missing:
        return False, "Missing dependencies: " + ", ".join(missing)
    return True, f"All {len(REQUIRED_DEPENDENCIES)} core dependencies declared"


def gate_makefile_targets() -> tuple[bool, str]:
    path = REPO_ROOT / "Makefile"
    if not path.exists():
        return False, "Makefile missing"
    content = path.read_text(encoding="utf-8")
    missing = [t for t in REQUIRED_MAKE_TARGETS if not re.search(rf"^\s*{t}\s*:", content, re.MULTILINE)]
    if missing:
        return False, "Missing Makefile targets: " + ", ".join(missing)
    return True, f"All {len(REQUIRED_MAKE_TARGETS)} Makefile targets declared"


def scan_text(path: Path) -> list[str]:
    findings: list[str] = []
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return findings
    for match in EMOJI_PATTERN.finditer(content):
        findings.append(f"emoji at {path}:{content.count(chr(10), 0, match.start()) + 1}: U+{ord(match.group(0)):04X}")
    for match in TIMELINE_PATTERN.finditer(content):
        findings.append(f"artificial timeline at {path}:{content.count(chr(10), 0, match.start()) + 1}: {match.group(0)}")
    return findings


def gate_clean_text_policy() -> tuple[bool, str]:
    findings: list[str] = []
    for root, _dirs, files in os.walk(REPO_ROOT):
        parts = root.split(os.sep)
        if ".git" in parts or ".superpowers" in parts or "superpowers" in parts:
            continue
        for name in files:
            p = Path(root) / name
            if p.suffix in TEXT_EXTENSIONS or p.name == "Makefile":
                findings.extend(scan_text(p))
    if findings:
        return False, "Clean Text Policy violations: " + "; ".join(findings[:10])
    return True, "No emoji or decorative icon violations detected"


def gate_no_artificial_timelines() -> tuple[bool, str]:
    findings: list[str] = []
    for root, _dirs, files in os.walk(REPO_ROOT):
        parts = root.split(os.sep)
        if ".git" in parts or ".superpowers" in parts or "superpowers" in parts:
            continue
        for name in files:
            p = Path(root) / name
            if p.suffix in TEXT_EXTENSIONS or p.name == "Makefile":
                findings.extend(scan_text(p))
    timeline_only = [f for f in findings if "artificial timeline" in f]
    if timeline_only:
        return False, "Artificial timeline violations: " + "; ".join(timeline_only[:10])
    return True, "No artificial timeline mentions detected"


def gate_agents_md() -> tuple[bool, str]:
    path = REPO_ROOT / "AGENTS.md"
    if not path.exists():
        return False, "AGENTS.md missing"
    content = path.read_text(encoding="utf-8")
    required = ["Session Start", "Directory Boundary", "Clean Text Policy", "Pre-commit"]
    missing = [r for r in required if r not in content]
    if missing:
        return False, "AGENTS.md missing sections: " + ", ".join(missing)
    return True, "AGENTS.md session protocol present"


def gate_mock_evaluation() -> tuple[bool, str]:
    """Deterministic smoke test: verify project constants are internally consistent."""
    checks = 0
    total = 3
    checks += 1 if len(REQUIRED_FILES) == 7 else 0
    checks += 1 if len(REQUIRED_DEPENDENCIES) == 8 else 0
    checks += 1 if len(REQUIRED_MAKE_TARGETS) == 4 else 0
    if checks != total:
        return False, f"Mock evaluation failed: {checks}/{total} checks passed"
    return True, f"Mock evaluation passed ({checks}/{total} checks)"


GATES = [
    ("Gate 1: Directory Integrity", gate_directory_integrity),
    ("Gate 2: Requirements Manifest", gate_requirements_manifest),
    ("Gate 3: Makefile Targets", gate_makefile_targets),
    ("Gate 4: Clean Text Policy", gate_clean_text_policy),
    ("Gate 5: No Artificial Timelines", gate_no_artificial_timelines),
    ("Gate 6: AGENTS.md Protocol", gate_agents_md),
    ("Gate 7: Mock Evaluation", gate_mock_evaluation),
]


def main() -> int:
    print("Verifikasi Pipeline — 7-Gate Quality Gate")
    print("Repository: mesin-pencari-wisata-nusantara (Kelompok 10)")
    print("-" * 60)

    passed = 0
    failed = 0
    for name, func in GATES:
        ok, message = func()
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {name}: {message}")
        if ok:
            passed += 1
        else:
            failed += 1

    print("-" * 60)
    print(f"Result: {passed} passed, {failed} failed out of {len(GATES)} gates")
    if failed:
        print("QUALITY GATE FAILED — fix violations before committing.")
        return 1
    print("QUALITY GATE PASSED — all gates green.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
