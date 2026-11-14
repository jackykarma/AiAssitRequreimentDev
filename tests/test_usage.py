"""Token usage recording and board summary tests."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from aiassitrequreimentdev.board import refresh_board
from aiassitrequreimentdev.gates import init_feature
from aiassitrequreimentdev.usage import (
    format_usage_report,
    load_usage,
    record_usage,
    summarize_usage,
)


class UsageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.feature = init_feature(self.root, "FEAT-USAGE")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_template_has_usage_yaml(self) -> None:
        self.assertTrue((self.feature / "usage.yaml").is_file())

    def test_record_and_summarize_by_role_and_stage(self) -> None:
        record_usage(
            self.feature,
            role="product",
            stage="clarify",
            input_tokens=1000,
            output_tokens=200,
        )
        record_usage(
            self.feature,
            role="architect",
            stage="tech",
            input_tokens=3000,
            output_tokens=800,
            model="test-model",
        )
        record_usage(
            self.feature,
            role="产品经理",
            stage="clarify",
            total_tokens=500,
        )
        doc = load_usage(self.feature)
        self.assertEqual(len(doc["entries"]), 3)
        summary = summarize_usage(doc)
        self.assertEqual(summary["byRole"]["product"]["totalTokens"], 1700)
        self.assertEqual(summary["byRole"]["architect"]["totalTokens"], 3800)
        self.assertEqual(summary["byStage"]["clarify"]["totalTokens"], 1700)
        self.assertEqual(summary["grandTotal"]["totalTokens"], 5500)

    def test_board_includes_usage_section(self) -> None:
        record_usage(
            self.feature,
            role="developer",
            input_tokens=10,
            output_tokens=5,
        )
        board = refresh_board(self.feature).read_text(encoding="utf-8")
        self.assertIn("Token 用量", board)
        self.assertIn("开发", board)
        self.assertIn("15", board)

    def test_show_report_non_empty(self) -> None:
        record_usage(self.feature, role="tester", input_tokens=1, output_tokens=1)
        text = format_usage_report(self.feature)
        self.assertIn("按角色", text)
        self.assertIn("按阶段", text)

    def test_rejects_unknown_role(self) -> None:
        with self.assertRaises(ValueError):
            record_usage(self.feature, role="nobody", total_tokens=1)


if __name__ == "__main__":
    unittest.main()
