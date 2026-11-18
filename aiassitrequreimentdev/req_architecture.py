"""
/*********************************************************************************
 ** Copyright (C), 2019-2029, OPLUS Mobile Comm Corp., Ltd
 ** All rights reserved.
 **
 ** File: - req_architecture.py
 ** Description: requirements/.../architecture 校验（check-req 硬门槛）。
 ** Version: 1.1
 ** Date: 2026/11/18
 ** Author: limao2@Apps.Gallery
 **
 ** ------------------------------- Revision History: ----------------------------
 ** <author> <date> <version> <desc>
 ** ------------------------------------------------------------------------------
 ** limao2@Apps.Gallery 2026/11/18 1.0 INIT
 ** limao2@Apps.Gallery 2026/11/18 1.1 §八～§十一强制 design 展开件
 *********************************************************************************/
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from aiassitrequreimentdev.gates import Violation
from aiassitrequreimentdev.template_headings import (
    REQ_ARCH_EXPAND_FILES,
    REQ_ARCH_EXPAND_LINKS,
    REQ_ARCH_H2,
    REQ_ARCH_H3_REQUIRED,
    extract_markdown_headings,
    missing_headings,
)

PLACEHOLDER_TOKENS = ("PLACEHOLDER", "待填写", "TODO", "TBD")


def _is_placeholder_text(value: str) -> bool:
    text = value.strip()
    if not text:
        return True
    return any(token in text for token in PLACEHOLDER_TOKENS)


def _check_archify_html(path: Path) -> str | None:
    if not path.is_file():
        return f"文件不存在: {path.name}"
    raw = path.read_text(encoding="utf-8", errors="ignore")
    lower = raw.lower()
    has_generator = bool(
        re.search(r'<meta\s+name=["\']generator["\']\s+content=["\']archify\b', lower)
    )
    has_contract = "archify-reader-contract" in lower
    has_fonts = 'id="archify-fonts"' in lower or "id='archify-fonts'" in lower
    if not (has_generator and has_contract and has_fonts):
        return (
            f"{path.name} 须为 Archify finalize 产物（meta generator=archify、"
            "archify-reader-contract、style#archify-fonts）"
        )
    return None


def _check_png(path: Path) -> str | None:
    if not path.is_file():
        return f"文件不存在: {path.name}"
    raw = path.read_bytes()
    if not raw.startswith(b"\x89PNG\r\n\x1a\n"):
        return f"{path.name} 不是有效 PNG"
    if len(raw) < 2048:
        return f"{path.name} 过小（须为可审阅 Archify 预览，禁止占位空壳）"
    return None


def _h2_section(md_text: str, h2_title: str) -> str:
    marker = f"## {h2_title}"
    start = md_text.find(marker)
    if start < 0:
        return ""
    nxt = md_text.find("\n## ", start + len(marker))
    return md_text[start : nxt if nxt > 0 else len(md_text)]


def _check_architecture_expands(arch_dir: Path, md_text: str | None) -> list[Violation]:
    """§八～§十一须独立落盘 design 展开件，且 architecture.md 对应章须引用。"""
    violations: list[Violation] = []
    for filename, required_h3 in REQ_ARCH_EXPAND_FILES.items():
        path = arch_dir / filename
        if not path.is_file():
            violations.append(
                Violation(
                    "REQ",
                    "ARCH_EXPAND_MISSING",
                    f"缺少 architecture/{filename}（§八～§十一须按 "
                    "templates/design/ 独立落盘，禁止只写在 architecture.md）",
                )
            )
            continue
        expand_text = path.read_text(encoding="utf-8")
        expand_h = extract_markdown_headings(expand_text)
        for title in missing_headings(expand_h.get(3, []), required_h3):
            violations.append(
                Violation(
                    "REQ",
                    "ARCH_EXPAND_HEADING",
                    f"{filename} 缺少三级标题（对齐 design 模板）：{title}",
                )
            )
    if md_text is None:
        return violations
    for h2, link_file in REQ_ARCH_EXPAND_LINKS.items():
        chunk = _h2_section(md_text, h2)
        if not chunk:
            continue
        if link_file not in chunk:
            violations.append(
                Violation(
                    "REQ",
                    "ARCH_EXPAND_UNLINKED",
                    f"architecture.md「{h2}」须引用独立展开件 ./{link_file} "
                    "（本节只保留摘要表 + 链接）",
                )
            )
    return violations


def evaluate_req_architecture(
    req_dir: Path,
    *,
    split_feature_ids: list[str] | None = None,
) -> list[Violation]:
    """校验需求级 architecture/；失败码挂在 gate=REQ。"""
    violations: list[Violation] = []
    arch_dir = req_dir / "architecture"
    if not arch_dir.is_dir():
        violations.append(
            Violation(
                "REQ",
                "ARCH_MISSING",
                "缺少 architecture/ 目录（大需求须产出整需求 L0/L1 架构）",
            )
        )
        return violations

    md_path = arch_dir / "architecture.md"
    md_text: str | None = None
    if not md_path.is_file():
        violations.append(
            Violation("REQ", "ARCH_MD_MISSING", "缺少 architecture/architecture.md")
        )
    else:
        md_text = md_path.read_text(encoding="utf-8")
        headings = extract_markdown_headings(md_text)
        missing = missing_headings(headings.get(2, []), REQ_ARCH_H2)
        for title in missing:
            violations.append(
                Violation(
                    "REQ",
                    "ARCH_MD_HEADING",
                    f"architecture.md 缺少二级标题：{title}",
                )
            )
        missing_h3 = missing_headings(headings.get(3, []), REQ_ARCH_H3_REQUIRED)
        for title in missing_h3:
            violations.append(
                Violation(
                    "REQ",
                    "ARCH_MD_H3",
                    f"architecture.md 缺少三级标题（须对齐 Epic Design 模板）：{title}",
                )
            )
        # 禁止仅用一行摘要糊弄 §六～§十一（模板要求表格）
        thin_markers = (
            ("## 六、技术风险与边界场景", "### 6.1"),
            ("## 七、关键功能与疑难点/亮点设计", "### 7.1"),
            ("## 八、技术评估（NFR）", "| 维度 |"),
            ("## 九、接口设计", "| ID |"),
            ("## 十、数据库设计", "| 存储 |"),
            ("## 十一、埋点技术方案", "| 事件 |"),
        )
        for h2, must in thin_markers:
            start = md_text.find(h2)
            if start < 0:
                continue
            nxt = md_text.find("\n## ", start + len(h2))
            chunk = md_text[start:nxt if nxt > 0 else len(md_text)]
            if must not in chunk:
                violations.append(
                    Violation(
                        "REQ",
                        "ARCH_MD_THIN",
                        f"{h2} 未按模板展开（缺少「{must}」结构，禁止只写一行摘要）",
                    )
                )

    violations.extend(_check_architecture_expands(arch_dir, md_text))

    yaml_path = arch_dir / "architecture.yaml"
    if not yaml_path.is_file():
        violations.append(
            Violation("REQ", "ARCH_YAML_MISSING", "缺少 architecture/architecture.yaml")
        )
        return violations

    try:
        doc = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        violations.append(
            Violation("REQ", "ARCH_YAML_PARSE", f"architecture.yaml 无法解析: {exc}")
        )
        return violations
    if not isinstance(doc, dict):
        violations.append(
            Violation("REQ", "ARCH_YAML_PARSE", "architecture.yaml 必须是映射")
        )
        return violations

    req_id = doc.get("requirementId")
    if not isinstance(req_id, str) or not req_id.strip():
        violations.append(
            Violation("REQ", "ARCH_YAML_SHAPE", "architecture.yaml requirementId 不能为空")
        )
    elif req_id.strip() != req_dir.name:
        violations.append(
            Violation(
                "REQ",
                "ARCH_YAML_SHAPE",
                f"architecture.yaml requirementId 与目录不一致：{req_id.strip()}",
            )
        )

    summary = doc.get("summary")
    if not isinstance(summary, str) or _is_placeholder_text(summary):
        violations.append(
            Violation(
                "REQ",
                "ARCH_YAML_SHAPE",
                "architecture.yaml summary 须填写整需求架构一句话摘要（非占位）",
            )
        )

    features = doc.get("features")
    if not isinstance(features, list):
        violations.append(
            Violation("REQ", "ARCH_YAML_SHAPE", "architecture.yaml features 必须是列表")
        )
        features = []
    elif split_feature_ids is not None:
        arch_ids = [x.strip() for x in features if isinstance(x, str) and x.strip()]
        if set(arch_ids) != set(split_feature_ids):
            violations.append(
                Violation(
                    "REQ",
                    "ARCH_FEATURE_TRACE",
                    "architecture.yaml features 须与 split.yaml features[].id 集合一致 "
                    f"（architecture={sorted(arch_ids)} split={sorted(split_feature_ids)}）",
                )
            )

    contracts = doc.get("contracts")
    if not isinstance(contracts, list):
        violations.append(
            Violation("REQ", "ARCH_YAML_SHAPE", "architecture.yaml contracts 必须是列表")
        )
    elif not contracts:
        reason = doc.get("contractsNoneReason")
        if not isinstance(reason, str) or not reason.strip():
            violations.append(
                Violation(
                    "REQ",
                    "ARCH_YAML_SHAPE",
                    "无跨 Feature 契约时须填写 contractsNoneReason",
                )
            )

    risks = doc.get("risks")
    if not isinstance(risks, list):
        violations.append(
            Violation("REQ", "ARCH_YAML_SHAPE", "architecture.yaml risks 必须是列表")
        )
    elif not risks:
        reason = doc.get("risksNoneReason")
        if not isinstance(reason, str) or not reason.strip():
            violations.append(
                Violation(
                    "REQ",
                    "ARCH_YAML_SHAPE",
                    "无风险时须填写 risksNoneReason",
                )
            )

    open_qs = doc.get("openTechQuestions")
    if not isinstance(open_qs, list):
        violations.append(
            Violation(
                "REQ",
                "ARCH_YAML_SHAPE",
                "architecture.yaml openTechQuestions 必须是列表",
            )
        )
    else:
        for index, item in enumerate(open_qs):
            if not isinstance(item, dict):
                violations.append(
                    Violation(
                        "REQ",
                        "ARCH_OPEN_Q",
                        f"openTechQuestions[{index}] 必须是映射",
                    )
                )
                continue
            if item.get("blocking") is True:
                violations.append(
                    Violation(
                        "REQ",
                        "ARCH_OPEN_BLOCKING",
                        f"openTechQuestions[{index}] blocking=true："
                        f"{item.get('question') or item.get('id') or index}；"
                        "闭合前不要批量 init Feature",
                    )
                )

    diagrams = doc.get("diagrams")
    if not isinstance(diagrams, list):
        violations.append(
            Violation("REQ", "ARCH_DIAGRAM", "architecture.yaml diagrams 必须是列表")
        )
        return violations

    layers: set[int] = set()
    if not diagrams:
        violations.append(
            Violation(
                "REQ",
                "ARCH_DIAGRAM",
                "diagrams 不能为空：须含 layer 0 与 1 的 architecture 图",
            )
        )
    for index, item in enumerate(diagrams):
        if not isinstance(item, dict):
            violations.append(
                Violation("REQ", "ARCH_DIAGRAM", f"diagrams[{index}] 必须是映射")
            )
            continue
        if item.get("type") != "architecture":
            continue
        if item.get("tool") != "archify":
            violations.append(
                Violation(
                    "REQ",
                    "ARCH_DIAGRAM",
                    f"diagrams[{index}].tool 必须为 archify",
                )
            )
        layer = item.get("layer")
        if layer in (0, "0"):
            layers.add(0)
        elif layer in (1, "1"):
            layers.add(1)
        else:
            violations.append(
                Violation(
                    "REQ",
                    "ARCH_DIAGRAM",
                    f"diagrams[{index}] architecture 的 layer 须为 0 或 1",
                )
            )
        for key in ("html", "png"):
            rel = item.get(key)
            if not isinstance(rel, str) or not rel.strip():
                violations.append(
                    Violation(
                        "REQ",
                        "ARCH_DIAGRAM",
                        f"diagrams[{index}].{key} 不能为空",
                    )
                )
                continue
            path_text = rel.strip().replace("\\", "/")
            if "PLACEHOLDER" in path_text.upper():
                violations.append(
                    Violation(
                        "REQ",
                        "ARCH_DIAGRAM_PLACEHOLDER",
                        f"diagrams[{index}].{key} 仍是 PLACEHOLDER，须替换为 Archify 真图",
                    )
                )
                continue
            target = (arch_dir / path_text).resolve()
            try:
                target.relative_to(arch_dir.resolve())
            except ValueError:
                violations.append(
                    Violation(
                        "REQ",
                        "ARCH_DIAGRAM",
                        f"diagrams[{index}].{key} 必须落在 architecture/ 内",
                    )
                )
                continue
            if key == "html":
                err = _check_archify_html(target)
            else:
                err = _check_png(target)
            if err:
                violations.append(Violation("REQ", "ARCH_DIAGRAM_QUALITY", err))

    if layers != {0, 1}:
        missing = sorted({0, 1} - layers)
        violations.append(
            Violation(
                "REQ",
                "ARCH_DIAGRAM",
                f"须同时登记 layer 0 与 1 的 architecture 图（缺少 {missing}）",
            )
        )

    return violations
