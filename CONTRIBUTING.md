# Contributing to EasyPR

First of all, thank you for considering contributing to EasyPR!

EasyPR is an open-source project that helps developers understand unfamiliar codebases, discover important files, and find relevant code through MCP tools.

Our goal is to make exploring repositories easier, especially for people who are new to open source.

**You do not need to be an experienced developer to contribute.** Whether you are fixing a typo, improving documentation, reporting a bug, writing a test, or improving the code, your contribution is welcome.

This guide will help you get started, even if this is your first open-source contribution.

## Table of Contents

- [Ways to Contribute](#ways-to-contribute)
- [Before You Start](#before-you-start)
- [Setting Up EasyPR](#setting-up-easypr)
- [Making Your First Change](#making-your-first-change)
- [Testing Your Changes](#testing-your-changes)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Contribution Guidelines](#contribution-guidelines)
- [Need Help?](#need-help)

## Ways to Contribute

There are many ways to help improve EasyPR. You do not have to start by writing code.

- **Fix a bug:** Help resolve an issue or unexpected behaviour.
- **Improve documentation:** Make explanations, setup instructions, or examples easier to understand.
- **Write tests:** Help ensure existing features continue to work correctly.
- **Improve code search:** Help EasyPR find more relevant files and code.
- **Test with other repositories:** Try EasyPR on different projects and report problems.
- **Suggest an improvement:** Share a clear idea for making EasyPR more useful.

If this is your first contribution, consider starting with a small documentation change or a clearly defined issue.

## Before You Start

### 1. Find something to work on

Visit the [EasyPR issues page](https://github.com/Ankith34/EasyPR/issues) to see reported bugs and proposed improvements.

Look for issues labelled `good first issue` if available.

If you have an idea that is not already discussed, you can open an issue to explain it before starting work. This helps avoid spending time on a change that may not fit the project's direction.

### 2. Fork the repository

A fork is your own copy of a repository on GitHub. It lets you make changes without directly modifying the original project.

1. Open the [EasyPR repository](https://github.com/Ankith34/EasyPR).
2. Click **Fork**.
3. Follow GitHub's instructions to create your copy.

You only need to do this once for your GitHub account.

### 3. Install the required tools

To work on EasyPR, you will need:

- Git
- Python
- pip, Python's package installer
- A terminal or command-line application
- A GitHub account to submit a pull request

If you already use Python for development, you may have most of these installed.

## Setting Up EasyPR

The following instructions are for Linux and macOS. Windows users can use the equivalent commands in PowerShell where needed.

### 1. Clone your fork

Cloning downloads a copy of a repository to your computer.

Replace `YOUR-USERNAME` with your GitHub username:

```bash
git clone https://github.com/YOUR-USERNAME/EasyPR.git
cd EasyPR
```

### 2. Create a virtual environment

A virtual environment keeps the project's Python dependencies separate from other Python projects on your computer.

```bash
python -m venv .venv
```

Activate it on Linux or macOS:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install EasyPR and development dependencies

Run:

```bash
python -m pip install -e ".[dev]"
```

This installs EasyPR in editable mode along with the development dependencies defined by the project.

### 4. Check that the project works

Run the tests:

```bash
python -m pytest
```

If the tests pass, your development environment is ready.

If something fails, read the error message carefully. You can also open an issue with the error details if you need help.

## Making Your First Change

### 1. Create a branch

A branch lets you work on your change separately from the main branch.

Choose a short name that describes your work:

```bash
git checkout -b docs/improve-setup-guide
```

For a bug fix, you could use a name such as `fix/search-ranking`.

### 2. Make your change

Open the relevant files in your editor and make your improvement.

A few examples:

- Clarify an installation step in the README.
- Fix an incorrect search result.
- Add a test for an edge case.
- Improve an error message.
- Correct a typo in the documentation.

Try to keep each change focused on one goal. Small, easy-to-review changes are often the best way to learn.

### 3. Review your changes

Run:

```bash
git status
git diff
```

These commands help you see which files changed and review the edits you made.

Before continuing, make sure you have not included unrelated files, local environment folders, credentials, or secrets.

## Testing Your Changes

We want EasyPR to remain reliable as it grows.

Before submitting your work, run:

```bash
python -m pytest
```

If you changed existing behaviour or added a feature, add or update tests where appropriate.

Please do not remove a test simply because it fails after your change. Investigate the cause and explain any unresolved problems in your pull request.

If you cannot get the tests to pass, you can still open a draft pull request and explain what you tried and what remains unresolved.

## Submitting a Pull Request

A pull request (PR) proposes your changes to the original repository so they can be reviewed.

### 1. Commit your changes

Stage the files you intend to include:

```bash
git add path/to/changed-file
```

Replace the example path with the actual file you changed. You can stage multiple files if they belong to the same improvement.

Commit the change with a clear message:

```bash
git commit -m "Improve setup documentation"
```

### 2. Push your branch

```bash
git push -u origin docs/improve-setup-guide
```

Use the name of your own branch if it is different.

### 3. Open a pull request

1. Visit your fork on GitHub.
2. Look for the option to compare your branch or create a pull request.
3. Set the original repository, `Ankith34/EasyPR`, as the base repository.
4. Select its `main` branch as the base branch.
5. Select your branch as the compare branch.
6. Create the pull request.

### 4. Describe your contribution

A useful pull request description answers three simple questions:

- **What changed?** Briefly describe your contribution.
- **Why was it needed?** Explain the problem it addresses.
- **How did you test it?** Mention the tests you ran and their results.

For example:

> **What changed?** Clarified the development setup instructions.
>
> **Why?** Help new contributors install the project more easily.
>
> **Testing:** Ran `python -m pytest`.

You do not need to write a long description for a small change. Clear and honest information is what matters.

### 5. Respond to feedback

Maintainers may ask questions or suggest improvements during review.

This is a normal part of open-source development. Read the feedback, ask questions if anything is unclear, and push any agreed changes to the same branch.

Your pull request will update automatically.

## Contribution Guidelines

To keep EasyPR maintainable and safe, please follow these guidelines:

- Keep code readable and consistent with the existing project.
- Prefer simple solutions over unnecessary complexity.
- Add or update tests when appropriate.
- Update documentation when behaviour or setup instructions change.
- Never commit passwords, API keys, access tokens, or other sensitive information.
- Preserve EasyPR's repository safety protections.
- Do not introduce repository-command execution without appropriate safety controls and review.
- Be respectful, constructive, and open to feedback.

All contributions should follow the project's [MIT License](LICENSE).

## Need Help?

Not sure where to begin? That is completely fine.

You can:

- Browse the [existing issues](https://github.com/Ankith34/EasyPR/issues).
- Open an issue to ask a question or discuss an idea.
- Read the [README](README.md) to understand the project.
- Ask for clarification on any step in this guide.

You are not expected to know everything before making your first contribution.

**Every experienced open-source developer started somewhere. We hope EasyPR can be a good place for you to start, too.**

Thank you for helping make EasyPR better!
