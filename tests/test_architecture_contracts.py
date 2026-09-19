"""Negative controls prove architecture gates reject the intended violations."""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class ArchitectureContractsTest(unittest.TestCase):
    def assert_rejected(self, changes: dict[str, str], diagnostics: dict[str, str]) -> None:
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(prefix="meerkritic-contract-") as directory:
            fixture = Path(directory)
            shutil.copytree(
                root / "src", fixture / "src", ignore=shutil.ignore_patterns("__pycache__")
            )
            for name in ("pyproject.toml", "tach.toml"):
                shutil.copyfile(root / name, fixture / name)
            for path, content in changes.items():
                (fixture / "src" / "semantic_reviewer" / path).write_text(content, encoding="utf-8")
            environment = os.environ.copy()
            environment["PYTHONPATH"] = str(fixture / "src")
            tool_path = str(Path(sys.executable).parent) + os.pathsep + environment["PATH"]
            arguments_by_tool = {"lint-imports": ["--no-cache"], "tach": ["check"]}
            for tool, diagnostic in diagnostics.items():
                with self.subTest(tool=tool):
                    executable = shutil.which(tool, path=tool_path)
                    self.assertIsNotNone(executable, f"Required tool is unavailable: {tool}")
                    result = subprocess.run(
                        [executable, *arguments_by_tool[tool]],
                        cwd=fixture,
                        env=environment,
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    output = result.stdout + result.stderr
                    self.assertEqual(result.returncode, 1, output)
                    self.assertIn(diagnostic, output)

    def test_domain_cannot_import_adapters(self) -> None:
        self.assert_rejected(
            {"domain/__init__.py": "from semantic_reviewer import adapters\n"},
            {
                "lint-imports": "Core logic does not depend on application or adapters BROKEN",
                "tach": "cannot depend on 'semantic_reviewer.adapters'",
            },
        )

    def test_worker_cannot_reach_web_through_shared_composition(self) -> None:
        self.assert_rejected(
            {
                "worker.py": "from semantic_reviewer import bootstrap\n",
                "bootstrap.py": "from semantic_reviewer import web\n",
            },
            {
                "lint-imports": "Worker and shared composition cannot pull in the web BROKEN",
                "tach": "cannot depend on 'semantic_reviewer.web'",
            },
        )

    def test_web_cannot_access_sqlite_directly(self) -> None:
        self.assert_rejected(
            {"web/__init__.py": "import sqlite3\n"},
            {"lint-imports": "Web cannot access concrete persistence or composition BROKEN"},
        )
