"""tasks scaffold 生成骨架。"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml

from aiassitrequreimentdev.board import set_path
from aiassitrequreimentdev.gates import init_feature
from aiassitrequreimentdev.tasks_scaffold import scaffold_tasks
from tests.test_gates import valid_spec, write_yaml


class TasksScaffoldTests(unittest.TestCase):
    def test_light_auto_generates_single_task(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = init_feature(Path(tmp), "FEAT-TS")
            set_path(feature, "light-auto")
            write_yaml(feature / "spec.yaml", valid_spec())
            path = scaffold_tasks(feature)
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
            self.assertEqual(len(doc["tasks"]), 1)
            self.assertEqual(doc["tasks"][0]["acceptance"], ["A1", "A2"])
            self.assertIn("CallbackIdempotencyTest", doc["tasks"][0]["verify"][0])

    def test_full_per_acceptance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = init_feature(Path(tmp), "FEAT-TS2")
            set_path(feature, "full")
            write_yaml(feature / "spec.yaml", valid_spec())
            path = scaffold_tasks(feature, mode="per-acceptance")
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
            self.assertEqual(len(doc["tasks"]), 2)
            self.assertEqual(doc["tasks"][1]["blockedBy"], ["T1"])

    def test_refuse_overwrite_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = init_feature(Path(tmp), "FEAT-TS3")
            set_path(feature, "full")
            write_yaml(feature / "spec.yaml", valid_spec())
            scaffold_tasks(feature, mode="single")
            with self.assertRaises(FileExistsError):
                scaffold_tasks(feature, mode="single")
            scaffold_tasks(feature, mode="single", force=True)


if __name__ == "__main__":
    unittest.main()
