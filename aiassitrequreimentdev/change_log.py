"""
/*********************************************************************************
 ** Copyright (C), 2019-2029, OPLUS Mobile Comm Corp., Ltd
 ** All rights reserved.
 **
 ** File: - change_log.py
 ** Description: Feature change.yaml 台账：记录发起人、原因、影响、时间。
 ** Version: 1.0
 ** Date: 2026/11/15
 ** Author: limao2@Apps.Gallery
 **
 ** ------------------------------- Revision History: ----------------------------
 ** <author> <date> <version> <desc>
 ** ------------------------------------------------------------------------------
 ** limao2@Apps.Gallery 2026/11/15 1.0 INIT
 ** limao2@Apps.Gallery 2026/11/15 1.1 需求级 change.yaml + C4 回退多 feature
 *********************************************************************************/
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import yaml

CHANGE_LEVELS = ("C0", "C1", "C2", "C3", "C4")
CHANGE_CATEGORIES = ("product", "ux", "tech", "tasks", "split", "other")
CHANGE_STATUSES = ("proposed", "approved", "applied")
CHANGE_ROLES = (
    "product",
    "ux",
    "architect",
    "developer",
    "tester",
    "deployer",
    "lead",
    "human",
    "reviewer",
)


def change_path(target_dir: Path) -> Path:
    return target_dir / "change.yaml"


def is_requirement_dir(target_dir: Path) -> bool:
    """需求目录：含 split.yaml，或位于 requirements/ 下。"""
    path = target_dir.resolve()
    if (path / "split.yaml").is_file():
        return True
    return path.parent.name == "requirements"


def repo_root_for(target_dir: Path) -> Path:
    path = target_dir.resolve()
    if path.parent.name in ("features", "requirements"):
        return path.parent.parent
    return path.parent


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def load_change_doc(target_dir: Path) -> dict:
    path = change_path(target_dir)
    if not path.is_file():
        if is_requirement_dir(target_dir):
            return {"requirementId": target_dir.name, "changes": []}
        return {"featureId": target_dir.name, "changes": []}
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(doc, dict):
        raise ValueError("change.yaml 必须是映射")
    if not isinstance(doc.get("changes"), list):
        doc["changes"] = []
    return doc


def save_change_doc(target_dir: Path, doc: dict) -> Path:
    path = change_path(target_dir)
    path.write_text(
        yaml.safe_dump(doc, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return path


def feature_ids_from_split(requirement_dir: Path) -> list[str]:
    split_path = requirement_dir / "split.yaml"
    if not split_path.is_file():
        return []
    doc = yaml.safe_load(split_path.read_text(encoding="utf-8")) or {}
    features = doc.get("features") if isinstance(doc, dict) else None
    if not isinstance(features, list):
        return []
    ids: list[str] = []
    for item in features:
        if isinstance(item, dict) and isinstance(item.get("id"), str) and item["id"].strip():
            ids.append(item["id"].strip())
    return ids


def resolve_rollback_feature_dirs(
    target_dir: Path,
    feature_ids: list[str],
) -> list[Path]:
    """解析应回退门禁的 feature 目录列表。"""
    target_dir = target_dir.resolve()
    root = repo_root_for(target_dir)
    if is_requirement_dir(target_dir):
        ids = list(feature_ids)
        if not ids:
            ids = feature_ids_from_split(target_dir)
        dirs: list[Path] = []
        for fid in ids:
            feat = root / "features" / fid
            if feat.is_dir():
                dirs.append(feat)
        return dirs
    # feature 目录：自身 + impacts.features 中已存在的兄弟
    dirs = [target_dir]
    for fid in feature_ids:
        feat = root / "features" / fid
        if feat.is_dir() and feat.resolve() != target_dir:
            dirs.append(feat)
    return dirs


def _next_change_id(changes: list) -> str:
    max_n = 0
    for item in changes:
        if not isinstance(item, dict):
            continue
        raw = item.get("id")
        if isinstance(raw, str) and raw.startswith("CHG-"):
            tail = raw[4:]
            if tail.isdigit():
                max_n = max(max_n, int(tail))
    return f"CHG-{max_n + 1:03d}"


def validate_change_entry(item: dict) -> list[str]:
    errors: list[str] = []
    identifier = item.get("id")
    if not isinstance(identifier, str) or not identifier.startswith("CHG-"):
        errors.append(f"id 须为 CHG-*，收到: {identifier}")
    at = item.get("at")
    if not isinstance(at, str) or not at.strip():
        errors.append(f"{identifier}: 缺少 at（ISO8601 时间）")
    initiated = item.get("initiatedBy")
    if not isinstance(initiated, dict):
        errors.append(f"{identifier}: 缺少 initiatedBy")
    else:
        role = initiated.get("role")
        if role not in CHANGE_ROLES:
            errors.append(f"{identifier}: initiatedBy.role 非法: {role}")
    reason = item.get("reason")
    if not isinstance(reason, str) or not reason.strip():
        errors.append(f"{identifier}: 缺少 reason")
    level = item.get("level")
    if level not in CHANGE_LEVELS:
        errors.append(f"{identifier}: level 须为 C0..C4")
    category = item.get("category")
    if category not in CHANGE_CATEGORIES:
        errors.append(f"{identifier}: category 非法")
    summary = item.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        errors.append(f"{identifier}: 缺少 summary")
    impacts = item.get("impacts")
    if not isinstance(impacts, dict):
        errors.append(f"{identifier}: 缺少 impacts")
    else:
        artifacts = impacts.get("artifacts")
        gates = impacts.get("gatesRollback")
        if not isinstance(artifacts, list):
            errors.append(f"{identifier}: impacts.artifacts 须为列表")
        if not isinstance(gates, list):
            errors.append(f"{identifier}: impacts.gatesRollback 须为列表")
        elif level in ("C1", "C2", "C3") and not gates:
            errors.append(f"{identifier}: {level} 须填写 impacts.gatesRollback")
        # C4：仅新增空 feature 时可无回退门禁；改/删既有切片仍应填 gatesRollback
    status = item.get("status")
    if status not in CHANGE_STATUSES:
        errors.append(f"{identifier}: status 非法")
    if level in ("C3", "C4") and status in ("approved", "applied"):
        confirmed = item.get("confirmedBy")
        if not isinstance(confirmed, dict) or not str(confirmed.get("role") or "").strip():
            errors.append(f"{identifier}: C3/C4 在 approved/applied 时须有 confirmedBy.role")
    return errors


def record_change(
    target_dir: Path,
    *,
    initiated_by: str,
    reason: str,
    level: str,
    category: str,
    summary: str,
    artifacts: list[str] | None = None,
    gates_rollback: list[str] | None = None,
    acceptance_ids: list[str] | None = None,
    features: list[str] | None = None,
    name: str = "",
    status: str = "proposed",
    confirmed_by_role: str = "",
    confirmed_by_name: str = "",
    at: str | None = None,
    apply_rollback: bool | None = None,
) -> dict:
    """写入 change.yaml。target_dir 可为 feature 或 requirement 目录。"""
    if initiated_by not in CHANGE_ROLES:
        raise ValueError(f"initiated_by 非法: {initiated_by}")
    if level not in CHANGE_LEVELS:
        raise ValueError(f"level 非法: {level}")
    if category not in CHANGE_CATEGORIES:
        raise ValueError(f"category 非法: {category}")
    if status not in CHANGE_STATUSES:
        raise ValueError(f"status 非法: {status}")

    target_dir = target_dir.resolve()
    req_scope = is_requirement_dir(target_dir)
    if req_scope and level in ("C0", "C1", "C2") and category != "split":
        raise ValueError(
            "需求目录台账用于范围/拆分（建议 level=C4、category=split）；"
            "单 feature 的 C0–C2 请记到 features/<id>/"
        )
    if level == "C4" and category not in ("split", "other", "product"):
        raise ValueError("C4 建议 category=split（或 product/other）")

    doc = load_change_doc(target_dir)
    changes = doc.setdefault("changes", [])
    if not isinstance(changes, list):
        changes = []
        doc["changes"] = changes
    if req_scope:
        doc["requirementId"] = doc.get("requirementId") or target_dir.name
        doc.pop("featureId", None)
    else:
        doc["featureId"] = doc.get("featureId") or target_dir.name

    feature_list = list(features or [])
    if req_scope and not feature_list and level == "C4":
        feature_list = feature_ids_from_split(target_dir)

    entry = {
        "id": _next_change_id(changes),
        "at": at or _now_iso(),
        "initiatedBy": {"role": initiated_by, "name": name or ""},
        "reason": reason.strip(),
        "level": level,
        "category": category,
        "summary": summary.strip(),
        "impacts": {
            "artifacts": list(artifacts or []),
            "gatesRollback": list(gates_rollback or []),
            "acceptanceIds": list(acceptance_ids or []),
            "features": feature_list,
        },
        "status": status,
    }
    if confirmed_by_role:
        entry["confirmedBy"] = {
            "role": confirmed_by_role,
            "name": confirmed_by_name or "",
            "at": _now_iso(),
        }
    errors = validate_change_entry(entry)
    if errors:
        raise ValueError("; ".join(errors))
    changes.append(entry)
    save_change_doc(target_dir, doc)

    # approved/applied 且声明了回退门禁时，默认自动把下游 gates 打回 pending
    should_rollback = apply_rollback
    if should_rollback is None:
        should_rollback = status in ("approved", "applied") and bool(
            entry["impacts"]["gatesRollback"]
        )
    if should_rollback and entry["impacts"]["gatesRollback"]:
        from aiassitrequreimentdev.progress import apply_gates_rollback

        targets = resolve_rollback_feature_dirs(
            target_dir, list(entry["impacts"]["features"])
        )
        if not targets:
            raise ValueError(
                "无法回退门禁：未找到受影响 feature 目录。"
                "请用 --features FEAT-001,FEAT-002 列出，或先 init 对应 feature。"
            )
        applied: list[dict] = []
        for feat_dir in targets:
            applied.append(
                {
                    "feature": feat_dir.name,
                    **apply_gates_rollback(
                        feat_dir, list(entry["impacts"]["gatesRollback"])
                    ),
                }
            )
        entry["_rollbackApplied"] = applied
    return entry


def format_change_report(target_dir: Path) -> str:
    doc = load_change_doc(target_dir)
    changes = doc.get("changes") or []
    scope = doc.get("requirementId") or doc.get("featureId") or target_dir.name
    kind = "需求" if doc.get("requirementId") or is_requirement_dir(target_dir) else "Feature"
    lines = [
        f"变更台账 · {kind} {scope}",
        f"共 {len(changes)} 条",
        "",
    ]
    if not changes:
        lines.append("（尚无变更记录）")
        return "\n".join(lines)
    for item in changes:
        if not isinstance(item, dict):
            continue
        who = item.get("initiatedBy") or {}
        name = who.get("name") or ""
        who_s = f"{who.get('role')}" + (f"/{name}" if name else "")
        impacts = item.get("impacts") or {}
        gates = ",".join(impacts.get("gatesRollback") or []) or "—"
        lines.append(
            f"- {item.get('id')} [{item.get('level')}/{item.get('category')}] "
            f"{item.get('status')} @ {item.get('at')}"
        )
        lines.append(f"  发起: {who_s}")
        lines.append(f"  原因: {item.get('reason')}")
        lines.append(f"  摘要: {item.get('summary')}")
        lines.append(f"  回退门禁: {gates}")
        arts = impacts.get("artifacts") or []
        if arts:
            lines.append(f"  影响文件: {', '.join(str(a) for a in arts)}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
