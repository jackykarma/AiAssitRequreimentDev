"""split.yaml / check-req 校验。"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from aiassitrequreimentdev.gates import init_requirement
from aiassitrequreimentdev.split import evaluate_requirement, validate_split_doc


def valid_split(req_id: str = "REQ-001-move-album-20220305") -> dict:
    return {
        "requirementId": req_id,
        "decision": "single",
        "rationale": "验收同窗上线，单一切片即可 G4",
        "confirmedByHuman": False,
        "features": [
            {
                "id": "FEAT-001",
                "title": "移动相册主路径",
                "scope": "图集内移动照片并覆盖 A1–A3",
                "path": "full",
                "dependsOn": [],
            }
        ],
    }


class SplitTests(unittest.TestCase):
    def test_validate_accepts_single(self) -> None:
        self.assertEqual(validate_split_doc(valid_split()), [])

    def test_multi_requires_human_confirm(self) -> None:
        doc = valid_split()
        doc["decision"] = "multi"
        doc["features"].append(
            {
                "id": "FEAT-002",
                "title": "埋点",
                "scope": "移动成功埋点",
                "path": "light-auto",
                "dependsOn": ["FEAT-001"],
            }
        )
        errors = validate_split_doc(doc)
        self.assertTrue(any("confirmedByHuman" in e for e in errors))
        doc["confirmedByHuman"] = True
        self.assertEqual(validate_split_doc(doc), [])

    def test_rejects_placeholder_and_unknown_depends(self) -> None:
        doc = valid_split()
        doc["rationale"] = "待产品填写"
        doc["features"][0]["dependsOn"] = ["FEAT-999"]
        errors = validate_split_doc(doc)
        self.assertTrue(any("占位" in e for e in errors))
        self.assertTrue(any("不存在" in e for e in errors))

    def test_check_req_on_init_template_fails_until_filled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            req_id = "REQ-300-split-check-20220305"
            dest = init_requirement(Path(tmp), req_id)
            codes = {v.code for v in evaluate_requirement(dest)}
            self.assertIn("SPLIT_SHAPE", codes)

    def test_check_req_ready_after_fill(self) -> None:
        import yaml

        with tempfile.TemporaryDirectory() as tmp:
            req_id = "REQ-301-split-ok-20220305"
            dest = init_requirement(Path(tmp), req_id)
            (dest / "split.yaml").write_text(
                yaml.safe_dump(valid_split(req_id), allow_unicode=True, sort_keys=False),
                encoding="utf-8",
            )
            self.assertEqual(evaluate_requirement(dest), [])


if __name__ == "__main__":
    unittest.main()
