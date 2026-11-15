import tempfile
import unittest
from pathlib import Path

import json

from aiassitrequreimentdev.board import set_path
from aiassitrequreimentdev.change_log import format_change_report, record_change
from aiassitrequreimentdev.gates import evaluate, init_feature, init_requirement
from aiassitrequreimentdev.progress import accept_gate


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
            set_path(feature, "full", recommended="full")
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
                apply_rollback=False,
            )
            self.assertEqual(entry["id"], "CHG-001")
            self.assertEqual(entry["initiatedBy"]["role"], "product")
            self.assertIn("验收口径", entry["reason"])
            report = format_change_report(feature)
            self.assertIn("CHG-001", report)
            self.assertEqual(evaluate(feature).codes("G0"), [])

    def test_approved_change_rolls_back_gates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feature = init_feature(Path(tmp), "FEAT-CHG4")
            set_path(feature, "full")
            # 先把若干门禁标为 accepted（G0 即可）
            accept_gate(feature, "G0")
            state = json.loads((feature / "state.json").read_text(encoding="utf-8"))
            state["gates"]["G2"] = "accepted"
            state["gates"]["G2T"] = "accepted"
            state["gates"]["G3"] = "accepted"
            (feature / "state.json").write_text(
                json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            entry = record_change(
                feature,
                initiated_by="architect",
                reason="接口契约调整",
                level="C1",
                category="tech",
                summary="改 IF-1",
                artifacts=["tech.yaml"],
                gates_rollback=["G2T"],
                status="approved",
            )
            self.assertIn("_rollbackApplied", entry)
            saved = json.loads((feature / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(saved["gates"]["G2T"], "pending")
            self.assertEqual(saved["gates"]["G3"], "pending")
            self.assertEqual(saved["gates"]["G2"], "accepted")
            self.assertEqual(saved["stage"], "tech")

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

    def test_requirement_c4_rolls_back_listed_features(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            req_id = "REQ-500-split-c4-20220305"
            req = init_requirement(root, req_id)
            self.assertTrue((req / "change.yaml").is_file())
            f1 = init_feature(root, "FEAT-A", requirement_id=req_id)
            f2 = init_feature(root, "FEAT-B", requirement_id=req_id)
            set_path(f1, "full")
            set_path(f2, "full")
            accept_gate(f1, "G0")
            accept_gate(f2, "G0")
            for feat in (f1, f2):
                state = json.loads((feat / "state.json").read_text(encoding="utf-8"))
                state["gates"]["G2T"] = "accepted"
                (feat / "state.json").write_text(
                    json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
                )
            entry = record_change(
                req,
                initiated_by="product",
                reason="埋点可独立上线",
                level="C4",
                category="split",
                summary="拆出 FEAT-B",
                artifacts=["split.yaml"],
                gates_rollback=["G2T"],
                features=["FEAT-A", "FEAT-B"],
                status="approved",
                confirmed_by_role="human",
                confirmed_by_name="负责人",
            )
            self.assertEqual(len(entry["_rollbackApplied"]), 2)
            for feat in (f1, f2):
                saved = json.loads((feat / "state.json").read_text(encoding="utf-8"))
                self.assertEqual(saved["gates"]["G2T"], "pending")
            report = format_change_report(req)
            self.assertIn("需求", report)
            self.assertIn("CHG-001", report)


if __name__ == "__main__":
    unittest.main()
