import os


def test_project_structure_exists():
    required_paths = [
        "docs/TEAM_WORKFLOW.md",
        "docs/PROGRESS.md",
        "AGENTS.md",
        "requirements.txt",
        "Makefile",
        "scripts/verify_pipeline.py"
    ]
    for path in required_paths:
        assert os.path.exists(path), f"Required file missing: {path}"
