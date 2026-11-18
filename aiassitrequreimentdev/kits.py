"""
/*********************************************************************************
 ** Copyright (C), 2019-2029, OPLUS Mobile Comm Corp., Ltd
 ** All rights reserved.
 **
 ** File: - kits.py
 ** Description: research/ui-kits catalog — visual.baseline menu for UX G2
 ** Version: 1.1
 ** Date: 2026/11/18
 ** Author: limao2@Apps.Gallery
 **
 ** ------------------------------- Revision History: ----------------------------
 ** <author> <date> <version> <desc>
 ** ------------------------------------------------------------------------------
 ** limao2@Apps.Gallery 2026/11/18 1.0 INIT three style kits + custom
 ** limao2@Apps.Gallery 2026/11/18 1.1 projectStyle.locked skips forced 3-way choice
 *********************************************************************************/

Visual baseline catalog helpers (project-locked / ui-kit / painless / midoo / custom…).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from aiassitrequreimentdev.change_log import repo_root_for


@dataclass(frozen=True)
class KitOption:
    id: str
    label: str
    description: str
    path: str | None
    prefix: str | None
    source: str
    package: str | None = None
    showcase: str | None = None


@dataclass(frozen=True)
class ProjectStyle:
    locked: bool
    id: str
    label: str
    description: str
    path: str | None
    prefix: str | None
    theme_doc: str | None
    notes: str


FALLBACK_KITS = (
    KitOption(
        id="ui-kit",
        label="Music 默认 kit",
        description="仓内模板 Apple Music 风亮/暗双主题（uk-*）",
        path="aiassitrequreimentdev/templates/feature/prototype/shared/ui-kit",
        prefix="uk",
        source="template",
    ),
    KitOption(
        id="painless",
        label="无痛单词（painless）",
        description="护眼纸感 + 苔藓绿 + 翻译防剧透模糊（pk-*）",
        path="research/painless-ui/ui-kit",
        prefix="pk",
        source="apk-uikit",
        package="tech.xiangzi.painless",
    ),
    KitOption(
        id="midoo",
        label="Midoo AI",
        description="淡紫蓝渐变画布 + 毛玻璃底栏 + 渐变 CTA（md-*）",
        path="research/midoo-ui/ui-kit",
        prefix="md",
        source="apk-uikit",
        package="com.midoo.ai",
    ),
    KitOption(
        id="custom",
        label="自由发挥",
        description="不强制引用已有 kit；须写 visual.notes",
        path=None,
        prefix=None,
        source="freeform",
    ),
)

DEFAULT_PROJECT_STYLE = ProjectStyle(
    locked=False,
    id="project",
    label="项目自有风格",
    description="当前产品已有 UI 规范，原型与视觉须对齐",
    path=None,
    prefix=None,
    theme_doc=None,
    notes="",
)


def catalog_path(repo_root: Path | None = None) -> Path:
    root = repo_root if repo_root is not None else Path.cwd()
    return root / "research" / "ui-kits" / "catalog.yaml"


def _resolve_root(repo_root: Path | None, change_dir: Path | None) -> Path:
    if repo_root is not None:
        return repo_root
    if change_dir is not None:
        return repo_root_for(change_dir)
    return Path.cwd()


def load_catalog_doc(repo_root: Path | None = None, change_dir: Path | None = None) -> dict:
    root = _resolve_root(repo_root, change_dir)
    path = catalog_path(root)
    if not path.is_file():
        return {
            "default": "ui-kit",
            "styleKitIds": ["ui-kit", "painless", "midoo"],
            "projectStyle": {
                "locked": False,
                "id": "project",
                "label": DEFAULT_PROJECT_STYLE.label,
            },
            "kits": [
                {
                    "id": k.id,
                    "label": k.label,
                    "description": k.description,
                    "path": k.path,
                    "prefix": k.prefix,
                    "source": k.source,
                    "package": k.package,
                }
                for k in FALLBACK_KITS
            ],
        }
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return doc if isinstance(doc, dict) else {}


def load_project_style(
    repo_root: Path | None = None, change_dir: Path | None = None
) -> ProjectStyle:
    doc = load_catalog_doc(repo_root=repo_root, change_dir=change_dir)
    raw = doc.get("projectStyle")
    if not isinstance(raw, dict):
        return DEFAULT_PROJECT_STYLE
    kit_id = raw.get("id")
    if not isinstance(kit_id, str) or not kit_id.strip():
        kit_id = "project"
    return ProjectStyle(
        locked=bool(raw.get("locked")),
        id=kit_id.strip(),
        label=str(raw.get("label") or "项目自有风格"),
        description=str(raw.get("description") or DEFAULT_PROJECT_STYLE.description),
        path=raw.get("path") if isinstance(raw.get("path"), str) else None,
        prefix=raw.get("prefix") if isinstance(raw.get("prefix"), str) else None,
        theme_doc=raw.get("themeDoc") if isinstance(raw.get("themeDoc"), str) else None,
        notes=str(raw.get("notes") or ""),
    )


def project_style_locked(
    repo_root: Path | None = None, change_dir: Path | None = None
) -> bool:
    return load_project_style(repo_root=repo_root, change_dir=change_dir).locked


def default_baseline(
    repo_root: Path | None = None, change_dir: Path | None = None
) -> str:
    ps = load_project_style(repo_root=repo_root, change_dir=change_dir)
    if ps.locked:
        return ps.id
    doc = load_catalog_doc(repo_root=repo_root, change_dir=change_dir)
    raw = doc.get("default")
    return raw.strip() if isinstance(raw, str) and raw.strip() else "ui-kit"


def load_kits(repo_root: Path | None = None, change_dir: Path | None = None) -> list[KitOption]:
    doc = load_catalog_doc(repo_root=repo_root, change_dir=change_dir)
    raw = doc.get("kits")
    out: list[KitOption] = []
    if isinstance(raw, list):
        for item in raw:
            if not isinstance(item, dict):
                continue
            kit_id = item.get("id")
            if not isinstance(kit_id, str) or not kit_id.strip():
                continue
            out.append(
                KitOption(
                    id=kit_id.strip(),
                    label=str(item.get("label") or kit_id),
                    description=str(item.get("description") or ""),
                    path=item.get("path") if isinstance(item.get("path"), str) else None,
                    prefix=item.get("prefix") if isinstance(item.get("prefix"), str) else None,
                    source=str(item.get("source") or ""),
                    package=item.get("package") if isinstance(item.get("package"), str) else None,
                    showcase=item.get("showcase") if isinstance(item.get("showcase"), str) else None,
                )
            )
    if not out:
        out = list(FALLBACK_KITS)

    # 锁定项目风格时，确保 project id 出现在列表中
    ps = load_project_style(repo_root=repo_root, change_dir=change_dir)
    if ps.locked and not any(k.id == ps.id for k in out):
        out.insert(
            0,
            KitOption(
                id=ps.id,
                label=ps.label,
                description=ps.description,
                path=ps.path,
                prefix=ps.prefix,
                source="project",
            ),
        )
    return out


def style_kits(kits: list[KitOption] | None = None) -> list[KitOption]:
    """内置三种移动端风格（不含 custom / project）。"""
    items = kits if kits is not None else load_kits()
    return [k for k in items if k.id not in {"custom", "project"} and k.source != "project"]


def resolve_kit(token: str, kits: list[KitOption] | None = None) -> KitOption | None:
    items = kits if kits is not None else load_kits()
    text = token.strip()
    if not text:
        return None
    if text.isdigit():
        idx = int(text)
        if 1 <= idx <= len(items):
            return items[idx - 1]
    lowered = text.lower()
    aliases = {
        "music": "ui-kit",
        "default": "ui-kit",
        "默认": "ui-kit",
        "无痛": "painless",
        "无痛单词": "painless",
        "pk": "painless",
        "米豆": "midoo",
        "md": "midoo",
        "自由": "custom",
        "自由发挥": "custom",
        "项目": "project",
        "自有": "project",
        "项目风格": "project",
    }
    target = aliases.get(lowered, lowered)
    for item in items:
        if item.id.lower() == target or item.label.lower() == lowered:
            return item
    return None


def menu_text(repo_root: Path | None = None, change_dir: Path | None = None) -> str:
    ps = load_project_style(repo_root=repo_root, change_dir=change_dir)
    items = load_kits(repo_root=repo_root, change_dir=change_dir)

    if ps.locked:
        lines = [
            "视觉基线：项目已锁定自有 UI 风格（不强制三选一）",
            "打断码：I_VISUAL_BASELINE（仅确认/例外）",
            "",
            f"默认 baseline: {ps.id} — {ps.label}",
            f"  {ps.description}",
        ]
        if ps.path:
            lines.append(f"  path: {ps.path}")
        if ps.prefix:
            lines.append(f"  prefix: {ps.prefix}")
        if ps.theme_doc:
            lines.append(f"  themeDoc: {ps.theme_doc}")
        if ps.notes:
            lines.append(f"  notes: {ps.notes}")
        lines.extend(
            [
                "",
                "出设计 / UX 原型须遵循上述项目风格，勿改套竞品 kit。",
                "若需例外（ui-kit / painless / midoo / custom）：须在 visual.notes 说明原因。",
                "",
                "【例外可选】",
            ]
        )
        n = 1
        for item in items:
            if item.id == ps.id:
                continue
            lines.append(f"  {n}) {item.id} — {item.label}（例外，须 notes）")
            n += 1
        lines.append("")
        lines.append("动效合同：research/ui-kits/MOTION.md")
        lines.append("目录：research/ui-kits/catalog.yaml → projectStyle.locked")
        return "\n".join(lines)

    lines = [
        "视觉基线人选（写入 ux.yaml → visual.baseline）",
        "打断码：I_VISUAL_BASELINE",
        "",
        "【三种内置移动端风格】（项目未锁定自有风格时）",
    ]
    n = 1
    for item in items:
        if item.id == "custom":
            continue
        prefix = f"prefix={item.prefix}" if item.prefix else "no-prefix"
        lines.append(f"  {n}) {item.id} — {item.label}")
        lines.append(f"     {item.description}")
        lines.append(f"     {prefix}" + (f" · {item.path}" if item.path else ""))
        n += 1
    custom = next((k for k in items if k.id == "custom"), None)
    if custom is not None:
        lines.append("")
        lines.append("【可选】")
        lines.append(f"  {n}) custom — {custom.label}")
        lines.append(f"     {custom.description}")
    lines.append("")
    lines.append("若业务仓已有设计系统：将 catalog.yaml 的 projectStyle.locked 设为 true。")
    lines.append("动效合同：research/ui-kits/MOTION.md")
    lines.append("目录：research/ui-kits/catalog.yaml")
    return "\n".join(lines)


def menu_choices_for_ask(repo_root: Path | None = None) -> list[dict[str, str]]:
    """Structured choices for AskQuestion / lead interrupt."""
    ps = load_project_style(repo_root=repo_root)
    items = load_kits(repo_root=repo_root)
    if ps.locked:
        choices = [
            {
                "id": ps.id,
                "label": f"{ps.label}（{ps.id}·推荐）",
                "description": "遵循项目自有 UI，不强制三选一",
            }
        ]
        for item in items:
            if item.id == ps.id:
                continue
            choices.append(
                {
                    "id": item.id,
                    "label": f"{item.label}（{item.id}·例外）",
                    "description": "例外偏离项目风格，须 visual.notes",
                }
            )
        return choices

    choices: list[dict[str, str]] = []
    for item in items:
        if item.id == "custom":
            continue
        choices.append(
            {
                "id": item.id,
                "label": f"{item.label}（{item.id}）",
                "description": item.description,
            }
        )
    custom = next((k for k in items if k.id == "custom"), None)
    if custom is not None:
        choices.append(
            {
                "id": "custom",
                "label": f"{custom.label}（custom）",
                "description": custom.description,
            }
        )
    return choices
