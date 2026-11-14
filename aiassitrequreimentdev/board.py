"""
/*********************************************************************************
 ** Copyright (C), 2019-2029, OPLUS Mobile Comm Corp., Ltd
 ** All rights reserved.
 **
 ** File: - board.py
 ** Description: 共仓看板。汇总 features/<id>/ 下各角色产物，供切换角色时共享。
 ** Version: 1.1
 ** Date: 2026/11/08
 ** Author: limao2@Apps.Gallery
 **
 ** ------------------------------- Revision History: ----------------------------
 ** <author> <date> <version> <desc>
 ** ------------------------------------------------------------------------------
 ** limao2@Apps.Gallery 2026/11/08 1.0 INIT
 ** limao2@Apps.Gallery 2026/11/08 1.1 path confirm
 ** limao2@Apps.Gallery 2026/11/14 1.2 token usage section
 *********************************************************************************/
"""

from __future__ import annotations

import json
from pathlib import Path

from aiassitrequreimentdev.paths import PATH_BY_ID, resolve_path
from aiassitrequreimentdev.roles import ROLE_BY_ID, ROLES, resolve_menu_choice
from aiassitrequreimentdev.usage import board_usage_section


ARTIFACTS = (
    ("prd.md", "产品 PRD（给人）"),
    ("prototype/index.html", "产品可交互 HTML 原型（给人）"),
    ("spec.yaml", "结构化规格（给 Agent/门禁）"),
    ("ux.yaml", "交互视觉合同"),
    ("prototype/ux/index.html", "UX 可交互 HTML 原型（给人）"),
    ("tech.md", "技术方案文档（给人）"),
    ("tech.yaml", "技术方案合同（给门禁）"),
    ("tasks.yaml", "任务图"),
    ("review.yaml", "代码评审"),
    ("evidence.yaml", "测试证据"),
    ("deploy.yaml", "部署清单"),
    ("usage.yaml", "角色阶段 token 用量"),
)


def adopt_role(change_dir: Path, token: str) -> dict:
    role = resolve_menu_choice(token)
    if role is None:
        raise ValueError(f"未知角色: {token}")
    state_path = change_dir / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["actorRole"] = role.id
    state["actorLabel"] = role.label
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    refresh_board(change_dir)
    return state


def set_path(change_dir: Path, token: str, *, recommended: str | None = None) -> dict:
    option = resolve_path(token)
    if option is None:
        raise ValueError(f"未知路径: {token}")
    state_path = change_dir / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["path"] = option.id
    state["pathConfirmed"] = True
    if recommended:
        state["pathRecommended"] = recommended
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    refresh_board(change_dir)
    return state


def refresh_board(change_dir: Path) -> Path:
    state_path = change_dir / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.is_file() else {}
    actor = state.get("actorRole")
    role = ROLE_BY_ID.get(actor) if isinstance(actor, str) else None
    path_id = state.get("path")
    path = PATH_BY_ID.get(path_id) if isinstance(path_id, str) else None
    lines = [
        "# Feature 共仓看板",
        "",
        f"目录：`{change_dir.as_posix()}`",
        "",
        "各角色只写自己的工件，其余文件只读共享。一条需求可对应多个 feature。切换角色前先刷新本看板。",
        "",
    ]
    if path:
        confirmed = "已确认" if state.get("pathConfirmed") else "未确认（模板默认）"
        recommended = state.get("pathRecommended")
        lines.extend(
            [
                "## 研发路径",
                "",
                f"- 当前：{path.label}（`{path.id}`）· {confirmed}",
                f"- 说明：{path.summary}",
            ]
        )
        if recommended:
            lines.append(f"- 系统曾推荐：`{recommended}`")
        lines.append("")
    if role:
        lines.extend(
            [
                "## 当前角色",
                "",
                f"- 身份：{role.label}（`{role.id}`）",
                f"- 技能：`{role.skill}`",
                f"- 建议阶段：`{role.stage_hint}` / 门禁 `{role.gate_hint}`",
                f"- 本角色可写：{', '.join(f'`{item}`' for item in role.writes)}",
                f"- 本角色必读：{', '.join(f'`{item}`' for item in role.reads)}",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "## 当前角色",
                "",
                "尚未选择。启动时请先选定：产品经理 / 架构师SE / 开发 / 测试 / 部署。",
                "",
            ]
        )

    lines.extend(["## 产物状态", "", "| 文件 | 说明 | 状态 |", "| --- | --- | --- |"])
    for relative, title in ARTIFACTS:
        path = change_dir / relative
        status = "已有" if path.is_file() else "缺失"
        if relative.endswith("/") or relative.endswith("index.html"):
            status = "已有" if path.is_file() else "缺失"
        lines.append(f"| `{relative}` | {title} | {status} |")

    lines.append("")
    lines.extend(board_usage_section(change_dir))

    lines.extend(["## 角色入口", "", "| 角色 | 技能 | 写出 |", "| --- | --- | --- |"])
    for item in ROLES:
        lines.append(
            f"| {item.label} | `{item.skill}` | {', '.join(f'`{w}`' for w in item.writes)} |"
        )
    lines.append("")

    board_path = change_dir / "BOARD.md"
    board_path.write_text("\n".join(lines), encoding="utf-8")
    return board_path
