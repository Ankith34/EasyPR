from __future__ import annotations

import json

import pytest

from easypr import repository
from easypr.repository import RepositoryError, extract_terms, find_relevant_code

from conftest import write


def _by_path(result: dict) -> dict[str, dict]:
    return {r["path"]: r for r in result["results"]}


def test_extract_terms_handles_identifiers_and_stopwords():
    terms = extract_terms("Fix the login_user bug when parseConfig fails")
    assert "login_user" in terms and "login" in terms and "user" in terms
    assert "parseconfig" in terms and "parse" in terms and "config" in terms
    assert "the" not in terms and "fix" not in terms and "bug" not in terms


def test_finds_implementation_with_line_numbers(sample_repo):
    result = find_relevant_code(sample_repo, "login_user rejects wrong password")
    hits = _by_path(result)
    auth = hits["app/auth.py"]
    assert auth["role"] == "source" and auth["kind"] == "inferred"
    definition = [m for m in auth["matches"] if m["is_definition"]]
    assert definition and definition[0]["line"] == 4
    assert "def login_user" in definition[0]["text"]
    assert "Verify" in auth["why"]


def test_source_ranks_above_unrelated_and_tests_are_labelled(sample_repo):
    result = find_relevant_code(sample_repo, "login_user")
    hits = _by_path(result)
    assert hits["tests/test_auth.py"]["role"] == "test"
    assert "app/utils.py" not in hits
    assert result["results"][0]["path"] == "app/auth.py"
    texts = " ".join(s["text"] for s in result["suggestions"])
    assert "app/auth.py" in texts and "tests/test_auth.py" in texts


def test_never_reads_sensitive_files_or_ignored_dirs_or_binaries(sample_repo):
    # .env contains both "login_user" and a secret; node_modules and logo.png contain "login_user" too.
    result = find_relevant_code(sample_repo, "login_user")
    paths = set(_by_path(result))
    assert ".env" not in paths
    assert not any(p.startswith("node_modules") for p in paths)
    assert "logo.png" not in paths
    assert "supersecretvalue123456" not in json.dumps(result)
    assert "leaked" not in json.dumps(result)
    assert any("commonly hold secrets" in n for n in result["notes"])


def test_snippets_are_redacted_and_clipped(tmp_path):
    write(tmp_path / "config.py", 'password = "hunter2hunter2"  # login\n' + "login " + "x" * 500 + "\n")
    result = find_relevant_code(tmp_path, "login")
    snippets = [m["text"] for m in result["results"][0]["matches"]]
    assert all("hunter2hunter2" not in s for s in snippets)
    assert all(len(s) <= repository.MAX_SNIPPET_CHARS for s in snippets)


def test_max_results_is_clamped(tmp_path):
    for i in range(30):
        write(tmp_path / f"mod{i}.py", "widget = 1\n")
    assert len(find_relevant_code(tmp_path, "widget", max_results=999)["results"]) == repository.MAX_RESULTS_CAP
    assert len(find_relevant_code(tmp_path, "widget", max_results=0)["results"]) == 1
    assert len(find_relevant_code(tmp_path, "widget", max_results=3)["results"]) == 3


def test_no_match_gives_honest_note(sample_repo):
    result = find_relevant_code(sample_repo, "zzzquuxnonexistent")
    assert result["results"] == [] and any("Nothing matched" in n for n in result["notes"])


@pytest.mark.parametrize("query", ["", "   ", "to be or", "!!! ???"])
def test_unusable_queries_raise(sample_repo, query):
    with pytest.raises(RepositoryError):
        find_relevant_code(sample_repo, query)


def test_large_files_are_skipped(tmp_path, monkeypatch):
    monkeypatch.setattr(repository, "MAX_FILE_BYTES", 50)
    write(tmp_path / "big.py", "login = 1\n" * 100)
    result = find_relevant_code(tmp_path, "login")
    assert result["results"] == [] and any("skipped" in n for n in result["notes"])


def test_respects_approved_roots(sample_repo, tmp_path_factory):
    other = tmp_path_factory.mktemp("other")
    roots = repository.parse_allowed_roots([sample_repo])
    with pytest.raises(RepositoryError, match="outside the approved"):
        find_relevant_code(other, "login", allowed_roots=roots)
