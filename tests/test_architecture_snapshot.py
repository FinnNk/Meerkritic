"""Architecture evidence must expose declared contracts and observed dependency changes."""

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
    def test_snapshot_exposes_contracts_and_adapter_edges(self):
        value = architecture.snapshot(ROOT)
        self.assertEqual(value, architecture.snapshot(ROOT))
        self.assertEqual(len(value.contracts), 5)
        self.assertTrue(value.forbid_cycles)
        self.assertIn(
            architecture.Import("semantic_reviewer.adapters.registry", "sqlite3"), value.imports
        )
        old = asdict(value)
        new = {**old, "imports": (*old["imports"], {"source": "example", "target": "sqlite3"})}
        changes = architecture.delta(old, new)["changes"]
        self.assertEqual(changes["imports"]["added"], [{"source": "example", "target": "sqlite3"}])
        self.assertEqual(changes["contracts"], {"added": [], "removed": []})
