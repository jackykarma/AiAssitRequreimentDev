"""
/*********************************************************************************
 ** Copyright (C), 2019-2029, OPLUS Mobile Comm Corp., Ltd
 ** All rights reserved.
 **
 ** File: - tasks_scaffold.py
 ** Description: 按 spec.acceptance 生成 tasks.yaml 骨架（G2T 后主控用）。
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
from typing import Any

import yaml

from aiassitrequreimentdev.paths import is_light_path

SCOPE_PLACEHOLDER = "TODO_SET_WRITE_SCOPE/"
MODES = ("auto", "single", "per-acceptance")


def _load_spec(feature_dir: Path) -> dict:
    path = feature_dir / "spec.yaml"
    if not path.is_file():
        raise FileNotFoundError(f"缺少 spec.yaml: {path}")
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(doc, dict):
        raise ValueError("spec.yaml 必须是映射")
    return doc


def _load_path(feature_dir: Path) -> str | None:
    state_path = feature_dir / "state.json"
    if not state_path.is_file():
        return None
    state = json.loads(state_path.read_text(encoding="utf-8"))
    path = state.get("path")
    return path if isinstance(path, str) else None


def _acceptance_items(spec: dict) -> list[dict]:
    raw = spec.get("acceptance")
    if not isinstance(raw, list) or not raw:
        raise ValueError("spec.acceptance 至少一条，才能生成任务骨架")
    items: list[dict] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        aid = item.get("id")
        if not isinstance(aid, str) or not aid.strip():
            continue
        items.append(item)
    if not items:
        raise ValueError("spec.acceptance 无有效 id")
    return items


def _verify_list(item: dict) -> list[str]:
    verify = item.get("verify")
    if isinstance(verify, str) and verify.strip():
        return [verify.strip()]
    if isinstance(verify, list):
        return [str(v).strip() for v in verify if str(v).strip()]
    return ["TODO_SET_VERIFY"]


def build_tasks_skeleton(
    feature_dir: Path,
    *,
    mode: str = "auto",
) -> dict[str, Any]:
    if mode not in MODES:
        raise ValueError(f"mode 须为 {', '.join(MODES)}")
    spec = _load_spec(feature_dir)
    path = _load_path(feature_dir)
    items = _acceptance_items(spec)

    if mode == "auto":
        use_single = is_light_path(path) or len(items) == 1
    else:
        use_single = mode == "single"

    if use_single:
        all_ids = [str(item["id"]) for item in items]
        verifies: list[str] = []
        for item in items:
            for cmd in _verify_list(item):
                if cmd not in verifies:
                    verifies.append(cmd)
        tasks = [
            {
                "id": "T1",
                "title": "实现本切片验收",
                "blockedBy": [],
                "writeScopes": [SCOPE_PLACEHOLDER],
                "acceptance": all_ids,
                "verify": verifies,
                "note": "请将 writeScopes 改为真实写集；verify 须与 A* 同源可跑命令",
            }
        ]
    else:
        tasks = []
        for index, item in enumerate(items, start=1):
            aid = str(item["id"])
            tasks.append(
                {
                    "id": f"T{index}",
                    "title": f"覆盖 {aid}",
                    "blockedBy": [f"T{index - 1}"] if index > 1 else [],
                    "writeScopes": [f"{SCOPE_PLACEHOLDER}{aid}/"],
                    "acceptance": [aid],
                    "verify": _verify_list(item),
                    "note": "请将 writeScopes 改为真实写集（任务间写集不得相交）",
                }
            )

    return {
        "tasks": tasks,
        "_meta": {
            "generatedBy": "aiassitrequreimentdev tasks scaffold",
            "mode": "single" if use_single else "per-acceptance",
            "path": path,
            "acceptanceCount": len(items),
        },
    }


def scaffold_tasks(
    feature_dir: Path,
    *,
    mode: str = "auto",
    force: bool = False,
) -> Path:
    """写入 tasks.yaml；已有非空任务且未 force 则拒绝覆盖。"""
    feature_dir = feature_dir.resolve()
    out = feature_dir / "tasks.yaml"
    if out.is_file() and not force:
        existing = yaml.safe_load(out.read_text(encoding="utf-8")) or {}
        tasks = existing.get("tasks") if isinstance(existing, dict) else None
        if isinstance(tasks, list) and tasks:
            raise FileExistsError(
                f"tasks.yaml 已有 {len(tasks)} 个任务；覆盖请加 --force"
            )

    doc = build_tasks_skeleton(feature_dir, mode=mode)
    # 落盘去掉仅供 CLI 打印的 _meta？保留有助于追溯；G3 只读 tasks 键，忽略 _meta
    out.write_text(
        yaml.safe_dump(doc, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return out
