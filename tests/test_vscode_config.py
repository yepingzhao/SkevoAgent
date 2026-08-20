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
            self.assertNotIn("env", configuration)

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
        self.assertEqual(configurations[3]["envFile"], "")

        self.assertEqual(configurations[4]["module"], "unittest")
        self.assertEqual(
            configurations[4]["args"],
            ["discover", "-s", "tests", "-p", "test_*.py", "-v"],
        )
        self.assertEqual(configurations[4]["envFile"], "")

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


if __name__ == "__main__":
    unittest.main()
