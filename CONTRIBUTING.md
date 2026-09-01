# Contributing to ogentic-adapter-sdk

Thank you for your interest in contributing! We welcome contributions from everyone. This document outlines the guidelines for how to contribute effectively.

---

## Types of Contributions We Welcome

We appreciate various kinds of contributions, including but not limited to:

- **Protocol design feedback** &mdash; the `Adapter` interface is the contract every LLM backend implements; input on ergonomics and edge cases is valuable
- **New adapter implementations** &mdash; reference adapters for OpenAI, Anthropic, local models, or other providers
- **Bug fixes** &mdash; issues with the contract, type stubs, or packaging
- **Tests** &mdash; especially edge cases around request/response validation
- **Documentation** &mdash; usage examples, integration guides, API docs

---

## How to Ask Questions

If you have questions:

1. Check the [README](./README.md) and existing [issues](https://github.com/OgenticAI/ogentic-adapter-sdk/issues) first.
2. If your question hasn't been addressed, open a new issue with the `question` label.

---

## How to Report Bugs

When reporting a bug, please include:

- A clear and descriptive title
- The code that produced unexpected results
- Expected vs. actual behavior
- Your `ogentic-adapter-sdk` version
- Python version and OS

---

## How to Suggest a Feature

To suggest a new feature:

1. Search existing issues to avoid duplicates.
2. Open a new issue describing your idea and use cases.
3. For protocol changes, note that this package follows semver — breaking changes to anything exported from `ogentic_adapter_sdk.__init__` require a major bump and a deprecation notice first.

---

## How to Contribute Code

### Prerequisites

- Python 3.11+
- pip (or [uv](https://github.com/astral-sh/uv))
- Git

### Step-by-Step Process

1. **Fork** the repository.

2. **Clone** your fork:

   ```bash
   git clone https://github.com/your-username/ogentic-adapter-sdk.git
   cd ogentic-adapter-sdk
   ```

3. **Create a feature branch:**

   ```bash
   git checkout -b feat/my-feature
   ```

   Branch prefixes: `feat/`, `fix/`, `test/`, `docs/`, `refactor/`

4. **Install in development mode:**

   ```bash
   pip install -e ".[dev]"
   ```

5. **Make your changes** following the patterns in [CLAUDE.md](./CLAUDE.md):

   - Type hints on all public functions
   - Pydantic models as the typed boundary for any data crossing an interface
   - No new runtime dependencies beyond Pydantic without prior discussion — this package must stay dependency-light

6. **Run quality checks:**

   ```bash
   ruff check src/ tests/
   mypy src/ogentic_adapter_sdk/
   pytest tests/ -v
   ```

   All three must pass before submitting a PR.

7. **Push** your branch:

   ```bash
   git push origin feat/my-feature
   ```

8. **Open a Pull Request** against the `main` branch with a clear description of what you changed and why.

---

## Coding Style

- Follow [PEP 8](https://peps.python.org/pep-0008/) conventions
- Use [ruff](https://docs.astral.sh/ruff/) for linting (configured in `pyproject.toml`)
- Use `mypy --strict` for type checking (configured in `pyproject.toml`)
- Type hints on all public functions
- Docstrings on all classes and public methods
- No `print()` &mdash; use `logging`

---

## Commit Message Guidelines

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>: <short summary>
```

Types:

| Type | Use for |
|------|---------|
| `feat` | New feature |
| `fix` | Bug fix |
| `test` | Adding or updating tests |
| `docs` | Documentation changes |
| `refactor` | Code restructuring without behavior change |
| `perf` | Performance improvement |

Examples:

```
feat: add Adapter protocol base class
fix: correct type stub for streaming response
test: add edge cases for request validation
docs: add integration example for OpenAI adapter
```

---

## PR Requirements

Before a PR can be merged:

- `ruff check src/ tests/` passes with zero errors
- `mypy src/ogentic_adapter_sdk/` passes with zero errors
- `pytest tests/ -v` passes with all tests green
- No secrets, API keys, or credentials in code
- Commit messages follow conventional format

---

## Code of Conduct

Please read and follow our [Code of Conduct](./CODE_OF_CONDUCT.md).

---

## Questions?

Open an issue or start a discussion. We're happy to help you get started.

Thank you for helping build the contract layer for AI infrastructure.
