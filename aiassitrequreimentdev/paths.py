"""
/*********************************************************************************
 ** Copyright (C), 2019-2029, OPLUS Mobile Comm Corp., Ltd
 ** All rights reserved.
 **
 ** File: - paths.py
 ** Description: 全量/轻量/轻量自动路径推荐与确认。人最终选择写入 state.path。
 ** Version: 1.1
 ** Date: 2026/11/15
 ** Author: limao2@Apps.Gallery
 **
 ** ------------------------------- Revision History: ----------------------------
 ** <author> <date> <version> <desc>
 ** ------------------------------------------------------------------------------
 ** limao2@Apps.Gallery 2026/11/08 1.0 INIT
 ** limao2@Apps.Gallery 2026/11/15 1.1 light-auto（无 UI 小需求 seal 后连跑）
 *********************************************************************************/
"""

from __future__ import annotations

from dataclasses import dataclass


LIGHT_HINTS = (
    "bug",
    "缺陷",
    "修复",
    "hotfix",
    "小改",
    "文案",
    "样式",
    "日志",
    "单模块",
    "单文件",
    "回归",
    "已有验收",
    "行为修正",
    "崩溃",
    "空指针",
    "crash",
    "typo",
)

AUTO_HINTS = (
    "无ui",
    "无界面",
    "不改ui",
    "不改界面",
    "无前端",
    "纯逻辑",
    "仅后端",
    "后台",
    "cli",
    "接口修复",
    "全自动",
    "goal",
    "light-auto",
    "轻量自动",
)

FULL_HINTS = (
    "新功能",
    "新能力",
    "全新",
    "跨模块",
    "跨领域",
    "状态机",
    "对外契约",
    "对外接口",
    "协议",
    "数据迁移",
    "权限",
    "安全",
    "多端",
    "新页面",
    "主流程",
    "产品",
    "prd",
    "原型",
    "架构",
    "平台化",
)

# light 与 light-auto 共享「单 affected + 单任务 + 可跳 UX」约束
LIGHT_FAMILY = frozenset({"light", "light-auto"})


@dataclass(frozen=True)
class PathOption:
    id: str
    label: str
    summary: str
    includes: tuple[str, ...]


PATHS = (
    PathOption(
        id="full",
        label="全量模式（重）",
        summary="新产品能力、跨模块、改状态/契约时走完整门禁与角色链。",
        includes=(
            "产品 PRD + 原型 + spec",
            "交互视觉 G2（可 skip）",
            "技术方案 G2T",
            "多任务可并行（写集不交）",
            "Review / 测试 / 部署",
        ),
    ),
    PathOption(
        id="light",
        label="轻量模式（小需求）",
        summary="单模块、已有验收的缺陷或小行为修正；跳过重规划，阶段仍按角色推进。",
        includes=(
            "规格仍用 spec.yaml（可链已有验收）",
            "可跳过 ux 文件",
            "技术方案仍要覆盖验收",
            "只能一个任务",
            "Review / 测试仍要过",
        ),
    ),
    PathOption(
        id="light-auto",
        label="轻量自动（无 UI）",
        summary="无 UX/UI 的小需求：G1 seal 后人闸，之后 goal 式连跑至 G4；部署仍打断。",
        includes=(
            "须 uiRequired=false",
            "与 light 相同：单 affected + 单任务 + 可跳 UX",
            "G1 seal 后自动：tech → 单任务 → 开发 → Review → 测试",
            "blocking 自动打回开发；dispute / 测试卡死 / 部署仍打断",
        ),
    ),
)

PATH_BY_ID = {item.id: item for item in PATHS}


@dataclass(frozen=True)
class PathRecommendation:
    path: str
    confidence: str
    reasons: tuple[str, ...]
    matched_light: tuple[str, ...]
    matched_full: tuple[str, ...]
    matched_auto: tuple[str, ...] = ()


def is_light_path(path: str | None) -> bool:
    return path in LIGHT_FAMILY


def resolve_path(token: str) -> PathOption | None:
    text = token.strip().lower()
    aliases = {
        "full": "full",
        "heavy": "full",
        "重": "full",
        "全量": "full",
        "全量模式": "full",
        "全量模式（重）": "full",
        "light": "light",
        "lite": "light",
        "轻": "light",
        "轻量": "light",
        "轻量模式": "light",
        "轻量模式（小需求）": "light",
        "小需求": "light",
        "light-auto": "light-auto",
        "light_auto": "light-auto",
        "lightauto": "light-auto",
        "auto": "light-auto",
        "goal": "light-auto",
        "轻量自动": "light-auto",
        "轻量自动（无 ui）": "light-auto",
        "轻量自动（无 UI）": "light-auto",
        "无ui轻量": "light-auto",
        "1": "full",
        "2": "light",
        "3": "light-auto",
    }
    raw = token.strip()
    if raw in PATH_BY_ID:
        return PATH_BY_ID[raw]
    mapped = aliases.get(raw) or aliases.get(text)
    return PATH_BY_ID.get(mapped) if mapped else None


def _match_hints(text: str, lowered: str, hints: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(hint for hint in hints if hint.lower() in lowered or hint in text)


def recommend_path(need: str) -> PathRecommendation:
    text = need.strip()
    if not text:
        return PathRecommendation(
            path="full",
            confidence="low",
            reasons=("未提供需求描述，默认建议全量，避免漏掉规格与方案。",),
            matched_light=(),
            matched_full=(),
            matched_auto=(),
        )
    lowered = text.lower()
    matched_light = _match_hints(text, lowered, LIGHT_HINTS)
    matched_full = _match_hints(text, lowered, FULL_HINTS)
    matched_auto = _match_hints(text, lowered, AUTO_HINTS)
    light_score = len(matched_light)
    full_score = len(matched_full) + (1 if light_score == 0 else 0)
    auto_score = len(matched_auto)

    if light_score > full_score:
        if auto_score > 0:
            return PathRecommendation(
                path="light-auto",
                confidence="high" if light_score >= 2 and auto_score >= 1 else "medium",
                reasons=(
                    "命中轻量信号：" + "、".join(matched_light),
                    "命中无 UI / 自动连跑信号：" + "、".join(matched_auto),
                    "建议 light-auto：G1 seal 后连跑至测试；有界面或需逐步确认请改选 light/full。",
                ),
                matched_light=matched_light,
                matched_full=matched_full,
                matched_auto=matched_auto,
            )
        return PathRecommendation(
            path="light",
            confidence="high" if light_score >= 2 else "medium",
            reasons=(
                "命中轻量信号：" + "、".join(matched_light),
                "适合单点修复；若无 UI 且希望 seal 后全自动，可选 light-auto。",
            ),
            matched_light=matched_light,
            matched_full=matched_full,
            matched_auto=matched_auto,
        )
    if full_score > light_score:
        reasons = []
        if matched_full:
            reasons.append("命中全量信号：" + "、".join(matched_full))
        else:
            reasons.append("未命中明确小改信号，倾向完整规格与方案。")
        reasons.append("新能力、跨模块或契约变更请走全量。")
        return PathRecommendation(
            path="full",
            confidence="high" if matched_full else "medium",
            reasons=tuple(reasons),
            matched_light=matched_light,
            matched_full=matched_full,
            matched_auto=matched_auto,
        )
    return PathRecommendation(
        path="full",
        confidence="low",
        reasons=(
            "轻量与全量信号接近或冲突，默认建议全量更稳妥。",
            "若确认单模块无 UI，可选手动 light 或 light-auto。",
        ),
        matched_light=matched_light,
        matched_full=matched_full,
        matched_auto=matched_auto,
    )


def menu_text(recommendation: PathRecommendation | None = None) -> str:
    lines = [
        "请选择研发路径（回复编号或名称）：",
        "",
        "1. 全量模式（重）→ full",
        "   新产品能力 / 跨模块 / 改状态或对外契约",
        "2. 轻量模式（小需求）→ light",
        "   单模块缺陷或已有验收的小行为修正（阶段仍逐步推进）",
        "3. 轻量自动（无 UI）→ light-auto",
        "   无 UX/UI；G1 seal 后 goal 连跑至 G4，部署仍打断",
        "",
    ]
    if recommendation is not None:
        option = PATH_BY_ID[recommendation.path]
        lines.append(
            f"系统推荐：{option.label}（{recommendation.path}），置信度 {recommendation.confidence}"
        )
        for reason in recommendation.reasons:
            lines.append(f"- {reason}")
        lines.append("")
    lines.append(
        "确认后写入 state.path。可随时改选；light / light-auto 须仍满足「affected 一项 + 单任务」。"
    )
    return "\n".join(lines)
