"""check --accept / stage 推进。"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from aiassitrequreimentdev.board import set_path
from aiassitrequreimentdev.gates import init_feature
from aiassitrequreimentdev.progress import accept_gate, next_stage_for_gate
from tests.test_gates import valid_spec, write_spec_prd, write_yaml


class ProgressTests(unittest.TestCase):
    def test_light_g1_next_is_tech(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = init_feature(Path(tmp), "FEAT-001-progress")
            set_path(feature, "light-auto")
            write_yaml(feature / "spec.yaml", valid_spec())
            self.assertEqual(
                next_stage_for_gate("G1", path="light-auto", feature_dir=feature),
                "tech",
            )

    def test_accept_g0_advances_stage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = init_feature(Path(tmp), "FEAT-002-progress")
            set_path(feature, "full")
            write_yaml(feature / "spec.yaml", valid_spec())
            state = accept_gate(feature, "G0")
            self.assertEqual(state["gates"]["G0"], "accepted")
            self.assertEqual(state["stage"], "clarify")

    def test_accept_g1_seals_and_advances(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = init_feature(Path(tmp), "FEAT-003-progress")
            set_path(feature, "light-auto")
            write_yaml(feature / "spec.yaml", valid_spec())
            write_spec_prd(feature / "prd.md")
            # G0 first so board/path ok; G1 accept seals
            accept_gate(feature, "G0")
            state = accept_gate(feature, "G1")
            self.assertEqual(state["gates"]["G1"], "accepted")
            self.assertTrue(state.get("specHash"))
            self.assertEqual(state["stage"], "tech")
            saved = json.loads((feature / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(saved["gates"]["G1"], "accepted")

    def test_accept_rejects_when_not_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = init_feature(Path(tmp), "FEAT-004-progress")
            set_path(feature, "full")
            # template openQuestions 未清空 → G1 失败
            with self.assertRaises(ValueError):
                accept_gate(feature, "G1")


if __name__ == "__main__":
    unittest.main()
