# VS Code Python Debugging Design

## Context

BearCode is a Python 3.11+ command-line application managed by `uv`. The installed `bear-code` console command and the supported module command both enter the same `agents.main:main` function. The repository currently has no shared `.vscode` configuration, so developers must select the project interpreter and recreate launch arguments manually before they can use breakpoints.

The shared configuration will make the project directly debuggable in VS Code while preserving `uv` as the environment manager. VS Code will attach its Python debugger to the application module itself rather than to the generated console-script wrapper or the `uv` parent process.

## Goals

- Select the project-local `.venv` interpreter created by `uv sync`.
- Debug `agents.main` directly with normal Python breakpoints.
- Cover interactive REPL, one-shot prompt, Plan Mode, one test file, and the complete test suite.
- Use the integrated terminal wherever application input, confirmation, or interrupt handling is needed.
- Load local model-provider settings from the project `.env` without storing credentials in committed editor files.
- Expose explicit tasks for locked environment synchronization and lock-file validation.
- Recommend the VS Code extensions required for Python debugging.

## Non-goals

- Debugging the generated `.venv/bin/bear-code` wrapper.
- Starting the debugger through `uv run` or attaching to an uv child process.
- Adding API keys, endpoint URLs, model names, or other personal settings to `.vscode`.
- Adding pytest or changing the existing standard-library `unittest` suite.
- Automatically running `uv sync` before every debug session.
- Changing application runtime behavior, command-line parsing, packaging, or dependencies.
- Committing, reverting, or otherwise changing the unrelated deletions and `.DS_Store` already present in the working tree.

## Shared VS Code Files

Add four committed files under `.vscode/`:

- `launch.json` defines the five supported debugger profiles.
- `settings.json` selects the project interpreter and configures test discovery.
- `tasks.json` provides explicit uv maintenance tasks.
- `extensions.json` recommends the Python and Python Debugger extensions.

All four files will use strict JSON without comments so they can also be validated by standard JSON tooling.

## Interpreter and Environment

Set `python.defaultInterpreterPath` to `${workspaceFolder}/.venv/bin/python`. BearCode officially targets macOS and Linux, and uv creates its project environment at this path by default.

Every application launch profile will:

- use the Python debugger type;
- launch the module `agents.main`;
- set `cwd` to `${workspaceFolder}` so `.env`, project Skills, sessions, and relative paths resolve from the repository root;
- set `envFile` to `${workspaceFolder}/.env`;
- use `integratedTerminal` for standard input and signal behavior;
- keep `justMyCode` enabled so normal stepping stays within BearCode unless the developer explicitly enters dependency code.

The configuration will not duplicate `.env` values in an `env` object. Missing or incomplete provider credentials will continue to fail through the application's existing runtime behavior.

## Debugger Profiles

`launch.json` will contain these profiles:

1. `Bear Code: Interactive REPL` launches `agents.main` without arguments.
2. `Bear Code: One-shot Prompt` launches `agents.main` with a prompt collected through a VS Code input variable.
3. `Bear Code: Plan Mode` launches `agents.main` with `--plan` followed by a prompt collected through a separate input variable.
4. `Tests: Current File` launches `unittest` for `${relativeFile}` with verbose output. This profile is intended for a currently open `tests/test_*.py` file.
5. `Tests: All` launches `unittest discover -s tests -p test_*.py -v`.

The two prompt inputs will be declared in the top-level `inputs` array. Each will use `promptString`, a descriptive label, and a harmless default prompt that can be replaced at launch time. Secrets will never be requested through these inputs.

Test profiles will use the same workspace, interpreter, and integrated terminal as the application profiles. They will launch the `unittest` module directly and will not load `.env`, because the current CLI contract tests are intentionally credential-free and network-free.

## Python Test Discovery

`settings.json` will:

- enable `python.testing.unittestEnabled`;
- disable `python.testing.pytestEnabled`;
- configure unittest discovery with `-v`, `-s tests`, and `-p test_*.py`;
- enable terminal environment activation.

This makes the Test Explorer and the explicit debug profiles agree on the framework, directory, and filename pattern.

## uv Tasks

`tasks.json` will define two shell tasks:

- `uv: Sync Locked Environment` runs `uv sync --locked` from the workspace root and is grouped as the default build task.
- `uv: Check Lock File` runs `uv lock --check` from the workspace root and is grouped as a test task.

Both tasks use the integrated terminal and dedicated problem matchers are unnecessary because uv already prints actionable failures. Neither task is a `preLaunchTask`; dependency synchronization remains an explicit developer action rather than a cost paid on every F5 launch.

## Extension Recommendations

`extensions.json` will recommend:

- `ms-python.python` for interpreter selection and test discovery;
- `ms-python.debugpy` for Python debugging.

No formatter, linter, type checker, or unrelated editor preference will be imposed.

## Failure Behavior

- If `.venv` does not exist, the Python extension reports that the configured interpreter is unavailable; the developer can run the provided locked-sync task.
- If `uv.lock` is stale, both uv tasks fail visibly and do not rewrite the lock file when invoked with their specified arguments.
- If `.env` is missing, launch still proceeds and the application retains its existing missing-credential behavior.
- If `Tests: Current File` is launched for a non-test file, unittest reports that file's import or discovery error rather than silently substituting another test target.

## Verification

Implementation verification will include:

1. Parse every `.vscode/*.json` file with a strict JSON parser.
2. Confirm the five launch names, module targets, arguments, working directory, terminal, and prompt inputs.
3. Confirm the configured interpreter resolves to the uv-created `.venv` Python executable after `uv sync --locked`.
4. Run the command equivalent of `Tests: Current File` against `tests/test_cli.py`.
5. Run the command equivalent of `Tests: All` and confirm the complete suite passes.
6. Run the non-interactive application equivalents for one-shot Prompt and Plan Mode only far enough to verify argument parsing without making a model request; use the existing help path for a network-free module-launch check.
7. Confirm only the intended `.vscode` files and documentation are introduced and all pre-existing working-tree changes remain untouched.

## Acceptance Criteria

1. After `uv sync --locked`, a developer can open the repository in VS Code, select any of the five named profiles, and start the relevant Python module under the debugger.
2. REPL and prompt-driven profiles accept terminal input and support the application's existing interrupt and confirmation behavior.
3. Prompt and Plan profiles obtain their task text at launch time instead of embedding personal prompts in source control.
4. VS Code Test Explorer discovers the same standard-library unittest suite used by the debug profiles.
5. No secret or machine-specific absolute path is committed.
6. The uv tasks validate or reproduce the committed environment without maintaining a second dependency source.
7. Existing unrelated working-tree changes are not included in the configuration commit.
