"""
/*********************************************************************************
 ** Copyright (C), 2019-2029, OPLUS Mobile Comm Corp., Ltd
 ** All rights reserved.
 **
 ** File: - progress.py
 ** Description: 门禁通过后写入 gates.accepted 并推进 state.stage。
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

import json
from pathlib import Path

from aiassitrequreimentdev.gates import GATES, evaluate, seal_spec
from aiassitrequreimentdev.paths import is_light_path

# 门禁通过后建议进入的下一 stage（与 USAGE_STAGES / 架构文档对齐）
GATE_NEXT_STAGE: dict[str, str] = {
    "G0": "clarify",
    "G1": "ux",
    "G2": "tech",
    "G2T": "plan",
    "G3": "implement",
    "GR": "verify",
    "G4": "qa-ready",
    "GQA": "release",
    "GD": "done",
}

# 回退到该门禁时，stage 应回到「正在做这道门」的阶段
GATE_WORK_STAGE: dict[str, str] = {
    "G0": "intake",
    "G1": "clarify",
    "G2": "ux",
    "G2T": "tech",
    "G3": "plan",
    "GR": "review",
    "G4": "verify",
    "GQA": "qa",
    "GD": "release",
}

# light 族无 UX 文件时，G1 后可直接进 tech
LIGHT_G1_NEXT = "tech"


def next_stage_for_gate(gate: str, *, path: str | None, feature_dir: Path) -> str:
    if gate == "G1" and is_light_path(path):
        ux = feature_dir / "ux.yaml"
        if not ux.is_file():
            return LIGHT_G1_NEXT
        # 有 ux 但仍可能 skip；读 skip 标志
        try:
            import yaml

            doc = yaml.safe_load(ux.read_text(encoding="utf-8")) or {}
            if isinstance(doc, dict) and doc.get("skip") is True:
                return LIGHT_G1_NEXT
        except Exception:  # noqa: BLE001
            pass
        # uiRequired=false 时 G2 短路，也可进 tech
        try:
            import yaml

            spec = yaml.safe_load((feature_dir / "spec.yaml").read_text(encoding="utf-8")) or {}
            if isinstance(spec, dict) and spec.get("uiRequired") is False:
                return LIGHT_G1_NEXT
        except Exception:  # noqa: BLE001
            pass
    return GATE_NEXT_STAGE.get(gate, "clarify")


def accept_gate(
    feature_dir: Path,
    gate: str,
    *,
    advance_stage: bool = True,
) -> dict:
    """在指定门禁无违规时写入 accepted，并可选推进 stage。

    不绕过检查器：有该门禁违规则抛 ValueError。
    G1 建议仍走 seal（写 specHash）；本函数也可将 G1 标为 accepted，但不写哈希。
    """
    if gate not in GATES:
        raise ValueError(f"未知门禁: {gate}；可选 {', '.join(GATES)}")

    feature_dir = feature_dir.resolve()
    report = evaluate(feature_dir)
    blockers = [item for item in report.violations if item.gate == gate]
    if blockers:
        detail = "; ".join(f"{item.code} {item.message}" for item in blockers[:5])
        raise ValueError(f"{gate} 未通过，不能 accept：{detail}")

    # G1：必须经 seal 写 specHash，避免「accepted 无哈希」
    if gate == "G1":
        seal_spec(feature_dir)

    state_path = feature_dir / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    gates = state.setdefault("gates", {})
    if not isinstance(gates, dict):
        gates = {}
        state["gates"] = gates
    gates[gate] = "accepted"

    if advance_stage:
        path = state.get("path") if isinstance(state.get("path"), str) else None
        state["stage"] = next_stage_for_gate(gate, path=path, feature_dir=feature_dir)

    state_path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return state


def expand_gates_rollback(gates: list[str]) -> list[str]:
    """从最早回退点起，下游门禁一并 pending（含该点）。"""
    indices = [GATES.index(g) for g in gates if g in GATES]
    if not indices:
        return []
    return list(GATES[min(indices) :])


def apply_gates_rollback(
    feature_dir: Path,
    gates: list[str],
    *,
    expand_downstream: bool = True,
) -> dict:
    """将指定门禁（默认并扩展下游）标为 pending；含 G1 时清空 specHash。"""
    feature_dir = feature_dir.resolve()
    target = expand_gates_rollback(gates) if expand_downstream else [
        g for g in gates if g in GATES
    ]
    if not target:
        raise ValueError("gatesRollback 为空或门禁名非法")

    state_path = feature_dir / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    gate_map = state.setdefault("gates", {})
    if not isinstance(gate_map, dict):
        gate_map = {}
        state["gates"] = gate_map
    for gate in target:
        gate_map[gate] = "pending"
    if "G1" in target:
        state["specHash"] = None
    earliest = target[0]
    state["stage"] = GATE_WORK_STAGE.get(earliest, "clarify")
    state_path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return {"rolledBack": target, "stage": state["stage"], "gates": gate_map}
