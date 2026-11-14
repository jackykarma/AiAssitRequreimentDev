"""
/*********************************************************************************
 ** Copyright (C), 2019-2029, OPLUS Mobile Comm Corp., Ltd
 ** All rights reserved.
 **
 ** File: - usage.py
 ** Description: 各角色阶段 token 用量统计。写入 features/<id>/usage.yaml，看板汇总。
 ** Version: 1.0
 ** Date: 2026/11/14
 ** Author: limao2@Apps.Gallery
 **
 ** ------------------------------- Revision History: ----------------------------
 ** <author> <date> <version> <desc>
 ** ------------------------------------------------------------------------------
 ** limao2@Apps.Gallery 2026/11/14 1.0 INIT
 *********************************************************************************/
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from aiassitrequreimentdev.roles import ROLE_BY_ID, ROLES

USAGE_FILE = "usage.yaml"

# 流水线阶段（与 state.stage 对齐）；角色可为 ROLES 或扩展 id
USAGE_STAGES = (
    "intake",
    "clarify",
    "ux",
    "tech",
    "plan",
    "implement",
    "review",
    "verify",
    "release",
    "done",
)

EXTENDED_ROLES = {
    "lead": "主控",
    "ux": "交互视觉",
    "reviewer": "Code Review",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def usage_path(change_dir: Path) -> Path:
    return change_dir / USAGE_FILE


def empty_usage() -> dict[str, Any]:
    return {"version": 1, "entries": []}


def load_usage(change_dir: Path) -> dict[str, Any]:
    path = usage_path(change_dir)
    if not path.is_file():
        return empty_usage()
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return empty_usage()
    entries = raw.get("entries")
    if not isinstance(entries, list):
        raw["entries"] = []
    raw.setdefault("version", 1)
    return raw


def save_usage(change_dir: Path, doc: dict[str, Any]) -> Path:
    path = usage_path(change_dir)
    path.write_text(
        yaml.safe_dump(doc, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return path


def resolve_usage_role(token: str) -> tuple[str, str] | None:
    """返回 (role_id, label)。"""
    text = token.strip()
    if not text:
        return None
    if text in ROLE_BY_ID:
        role = ROLE_BY_ID[text]
        return role.id, role.label
    if text in EXTENDED_ROLES:
        return text, EXTENDED_ROLES[text]
    for role in ROLES:
        if text == role.label:
            return role.id, role.label
    lowered = text.lower()
    aliases = {
        "pm": "product",
        "产品": "product",
        "产品经理": "product",
        "se": "architect",
        "架构": "architect",
        "架构师": "architect",
        "架构师se": "architect",
        "dev": "developer",
        "开发": "developer",
        "qa": "tester",
        "测试": "tester",
        "ops": "deployer",
        "部署": "deployer",
        "主控": "lead",
        "交互": "ux",
        "视觉": "ux",
        "review": "reviewer",
        "评审": "reviewer",
    }
    mapped = aliases.get(text) or aliases.get(lowered)
    if mapped and mapped in ROLE_BY_ID:
        role = ROLE_BY_ID[mapped]
        return role.id, role.label
    if mapped and mapped in EXTENDED_ROLES:
        return mapped, EXTENDED_ROLES[mapped]
    return None


def default_stage_for_role(role_id: str) -> str:
    if role_id in ROLE_BY_ID:
        return ROLE_BY_ID[role_id].stage_hint
    defaults = {"lead": "plan", "ux": "ux", "reviewer": "review"}
    return defaults.get(role_id, "clarify")


def record_usage(
    change_dir: Path,
    *,
    role: str,
    stage: str | None = None,
    input_tokens: int = 0,
    output_tokens: int = 0,
    total_tokens: int | None = None,
    model: str = "",
    gate: str = "",
    note: str = "",
) -> dict[str, Any]:
    resolved = resolve_usage_role(role)
    if resolved is None:
        raise ValueError(f"未知角色: {role}")
    role_id, role_label = resolved
    stage_id = (stage or default_stage_for_role(role_id)).strip()
    if stage_id not in USAGE_STAGES:
        raise ValueError(f"未知阶段: {stage_id}；可选 {', '.join(USAGE_STAGES)}")
    if input_tokens < 0 or output_tokens < 0:
        raise ValueError("token 数不能为负")
    total = total_tokens if total_tokens is not None else input_tokens + output_tokens
    if total < 0:
        raise ValueError("totalTokens 不能为负")
    if total_tokens is None and input_tokens == 0 and output_tokens == 0:
        raise ValueError("请至少提供 --input / --output，或 --total")

    doc = load_usage(change_dir)
    entry = {
        "role": role_id,
        "roleLabel": role_label,
        "stage": stage_id,
        "gate": gate or (ROLE_BY_ID[role_id].gate_hint if role_id in ROLE_BY_ID else ""),
        "inputTokens": int(input_tokens),
        "outputTokens": int(output_tokens),
        "totalTokens": int(total),
        "model": model or "",
        "note": note or "",
        "recordedAt": _utc_now(),
    }
    entries = doc.setdefault("entries", [])
    if not isinstance(entries, list):
        entries = []
        doc["entries"] = entries
    entries.append(entry)
    save_usage(change_dir, doc)
    return entry


def summarize_usage(doc: dict[str, Any]) -> dict[str, Any]:
    by_role: dict[str, dict[str, int | str]] = {}
    by_stage: dict[str, dict[str, int]] = {}
    grand = {"inputTokens": 0, "outputTokens": 0, "totalTokens": 0, "entries": 0}
    entries = doc.get("entries")
    if not isinstance(entries, list):
        return {"byRole": by_role, "byStage": by_stage, "grandTotal": grand}

    for item in entries:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        stage = item.get("stage")
        if not isinstance(role, str) or not isinstance(stage, str):
            continue
        inp = int(item.get("inputTokens") or 0)
        out = int(item.get("outputTokens") or 0)
        total = int(item.get("totalTokens") or (inp + out))
        label = item.get("roleLabel") if isinstance(item.get("roleLabel"), str) else role

        bucket = by_role.setdefault(
            role,
            {
                "roleLabel": label,
                "inputTokens": 0,
                "outputTokens": 0,
                "totalTokens": 0,
                "entries": 0,
            },
        )
        bucket["inputTokens"] = int(bucket["inputTokens"]) + inp
        bucket["outputTokens"] = int(bucket["outputTokens"]) + out
        bucket["totalTokens"] = int(bucket["totalTokens"]) + total
        bucket["entries"] = int(bucket["entries"]) + 1

        stage_bucket = by_stage.setdefault(
            stage, {"inputTokens": 0, "outputTokens": 0, "totalTokens": 0, "entries": 0}
        )
        stage_bucket["inputTokens"] += inp
        stage_bucket["outputTokens"] += out
        stage_bucket["totalTokens"] += total
        stage_bucket["entries"] += 1

        grand["inputTokens"] += inp
        grand["outputTokens"] += out
        grand["totalTokens"] += total
        grand["entries"] += 1

    return {"byRole": by_role, "byStage": by_stage, "grandTotal": grand}


def format_usage_report(change_dir: Path) -> str:
    doc = load_usage(change_dir)
    summary = summarize_usage(doc)
    lines = [
        "# Token 用量",
        "",
        f"文件：`{USAGE_FILE}`",
        "",
        "## 按角色",
        "",
        "| 角色 | 记录次数 | input | output | total |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    by_role = summary["byRole"]
    if not by_role:
        lines.append("| （尚无） | 0 | 0 | 0 | 0 |")
    else:
        for role_id, bucket in sorted(by_role.items()):
            label = bucket.get("roleLabel", role_id)
            lines.append(
                f"| {label}（`{role_id}`） | {bucket['entries']} | "
                f"{bucket['inputTokens']} | {bucket['outputTokens']} | {bucket['totalTokens']} |"
            )

    lines.extend(
        [
            "",
            "## 按阶段",
            "",
            "| 阶段 | 记录次数 | input | output | total |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    by_stage = summary["byStage"]
    if not by_stage:
        lines.append("| （尚无） | 0 | 0 | 0 | 0 |")
    else:
        for stage in USAGE_STAGES:
            if stage not in by_stage:
                continue
            bucket = by_stage[stage]
            lines.append(
                f"| `{stage}` | {bucket['entries']} | "
                f"{bucket['inputTokens']} | {bucket['outputTokens']} | {bucket['totalTokens']} |"
            )

    grand = summary["grandTotal"]
    lines.extend(
        [
            "",
            f"**合计**：{grand['entries']} 条 · "
            f"input `{grand['inputTokens']}` · "
            f"output `{grand['outputTokens']}` · "
            f"total `{grand['totalTokens']}`",
            "",
        ]
    )
    return "\n".join(lines)


def board_usage_section(change_dir: Path) -> list[str]:
    doc = load_usage(change_dir)
    summary = summarize_usage(doc)
    grand = summary["grandTotal"]
    lines = [
        "## Token 用量（按角色 / 阶段）",
        "",
    ]
    if grand["entries"] == 0:
        lines.extend(
            [
                "尚无记录。角色结束本阶段时由主控代跑：",
                "",
                "```bash",
                "python -m aiassitrequreimentdev usage <feature目录> record --role <角色> "
                "--stage <阶段> --input <N> --output <N>",
                "```",
                "",
            ]
        )
        return lines

    lines.extend(
        [
            "| 角色 | 次数 | total tokens |",
            "| --- | ---: | ---: |",
        ]
    )
    for role_id, bucket in sorted(summary["byRole"].items()):
        label = bucket.get("roleLabel", role_id)
        lines.append(f"| {label} | {bucket['entries']} | {bucket['totalTokens']} |")
    lines.extend(
        [
            "",
            "| 阶段 | 次数 | total tokens |",
            "| --- | ---: | ---: |",
        ]
    )
    for stage in USAGE_STAGES:
        bucket = summary["byStage"].get(stage)
        if not bucket:
            continue
        lines.append(f"| `{stage}` | {bucket['entries']} | {bucket['totalTokens']} |")
    lines.extend(
        [
            "",
            f"合计 total：`{grand['totalTokens']}`（input `{grand['inputTokens']}` / "
            f"output `{grand['outputTokens']}`，{grand['entries']} 条）。详情见 `{USAGE_FILE}`。",
            "",
        ]
    )
    return lines
