# VS Code Python Debugging Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a committed VS Code workspace configuration that directly debugs `agents.main` with the uv-managed `.venv` and covers application and unittest workflows.

**Architecture:** VS Code selects `${workspaceFolder}/.venv/bin/python` and launches Python modules through debugpy, never through the generated console wrapper or an uv parent process. Strict-JSON workspace files separate interpreter/test settings, uv tasks, extension recommendations, and debug profiles; a standard-library unittest contract locks down their portable, secret-free structure.

**Tech Stack:** VS Code Python extension, debugpy, uv, Python 3.11+, standard-library `json`, `pathlib`, and `unittest`.

---

## File Structure

- Create `.vscode/settings.json`: select the uv-created interpreter and configure unittest discovery.
- Create `.vscode/extensions.json`: recommend only the Python and Python Debugger extensions.
- Create `.vscode/tasks.json`: expose explicit locked-sync and lock-check tasks.
- Create `.vscode/launch.json`: define the five direct Python-module debug profiles and prompt inputs.
- Create `tests/test_vscode_config.py`: parse every shared configuration as strict JSON and enforce the agreed workspace contracts.

### Task 1: Configure the Python environment, tests, uv tasks, and extensions

**Files:**
- Create: `.vscode/settings.json`
- Create: `.vscode/extensions.json`
- Create: `.vscode/tasks.json`
- Create: `tests/test_vscode_config.py`

- [ ] **Step 1: Write failing contracts for settings, tasks, and extension recommendations**

Create `tests/test_vscode_config.py` with:

```python
"""Contracts for the shared VS Code workspace configuration."""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VSCODE_DIRECTORY = REPOSITORY_ROOT / ".vscode"


def load_vscode_json(filename: str) -> dict[str, Any]:
    """Load one committed VS Code file as strict JSON."""
    with (VSCODE_DIRECTORY / filename).open(encoding="utf-8") as config_file:
        return json.load(config_file)


class VSCodeWorkspaceConfigTests(unittest.TestCase):
    def test_python_settings_use_uv_environment_and_unittest(self) -> None:
        settings = load_vscode_json("settings.json")

        self.assertEqual(
            settings,
            {
                "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
                "python.terminal.activateEnvironment": True,
                "python.testing.unittestEnabled": True,
                "python.testing.pytestEnabled": False,
                "python.testing.unittestArgs": [
                    "-v",
                    "-s",
                    "tests",
                    "-p",
                    "test_*.py",
                ],
            },
        )

    def test_uv_tasks_are_explicit_and_locked(self) -> None:
        tasks_config = load_vscode_json("tasks.json")

        self.assertEqual(tasks_config["version"], "2.0.0")
        self.assertEqual(
            tasks_config["tasks"],
            [
                {
                    "label": "uv: Sync Locked Environment",
                    "type": "shell",
                    "command": "uv",
                    "args": ["sync", "--locked"],
                    "options": {"cwd": "${workspaceFolder}"},
                    "group": {"kind": "build", "isDefault": True},
                    "presentation": {"reveal": "always", "panel": "shared"},
                    "problemMatcher": [],
                },
                {
                    "label": "uv: Check Lock File",
                    "type": "shell",
                    "command": "uv",
                    "args": ["lock", "--check"],
                    "options": {"cwd": "${workspaceFolder}"},
                    "group": "test",
                    "presentation": {"reveal": "always", "panel": "shared"},
                    "problemMatcher": [],
                },
            ],
        )

    def test_only_required_python_extensions_are_recommended(self) -> None:
        extensions = load_vscode_json("extensions.json")

        self.assertEqual(
            extensions,
            {"recommendations": ["ms-python.python", "ms-python.debugpy"]},
        )


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the focused test and confirm the configuration is missing**

Run:

```bash
.venv/bin/python -m unittest tests.test_vscode_config -v
```

Expected: FAIL with `FileNotFoundError` for `.vscode/settings.json` before any workspace configuration is created.

- [ ] **Step 3: Add strict-JSON environment and test settings**

Create `.vscode/settings.json` with:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "python.testing.unittestEnabled": true,
  "python.testing.pytestEnabled": false,
  "python.testing.unittestArgs": [
    "-v",
    "-s",
    "tests",
    "-p",
    "test_*.py"
  ]
}
```

- [ ] **Step 4: Add the required extension recommendations**

Create `.vscode/extensions.json` with:

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.debugpy"
  ]
}
```

- [ ] **Step 5: Add explicit locked uv tasks**

Create `.vscode/tasks.json` with:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "uv: Sync Locked Environment",
      "type": "shell",
      "command": "uv",
      "args": [
        "sync",
        "--locked"
      ],
      "options": {
        "cwd": "${workspaceFolder}"
      },
      "group": {
        "kind": "build",
        "isDefault": true
      },
      "presentation": {
        "reveal": "always",
        "panel": "shared"
      },
      "problemMatcher": []
    },
    {
      "label": "uv: Check Lock File",
      "type": "shell",
      "command": "uv",
      "args": [
        "lock",
        "--check"
      ],
      "options": {
        "cwd": "${workspaceFolder}"
      },
      "group": "test",
      "presentation": {
        "reveal": "always",
        "panel": "shared"
      },
      "problemMatcher": []
    }
  ]
}
```

- [ ] **Step 6: Run the focused and complete test suites**

Run:

```bash
.venv/bin/python -m unittest tests.test_vscode_config -v
```

Expected: PASS with three tests.

Run:

```bash
.venv/bin/python -m unittest discover -s tests -p "test_*.py" -v
```

Expected: PASS with the two existing CLI tests plus the three VS Code configuration tests.

- [ ] **Step 7: Commit the environment configuration**

```bash
git add .vscode/settings.json .vscode/extensions.json .vscode/tasks.json tests/test_vscode_config.py
git commit -m "chore(vscode): configure Python environment"
```

### Task 2: Add direct Python-module debug profiles

**Files:**
- Create: `.vscode/launch.json`
- Modify: `tests/test_vscode_config.py`

- [ ] **Step 1: Add failing contracts for the five launch profiles and prompt inputs**

Add these methods to `VSCodeWorkspaceConfigTests` in `tests/test_vscode_config.py`:

```python
    def test_launch_profiles_debug_python_modules_directly(self) -> None:
        launch = load_vscode_json("launch.json")
        configurations = launch["configurations"]

        self.assertEqual(launch["version"], "0.2.0")
        self.assertEqual(
            [configuration["name"] for configuration in configurations],
            [
                "Skevo: Interactive REPL",
                "Skevo: One-shot Prompt",
                "Skevo: Plan Mode",
                "Tests: Current File",
                "Tests: All",
            ],
        )

        for configuration in configurations:
            self.assertEqual(configuration["type"], "debugpy")
            self.assertEqual(configuration["request"], "launch")
            self.assertEqual(configuration["cwd"], "${workspaceFolder}")
            self.assertEqual(configuration["console"], "integratedTerminal")
            self.assertTrue(configuration["justMyCode"])
            self.assertNotIn("program", configuration)
            self.assertNotIn("python", configuration)

        for configuration in configurations[:3]:
            self.assertEqual(configuration["module"], "agents.main")
            self.assertEqual(configuration["envFile"], "${workspaceFolder}/.env")

        self.assertNotIn("args", configurations[0])
        self.assertEqual(configurations[1]["args"], ["${input:skevoPrompt}"])
        self.assertEqual(
            configurations[2]["args"],
            ["--plan", "${input:skevoPlanPrompt}"],
        )

        self.assertEqual(configurations[3]["module"], "unittest")
        self.assertEqual(configurations[3]["args"], ["-v", "${relativeFile}"])
        self.assertNotIn("envFile", configurations[3])

        self.assertEqual(configurations[4]["module"], "unittest")
        self.assertEqual(
            configurations[4]["args"],
            ["discover", "-s", "tests", "-p", "test_*.py", "-v"],
        )
        self.assertNotIn("envFile", configurations[4])

    def test_launch_prompt_inputs_are_non_secret_and_replaceable(self) -> None:
        launch = load_vscode_json("launch.json")

        self.assertEqual(
            launch["inputs"],
            [
                {
                    "id": "skevoPrompt",
                    "type": "promptString",
                    "description": "Prompt to run once",
                    "default": "Summarize this project",
                },
                {
                    "id": "skevoPlanPrompt",
                    "type": "promptString",
                    "description": "Prompt to analyze in Plan Mode",
                    "default": "Analyze how to improve this project",
                },
            ],
        )
```

- [ ] **Step 2: Run the focused test and confirm the launch configuration is missing**

Run:

```bash
.venv/bin/python -m unittest tests.test_vscode_config -v
```

Expected: FAIL with `FileNotFoundError` for `.vscode/launch.json`, while the three Task 1 contracts still pass.

- [ ] **Step 3: Add the five direct module-launch configurations**

Create `.vscode/launch.json` with:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Skevo: Interactive REPL",
      "type": "debugpy",
      "request": "launch",
      "module": "agents.main",
      "cwd": "${workspaceFolder}",
      "envFile": "${workspaceFolder}/.env",
      "console": "integratedTerminal",
      "justMyCode": true
    },
    {
      "name": "Skevo: One-shot Prompt",
      "type": "debugpy",
      "request": "launch",
      "module": "agents.main",
      "args": [
        "${input:skevoPrompt}"
      ],
      "cwd": "${workspaceFolder}",
      "envFile": "${workspaceFolder}/.env",
      "console": "integratedTerminal",
      "justMyCode": true
    },
    {
      "name": "Skevo: Plan Mode",
      "type": "debugpy",
      "request": "launch",
      "module": "agents.main",
      "args": [
        "--plan",
        "${input:skevoPlanPrompt}"
      ],
      "cwd": "${workspaceFolder}",
      "envFile": "${workspaceFolder}/.env",
      "console": "integratedTerminal",
      "justMyCode": true
    },
    {
      "name": "Tests: Current File",
      "type": "debugpy",
      "request": "launch",
      "module": "unittest",
      "args": [
        "-v",
        "${relativeFile}"
      ],
      "cwd": "${workspaceFolder}",
      "console": "integratedTerminal",
      "justMyCode": true
    },
    {
      "name": "Tests: All",
      "type": "debugpy",
      "request": "launch",
      "module": "unittest",
      "args": [
        "discover",
        "-s",
        "tests",
        "-p",
        "test_*.py",
        "-v"
      ],
      "cwd": "${workspaceFolder}",
      "console": "integratedTerminal",
      "justMyCode": true
    }
  ],
  "inputs": [
    {
      "id": "skevoPrompt",
      "type": "promptString",
      "description": "Prompt to run once",
      "default": "Summarize this project"
    },
    {
      "id": "skevoPlanPrompt",
      "type": "promptString",
      "description": "Prompt to analyze in Plan Mode",
      "default": "Analyze how to improve this project"
    }
  ]
}
```

- [ ] **Step 4: Run the focused configuration contracts**

Run:

```bash
.venv/bin/python -m unittest tests.test_vscode_config -v
```

Expected: PASS with five tests, including strict JSON parsing of all four `.vscode` files.

- [ ] **Step 5: Exercise the equivalent module and unittest commands**

Run:

```bash
.venv/bin/python -m agents.main --help
```

Expected: exit 0 and output beginning with `Usage: skevo [options] [prompt]` without requiring API credentials.

Run:

```bash
.venv/bin/python -m unittest -v tests/test_cli.py
```

Expected: PASS with the two current-file CLI tests.

Run:

```bash
.venv/bin/python -m unittest discover -s tests -p "test_*.py" -v
```

Expected: PASS with all seven CLI and configuration tests.

Run:

```bash
.venv/bin/python -c "import sys; from agents.main import parse_args; sys.argv = ['skevo', '--plan', 'debug prompt']; args = parse_args(); assert args.plan is True and args.prompt == ['debug prompt']"
```

Expected: exit 0, confirming the Plan Mode argument order used by `launch.json` reaches the existing parser without making a model request.

- [ ] **Step 6: Commit the launch profiles and expanded contract**

```bash
git add .vscode/launch.json tests/test_vscode_config.py
git commit -m "chore(vscode): add Python debug profiles"
```

### Task 3: Run final locked-environment verification

**Files:**
- Verify: `.vscode/settings.json`
- Verify: `.vscode/extensions.json`
- Verify: `.vscode/tasks.json`
- Verify: `.vscode/launch.json`
- Verify: `tests/test_vscode_config.py`

- [ ] **Step 1: Reproduce the environment through the shared uv workflow**

Run:

```bash
uv sync --locked
```

Expected: exit 0 without changing `pyproject.toml` or `uv.lock`.

Run:

```bash
uv lock --check
```

Expected: exit 0 with the committed lock file accepted.

- [ ] **Step 2: Parse each workspace file as strict JSON**

Run each command independently:

```bash
.venv/bin/python -m json.tool .vscode/settings.json
.venv/bin/python -m json.tool .vscode/extensions.json
.venv/bin/python -m json.tool .vscode/tasks.json
.venv/bin/python -m json.tool .vscode/launch.json
```

Expected: every command exits 0 and prints normalized JSON.

- [ ] **Step 3: Run the complete regression suite**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests -p "test_*.py" -v
```

Expected: PASS with seven tests and no credential or network requirement.

- [ ] **Step 4: Verify the final diff and preserve unrelated worktree changes**

Run:

```bash
git diff --check HEAD~2..HEAD
git status --short
git log --oneline -4
```

Expected:

- `git diff --check` exits 0.
- The only new implementation files in the two most recent commits are the four `.vscode` files and `tests/test_vscode_config.py`.
- The previously present `.idea` and documentation deletions and untracked `.DS_Store` remain unstaged and unchanged.
- The two implementation commit subjects are English and match the messages specified above.
