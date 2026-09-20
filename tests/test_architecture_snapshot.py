"""Architecture evidence must expose declared contracts and observed dependency changes."""

import ast
import importlib.util
import sys
import unittest
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("architecture", ROOT / "tools" / "architecture.py")
architecture = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = architecture
SPEC.loader.exec_module(architecture)


class ArchitectureSnapshotTest(unittest.TestCase):
    def test_contract_changes_are_visible_without_dependency_changes(self):
        source = """
class Store(Protocol):
    count: int = 0
    async def read(self, key: str, /, *, limit: int = 20) -> str: ...
    def _private(self): ...
"""
        before = asdict(architecture.snapshot(ROOT))
        before["interfaces"] = [
            asdict(item) for item in architecture.interfaces(ast.parse(source), "example")
        ]
        changed = source.replace("limit: int = 20", "limit: int = 10").replace(
            "count: int", "count: int | None"
        )
        after = {
            **before,
            "interfaces": [
                asdict(item) for item in architecture.interfaces(ast.parse(changed), "example")
            ],
        }
        changes = architecture.delta(before, after)["changes"]
        self.assertEqual(len(changes["interfaces"]["added"]), 2)
        self.assertEqual(changes["imports"], {"added": [], "removed": []})
        self.assertFalse(any("_private" in item["name"] for item in before["interfaces"]))
        self.assertIn(
            "async def read(self, key: str, /, *, limit: int=20) -> str",
            before["interfaces"][2]["declaration"],
        )
        with self.assertRaises(ValueError):
            architecture.delta(before, {**after, "schema_version": 1})

    def test_snapshot_exposes_contracts_and_adapter_edges(self):
        value = architecture.snapshot(ROOT)
        self.assertEqual(value, architecture.snapshot(ROOT))
        self.assertEqual(len(value.contracts), 5)
        self.assertTrue(value.forbid_cycles)
        self.assertIn(
            architecture.Import("semantic_reviewer.adapters.state", "sqlite3"), value.imports
        )
        old = asdict(value)
        new = {**old, "imports": (*old["imports"], {"source": "example", "target": "sqlite3"})}
        changes = architecture.delta(old, new)["changes"]
        self.assertEqual(changes["imports"]["added"], [{"source": "example", "target": "sqlite3"}])
        self.assertEqual(changes["contracts"], {"added": [], "removed": []})
