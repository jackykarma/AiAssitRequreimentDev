"""split.yaml / check-req 校验（含需求级 architecture）。"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml

from aiassitrequreimentdev.gates import init_requirement
from aiassitrequreimentdev.split import evaluate_requirement, validate_split_doc
from aiassitrequreimentdev.template_headings import (
    REQ_ARCH_EXPAND_FILES,
    REQ_ARCH_H2,
    REQ_ARCH_H3_REQUIRED,
)


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


def _md_from_titles(
    h1: str,
    h2: tuple[str, ...],
    h3: tuple[str, ...] = (),
) -> str:
    lines = [f"# {h1}", ""]
    for title in h2:
        lines.append(f"## {title}")
        lines.append("")
        if title == "六、技术风险与边界场景":
            lines.append("### 6.1 技术风险与消解策略（绑定 Feature / Story）")
            lines.append("")
            lines.append("| ID | 风险 | 影响 | 落在 Feature / Story | 对策 |")
            lines.append("| --- | --- | --- | --- | --- |")
            lines.append("| RISK-1 | 测试 | 低 | FEAT-001-move-album | 缓解 |")
            lines.append("")
            lines.append("### 6.2 边界与异常场景枚举")
            lines.append("")
            lines.append("| 场景 | 类别 | 对策落点 |")
            lines.append("| --- | --- | --- |")
            lines.append("| 空数据 | 数据 | §七 |")
            lines.append("")
        elif title == "七、关键功能与疑难点/亮点设计":
            lines.append("### 7.1 关键设计清单")
            lines.append("")
            lines.append("| KD | 名称 | 类型 | 前置 KD | 影响 Feature | 文件 |")
            lines.append("| --- | --- | --- | --- | --- | --- |")
            lines.append("| — | 无 | — | — | — | — |")
            lines.append("")
            lines.append("### 7.2 详细设计引用")
            lines.append("")
            lines.append("无需求级 KD；见 keyDesignsNoneReason。")
            lines.append("")
        elif title == "八、技术评估（NFR）":
            lines.append("> 详表：[./nfr.md](./nfr.md)")
            lines.append("")
            lines.append("| 维度 | 结论 / 预算 | 缓解 | 详表 |")
            lines.append("| --- | --- | --- | --- |")
            lines.append("| 性能 | 可接受 | — | [./nfr.md](./nfr.md) |")
            lines.append("")
        elif title == "九、接口设计":
            lines.append("> 详表：[./interface-design.md](./interface-design.md)")
            lines.append("")
            lines.append("| ID | 方向 | 类型 | 提供方 | 消费方 | 摘要 | 冻结时机 |")
            lines.append("| --- | --- | --- | --- | --- | --- | --- |")
            lines.append("| — | — | — | — | — | N/A | — |")
            lines.append("")
        elif title == "十、数据库设计":
            lines.append("> 详表：[./database-design.md](./database-design.md)")
            lines.append("")
            lines.append("| 存储 | 变更 | 目的 | Owner Feature |")
            lines.append("| --- | --- | --- | --- |")
            lines.append("| — | none | N/A | — |")
            lines.append("")
        elif title == "十一、埋点技术方案":
            lines.append("> 详表：[./analytics-tracking.md](./analytics-tracking.md)")
            lines.append("")
            lines.append("| 事件 | 触发 | 关键字段 | Owner |")
            lines.append("| --- | --- | --- | --- |")
            lines.append("| — | — | N/A | — |")
            lines.append("")
        else:
            lines.append("（测试占位）")
            lines.append("")
    for title in h3:
        lines.append(f"### {title}")
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


def write_arch_expand_stubs(arch: Path, req_id: str) -> None:
    """按 design 模板三级标题落盘 §八～§十一展开件（单元测试用）。"""
    for filename, h3s in REQ_ARCH_EXPAND_FILES.items():
        lines = [f"# {filename} stub：{req_id}", ""]
        for h3 in h3s:
            lines.append(f"### {h3}")
            lines.append("")
            lines.append("N/A（单元测试占位，保留模板标题）。")
            lines.append("")
        (arch / filename).write_text("\n".join(lines), encoding="utf-8")


def fill_architecture(req_dir: Path, req_id: str, feature_ids: list[str]) -> None:
    arch = req_dir / "architecture"
    (arch / "architecture.md").write_text(
        _md_from_titles(
            f"需求级架构：{req_id}",
            REQ_ARCH_H2,
            REQ_ARCH_H3_REQUIRED,
        ),
        encoding="utf-8",
    )
    write_arch_expand_stubs(arch, req_id)
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

    def test_check_req_rejects_thin_architecture_without_h3(self) -> None:
        """仅 ## + 一行摘要不得过 check-req（须对齐 Epic 模板 ### / 表格）。"""
        with tempfile.TemporaryDirectory() as tmp:
            req_id = "REQ-303-thin-arch-20220305"
            dest = init_requirement(Path(tmp), req_id)
            (dest / "split.yaml").write_text(
                yaml.safe_dump(valid_split(req_id), allow_unicode=True, sort_keys=False),
                encoding="utf-8",
            )
            fill_architecture(dest, req_id, ["FEAT-001-move-album"])
            # 故意压成「只有 H2 一行摘要」
            thin_lines = [f"# 需求级架构：{req_id}", ""]
            for title in REQ_ARCH_H2:
                thin_lines += [f"## {title}", "", "一行摘要糊弄。", ""]
            (dest / "architecture" / "architecture.md").write_text(
                "\n".join(thin_lines), encoding="utf-8"
            )
            codes = {v.code for v in evaluate_requirement(dest)}
            self.assertTrue({"ARCH_MD_H3", "ARCH_MD_THIN"} & codes)

    def test_check_req_requires_design_expand_files(self) -> None:
        """§八～§十一须独立展开件 + 章内链接（对齐 templates/design/）。"""
        with tempfile.TemporaryDirectory() as tmp:
            req_id = "REQ-304-expand-20220305"
            dest = init_requirement(Path(tmp), req_id)
            (dest / "split.yaml").write_text(
                yaml.safe_dump(valid_split(req_id), allow_unicode=True, sort_keys=False),
                encoding="utf-8",
            )
            fill_architecture(dest, req_id, ["FEAT-001-move-album"])
            self.assertEqual(evaluate_requirement(dest), [])
            # 删掉展开件 → ARCH_EXPAND_MISSING
            for name in REQ_ARCH_EXPAND_FILES:
                (dest / "architecture" / name).unlink()
            codes = {v.code for v in evaluate_requirement(dest)}
            self.assertIn("ARCH_EXPAND_MISSING", codes)
            # 恢复文件但去掉标题 → ARCH_EXPAND_HEADING
            write_arch_expand_stubs(dest / "architecture", req_id)
            (dest / "architecture" / "nfr.md").write_text(
                "# NFR\n\n无模板三级标题。\n", encoding="utf-8"
            )
            codes = {v.code for v in evaluate_requirement(dest)}
            self.assertIn("ARCH_EXPAND_HEADING", codes)
            # 标题齐全但不在章内引用 → ARCH_EXPAND_UNLINKED
            write_arch_expand_stubs(dest / "architecture", req_id)
            md = (dest / "architecture" / "architecture.md").read_text(encoding="utf-8")
            md = md.replace("nfr.md", "MISSING_NFR_LINK")
            (dest / "architecture" / "architecture.md").write_text(md, encoding="utf-8")
            codes = {v.code for v in evaluate_requirement(dest)}
            self.assertIn("ARCH_EXPAND_UNLINKED", codes)

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
