import tempfile
import unittest
from pathlib import Path

from aiassitrequreimentdev.change_log import format_change_report, record_change
from aiassitrequreimentdev.gates import evaluate, init_feature


class ChangeLogTests(unittest.TestCase):
    def test_init_feature_includes_change_yaml(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = init_feature(Path(tmp), "FEAT-CHG")
            self.assertTrue((feature / "change.yaml").is_file())
            text = (feature / "change.yaml").read_text(encoding="utf-8")
            self.assertIn("FEAT-CHG", text)

    def test_record_change_requires_core_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = init_feature(Path(tmp), "FEAT-CHG2")
            entry = record_change(
                feature,
                initiated_by="product",
                name="测试",
                reason="验收口径调整",
                level="C3",
                category="product",
                summary="修改 A1",
                artifacts=["spec.yaml", "prd.md"],
                gates_rollback=["G1", "G2"],
                acceptance_ids=["A1"],
                status="approved",
                confirmed_by_role="human",
                confirmed_by_name="负责人",
            )
            self.assertEqual(entry["id"], "CHG-001")
            self.assertEqual(entry["initiatedBy"]["role"], "product")
            self.assertIn("验收口径", entry["reason"])
            report = format_change_report(feature)
            self.assertIn("CHG-001", report)
            self.assertEqual(evaluate(feature).codes("G0"), [])

    def test_c3_approved_requires_confirmed_by(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = init_feature(Path(tmp), "FEAT-CHG3")
            with self.assertRaises(ValueError):
                record_change(
                    feature,
                    initiated_by="product",
                    reason="x",
                    level="C3",
                    category="product",
                    summary="y",
                    gates_rollback=["G1"],
                    status="approved",
                )


if __name__ == "__main__":
    unittest.main()
