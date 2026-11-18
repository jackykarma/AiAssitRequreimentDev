"""
/*********************************************************************************
 ** Copyright (C), 2019-2029, OPLUS Mobile Comm Corp., Ltd
 ** All rights reserved.
 **
 ** File: - template_headings.py
 ** Description: feature/prd/tech 模板必含 Markdown 标题（门禁逐条校验）
 ** Version: 1.2
 ** Date: 2026/11/18
 ** Author: limao2@Apps.Gallery
 **
 ** ------------------------------- Revision History: ----------------------------
 ** <author> <date> <version> <desc>
 ** ------------------------------------------------------------------------------
 ** limao2@Apps.Gallery 2026/11/15 1.0 INIT
 ** limao2@Apps.Gallery 2026/11/15 1.1 feature 级 tech 标题（去 EPIC/Story 漂移）
 ** limao2@Apps.Gallery 2026/11/18 1.2 REQ Epic §八～§十一展开件标题
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
    "整需求架构",
    "开放问题",
)

# requirements/.../architecture/architecture.md（Epic Design，对齐 AISDD epic-design）
REQ_ARCH_H2 = (
    "变更记录（增量变更）",
    "设计前置检查",
    "一、简介",
    "二、需求概述",
    "三、领域模型",
    "四、零层架构（L0）",
    "五、一层架构（L1）",
    "六、技术风险与边界场景",
    "七、关键功能与疑难点/亮点设计",
    "八、技术评估（NFR）",
    "九、接口设计",
    "十、数据库设计",
    "十一、埋点技术方案",
    "十二、Feature 与 Story 拆解索引",
    "十三、Story 详细设计索引",
    "附录：与 Feature tech / Story / tasks 的对应关系",
)

# architecture.md 强制三级标题（与 templates/requirement/architecture/architecture.md 对齐）
REQ_ARCH_H3_REQUIRED = (
    "前置检查清单",
    "跨 Feature 共享能力登记",
    "P0 覆盖快照（与各 Feature spec 对照）",
    "前置检查结论",
    "1.1 目的和对象",
    "1.2 范围",
    "2.1 需求背景",
    "2.2 需求范围及限制（按 Feature 索引）",
    "3.1 领域概念",
    "3.2 领域概念词汇表（必须）",
    "4.1 边界说明",
    "4.2 零层架构图（必须）",
    "4.3 架构设计说明（必须）",
    "4.4 外部依赖清单",
    "5.1 一层框架图（必须）",
    "5.2 组件清单与职责（必须）",
    "5.3 组件协作流程图（必须）",
    "5.4 技术方案选型",
    "6.1 技术风险与消解策略（绑定 Feature / Story）",
    "6.2 边界与异常场景枚举",
    "7.1 关键设计清单",
    "7.2 详细设计引用",
    "12.1 拆解策略与约束",
    "12.2 Feature 列表（与 split 对齐）",
    "12.3 Story 列表（按 Feature 分组，可选）",
    "12.4 Story 依赖与并行度",
    "12.5 Feature → 设计覆盖矩阵",
    "13.1 索引表",
    "13.2 依赖总览",
    "13.3 覆盖度检查",
)

# requirements/.../architecture/ 展开件（§八～§十一必须独立落盘，正文只保留摘要+链接）
# 文件名 → 必含 ### 标题（对齐 templates/design/）
REQ_ARCH_EXPAND_FILES: dict[str, tuple[str, ...]] = {
    "nfr.md": (
        "8.1 算法评估（如适用）",
        "8.2 功耗评估（必须量化，基于场景）",
        "8.3 性能评估（必须量化，基于场景）",
        "8.4 内存评估（必须量化，基于场景）",
        "8.5 安全评估（如适用）",
        "8.6 兼容性评估（必须）",
        "8.7 RomSize 增量评估（必须）",
    ),
    "interface-design.md": (
        "9.1 对外提供的接口",
        "9.2 依赖的外部接口",
        "9.3 接口一致性自检",
    ),
    "database-design.md": (
        "10.1 数据库概览",
        "10.2 数据表详细设计",
        "10.3 数据设计说明",
        "10.4 数据库设计一致性自检",
    ),
    "analytics-tracking.md": (
        "11.1 埋点事件与字段规约",
        "11.2 埋点一致性自检（推荐）",
    ),
}

# architecture.md 各章须引用的相对路径（禁止只在章内写满详表却无展开件）
REQ_ARCH_EXPAND_LINKS: dict[str, str] = {
    "八、技术评估（NFR）": "nfr.md",
    "九、接口设计": "interface-design.md",
    "十、数据库设计": "database-design.md",
    "十一、埋点技术方案": "analytics-tracking.md",
}

# 兼容旧名
EPIC_PRD_H2 = REQ_PRD_H2

# feature/tech.md · 薄切片交付合同（整册在 REQ Epic Design）
TECH_MD_H2 = (
    "变更记录",
    "设计前置检查",
    "一、简介与交付范围",
    "二、验收追溯",
    "三、Epic 引用与本切片增量",
    "四、本切片架构增量",
    "五、本切片关键设计",
    "六、本切片约束与风险增量",
    "七、Story 与任务指引",
    "附录：与 tech.yaml / Epic / Story 对应",
)

# full 路径强制；light 族可省略（见 gates._check_g2t）
TECH_MD_H3_REQUIRED = (
    "4.1 相对 Epic 的架构说明",
    "4.2 本切片架构图（增量或引用内嵌）",
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
