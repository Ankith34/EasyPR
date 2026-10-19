from __future__ import annotations

import os
from pathlib import Path

import pytest

from easypr import repository
from easypr.repository import RepositoryError, inspect_repository, parse_allowed_roots


def _paths(result: dict) -> set[str]:
    return {item["path"] for item in result["important_files"]}


# ---- basic inspection ---------------------------------------------------- #


def test_inspect_basic_layout(sample_repo):
    result = inspect_repository(sample_repo)
    assert result["name"] == "sample"
    assert set(result["top_level"]["directories"]) >= {"app", "tests"}
    assert "README.md" in result["top_level"]["files"]


def test_inspect_ignores_noise_directories(sample_repo):
    result = inspect_repository(sample_repo)
    assert "node_modules" not in result["top_level"]["directories"]
    assert "node_modules" in result["top_level"]["ignored_directories"]
    # The JavaScript file inside node_modules must not be counted.
    assert all(item["language"] != "JavaScript" for item in result["languages"])


def test_inspect_detects_language_and_project_type(sample_repo):
    result = inspect_repository(sample_repo)
    assert result["languages"][0]["language"] == "Python"
    assert result["languages"][0]["share"] == 1.0
    assert result["project_types"][0]["type"] == "Python project"
    assert result["project_types"][0]["evidence"] == ["requirements.txt"]
    names = {f["name"] for f in result["frameworks"]}
    assert {"flask", "pytest"} <= names


def test_inspect_finds_important_files(sample_repo):
    paths = _paths(inspect_repository(sample_repo))
    assert {"README.md", "CONTRIBUTING.md", "LICENSE", "requirements.txt"} <= paths
    assert ".github/workflows/ci.yml" in paths
    assert "tests/" in paths


def test_every_finding_has_a_kind(sample_repo):
    result = inspect_repository(sample_repo)
    for key in ("important_files", "languages", "project_types", "frameworks"):
        assert all(item["kind"] in {"fact", "inferred"} for item in result[key])


def test_inspect_empty_directory(tmp_path):
    result = inspect_repository(tmp_path)
    assert result["languages"] == []
    assert result["important_files"] == []
    assert result["stats"]["files_scanned"] == 0
    assert any("No recognised source-code files" in n for n in result["notes"])


def test_scan_limit_is_reported(sample_repo, monkeypatch):
    monkeypatch.setattr(repository, "MAX_FILES_SCANNED", 2)
    result = inspect_repository(sample_repo)
    assert result["stats"]["scan_truncated"] is True
    assert any("partial" in n for n in result["notes"])


# ---- invalid input ------------------------------------------------------- #


def test_nonexistent_path(tmp_path):
    with pytest.raises(RepositoryError, match="does not exist"):
        inspect_repository(tmp_path / "nope")


def test_file_is_not_a_directory(sample_repo):
    with pytest.raises(RepositoryError, match="not a directory"):
        inspect_repository(sample_repo / "README.md")


@pytest.mark.parametrize("bad", ["", "   ", "a\x00b"])
def test_invalid_path_strings(bad):
    with pytest.raises(RepositoryError):
        inspect_repository(bad)


# ---- approved roots and symlinks ----------------------------------------- #


def test_path_inside_root_is_allowed(sample_repo):
    roots = parse_allowed_roots([sample_repo.parent])
    assert inspect_repository(sample_repo, roots)["name"] == "sample"


def test_path_outside_root_is_rejected(sample_repo, tmp_path_factory):
    other = tmp_path_factory.mktemp("other")
    roots = parse_allowed_roots([sample_repo])
    with pytest.raises(RepositoryError, match="outside the approved"):
        inspect_repository(other, roots)


def test_dotdot_traversal_is_rejected(sample_repo):
    roots = parse_allowed_roots([sample_repo])
    with pytest.raises(RepositoryError, match="outside the approved"):
        inspect_repository(sample_repo / ".." / "..", roots)


def test_relative_path_resolves_against_first_root(sample_repo):
    roots = parse_allowed_roots([sample_repo.parent])
    assert inspect_repository("sample", roots)["name"] == "sample"


def test_symlink_root_pointing_outside_is_rejected(sample_repo, tmp_path_factory):
    outside = tmp_path_factory.mktemp("outside")
    link = sample_repo / "escape"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks not supported here")
    roots = parse_allowed_roots([sample_repo])
    with pytest.raises(RepositoryError, match="outside the approved"):
        inspect_repository(link, roots)


def test_symlinks_inside_repo_are_not_followed(sample_repo, tmp_path_factory):
    outside = tmp_path_factory.mktemp("outside")
    (outside / "secret.py").write_text("def stolen(): pass\n")
    try:
        (sample_repo / "link_dir").symlink_to(outside, target_is_directory=True)
        (sample_repo / "link_file.py").symlink_to(outside / "secret.py")
    except (OSError, NotImplementedError):
        pytest.skip("symlinks not supported here")
    result = inspect_repository(sample_repo)
    assert result["stats"]["symlinks_skipped"] >= 2
    assert "link_dir" not in result["top_level"]["directories"]
    assert "link_file.py" not in result["top_level"]["files"]


def test_parse_allowed_roots_validation(sample_repo):
    with pytest.raises(RepositoryError, match="does not exist"):
        parse_allowed_roots([sample_repo / "missing"])
    with pytest.raises(RepositoryError, match="not a directory"):
        parse_allowed_roots([sample_repo / "README.md"])
    assert parse_allowed_roots([sample_repo, sample_repo]) == [sample_repo.resolve()]


# ---- redaction and sensitive files --------------------------------------- #


@pytest.mark.parametrize(
    "name", [".env", ".env.local", "id_rsa", "server.pem", "credentials.json", "secrets.yml"]
)
def test_sensitive_names_detected(name):
    assert repository.is_sensitive_file(name)


@pytest.mark.parametrize("name", ["README.md", "auth.py", "environment.py", "keyboard.py"])
def test_normal_names_not_sensitive(name):
    assert not repository.is_sensitive_file(name)


def test_redact_hides_secret_values():
    out = repository.redact('api_key = "abcd1234efgh5678"')
    assert "abcd1234efgh5678" not in out and "[REDACTED]" in out
    assert "AKIAIOSFODNN7EXAMPLE" not in repository.redact("id AKIAIOSFODNN7EXAMPLE")
    assert "author" in repository.redact('author = "someone"')  # not over-redacted
