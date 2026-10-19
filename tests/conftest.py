from __future__ import annotations

from pathlib import Path

import pytest

README = """\
# Sample App

A tiny app used for EasyPR tests.

## Installation

```bash
$ pip install -r requirements.txt
```

## Running tests

```
pytest -q
```

## Unrelated section

```bash
echo "this block is not under a setup heading"
```
"""

AUTH = '''\
"""Authentication helpers."""


def login_user(username, password):
    """Check credentials and start a session."""
    return username == "admin"


def logout_user(session):
    session.clear()
'''

CI = """\
name: CI
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest -q
          python -m compileall app
"""


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@pytest.fixture
def sample_repo(tmp_path: Path) -> Path:
    """A small realistic repository built in a temporary directory."""
    repo = tmp_path / "sample"
    write(repo / "README.md", README)
    write(repo / "CONTRIBUTING.md", "# Contributing\n")
    write(repo / "LICENSE", "MIT\n")
    write(repo / "requirements.txt", "flask==3.0.0\npytest\n")
    write(repo / "app" / "__init__.py", "")
    write(repo / "app" / "auth.py", AUTH)
    write(repo / "app" / "utils.py", "def slugify(text):\n    return text.lower()\n")
    write(repo / "tests" / "test_auth.py", "from app.auth import login_user\n\n\ndef test_login():\n    assert login_user('admin', 'x')\n")
    write(repo / ".github" / "workflows" / "ci.yml", CI)
    # Things EasyPR must ignore or never read:
    write(repo / ".env", "SECRET_KEY=supersecretvalue123456\nlogin_user=leaked\n")
    write(repo / "node_modules" / "junk" / "index.js", "function login_user() {}\n")
    (repo / "logo.png").write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00login_user")
    return repo
