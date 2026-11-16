import json
import tempfile
import unittest
from pathlib import Path

from aiassitrequreimentdev.board import set_path
from aiassitrequreimentdev.gates import init_feature
from aiassitrequreimentdev.paths import is_light_path, recommend_path, resolve_path


class PathTests(unittest.TestCase):
    def test_resolve_aliases(self) -> None:
        self.assertEqual(resolve_path("全量").id, "full")
        self.assertEqual(resolve_path("轻量").id, "light")
        self.assertEqual(resolve_path("2").id, "light")
        self.assertEqual(resolve_path("轻量自动").id, "light-auto")
        self.assertEqual(resolve_path("3").id, "light-auto")
        self.assertEqual(resolve_path("goal").id, "light-auto")

    def test_is_light_path(self) -> None:
        self.assertTrue(is_light_path("light"))
        self.assertTrue(is_light_path("light-auto"))
        self.assertFalse(is_light_path("full"))
        self.assertFalse(is_light_path(None))

    def test_recommend_light_for_hotfix(self) -> None:
        result = recommend_path("修复单模块空指针崩溃，已有验收")
        self.assertEqual(result.path, "light")
        self.assertGreaterEqual(len(result.matched_light), 1)

    def test_recommend_light_auto_for_no_ui_hotfix(self) -> None:
        result = recommend_path("修复单模块空指针崩溃，无UI，已有验收")
        self.assertEqual(result.path, "light-auto")
        self.assertGreaterEqual(len(result.matched_auto), 1)

    def test_recommend_light_auto_for_chinese_hot_fix(self) -> None:
        result = recommend_path("无UI热修配置开关")
        self.assertEqual(result.path, "light-auto")
        self.assertIn("热修", result.matched_light)
        self.assertGreaterEqual(len(result.matched_auto), 1)

    def test_recommend_light_auto_for_auto_only_signal(self) -> None:
        result = recommend_path("纯逻辑无界面回调")
        self.assertEqual(result.path, "light-auto")
        self.assertGreaterEqual(len(result.matched_auto), 1)

    def test_recommend_full_for_new_capability(self) -> None:
        result = recommend_path("新功能：跨模块订单状态机与对外契约改造")
        self.assertEqual(result.path, "full")
        self.assertGreaterEqual(len(result.matched_full), 1)

    def test_set_path_confirms_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = init_feature(Path(tmp), "FEAT-001-path")
            state = set_path(feature, "轻量", recommended="light")
            self.assertEqual(state["path"], "light")
            self.assertTrue(state["pathConfirmed"])
            self.assertEqual(state["pathRecommended"], "light")
            board = (feature / "BOARD.md").read_text(encoding="utf-8")
            self.assertIn("轻量模式", board)
            saved = json.loads((feature / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(saved["path"], "light")

    def test_set_path_light_auto(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = init_feature(Path(tmp), "FEAT-001-auto")
            state = set_path(feature, "light-auto", recommended="light-auto")
            self.assertEqual(state["path"], "light-auto")
            self.assertTrue(state["pathConfirmed"])
            board = (feature / "BOARD.md").read_text(encoding="utf-8")
            self.assertIn("轻量自动", board)


if __name__ == "__main__":
    unittest.main()
