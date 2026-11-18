"""
/*********************************************************************************
 ** Copyright (C), 2019-2029, OPLUS Mobile Comm Corp., Ltd
 ** All rights reserved.
 **
 ** File: - stories.py
 ** Description: Feature 内可选 Story 索引校验（并行实现单元，不对 G4 负责）。
 ** Version: 1.0
 ** Date: 2026/11/18
 ** Author: limao2@Apps.Gallery
 **
 ** ------------------------------- Revision History: ----------------------------
 ** <author> <date> <version> <desc>
 ** ------------------------------------------------------------------------------
 ** limao2@Apps.Gallery 2026/11/18 1.0 INIT
 *********************************************************************************/
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from aiassitrequreimentdev.gates import Violation

STORY_ID_RE = re.compile(r"^ST-\d+-[a-z0-9]+(?:-[a-z0-9]+)*$")


def load_stories(feature_dir: Path) -> dict | None:
    path = feature_dir / "stories.yaml"
    if not path.is_file():
        return None
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return raw if isinstance(raw, dict) else None


def story_ids(doc: dict) -> set[str]:
    stories = doc.get("stories")
    if not isinstance(stories, list):
        return set()
    result: set[str] = set()
    for item in stories:
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            result.add(item["id"].strip())
    return result


def evaluate_stories(
    feature_dir: Path,
    *,
    feature_id: str | None,
    acceptance_ids: set[str],
) -> list[Violation]:
    """storiesEnabled=true 时校验；未启用或缺失文件不挡门禁。"""
    path = feature_dir / "stories.yaml"
    if not path.is_file():
        return []
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return [Violation("G2T", "STORY_PARSE", f"stories.yaml 无法解析: {exc}")]
    if not isinstance(doc, dict):
        return [Violation("G2T", "STORY_PARSE", "stories.yaml 必须是映射")]

    enabled = doc.get("storiesEnabled")
    if enabled is not True:
        return []

    violations: list[Violation] = []
    fid = doc.get("featureId")
    if feature_id and isinstance(fid, str) and fid.strip() and fid.strip() != feature_id:
        violations.append(
            Violation(
                "G2T",
                "STORY_FEATURE",
                f"stories.yaml featureId 与目录不一致：{fid.strip()}",
            )
        )

    rationale = doc.get("rationale")
    if not isinstance(rationale, str) or not rationale.strip():
        violations.append(
            Violation(
                "G2T",
                "STORY_RATIONALE",
                "启用 Story 时须填写 rationale（对应触发条件）",
            )
        )

    stories = doc.get("stories")
    if not isinstance(stories, list) or not stories:
        violations.append(
            Violation("G2T", "STORY_EMPTY", "storiesEnabled=true 时 stories 至少一条")
        )
        return violations

    seen: set[str] = set()
    id_set: set[str] = set()
    scope_hints: list[tuple[str, str]] = []
    for index, item in enumerate(stories):
        prefix = f"stories[{index}]"
        if not isinstance(item, dict):
            violations.append(Violation("G2T", "STORY_SHAPE", f"{prefix} 必须是映射"))
            continue
        sid = item.get("id")
        if not isinstance(sid, str) or not sid.strip():
            violations.append(Violation("G2T", "STORY_SHAPE", f"{prefix}.id 不能为空"))
            continue
        sid = sid.strip()
        if not STORY_ID_RE.fullmatch(sid):
            violations.append(
                Violation(
                    "G2T",
                    "STORY_ID",
                    f"{prefix}.id 须为 ST-<序号>-<kebab>，收到: {sid}",
                )
            )
        if sid in seen:
            violations.append(Violation("G2T", "STORY_ID", f"Story id 重复: {sid}"))
        seen.add(sid)
        id_set.add(sid)

        title = item.get("title")
        if not isinstance(title, str) or not title.strip():
            violations.append(Violation("G2T", "STORY_SHAPE", f"{prefix}.title 不能为空"))

        covers = item.get("coversAcceptance")
        if not isinstance(covers, list) or not covers:
            violations.append(
                Violation(
                    "G2T",
                    "STORY_ACCEPTANCE",
                    f"{prefix}.coversAcceptance 至少引用一条本 Feature A*",
                )
            )
        else:
            for acc in covers:
                if acc not in acceptance_ids:
                    violations.append(
                        Violation(
                            "G2T",
                            "STORY_ACCEPTANCE",
                            f"{prefix} 引用了不存在的验收 {acc}（禁止 Story 自造交付）",
                        )
                    )

        hints = item.get("writeScopeHint")
        if isinstance(hints, list):
            for hint in hints:
                if isinstance(hint, str) and hint.strip():
                    scope_hints.append((sid, hint.strip().replace("\\", "/").rstrip("/")))

        story_dir = feature_dir / "stories" / sid
        tech_md = story_dir / "story-tech.md"
        if not tech_md.is_file():
            violations.append(
                Violation(
                    "G2T",
                    "STORY_TECH_MISSING",
                    f"缺少 {tech_md.relative_to(feature_dir).as_posix()}（模板见 templates/story/）",
                )
            )

        # 禁止 Story 冒充交付证据
        if (story_dir / "evidence.yaml").is_file():
            violations.append(
                Violation(
                    "G2T",
                    "STORY_NO_EVIDENCE",
                    f"{sid} 不得放置 evidence.yaml（G4 只认 Feature）",
                )
            )

    for index, item in enumerate(stories):
        if not isinstance(item, dict):
            continue
        sid = item.get("id")
        deps = item.get("dependsOnStories") or []
        if not isinstance(deps, list):
            violations.append(
                Violation(
                    "G2T",
                    "STORY_SHAPE",
                    f"stories[{index}].dependsOnStories 必须是列表",
                )
            )
            continue
        for dep in deps:
            if not isinstance(dep, str) or dep.strip() not in id_set:
                violations.append(
                    Violation(
                        "G2T",
                        "STORY_DEPENDENCY",
                        f"stories[{index}] 依赖了不存在的 Story: {dep}",
                    )
                )
            elif isinstance(sid, str) and dep.strip() == sid.strip():
                violations.append(
                    Violation(
                        "G2T",
                        "STORY_DEPENDENCY",
                        f"stories[{index}] 不能依赖自身",
                    )
                )

    # 简单写集提示相交（同路径前缀）
    for i, (left_id, left_scope) in enumerate(scope_hints):
        for right_id, right_scope in scope_hints[i + 1 :]:
            if left_id == right_id:
                continue
            if left_scope == right_scope or left_scope.startswith(
                right_scope + "/"
            ) or right_scope.startswith(left_scope + "/"):
                violations.append(
                    Violation(
                        "G2T",
                        "STORY_SCOPE_OVERLAP",
                        f"{left_id} 与 {right_id} 的 writeScopeHint 相交（{left_scope} / {right_scope}）",
                    )
                )

    return violations


def validate_task_story_ids(
    feature_dir: Path,
    tasks: list,
) -> list[Violation]:
    """G3：任务若带 storyId，须指向已启用的 stories.yaml。"""
    doc = load_stories(feature_dir)
    known: set[str] = set()
    enabled = False
    if isinstance(doc, dict) and doc.get("storiesEnabled") is True:
        enabled = True
        known = story_ids(doc)

    violations: list[Violation] = []
    for task in tasks:
        if not isinstance(task, dict):
            continue
        sid = task.get("storyId")
        if sid is None or sid == "" or sid == "—":
            continue
        if not isinstance(sid, str):
            violations.append(
                Violation("G3", "TASK_STORY", f"{task.get('id')} storyId 必须是字符串")
            )
            continue
        if not enabled:
            violations.append(
                Violation(
                    "G3",
                    "TASK_STORY",
                    f"{task.get('id')} 引用了 storyId={sid}，但 storiesEnabled 未开启",
                )
            )
        elif sid.strip() not in known:
            violations.append(
                Violation(
                    "G3",
                    "TASK_STORY",
                    f"{task.get('id')} 引用了不存在的 storyId={sid.strip()}",
                )
            )
    return violations
