from __future__ import annotations

import subprocess
import sys
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CliContractTests(unittest.TestCase):
    def test_console_script_targets_main(self) -> None:
        project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

        self.assertEqual(project["project"]["scripts"]["bear-code"], "agents.main:main")

    def test_help_uses_bear_code_name(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-m", "agents.main", "--help"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        output = completed.stdout + completed.stderr

        self.assertEqual(completed.returncode, 0, output)
        self.assertIn("Usage: bear-code", output)
        self.assertNotIn("mini-claude", output)


if __name__ == "__main__":
    unittest.main()
