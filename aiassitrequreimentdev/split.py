"""
/*********************************************************************************
 ** Copyright (C), 2019-2029, OPLUS Mobile Comm Corp., Ltd
 ** All rights reserved.
 **
 ** File: - split.py
 ** Description: requirements/.../split.yaml 结构校验（拆 feature 决策）。
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

from pathlib import Path

import yaml

from aiassitrequreimentdev.gates import REQUIREMENT_ID_RE, Violation, validate_requirement_id
from aiassitrequreimentdev.paths import resolve_path

PLACEHOLDER_RATIONALE = ("待产品", "待填写", "TODO", "TBD")


def load_split(path: Path) -> dict | None:
    if not path.is_file():
        return None
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return raw if isinstance(raw, dict) else None


def validate_split_doc(
    doc: dict,
    *,
    expected_requirement_id: str | None = None,
) -> list[str]:
    """返回人类可读错误列表；空列表表示通过。"""
    errors: list[str] = []
    req_id = doc.get("requirementId")
    if not isinstance(req_id, str) or not req_id.strip():
        errors.append("requirementId 不能为空")
    else:
        try:
            validate_requirement_id(req_id.strip())
        except ValueError as exc:
            errors.append(str(exc))
        if expected_requirement_id and req_id.strip() != expected_requirement_id:
            errors.append(
                f"requirementId 与目录不一致：文档={req_id.strip()} 目录={expected_requirement_id}"
            )

    decision = doc.get("decision")
    if decision not in ("single", "multi"):
        errors.append("decision 必须是 single 或 multi")

    rationale = doc.get("rationale")
    if not isinstance(rationale, str) or not rationale.strip():
        errors.append("rationale 不能为空")
    elif any(token in rationale for token in PLACEHOLDER_RATIONALE):
        errors.append("rationale 仍是占位文案，须写明拆分理由")

    confirmed = doc.get("confirmedByHuman")
    if not isinstance(confirmed, bool):
        errors.append("confirmedByHuman 必须是布尔")
    elif decision == "multi" and confirmed is not True:
        errors.append("decision=multi 时须 confirmedByHuman=true（主控打断人确认后）")

    features = doc.get("features")
    if not isinstance(features, list) or not features:
        errors.append("features 至少一条")
        return errors

    if decision == "single" and len(features) != 1:
        errors.append("decision=single 时 features 必须恰好 1 条")
    if decision == "multi" and len(features) < 2:
        errors.append("decision=multi 时 features 至少 2 条")

    seen_ids: set[str] = set()
    feature_ids: list[str] = []
    for index, item in enumerate(features):
        prefix = f"features[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} 必须是映射")
            continue
        fid = item.get("id")
        if not isinstance(fid, str) or not fid.strip():
            errors.append(f"{prefix}.id 不能为空")
        else:
            fid = fid.strip()
            if fid in seen_ids:
                errors.append(f"feature id 重复: {fid}")
            seen_ids.add(fid)
            feature_ids.append(fid)
            if fid.startswith("FEAT-000") or fid == "FEAT-000":
                errors.append(f"{prefix}.id 仍是模板占位 FEAT-000")

        title = item.get("title")
        if not isinstance(title, str) or not title.strip() or title.strip() == "待填写":
            errors.append(f"{prefix}.title 须填写真实标题")

        scope = item.get("scope")
        if not isinstance(scope, str) or not scope.strip():
            errors.append(f"{prefix}.scope 不能为空")
        elif "待填写" in scope or scope.strip().startswith("本 feature 覆盖"):
            # 模板默认句视为未填
            if scope.strip() in (
                "本 feature 覆盖的能力与验收边界",
                "待填写",
            ):
                errors.append(f"{prefix}.scope 仍是模板占位")

        path = item.get("path")
        if not isinstance(path, str) or resolve_path(path) is None:
            errors.append(f"{prefix}.path 必须是 full / light / light-auto")

        depends = item.get("dependsOn")
        if depends is None:
            depends = []
        if not isinstance(depends, list):
            errors.append(f"{prefix}.dependsOn 必须是列表")
        else:
            for dep in depends:
                if not isinstance(dep, str) or not dep.strip():
                    errors.append(f"{prefix}.dependsOn 含非法项")
                elif dep.strip() == fid:
                    errors.append(f"{prefix}.dependsOn 不能依赖自身")

    # 依赖须指向本 split 内其它 feature
    id_set = set(feature_ids)
    for index, item in enumerate(features):
        if not isinstance(item, dict):
            continue
        depends = item.get("dependsOn") or []
        if not isinstance(depends, list):
            continue
        for dep in depends:
            if isinstance(dep, str) and dep.strip() and dep.strip() not in id_set:
                errors.append(
                    f"features[{index}].dependsOn 引用了不存在的 feature: {dep.strip()}"
                )

    return errors


def evaluate_requirement(req_dir: Path) -> list[Violation]:
    """校验需求目录：split.yaml（及 requirementId 与目录名一致）。"""
    violations: list[Violation] = []
    req_dir = req_dir.resolve()
    if not req_dir.is_dir():
        violations.append(Violation("G0", "REQ_MISSING", f"需求目录不存在: {req_dir}"))
        return violations

    dir_name = req_dir.name
    if not REQUIREMENT_ID_RE.match(dir_name):
        violations.append(
            Violation(
                "G0",
                "REQ_ID",
                f"需求目录名须为 REQ-序号-名称-YYYYMMDD，当前: {dir_name}",
            )
        )

    split_path = req_dir / "split.yaml"
    if not split_path.is_file():
        violations.append(Violation("G0", "SPLIT_MISSING", "缺少 split.yaml"))
        return violations

    try:
        doc = yaml.safe_load(split_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        violations.append(Violation("G0", "SPLIT_PARSE", f"split.yaml 无法解析: {exc}"))
        return violations
    if not isinstance(doc, dict):
        violations.append(Violation("G0", "SPLIT_PARSE", "split.yaml 必须是映射"))
        return violations

    expected = dir_name if REQUIREMENT_ID_RE.match(dir_name) else None
    for message in validate_split_doc(doc, expected_requirement_id=expected):
        violations.append(Violation("G0", "SPLIT_SHAPE", message))
    return violations


def feature_listed_in_split(split_doc: dict, feature_id: str) -> bool:
    features = split_doc.get("features")
    if not isinstance(features, list):
        return False
    for item in features:
        if isinstance(item, dict) and item.get("id") == feature_id:
            return True
    return False
