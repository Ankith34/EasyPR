from __future__ import annotations

import json

from easypr.repository import get_setup_guide

from conftest import write


def _hint(result: dict, purpose: str, command: str) -> dict | None:
    for item in result["manifest_hints"]:
        if item["purpose"] == purpose and item["command"] == command:
            return item
    return None


def test_documented_steps_come_from_readme_with_location(sample_repo):
    result = get_setup_guide(sample_repo)
    blocks = result["documented_steps"]
    assert [b["section"] for b in blocks] == ["Installation", "Running tests"]
    install = blocks[0]
    assert install["source"] == "README.md"
    assert install["lines"] == ["pip install -r requirements.txt"]  # "$ " prompt stripped
    assert install["kind"] == "documented"
    assert install["start_line"] == 8  # line number of the first line inside the block


def test_blocks_outside_setup_sections_are_ignored(sample_repo):
    lines = [line for b in get_setup_guide(sample_repo)["documented_steps"] for line in b["lines"]]
    assert not any("not under a setup heading" in line for line in lines)


def test_hints_are_inferred_and_never_verified(sample_repo):
    result = get_setup_guide(sample_repo)
    hint = _hint(result, "install", "pip install -r requirements.txt")
    assert hint and hint["kind"] == "inferred" and hint["verified"] is False
    assert all(h["verified"] is False and h["kind"] == "inferred" for h in result["manifest_hints"])
    assert any("has not run" in w for w in result["warnings"])


def test_ci_commands_parsed_including_block_scalars(sample_repo):
    commands = [c["command"] for c in get_setup_guide(sample_repo)["ci_commands"]]
    assert commands == ["pip install -r requirements.txt", "pytest -q", "python -m compileall app"]


def test_contributing_docs_listed(sample_repo):
    paths = [d["path"] for d in get_setup_guide(sample_repo)["contributing_docs"]]
    assert "CONTRIBUTING.md" in paths


def test_node_project_hints(tmp_path):
    write(tmp_path / "package.json", json.dumps({"scripts": {"test": "jest", "build": "tsc", "x": "y"}}))
    write(tmp_path / "pnpm-lock.yaml", "")
    result = get_setup_guide(tmp_path)
    assert _hint(result, "install", "pnpm install")
    assert _hint(result, "test", "pnpm run test")["detail"] == 'scripts.test = "jest"'
    assert _hint(result, "build", "pnpm run build")
    assert not any(h["command"].endswith(" x") for h in result["manifest_hints"])


def test_broken_package_json_does_not_crash(tmp_path):
    write(tmp_path / "package.json", "{ not json")
    result = get_setup_guide(tmp_path)
    assert _hint(result, "install", "npm install")


def test_makefile_targets(tmp_path):
    write(tmp_path / "Makefile", "test:\n\tpytest\n\nlint:\n\truff .\nVAR := 1\n")
    result = get_setup_guide(tmp_path)
    assert _hint(result, "test", "make test")
    assert _hint(result, "lint", "make lint")


def test_pyproject_install_hint_has_caveat(tmp_path):
    write(tmp_path / "pyproject.toml", "[project]\nname='x'\n[tool.pytest.ini_options]\n")
    result = get_setup_guide(tmp_path)
    install = _hint(result, "install", "pip install -e .")
    assert install and "Check its docs" in install["detail"]
    assert _hint(result, "test", "pytest")


def test_env_template_is_noted_but_never_read(tmp_path):
    write(tmp_path / ".env.example", "API_KEY=changeme123456\n")
    result = get_setup_guide(tmp_path)
    hint = _hint(result, "configure", "cp .env.example .env")
    assert hint and "changeme123456" not in json.dumps(result)


def test_rst_readme_is_flagged_as_not_parsed(tmp_path):
    write(tmp_path / "README.rst", "Title\n=====\n")
    result = get_setup_guide(tmp_path)
    assert result["readme"] == {"path": "README.rst", "parsed": False, "kind": "fact"}
    assert any("not Markdown" in w for w in result["warnings"])


def test_repo_without_docs_reports_honestly(tmp_path):
    result = get_setup_guide(tmp_path)
    assert result["readme"] is None
    assert result["documented_steps"] == [] and result["manifest_hints"] == []
    assert any("No README" in w for w in result["warnings"])


def test_secrets_in_readme_blocks_are_redacted(tmp_path):
    write(tmp_path / "README.md", "## Setup\n\n```\nexport API_KEY=abcdef123456789\n```\n")
    lines = get_setup_guide(tmp_path)["documented_steps"][0]["lines"]
    assert "abcdef123456789" not in lines[0]
