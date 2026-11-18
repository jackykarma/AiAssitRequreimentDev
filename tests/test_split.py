"""split.yaml / check-req 校验（含需求级 architecture）。"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml

from aiassitrequreimentdev.gates import init_requirement
from aiassitrequreimentdev.split import evaluate_requirement, validate_split_doc
from aiassitrequreimentdev.template_headings import REQ_ARCH_H2


def valid_split(req_id: str = "REQ-001-move-album-20220305") -> dict:
    return {
        "requirementId": req_id,
        "decision": "single",
        "rationale": "验收同窗上线，单一切片即可 G4",
        "confirmedByHuman": False,
        "features": [
            {
                "id": "FEAT-001-move-album",
                "title": "移动相册主路径",
                "scope": "图集内移动照片并覆盖 A1–A3",
                "path": "full",
                "dependsOn": [],
            }
        ],
    }


def _md_from_titles(h1: str, h2: tuple[str, ...]) -> str:
    lines = [f"# {h1}", ""]
    for title in h2:
        lines.append(f"## {title}")
        lines.append("")
        lines.append("（测试占位）")
        lines.append("")
    return "\n".join(lines)


def write_archify_html(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        """<!DOCTYPE html>
<html lang="en"><head>
  <meta charset="UTF-8">
  <meta name="generator" content="archify 3.2.0">
  <meta name="archify-reader-contract" content="declared-wide-v1">
  <style id="archify-fonts"></style>
</head><body>stub</body></html>
""",
        encoding="utf-8",
    )


def write_preview_png(path: Path, *, w: int = 640, h: int = 400) -> None:
    import struct
    import zlib

    path.parent.mkdir(parents=True, exist_ok=True)
    rows: list[bytes] = []
    for y in range(h):
        row = bytearray(1 + w * 3)
        row[0] = 0
        for x in range(w):
            i = 1 + x * 3
            row[i] = (x + y) & 0xFF
            row[i + 1] = (x * 3 + y * 5) & 0xFF
            row[i + 2] = (255 - ((x + y) & 0xFF)) & 0xFF
        rows.append(bytes(row))
    raw = b"".join(rows)

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


def fill_architecture(req_dir: Path, req_id: str, feature_ids: list[str]) -> None:
    arch = req_dir / "architecture"
    (arch / "architecture.md").write_text(
        _md_from_titles(f"需求级架构：{req_id}", REQ_ARCH_H2),
        encoding="utf-8",
    )
    diagrams = arch / "diagrams"
    write_archify_html(diagrams / "req.L0.architecture.html")
    write_preview_png(diagrams / "req.L0.architecture.png")
    write_archify_html(diagrams / "req.L1.architecture.html")
    write_preview_png(diagrams / "req.L1.architecture.png")
    doc = {
        "requirementId": req_id,
        "summary": "移动相册整需求上下文与模块归属",
        "features": feature_ids,
        "contracts": [],
        "contractsNoneReason": "单 Feature，无跨切片契约",
        "keyDesigns": [],
        "keyDesignsNoneReason": "无需求级 KD",
        "risks": [],
        "risksNoneReason": "无整需求级风险",
        "openTechQuestions": [],
        "diagrams": [
            {
                "id": "D-L0",
                "type": "architecture",
                "layer": 0,
                "title": "L0",
                "scope": "外部边界",
                "tool": "archify",
                "html": "diagrams/req.L0.architecture.html",
                "png": "diagrams/req.L0.architecture.png",
            },
            {
                "id": "D-L1",
                "type": "architecture",
                "layer": 1,
                "title": "L1",
                "scope": "模块归属",
                "tool": "archify",
                "html": "diagrams/req.L1.architecture.html",
                "png": "diagrams/req.L1.architecture.png",
            },
        ],
        "diagramsNoneReason": "",
    }
    (arch / "architecture.yaml").write_text(
        yaml.safe_dump(doc, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


class SplitTests(unittest.TestCase):
    def test_validate_accepts_single(self) -> None:
        self.assertEqual(validate_split_doc(valid_split()), [])

    def test_multi_requires_human_confirm(self) -> None:
        doc = valid_split()
        doc["decision"] = "multi"
        doc["features"].append(
            {
                "id": "FEAT-002-move-tracking",
                "title": "埋点",
                "scope": "移动成功埋点",
                "path": "light-auto",
                "dependsOn": ["FEAT-001-move-album"],
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
            self.assertTrue(
                {"ARCH_DIAGRAM_PLACEHOLDER", "ARCH_YAML_SHAPE", "ARCH_MD_HEADING"}
                & codes
                or any(c.startswith("ARCH_") for c in codes)
            )

    def test_check_req_ready_after_fill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            req_id = "REQ-301-split-ok-20220305"
            dest = init_requirement(Path(tmp), req_id)
            split = valid_split(req_id)
            (dest / "split.yaml").write_text(
                yaml.safe_dump(split, allow_unicode=True, sort_keys=False),
                encoding="utf-8",
            )
            fill_architecture(dest, req_id, ["FEAT-001-move-album"])
            self.assertEqual(evaluate_requirement(dest), [])

    def test_check_req_blocks_open_tech_question(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            req_id = "REQ-302-open-q-20220305"
            dest = init_requirement(Path(tmp), req_id)
            (dest / "split.yaml").write_text(
                yaml.safe_dump(valid_split(req_id), allow_unicode=True, sort_keys=False),
                encoding="utf-8",
            )
            fill_architecture(dest, req_id, ["FEAT-001-move-album"])
            arch_path = dest / "architecture" / "architecture.yaml"
            doc = yaml.safe_load(arch_path.read_text(encoding="utf-8"))
            doc["openTechQuestions"] = [
                {
                    "id": "Q1",
                    "question": "存储选型未定",
                    "blocking": True,
                    "owner": "architect",
                }
            ]
            arch_path.write_text(
                yaml.safe_dump(doc, allow_unicode=True, sort_keys=False),
                encoding="utf-8",
            )
            codes = {v.code for v in evaluate_requirement(dest)}
            self.assertIn("ARCH_OPEN_BLOCKING", codes)


if __name__ == "__main__":
    unittest.main()
