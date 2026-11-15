"""
/*********************************************************************************
 ** Copyright (C), 2019-2029, OPLUS Mobile Comm Corp., Ltd
 ** All rights reserved.
 **
 ** File: - template_headings.py
 ** Description: feature/prd/tech 模板必含 Markdown 标题（门禁逐条校验）
 ** Version: 1.1
 ** Date: 2026/11/15
 ** Author: limao2@Apps.Gallery
 **
 ** ------------------------------- Revision History: ----------------------------
 ** <author> <date> <version> <desc>
 ** ------------------------------------------------------------------------------
 ** limao2@Apps.Gallery 2026/11/15 1.0 INIT
 ** limao2@Apps.Gallery 2026/11/15 1.1 feature 级 tech 标题（去 EPIC/Story 漂移）
 *********************************************************************************/
"""

from __future__ import annotations

# feature/prd.md（## 级须齐全；底稿 templates/feature/prd.md）
SPEC_PRD_H2 = (
    "背景与目标",
    "范围与非目标",
    "核心用户旅程（UJ*）",
    "功能需求（FR*）",
    "非功能需求（NFR*）",
    "边界与异常（E*）",
    "验收标准（A*）",
    "产品原型",
    "补充场景（S*，可选）",
    "开放问题",
)

# requirements/.../prd.md（底稿 templates/requirement/prd.md）
REQ_PRD_H2 = (
    "背景与目标",
    "范围与非目标",
    "核心用户旅程总览",
    "功能与非功能总览",
    "边界与异常总览",
    "验收总览",
    "Feature 拆分依据",
    "开放问题",
)

# 兼容旧名
EPIC_PRD_H2 = REQ_PRD_H2

# feature/tech.md（底稿 templates/feature/tech.md）· 本切片技术方案
TECH_MD_H2 = (
    "变更记录",
    "设计前置检查",
    "一、简介与范围",
    "二、需求与验收追溯",
    "三、关键设计判定",
    "四、零层架构（L0）",
    "五、一层架构（L1）",
    "六、技术风险与边界",
    "七、关键设计",
    "八、NFR 评估",
    "九、接口设计",
    "十、数据设计",
    "十一、埋点",
    "十二、实现与任务指引",
    "附录：与 tech.yaml / tasks 对应",
)

# full 路径强制；light 族可省略（见 gates._check_g2t）
TECH_MD_H3_REQUIRED = (
    "4.2 零层架构图（必须）",
    "5.1 一层框架图（必须）",
    "5.3 组件协作流程（必须）",
)

# feature/tech-spec.md · 本切片工程/边界约束（非 EPIC 大包）
TECH_SPEC_H2 = (
    "Tech Spec 前置检查",
    "变更记录",
    "一、工程与运行时约束",
    "二、模块边界与依赖",
    "三、数据与存储约束",
    "四、安全与合规约束",
    "五、共享能力与外部依赖",
)


def extract_markdown_headings(text: str) -> dict[int, list[str]]:
    """返回 {级别: [标题正文, ...]}，标题正文不含 #。"""
    levels: dict[int, list[str]] = {1: [], 2: [], 3: []}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("#"):
            continue
        level = 0
        for ch in stripped:
            if ch == "#":
                level += 1
            else:
                break
        if level < 1 or level > 3:
            continue
        title = stripped[level:].strip()
        if title:
            levels.setdefault(level, []).append(title)
    return levels


def missing_headings(present: list[str], required: tuple[str, ...]) -> list[str]:
    """要求 required 中每一项在 present 中精确出现（完整标题字符串）。"""
    have = set(present)
    return [h for h in required if h not in have]
