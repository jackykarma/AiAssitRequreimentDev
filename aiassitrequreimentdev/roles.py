"""
/*********************************************************************************
 ** Copyright (C), 2019-2029, OPLUS Mobile Comm Corp., Ltd
 ** All rights reserved.
 **
 ** File: - roles.py
 ** Description: 启动角色目录：人选择身份后映射到技能与可写/共享工件。
 ** Version: 1.0
 ** Date: 2026/11/08
 ** Author: limao2@Apps.Gallery
 **
 ** ------------------------------- Revision History: ----------------------------
 ** <author> <date> <version> <desc>
 ** ------------------------------------------------------------------------------
 ** limao2@Apps.Gallery 2026/11/08 1.0 INIT
 *********************************************************************************/
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Role:
    id: str
    label: str
    skill: str
    writes: tuple[str, ...]
    reads: tuple[str, ...]
    stage_hint: str
    gate_hint: str
    note: str


ROLES: tuple[Role, ...] = (
    Role(
        id="product",
        label="产品经理",
        skill="aiassitrequreimentdev-product",
        writes=("prd.md", "prototype/", "spec.yaml"),
        reads=("BOARD.md", "modus/knowledge/"),
        stage_hint="clarify",
        gate_hint="G1",
        note="对话澄清后交付 PRD、HTML 原型与结构化 spec。",
    ),
    Role(
        id="architect",
        label="架构师SE",
        skill="aiassitrequreimentdev-tech",
        writes=("tech.md", "tech.yaml"),
        reads=("BOARD.md", "prd.md", "prototype/", "spec.yaml", "ux.yaml", "modus/knowledge/"),
        stage_hint="tech",
        gate_hint="G2T",
        note="读产品合同后写技术方案。若需交互精修，主控可加派 aiassitrequreimentdev-ux 写 ux.yaml。",
    ),
    Role(
        id="developer",
        label="开发",
        skill="aiassitrequreimentdev-dev",
        writes=("<任务写集内源码>",),
        reads=("BOARD.md", "spec.yaml", "tech.yaml", "tasks.yaml", "review.yaml"),
        stage_hint="implement",
        gate_hint="G3",
        note="按 tasks.yaml 任务包改写集；不改规格。",
    ),
    Role(
        id="tester",
        label="测试",
        skill="aiassitrequreimentdev-test",
        writes=("evidence.yaml",),
        reads=("BOARD.md", "spec.yaml", "tasks.yaml", "review.yaml"),
        stage_hint="verify",
        gate_hint="G4",
        note="GR 通过后按验收跑命令并写证据。",
    ),
    Role(
        id="deployer",
        label="部署",
        skill="aiassitrequreimentdev-deploy",
        writes=("deploy.yaml",),
        reads=("BOARD.md", "spec.yaml", "evidence.yaml", "tech.yaml"),
        stage_hint="release",
        gate_hint="GD",
        note="只写部署清单与回滚，不代执行上线。",
    ),
)

ROLE_BY_ID = {role.id: role for role in ROLES}
ROLE_BY_LABEL = {role.label: role for role in ROLES}


def resolve_role(token: str) -> Role | None:
    text = token.strip()
    if not text:
        return None
    if text in ROLE_BY_ID:
        return ROLE_BY_ID[text]
    if text in ROLE_BY_LABEL:
        return ROLE_BY_LABEL[text]
    lowered = text.lower()
    aliases = {
        "pm": "product",
        "产品": "product",
        "se": "architect",
        "架构": "architect",
        "架构师": "architect",
        "dev": "developer",
        "开发者": "developer",
        "qa": "tester",
        "测试同学": "tester",
        "ops": "deployer",
        "发布": "deployer",
    }
    if lowered in ROLE_BY_ID:
        return ROLE_BY_ID[lowered]
    mapped = aliases.get(text) or aliases.get(lowered)
    return ROLE_BY_ID.get(mapped) if mapped else None


def menu_text() -> str:
    lines = [
        "请选择你的角色（回复编号或名称）：",
        "",
    ]
    for index, role in enumerate(ROLES, start=1):
        lines.append(f"{index}. {role.label}（{role.id}）→ {role.skill}")
        lines.append(f"   写出：{', '.join(role.writes)}")
        lines.append(f"   共仓必读：{', '.join(role.reads)}")
    lines.append("")
    lines.append("产物一律落在同一个 features/<id>/，各角色只写自己的文件，其余只读共享。")
    return "\n".join(lines)


def resolve_menu_choice(token: str) -> Role | None:
    text = token.strip()
    if text.isdigit():
        index = int(text)
        if 1 <= index <= len(ROLES):
            return ROLES[index - 1]
    return resolve_role(text)
