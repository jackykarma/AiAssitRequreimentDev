"""Tests for visual baseline catalog / kits menu."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml

from aiassitrequreimentdev.kits import (
    default_baseline,
    load_kits,
    load_project_style,
    menu_text,
    project_style_locked,
    resolve_kit,
    style_kits,
)

REPO = Path(__file__).resolve().parents[1]


class KitsCatalogTests(unittest.TestCase):
    def test_loads_three_style_kits_plus_custom(self) -> None:
        kits = load_kits(repo_root=REPO)
        ids = [k.id for k in kits]
        self.assertIn("ui-kit", ids)
        self.assertIn("painless", ids)
        self.assertIn("midoo", ids)
        self.assertIn("custom", ids)
        styles = style_kits(kits)
        self.assertEqual([k.id for k in styles], ["ui-kit", "painless", "midoo"])
        self.assertFalse(project_style_locked(repo_root=REPO))
        self.assertEqual(default_baseline(repo_root=REPO), "ui-kit")

    def test_resolve_aliases(self) -> None:
        kits = load_kits(repo_root=REPO)
        self.assertEqual(resolve_kit("1", kits).id, "ui-kit")
        self.assertEqual(resolve_kit("无痛", kits).id, "painless")
        self.assertEqual(resolve_kit("midoo", kits).id, "midoo")
        self.assertEqual(resolve_kit("自由发挥", kits).id, "custom")

    def test_menu_lists_three_styles_when_unlocked(self) -> None:
        text = menu_text(repo_root=REPO)
        self.assertIn("三种内置移动端风格", text)
        self.assertIn("ui-kit", text)
        self.assertIn("painless", text)
        self.assertIn("midoo", text)
        self.assertIn("I_VISUAL_BASELINE", text)

    def test_project_locked_menu_skips_forced_three_way(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cat = root / "research" / "ui-kits"
            cat.mkdir(parents=True)
            (cat / "catalog.yaml").write_text(
                yaml.safe_dump(
                    {
                        "projectStyle": {
                            "locked": True,
                            "id": "project",
                            "label": "业务自有风格",
                            "path": "docs/design-system",
                            "prefix": "app",
                        },
                        "kits": [
                            {"id": "ui-kit", "label": "Music", "prefix": "uk", "path": "x"},
                            {"id": "custom", "label": "自由发挥", "prefix": None, "path": None},
                        ],
                    },
                    allow_unicode=True,
                ),
                encoding="utf-8",
            )
            self.assertTrue(project_style_locked(repo_root=root))
            self.assertEqual(default_baseline(repo_root=root), "project")
            ps = load_project_style(repo_root=root)
            self.assertEqual(ps.prefix, "app")
            text = menu_text(repo_root=root)
            self.assertIn("项目已锁定自有 UI 风格", text)
            self.assertIn("不强制三选一", text)
            self.assertNotIn("【三种内置移动端风格】", text)


if __name__ == "__main__":
    unittest.main()
