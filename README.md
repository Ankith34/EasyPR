<div align="center">

# EasyPR

**Your first PR starts here.**

A beginner-friendly [MCP](https://modelcontextprotocol.io) server that helps you understand an unfamiliar repository before your first open-source contribution.

[![CI](https://github.com/Ankith34/EasyPR/actions/workflows/ci.yml/badge.svg)](https://github.com/Ankith34/EasyPR/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-early%20alpha-orange)

</div>

---

## ✨ Why EasyPR?

Opening a new repository is overwhelming. Which files matter? How do I run it? Where is the code that this issue is about?

EasyPR gives your AI assistant a small set of **read-only repository tools** so it can answer those questions with **evidence from the actual repo** (filenames, line numbers, documented commands) instead of guesses.

> EasyPR is the tool layer, not a chatbot. Your MCP-compatible AI client does the talking; EasyPR supplies the facts.

```
AI client  ──►  EasyPR MCP server  ──►  Python functions that inspect a repo
   ▲                                              │
   └────────── evidence-labelled results ◄────────┘
```

## 🚦 Status

EasyPR is **early alpha**. Here is exactly what works today.

| Capability | Status |
| --- | --- |
| `inspect_repository`: layout, languages, key files | ✅ Working |
| `get_setup_guide`: documented install/test steps + labelled hints | ✅ Working |
| `find_relevant_code`: keyword search with line numbers | ✅ Working |
| `run_project_checks`: run a project's tests safely | 🗓️ Planned (needs a sandbox and permission model first) |
| Smarter retrieval (embeddings, symbol index) | 🗓️ Only if keyword search proves insufficient |
| PR description helper | 🗓️ Planned |

## 🚀 Quick start

Requires Python 3.10+.

```bash
git clone https://github.com/Ankith34/EasyPR.git
cd EasyPR
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

Check the command works:

```bash
easypr --version
```

## 🔌 Connect an MCP client

EasyPR speaks MCP over **stdio**. You must tell it which directories it may look at with `--root`. It refuses to start without one.

**Clients that use the common `mcpServers` JSON format:**

```json
{
  "mcpServers": {
    "easypr": {
      "command": "/absolute/path/to/EasyPR/.venv/bin/easypr",
      "args": ["--root", "/home/you/projects"]
    }
  }
}
```

**Claude Code:**

```bash
claude mcp add easypr -- /absolute/path/to/EasyPR/.venv/bin/easypr --root ~/projects
```

**MCP Inspector (for trying tools by hand):**

```bash
npx @modelcontextprotocol/inspector easypr --root ~/projects
```

Roots can also come from the `EASYPR_ALLOWED_ROOT` environment variable (separate several with `:` on Linux/macOS).

> Tested with the official Python MCP SDK client over stdio. Behaviour in specific desktop apps may vary, so please open an issue if something doesn't work.

## 🧰 Tools

| Tool | What it does |
| --- | --- |
| `inspect_repository(path)` | Top-level layout, important files (README, CONTRIBUTING, manifests, CI), language counts, project type, frameworks. |
| `get_setup_guide(path)` | Setup/test code blocks from the README, `run:` commands from CI workflows, and clearly labelled hints from manifests like `package.json`, `Makefile`, `requirements.txt`. |
| `find_relevant_code(path, query, max_results=10)` | Finds files related to an issue or task and says why, with line numbers, snippets and each file's role (source, test, docs, config). |

Relative paths are resolved against the first approved root.

### Evidence labels

Every finding says how much to trust it:

| Label | Meaning |
| --- | --- |
| `fact` | Seen directly in the repository |
| `documented` | The project itself says so (README, CI config) |
| `inferred` | EasyPR's guess from file names or contents |
| `suggestion` | A next step a human still needs to verify |

### Example

`find_relevant_code(path, "login_user rejects wrong password")` returns (trimmed):

```json
{
  "path": "app/auth.py",
  "role": "source",
  "matches": [{ "line": 4, "text": "def login_user(username, password):", "is_definition": true }],
  "why": "Keyword match: 3 line(s) mention 'login', 'login_user', 'password', 'user'; it defines a function/class/type that mentions them. Verify by reading the code.",
  "kind": "inferred"
}
```

## 🔒 Safety model

Repositories can contain untrusted files, so EasyPR is conservative by design.

- **Read-only.** It never writes files and **never runs repository code or commands**.
- **Approved roots only.** Paths are resolved first, then checked, so `..` tricks and symlinks that point outside a root are rejected.
- **Symlinks are never followed** while scanning a repository.
- **Secrets stay unread.** Files like `.env`, `*.pem`, `id_rsa` and `credentials.*` are never opened, and obvious secret values in returned text are redacted.
- **Repo text is untrusted data.** The server tells the AI client not to follow instructions found inside repository files.
- **Limits.** Caps on files scanned, file size, total bytes read, results and snippet length.
- **Honest output.** Setup commands are never marked as verified, and EasyPR never claims tests passed.

## ⚠️ Known limitations

- `find_relevant_code` is plain keyword matching. Short words can match inside longer ones (`user` matches `username`), and it does not understand meaning. Treat results as leads.
- `get_setup_guide` only parses Markdown READMEs and simple `run:` entries in GitHub Actions workflows.
- Redaction is pattern-based and best-effort. Do not point EasyPR at directories you would not want an AI assistant to read.
- Language and framework detection is heuristic.

## 🗂️ Project layout

```text
EasyPR/
├── src/easypr/
│   ├── repository.py   # core logic, plain Python, no MCP imports
│   ├── server.py       # thin MCP layer + command-line entry point
│   └── __init__.py
├── tests/              # pytest suite (temporary directories only)
├── .github/workflows/  # CI
├── pyproject.toml
└── LICENSE
```

## 🧪 Development

```bash
pip install -e ".[dev]"
pytest
```

Tests build throwaway repositories in temporary directories, so they don't depend on anything on your machine.

## 🤝 Contributing

Issues and pull requests are welcome, and this project is meant to be friendly to first-time contributors. Please add a test with each change and keep `repository.py` independent of MCP.

## 📄 License

[MIT](LICENSE) © 2026 Ankith
