"""Tests for the MCP layer, using the SDK's own in-memory client."""

from __future__ import annotations

import anyio
import pytest
from mcp.client import Client

from easypr import __version__, repository, server


def run_with_client(roots, scenario):
    """Start the server in memory, run ``scenario(client)``, return its result."""

    async def main():
        async with Client(server.create_server(roots)) as client:
            return await scenario(client)

    return anyio.run(main)


@pytest.fixture
def roots(sample_repo):
    return repository.parse_allowed_roots([sample_repo.parent])


def test_lists_the_three_read_only_tools(roots):
    async def scenario(client):
        return (await client.list_tools()).tools

    tools = {t.name: t for t in run_with_client(roots, scenario)}
    assert set(tools) == {"inspect_repository", "get_setup_guide", "find_relevant_code"}
    for tool in tools.values():
        assert tool.description
        assert tool.annotations.read_only_hint is True
        assert tool.annotations.destructive_hint is False
    assert "query" in tools["find_relevant_code"].input_schema["properties"]


def test_inspect_repository_returns_structured_result(roots, sample_repo):
    async def scenario(client):
        return await client.call_tool("inspect_repository", {"path": str(sample_repo)})

    result = run_with_client(roots, scenario)
    assert not result.is_error
    assert result.structured_content["name"] == "sample"
    assert result.structured_content["languages"][0]["language"] == "Python"


def test_relative_path_uses_first_root(roots):
    async def scenario(client):
        return await client.call_tool("get_setup_guide", {"path": "sample"})

    result = run_with_client(roots, scenario)
    assert not result.is_error
    assert result.structured_content["documented_steps"][0]["section"] == "Installation"


def test_find_relevant_code_over_mcp(roots, sample_repo):
    async def scenario(client):
        return await client.call_tool(
            "find_relevant_code",
            {"path": str(sample_repo), "query": "login_user fails", "max_results": 3},
        )

    result = run_with_client(roots, scenario)
    assert not result.is_error
    assert result.structured_content["results"][0]["path"] == "app/auth.py"


def test_outside_root_returns_readable_error(roots, tmp_path_factory):
    outside = tmp_path_factory.mktemp("outside")

    async def scenario(client):
        return await client.call_tool("inspect_repository", {"path": str(outside)})

    result = run_with_client(roots, scenario)
    assert result.is_error
    assert "outside the approved" in result.content[0].text


def test_bad_query_returns_readable_error(roots, sample_repo):
    async def scenario(client):
        return await client.call_tool("find_relevant_code", {"path": str(sample_repo), "query": "  "})

    result = run_with_client(roots, scenario)
    assert result.is_error and "query is empty" in result.content[0].text


def test_server_instructions_tell_clients_to_keep_evidence_labels(roots):
    async def scenario(client):
        return client.instructions

    text = run_with_client(roots, scenario)
    assert "untrusted" in text and "Never claim" in text


# ---- command line entry point ------------------------------------------- #


def test_create_server_requires_a_root():
    with pytest.raises(ValueError):
        server.create_server([])


def test_main_refuses_to_start_without_roots(monkeypatch, capsys):
    monkeypatch.delenv(server.ENV_ROOTS, raising=False)
    with pytest.raises(SystemExit) as exc:
        server.main([])
    assert exc.value.code == 2
    assert "no approved root" in capsys.readouterr().err


def test_main_rejects_missing_root(monkeypatch, capsys, tmp_path):
    monkeypatch.delenv(server.ENV_ROOTS, raising=False)
    with pytest.raises(SystemExit) as exc:
        server.main(["--root", str(tmp_path / "missing")])
    assert exc.value.code == 2
    assert "does not exist" in capsys.readouterr().err


def test_roots_can_come_from_environment(monkeypatch, tmp_path):
    monkeypatch.setenv(server.ENV_ROOTS, str(tmp_path))
    assert server.load_allowed_roots([]) == [tmp_path.resolve()]


def test_version_flag(capsys):
    with pytest.raises(SystemExit) as exc:
        server.main(["--version"])
    assert exc.value.code == 0
    assert __version__ in capsys.readouterr().out
