"""
/*********************************************************************************
 ** Copyright (C), 2019-2029, OPLUS Mobile Comm Corp., Ltd
 ** All rights reserved.
 **
 ** File: - test_plugin_smoke.py
 ** Description: 插件端到端烟测：落盘 smoke/ 真实需求文案 + Archify 真图
 ** Version: 1.3
 ** Date: 2026/11/18
 ** Author: limao2@Apps.Gallery
 **
 ** ------------------------------- Revision History: ----------------------------
 ** <author> <date> <version> <desc>
 ** ------------------------------------------------------------------------------
 ** limao2@Apps.Gallery 2026/11/18 1.0 INIT
 ** limao2@Apps.Gallery 2026/11/18 1.3 大需求改为 3 Feature 全产物
 *********************************************************************************/
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml

from aiassitrequreimentdev.template_headings import (
    REQ_ARCH_EXPAND_FILES,
    REQ_ARCH_EXPAND_LINKS,
    REQ_ARCH_H2,
    REQ_ARCH_H3_REQUIRED,
    REQ_PRD_H2,
    SPEC_PRD_H2,
    TECH_MD_H2,
    TECH_SPEC_H2,
    extract_markdown_headings,
    missing_headings,
)
from tests.smoke_diagrams import assert_fixtures_real
from tests.smoke_support import (
    FEATURE_LARGE_ALL,
    FEATURE_LARGE_FAVORITE,
    FEATURE_LARGE_REVIEW,
    FEATURE_LARGE_STREAK,
    FEATURE_SMALL_LIGHT,
    FEATURE_SMALL_LIGHT_AUTO,
    REQ_LARGE,
    SCENARIO_LARGE_REQ,
    SCENARIO_SMALL_LIGHT,
    SCENARIO_SMALL_LIGHT_AUTO,
    assert_files_exist,
    assert_markdown_has_substance,
    assert_real_diagram_pair,
    feature_stage_files,
    run_large_requirement,
    run_small_light,
    run_small_light_auto,
    smoke_root,
    write_smoke_index,
)


def _assert_headings(path: Path, required_h2: tuple[str, ...]) -> None:
    text = path.read_text(encoding="utf-8")
    present = extract_markdown_headings(text).get(2, [])
    missing = missing_headings(present, required_h2)
    if missing:
        raise AssertionError(f"{path} 缺章节: {missing}")


def _assert_gates_accepted(feature_dir: Path) -> dict:
    state = json.loads((feature_dir / "state.json").read_text(encoding="utf-8"))
    for gate in ("G0", "G1", "G2", "G2T", "G3", "GR", "G4", "GD"):
        if state["gates"].get(gate) != "accepted":
            raise AssertionError(f"{feature_dir.name} 门禁 {gate}={state['gates'].get(gate)}")
    if state.get("stage") != "done":
        raise AssertionError(f"{feature_dir.name} stage={state.get('stage')} 期望 done")
    return state


def _assert_feature_full_artifacts(feature_dir: Path, *, path: str) -> None:
    """与真实流程对齐：各阶段关键产物齐全，文案写满，真图到位。"""
    for paths in feature_stage_files(feature_dir).values():
        assert_files_exist(paths)
    assert_markdown_has_substance(feature_dir / "prd.md")
    assert_markdown_has_substance(feature_dir / "tech.md", min_chars=800)
    assert_markdown_has_substance(feature_dir / "tech-spec.md", min_chars=300)
    _assert_headings(feature_dir / "prd.md", SPEC_PRD_H2)
    _assert_headings(feature_dir / "tech.md", TECH_MD_H2)
    _assert_headings(feature_dir / "tech-spec.md", TECH_SPEC_H2)
    assert_real_diagram_pair(
        feature_dir / "diagrams" / "vocab.L1.architecture.html",
        feature_dir / "diagrams" / "vocab.L1.architecture.png",
    )
    tech_md = (feature_dir / "tech.md").read_text(encoding="utf-8")
    if "diagrams/vocab.L1.architecture.png" not in tech_md:
        raise AssertionError("tech.md 未内嵌 vocab.L1 真图")
    state = _assert_gates_accepted(feature_dir)
    self_path = state.get("path")
    if self_path != path:
        raise AssertionError(f"{feature_dir.name} path={self_path} 期望 {path}")
    if state.get("requirementId") not in (None, REQ_LARGE) and path.startswith("light"):
        pass
    tasks = yaml.safe_load((feature_dir / "tasks.yaml").read_text(encoding="utf-8"))
    if not isinstance(tasks, dict) or not tasks.get("tasks"):
        raise AssertionError("tasks.yaml 无任务")
    # full 路径必须有 UX + 产品原型（真实流程不省略）
    if path == "full":
        assert_files_exist(
            [
                feature_dir / "ux.yaml",
                feature_dir / "prototype" / "index.html",
                feature_dir / "prototype" / "ux" / "index.html",
            ]
        )
        ux = yaml.safe_load((feature_dir / "ux.yaml").read_text(encoding="utf-8"))
        if ux.get("visual", {}).get("baseline") != "painless":
            raise AssertionError(f"{feature_dir.name} 期望 visual.baseline=painless")


class PluginSmokeTests(unittest.TestCase):
    """每次运行在 `smoke/` 落盘真实需求文案 + Archify 真图。"""

    @classmethod
    def setUpClass(cls) -> None:
        assert_fixtures_real()
        write_smoke_index()

    def test_small_requirement_light_to_gd(self) -> None:
        feature = run_small_light()
        state = _assert_gates_accepted(feature)
        self.assertEqual(state["path"], "light")
        self.assertIsNone(state.get("requirementId"))
        _assert_feature_full_artifacts(feature, path="light")
        self.assertTrue((smoke_root() / SCENARIO_SMALL_LIGHT / "README.md").is_file())
        self.assertEqual(feature.name, FEATURE_SMALL_LIGHT)

    def test_small_requirement_light_auto_to_gd(self) -> None:
        feature = run_small_light_auto()
        state = _assert_gates_accepted(feature)
        self.assertEqual(state["path"], "light-auto")
        _assert_feature_full_artifacts(feature, path="light-auto")
        tasks = yaml.safe_load((feature / "tasks.yaml").read_text(encoding="utf-8"))
        self.assertEqual(len(tasks["tasks"]), 1)
        self.assertTrue((smoke_root() / SCENARIO_SMALL_LIGHT_AUTO / "README.md").is_file())
        self.assertEqual(feature.name, FEATURE_SMALL_LIGHT_AUTO)

    def test_large_requirement_three_features_full_artifacts(self) -> None:
        """大需求「无痛学环」：split multi × 3 Feature，每切片完整产物至 GD。"""
        req_dir, features = run_large_requirement()
        self.assertEqual(len(features), 3)
        by_name = {f.name: f for f in features}
        self.assertEqual(set(by_name), set(FEATURE_LARGE_ALL))

        split = yaml.safe_load((req_dir / "split.yaml").read_text(encoding="utf-8"))
        self.assertEqual(split["decision"], "multi")
        self.assertTrue(split["confirmedByHuman"])
        self.assertEqual(len(split["features"]), 3)
        self.assertEqual(req_dir.name, REQ_LARGE)

        assert_files_exist(
            [
                req_dir / "prd.md",
                req_dir / "split.yaml",
                req_dir / "architecture" / "architecture.md",
                req_dir / "architecture" / "architecture.yaml",
                req_dir / "architecture" / "nfr.md",
                req_dir / "architecture" / "interface-design.md",
                req_dir / "architecture" / "database-design.md",
                req_dir / "architecture" / "analytics-tracking.md",
                req_dir / "architecture" / "key-func-design" / "KD_001_daily_queue.md",
                req_dir / "architecture" / "key-func-design" / "KD_002_favorite_idempotent.md",
                req_dir / "architecture" / "key-func-design" / "KD_003_streak.md",
            ]
        )
        assert_markdown_has_substance(req_dir / "prd.md")
        assert_markdown_has_substance(
            req_dir / "architecture" / "architecture.md", min_chars=2000
        )
        _assert_headings(req_dir / "prd.md", REQ_PRD_H2)
        _assert_headings(req_dir / "architecture" / "architecture.md", REQ_ARCH_H2)
        arch_text = (req_dir / "architecture" / "architecture.md").read_text(encoding="utf-8")
        h3 = extract_markdown_headings(arch_text).get(3, [])
        self.assertEqual(missing_headings(h3, REQ_ARCH_H3_REQUIRED), [])
        for fid in FEATURE_LARGE_ALL:
            self.assertIn(fid, arch_text)
        for filename, required_h3 in REQ_ARCH_EXPAND_FILES.items():
            expand_path = req_dir / "architecture" / filename
            assert_markdown_has_substance(expand_path, min_chars=400)
            expand_h3 = extract_markdown_headings(
                expand_path.read_text(encoding="utf-8")
            ).get(3, [])
            self.assertEqual(
                missing_headings(expand_h3, required_h3),
                [],
                msg=f"{filename} 缺 design 模板三级标题",
            )
        for h2, link_file in REQ_ARCH_EXPAND_LINKS.items():
            self.assertIn(
                link_file,
                arch_text,
                msg=f"architecture.md「{h2}」须引用 {link_file}",
            )
        assert_real_diagram_pair(
            req_dir / "architecture" / "diagrams" / "req.L0.architecture.html",
            req_dir / "architecture" / "diagrams" / "req.L0.architecture.png",
        )
        assert_real_diagram_pair(
            req_dir / "architecture" / "diagrams" / "req.overview.workflow.html",
            req_dir / "architecture" / "diagrams" / "req.overview.workflow.png",
        )

        # 三切片：收藏 light-auto；复习/进度 full——均不省略阶段产物
        _assert_feature_full_artifacts(by_name[FEATURE_LARGE_FAVORITE], path="light-auto")
        self.assertEqual(
            json.loads(
                (by_name[FEATURE_LARGE_FAVORITE] / "state.json").read_text(encoding="utf-8")
            )["requirementId"],
            REQ_LARGE,
        )

        review = by_name[FEATURE_LARGE_REVIEW]
        _assert_feature_full_artifacts(review, path="full")
        for stem in (
            "vocab.L0.architecture",
            "vocab.review.workflow",
            "vocab.checkin.sequence",
            "vocab.review.class",
        ):
            assert_real_diagram_pair(
                review / "diagrams" / f"{stem}.html",
                review / "diagrams" / f"{stem}.png",
            )
        tech = (review / "tech.md").read_text(encoding="utf-8")
        self.assertIn("diagrams/vocab.review.workflow.png", tech)

        streak = by_name[FEATURE_LARGE_STREAK]
        _assert_feature_full_artifacts(streak, path="full")
        self.assertIn(
            "连续",
            (streak / "prd.md").read_text(encoding="utf-8"),
        )

        self.assertTrue((smoke_root() / SCENARIO_LARGE_REQ / "README.md").is_file())


if __name__ == "__main__":
    unittest.main()
