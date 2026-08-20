# uv Project Management Migration Design

## Context

Skevo is a Python 3.11+ command-line application. Its five direct runtime dependencies currently live in `requirements.txt`, local setup uses `venv` plus `pip`, Docker installs the same requirements with `pip`, and the application is started with `python -m agents.main`. The CLI help is also inconsistent: its usage block says `skevo`, while `argparse` and examples still use `mini-claude`.

This migration will make `uv` the single project and dependency manager for local development and Docker. It will also package the existing `agents` directory in place and expose a formal `skevo` console command.

## Goals

- Make `pyproject.toml` the only direct dependency declaration.
- Commit `uv.lock` so local and container environments resolve to the same versions.
- Package the existing `agents` directory without moving or renaming its modules.
- Expose `skevo` as the canonical command-line entry point.
- Keep `python -m agents.main` as a supported compatibility entry point under `uv run`.
- Use `uv` rather than `pip` to install locked dependencies in Docker.
- Update README setup and execution instructions to describe only the supported `uv` workflow.
- Add a small, network-free CLI regression test using the Python standard library.

## Non-goals

- Moving the application to a `src/` layout.
- Renaming the `agents` package or changing its internal imports.
- Changing model-provider behavior, the Agent loop, permissions, Skills, Memory, MCP, sessions, or evaluation logic.
- Publishing the package to PyPI.
- Adding a general test framework or broad application test suite.
- Committing, reverting, or otherwise altering the unrelated deletions and `.DS_Store` currently present in the working tree.

## Packaging and Dependency Model

Add `agents/__init__.py` so `agents` is an explicit Python package. Add a PEP 621 `pyproject.toml` with:

- project name `skevo`;
- an initial project version of `0.1.0`;
- `README.md` as the project readme;
- `requires-python = ">=3.11"`;
- the five existing runtime requirements, preserving their current lower bounds:
  - `anthropic>=0.25.0`;
  - `openai>=1.0.0`;
  - `python-dotenv>=1.0.0`;
  - `rich>=13.0.0`;
  - `tqdm>=4.66.0`;
- a `skevo = "agents.main:main"` console script;
- Hatchling as the build backend;
- an explicit Hatch wheel package list containing `agents`.

No `.python-version` file will be added. The supported range remains Python 3.11 and newer, allowing developers to use an already-installed compatible interpreter rather than forcing one exact minor or patch release.

Generate `uv.lock` from `pyproject.toml` and commit it. Delete `requirements.txt`; it will not be retained or generated as a compatibility artifact because that would create a second dependency representation that could drift.

The primary local workflow becomes:

```bash
uv sync
uv run skevo
```

The supported module form remains:

```bash
uv run python -m agents.main
```

## CLI Naming

The canonical executable name is `skevo`. Update `argparse.ArgumentParser(prog=...)`, the custom help examples in `agents/main.py`, and README command examples so they no longer refer to `mini-claude`.

Both the console script and module invocation call the existing `agents.main:main` function. No wrapper with a second execution path will be introduced.

## Docker Design

Keep `python:3.11-slim` as the runtime base. Copy a pinned `uv` binary from `ghcr.io/astral-sh/uv:0.10.9` rather than downloading an unversioned installer during the build.

The dependency layer will:

1. set `/app` as the project directory;
2. copy `pyproject.toml`, `uv.lock`, and the readme metadata required by the build backend;
3. run `uv sync --locked --no-dev --no-install-project` to install only locked third-party dependencies and maximize Docker layer reuse;
4. copy `agents/`;
5. run `uv sync --locked --no-dev` to install the application and register `skevo`.

Set the container entry point directly to `/app/.venv/bin/skevo`. The existing runtime working directory remains `/workspace`, and the existing system, Node.js, Playwright, volume, and MCP behavior stays unchanged.

The Docker build must fail if `pyproject.toml` and `uv.lock` disagree. It must not silently re-lock or fall back to `pip`.

## Documentation Changes

Update README sections that describe the directory tree, environment preparation, startup, Plan Mode, session restoration, and automatic Skill evolution commands:

- replace `requirements.txt` with `pyproject.toml` and `uv.lock` in the tree;
- replace manual `venv` and `pip install` steps with `uv sync`;
- use `uv run skevo` for all normal CLI examples;
- document `uv run python -m agents.main` only as a compatibility form;
- document `uv lock --check` and `uv sync --locked` for reproducibility;
- explain that dependency updates use `uv add`, `uv remove`, and `uv lock --upgrade` rather than editing a requirements file;
- retain the existing external Docker run interface because the image entry point absorbs the internal packaging change.

## Tests and Verification

Add `tests/test_cli.py` using `unittest`; do not add pytest or another test dependency. The test invokes the help path without an API key and asserts:

- help exits successfully;
- the output identifies `skevo`;
- the output no longer contains `mini-claude`.

The implementation is complete only when these commands pass:

```bash
uv lock --check
uv sync --locked
uv run python -m unittest discover -s tests -v
uv run skevo --help
uv run python -m agents.main --help
```

Also inspect the installed distribution metadata to confirm the `skevo` console entry maps to `agents.main:main`, confirm `requirements.txt` is absent, and confirm `uv.lock` is tracked.

If a Docker daemon is available, build the image to validate the complete locked installation and entry point. If no daemon is available, report that the Docker build was not executed; static inspection is not equivalent to a successful image build.

## Failure Behavior

- A stale lock file causes `uv lock --check` and Docker's locked sync to fail immediately.
- A packaging or console-script registration error is surfaced directly; there is no hidden `PYTHONPATH` or system-Python fallback.
- CLI help remains network-free and does not require model credentials.
- Existing application runtime errors and missing API-key handling remain unchanged.

## Acceptance Criteria

1. A developer with `uv` and Python 3.11+ can clone the repository, run `uv sync`, and invoke `uv run skevo --help` successfully.
2. `uv run skevo` and `uv run python -m agents.main` execute the same `main()` implementation.
3. `pyproject.toml` and committed `uv.lock` are the only project dependency sources; `requirements.txt` is removed.
4. Local development and Docker install from the same lock file.
5. All user-facing CLI examples use `skevo`, not `mini-claude`.
6. The CLI regression test passes without API credentials or network access.
7. No pre-existing working-tree deletion or untracked `.DS_Store` is included in the migration commits.
