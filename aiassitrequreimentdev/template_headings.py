"""
/*********************************************************************************
 ** Copyright (C), 2019-2029, OPLUS Mobile Comm Corp., Ltd
 ** All rights reserved.
 **
 ** File: - template_headings.py
 ** Description: Verity specify 模板必含 Markdown 标题（门禁逐条校验）
 ** Version: 1.0
 ** Date: 2026/11/15
 ** Author: limao2@Apps.Gallery
 **
 ** ------------------------------- Revision History: ----------------------------
 ** <author> <date> <version> <desc>
 ** ------------------------------------------------------------------------------
 ** limao2@Apps.Gallery 2026/11/15 1.0 INIT
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

# feature/tech.md（底稿 templates/feature/tech.md）
TECH_MD_H2 = (
    "变更记录（增量变更）",
    "设计前置检查（必须，在开始设计前完成）",
    "一、简介",
    "二、需求概述",
    "三、领域模型",
    "四、零层架构（EPIC 与外部/现有工程边界）",
    "五、一层架构（分层与模块职责）",
    "六、技术风险与边界场景（设计输入）",
    "七、关键功能与疑难点/亮点设计",
    "八、技术评估（设计产出验证，必须量化）",
    "九、接口设计",
    "十、数据库设计",
    "十一、埋点技术方案",
    "十二、Story 拆解",
    "十三、二层 Story 详细设计（L2）索引",
    "附录 A：设计说明书与 tech-spec/tasks 的对应关系",
)

# 架构相关强制三级标题（与模板「必须」一致）
TECH_MD_H3_REQUIRED = (
    "4.2 零层架构图（必须）",
    "5.1 一层框架图（必须）",
    "5.3 组件协作流程图（必须）",
)

# feature/tech-spec.md（底稿 templates/feature/tech-spec.md）
TECH_SPEC_H2 = (
    "Tech Spec 前置检查",
    "变更记录（增量变更）",
    "一、EPIC 级公共约束",
    "二、跨 Feature 边界与依赖规则",
    "三、统一运行时约束",
    "四、数据与存储总约束",
    "五、跨 Feature 共享能力识别",
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
