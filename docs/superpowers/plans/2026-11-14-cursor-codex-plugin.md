# Cursor / Codex 团队插件 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 AiAssitRequreimentDev 打成团队私有 Git marketplace 插件，Cursor 与 Codex 同一套源可装，业务仓装完即可用 lead 技能与 `aad` CLI。

**Architecture:** 单插件根 `plugins/aiassitrequreimentdev/`（Agent Plugins `plugin.json` + `.cursor-plugin` + `.codex-plugin`）；双 marketplace 清单；技能/精简 references 进插件；`scripts/aad` 懒装并转调仓库根 Python 包；本仓 `.cursor/skills` 由同步脚本从插件拷出，禁止双改。

**Tech Stack:** Python ≥3.11、现有 `aiassitrequreimentdev` 包、Cursor/Codex plugin manifests、unittest。

**Spec:** `docs/superpowers/specs/2026-11-14-cursor-codex-plugin-design.md`

## Global Constraints

- 首期只做团队/私有 Git marketplace，不上公共市场。
- 不把完整 `modus/`、Archify 打进插件；references 仅最小可跑集。
- 模板权威在 `aiassitrequreimentdev/templates/`，插件不维护第二份模板正文。
- 技能单源：`plugins/aiassitrequreimentdev/skills/`；`.cursor/skills` 仅为同步副本。
- CLI 权威：`python -m aiassitrequreimentdev`；插件只包装。
- 未获用户明确要求前不要 `git commit`（计划中的 commit 步骤改为「暂存说明，等用户下令再提交」）。
- 用户规则：回复简体中文；新建文件头按 OPLUS 版权格式（Python）。

---

## File map

| Path | Responsibility |
| --- | --- |
| `plugins/aiassitrequreimentdev/plugin.json` | Agent Plugins 标准清单 |
| `plugins/aiassitrequreimentdev/.cursor-plugin/plugin.json` | Cursor 兼容清单 |
| `plugins/aiassitrequreimentdev/.codex-plugin/plugin.json` | Codex 兼容清单 |
| `.cursor-plugin/marketplace.json` | Cursor 团队 marketplace |
| `.agents/plugins/marketplace.json` | Codex `/plugins` 团队源 |
| `plugins/aiassitrequreimentdev/skills/*/` | 角色技能（单源） |
| `plugins/aiassitrequreimentdev/rules/*.mdc` | always：需求开发用 lead |
| `plugins/aiassitrequreimentdev/references/*.md` | 精简知识 |
| `plugins/aiassitrequreimentdev/scripts/aad.py` | 懒装 + 转调 CLI |
| `plugins/aiassitrequreimentdev/scripts/aad` | Unix 入口（可选薄包装） |
| `plugins/aiassitrequreimentdev/scripts/aad.cmd` | Windows 入口 |
| `scripts/sync_plugin_skills.py` | 插件 skills → `.cursor/skills` |
| `tests/test_aad_launcher.py` | aad 解析/懒装/转调单测 |
| `README.md` | 团队安装说明 |
| `AGENTS.md` | 一句指向插件/lead |

---

### Task 1: 插件骨架与双端 marketplace

**Files:**
- Create: `plugins/aiassitrequreimentdev/plugin.json`
- Create: `plugins/aiassitrequreimentdev/.cursor-plugin/plugin.json`
- Create: `plugins/aiassitrequreimentdev/.codex-plugin/plugin.json`
- Create: `.cursor-plugin/marketplace.json`
- Create: `.agents/plugins/marketplace.json`
- Test: 手工 JSON 校验 + 后续 Task 用目录存在性断言（本任务用 PowerShell/`python -c` 校验 JSON）

**Interfaces:**
- Produces: 插件名恒为 `aiassitrequreimentdev`；marketplace `source.path` = `./plugins/aiassitrequreimentdev`

- [ ] **Step 1: 写入 Agent Plugins 根清单**

`plugins/aiassitrequreimentdev/plugin.json`:

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  "name": "aiassitrequreimentdev",
  "version": "0.1.0",
  "description": "AI 辅助需求开发：角色技能 + 规格门禁 CLI（团队 marketplace）",
  "author": { "name": "OPLUS Apps.Gallery" }
}
```

- [ ] **Step 2: 写入 Cursor / Codex 兼容清单**

`plugins/aiassitrequreimentdev/.cursor-plugin/plugin.json`:

```json
{
  "name": "aiassitrequreimentdev",
  "displayName": "AiAssitRequreimentDev",
  "version": "0.1.0",
  "description": "需求开发流水线：lead/product/ux/tech/dev/review/test/deploy 技能与门禁 CLI",
  "author": { "name": "OPLUS Apps.Gallery" },
  "keywords": ["requirements", "gates", "prd", "tech"]
}
```

`plugins/aiassitrequreimentdev/.codex-plugin/plugin.json`:

```json
{
  "name": "aiassitrequreimentdev",
  "version": "0.1.0",
  "description": "AI-assisted requirements pipeline skills and gate CLI",
  "skills": "./skills/"
}
```

- [ ] **Step 3: 写入双 marketplace**

`.cursor-plugin/marketplace.json`:

```json
{
  "name": "aiassitrequreimentdev-team",
  "owner": {
    "name": "OPLUS Apps.Gallery"
  },
  "metadata": {
    "description": "AiAssitRequreimentDev 团队插件源"
  },
  "plugins": [
    {
      "name": "aiassitrequreimentdev",
      "source": "plugins/aiassitrequreimentdev",
      "description": "需求开发角色技能与门禁 CLI",
      "version": "0.1.0"
    }
  ]
}
```

`.agents/plugins/marketplace.json`:

```json
{
  "name": "aiassitrequreimentdev-team",
  "interface": {
    "displayName": "AiAssitRequreimentDev Team"
  },
  "plugins": [
    {
      "name": "aiassitrequreimentdev",
      "source": {
        "source": "local",
        "path": "./plugins/aiassitrequreimentdev"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Productivity"
    }
  ]
}
```

- [ ] **Step 4: 校验 JSON 可解析**

Run:

```powershell
python -c "import json,pathlib; roots=[pathlib.Path('plugins/aiassitrequreimentdev/plugin.json'),pathlib.Path('plugins/aiassitrequreimentdev/.cursor-plugin/plugin.json'),pathlib.Path('plugins/aiassitrequreimentdev/.codex-plugin/plugin.json'),pathlib.Path('.cursor-plugin/marketplace.json'),pathlib.Path('.agents/plugins/marketplace.json')];
[json.loads(p.read_text(encoding='utf-8')) for p in roots]; print('ok', len(roots))"
```

Expected: `ok 5`

- [ ] **Step 5: 提交说明（等用户下令再 git commit）**

暂存候选：上述 5 个 JSON 文件。

---

### Task 2: 迁移技能单源 + 同步脚本

**Files:**
- Create: `plugins/aiassitrequreimentdev/skills/<name>/SKILL.md`（10 个，从 `.cursor/skills` 复制）
- Create: `scripts/sync_plugin_skills.py`
- Modify: 之后以插件目录为权威；`.cursor/skills` 由脚本覆盖生成
- Test: `python scripts/sync_plugin_skills.py --check`（实现后）

**Interfaces:**
- Consumes: 现有 `.cursor/skills/aiassitrequreimentdev-*/SKILL.md`
- Produces: `sync_plugin_skills(repo_root: Path, *, check: bool) -> int`；退出码 0=一致/已同步，1=check 发现漂移

- [ ] **Step 1: 复制技能到插件目录**

Run:

```powershell
$names = @(
  'aiassitrequreimentdev-lead','aiassitrequreimentdev-product','aiassitrequreimentdev-ux',
  'aiassitrequreimentdev-tech','aiassitrequreimentdev-dev','aiassitrequreimentdev-review',
  'aiassitrequreimentdev-test','aiassitrequreimentdev-deploy','aiassitrequreimentdev-brainstorm',
  'aiassitrequreimentdev-grill'
)
foreach ($n in $names) {
  New-Item -ItemType Directory -Force -Path "plugins/aiassitrequreimentdev/skills/$n" | Out-Null
  Copy-Item ".cursor/skills/$n/SKILL.md" "plugins/aiassitrequreimentdev/skills/$n/SKILL.md" -Force
}
```

Expected: 10 个 `SKILL.md` 存在于插件下。

- [ ] **Step 2: 写同步脚本（含 `--check`）**

`scripts/sync_plugin_skills.py` 核心逻辑：

```python
"""Sync plugins/.../skills -> .cursor/skills (single source of truth)."""
from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path

PLUGIN_SKILLS = Path("plugins/aiassitrequreimentdev/skills")
CURSOR_SKILLS = Path(".cursor/skills")


def sync(repo: Path, *, check: bool) -> int:
    src_root = repo / PLUGIN_SKILLS
    dst_root = repo / CURSOR_SKILLS
    if not src_root.is_dir():
        print(f"missing {src_root}", file=sys.stderr)
        return 2
    drift = False
    for skill_dir in sorted(p for p in src_root.iterdir() if p.is_dir()):
        src = skill_dir / "SKILL.md"
        if not src.is_file():
            continue
        dst = dst_root / skill_dir.name / "SKILL.md"
        if check:
            if not dst.is_file() or not filecmp.cmp(src, dst, shallow=False):
                print(f"drift: {dst}")
                drift = True
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return 1 if drift else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    return sync(args.repo.resolve(), check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 3: 跑同步并 check**

```powershell
python scripts/sync_plugin_skills.py
python scripts/sync_plugin_skills.py --check
```

Expected: 第二次退出码 `0`，无 `drift` 输出。

- [ ] **Step 4: 提交说明（等用户下令）**

暂存：`plugins/.../skills/**`、`scripts/sync_plugin_skills.py`。

---

### Task 3: Rules + 精简 references

**Files:**
- Create: `plugins/aiassitrequreimentdev/rules/aad-lead.mdc`
- Create: `plugins/aiassitrequreimentdev/references/README.md`
- Create: `plugins/aiassitrequreimentdev/references/constitution-summary.md`
- Create: `plugins/aiassitrequreimentdev/references/flow.md`
- Create: `plugins/aiassitrequreimentdev/references/gates.md`
- Create: `plugins/aiassitrequreimentdev/references/artifacts.md`
- Create: `plugins/aiassitrequreimentdev/references/decomposition.md`
- Modify: `plugins/aiassitrequreimentdev/skills/aiassitrequreimentdev-lead/SKILL.md`（指向 references + `scripts/aad`）
- Modify: 其它技能中「先读 modus/…」改为「先读插件 `references/`；业务仓有 `modus/` 则可作补充」
- Test: 文件存在 + lead 技能含 `references/` 与 `aad`

**Interfaces:**
- Produces: 技能约定 CLI 调用形式：`python <plugin>/scripts/aad.py <subcommand> ...` 或业务仓 PATH 上的 `aad`

- [ ] **Step 1: 写 always rule**

`plugins/aiassitrequreimentdev/rules/aad-lead.mdc`:

```markdown
---
description: 做需求开发时启用 AiAssitRequreimentDev 主控
alwaysApply: true
---

在业务仓库做需求 / PRD / feature / 门禁流水线时：启用技能 `aiassitrequreimentdev-lead`。
门禁与脚手架使用插件脚本 `scripts/aad.py`（转调 `python -m aiassitrequreimentdev`），不要手改 `gates.*.accepted`。
产物共仓于业务仓 `features/<id>/`。
```

- [ ] **Step 2: 写 references（从现有 docs/modus 压缩，保持中文短文）**

最少包含：

- `README.md`：索引表
- `constitution-summary.md`：宪法要点（角色只写自己的件、G1 seal、verify=命令退出码等）
- `flow.md`：G0→GD 与角色顺序
- `gates.md`：门禁表（含原型 G1/G2）
- `artifacts.md`：产物表
- `decomposition.md`：需求≠feature、tasks 在 G2T 后

内容从 `constitution.md`、`docs/architecture.md`、`modus/knowledge/domain/change/references/*` 摘录，**每文件建议 ≤80 行**。

- [ ] **Step 3: 改 lead 技能头部工作方式**

在 `plugins/.../skills/aiassitrequreimentdev-lead/SKILL.md` 靠近开头加入：

```markdown
## 插件上下文

- 知识：本插件 `references/`（业务仓完整 `modus/` 可选补充）
- CLI：`python <本插件>/scripts/aad.py …`（等价 `python -m aiassitrequreimentdev`）
- 同步本仓 Cursor 技能：`python scripts/sync_plugin_skills.py`
```

把文中 `python -m aiassitrequreimentdev` 保留为语义等价说明，并注明优先 `aad.py`。

- [ ] **Step 4: 批量替换其它技能中的硬编码 modus 入口**

对 `plugins/.../skills/*/SKILL.md`：将「知识从 `modus/knowledge/architecture-overview.md` 进入」改为「知识从插件 `references/README.md` 进入；若业务仓有 `modus/knowledge/` 可作域补充」。

- [ ] **Step 5: 再跑 sync**

```powershell
python scripts/sync_plugin_skills.py
python scripts/sync_plugin_skills.py --check
```

Expected: 退出码 0。

---

### Task 4: `aad` 启动器（TDD）

**Files:**
- Create: `plugins/aiassitrequreimentdev/scripts/aad.py`
- Create: `plugins/aiassitrequreimentdev/scripts/aad.cmd`
- Create: `tests/test_aad_launcher.py`
- Test: `python -m unittest tests.test_aad_launcher -v`

**Interfaces:**
- Produces:
  - `plugin_root_from(file: Path) -> Path` → `…/plugins/aiassitrequreimentdev`
  - `repo_root_from_plugin(plugin_root: Path) -> Path | None` → 若存在 `plugin_root.parent.parent / "aiassitrequreimentdev"` 包则返回 git 仓根
  - `ensure_package(*, plugin_root: Path, runner) -> None` → 可 import 则返回；否则 editable 或 git+ 安装
  - `main(argv: list[str]) -> int` → 转调模块 main

- [ ] **Step 1: 写失败单测（包未装时尝试 editable）**

`tests/test_aad_launcher.py`:

```python
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from importlib.util import spec_from_file_location, module_from_spec


def load_aad():
    path = Path("plugins/aiassitrequreimentdev/scripts/aad.py")
    spec = spec_from_file_location("aad_launcher", path)
    mod = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


class AadLauncherTests(unittest.TestCase):
    def test_plugin_root_from_script(self):
        aad = load_aad()
        script = Path("plugins/aiassitrequreimentdev/scripts/aad.py").resolve()
        root = aad.plugin_root_from(script)
        self.assertTrue((root / "plugin.json").is_file() or root.name == "aiassitrequreimentdev")

    def test_repo_root_detected_in_monorepo(self):
        aad = load_aad()
        plugin = Path("plugins/aiassitrequreimentdev").resolve()
        repo = aad.repo_root_from_plugin(plugin)
        self.assertIsNotNone(repo)
        self.assertTrue((repo / "aiassitrequreimentdev" / "__init__.py").is_file())

    def test_ensure_package_skips_when_importable(self):
        aad = load_aad()
        runner = mock.Mock()
        with mock.patch.object(aad, "package_importable", return_value=True):
            aad.ensure_package(plugin_root=Path("plugins/aiassitrequreimentdev"), runner=runner)
        runner.assert_not_called()


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 跑测确认失败（模块不存在）**

```powershell
python -m unittest tests.test_aad_launcher -v
```

Expected: FAIL / ERROR import `aad.py` 不存在或缺符号。

- [ ] **Step 3: 实现 `aad.py`（最小可用）**

```python
"""
/*********************************************************************************
 ** Copyright (C), 2019-2029, OPLUS Mobile Comm Corp., Ltd
 ** All rights reserved.
 **
 ** File: - aad.py
 ** Description: Plugin launcher: ensure package then run aiassitrequreimentdev CLI.
 ** Version: 1.0
 ** Date: 2026/11/14
 ** Author: limao2@Apps.Gallery
 **
 ** ------------------------------- Revision History: ----------------------------
 ** <author> <date> <version> <desc>
 ** ------------------------------------------------------------------------------
 ** limao2@Apps.Gallery 2026/11/14 1.0 INIT
 *********************************************************************************/
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def plugin_root_from(script_file: Path) -> Path:
    return script_file.resolve().parent.parent


def repo_root_from_plugin(plugin_root: Path) -> Path | None:
    candidate = plugin_root.resolve().parent.parent
    if (candidate / "aiassitrequreimentdev" / "__init__.py").is_file():
        return candidate
    return None


def package_importable() -> bool:
    try:
        import aiassitrequreimentdev  # noqa: F401
        return True
    except ImportError:
        return False


def ensure_package(*, plugin_root: Path, runner=subprocess.check_call) -> None:
    if package_importable():
        return
    repo = repo_root_from_plugin(plugin_root)
    if repo is not None:
        runner([sys.executable, "-m", "pip", "install", "-e", str(repo)])
        return
    remote = os.environ.get("AAD_GIT_REMOTE", "").strip()
    ref = os.environ.get("AAD_GIT_REF", "master").strip() or "master"
    if not remote:
        raise SystemExit(
            "aiassitrequreimentdev 未安装，且无法定位源仓。"
            "请设置 AAD_GIT_REMOTE（git+https://…）或在完整 clone 中使用本脚本。"
        )
    runner(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            f"git+{remote}@{ref}#egg=aiassitrequreimentdev",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    plugin_root = plugin_root_from(Path(__file__))
    ensure_package(plugin_root=plugin_root)
    from aiassitrequreimentdev.__main__ import main as cli_main

    return int(cli_main(argv))


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Windows 包装 `aad.cmd`**

```bat
@echo off
python "%~dp0aad.py" %*
```

- [ ] **Step 5: 跑通单测 + 冒烟**

```powershell
python -m unittest tests.test_aad_launcher -v
python plugins/aiassitrequreimentdev/scripts/aad.py --help
```

Expected: 单测 OK；help 打印现有 CLI 用法。

---

### Task 5: README / AGENTS 安装说明 + 回归

**Files:**
- Modify: `README.md`（增加「团队插件安装」）
- Modify: `AGENTS.md`（一句：插件路径 + lead）
- Modify: `docs/architecture.md`（可选一句插件入口）
- Test: `python -m unittest tests.test_gates tests.test_roles tests.test_paths tests.test_usage tests.test_aad_launcher`

- [ ] **Step 1: README 增加章节**

在 README 合适位置加入：

```markdown
## 团队插件安装（Cursor / Codex）

本仓库同时是团队 marketplace 源。

### Codex
1. 将本仓库加入 Codex marketplace（`.agents/plugins/marketplace.json`）
2. `/plugins` 安装 `aiassitrequreimentdev`
3. **新开会话**后使用 lead 等技能
4. CLI：`python <plugin>/scripts/aad.py check features/FEAT-001 --gate G1`

### Cursor
1. Customize → 从本 Git 仓库 / 团队 marketplace 安装
2. 新开 Agent 会话
3. 本仓开发技能同步：`python scripts/sync_plugin_skills.py`

业务仓无需自带完整 `modus/`；知识读插件 `references/`。Python ≥3.11。marketplace 仅含插件目录时，设置 `AAD_GIT_REMOTE` 供 `aad` 懒装 CLI 包。
```

- [ ] **Step 2: 更新 AGENTS.md 首段**

在现有「启用 lead」旁注明：若已装团队插件，技能来自插件；本仓请保持 `sync_plugin_skills` 无漂移。

- [ ] **Step 3: 全量相关单测**

```powershell
python -m unittest tests.test_gates tests.test_roles tests.test_paths tests.test_usage tests.test_aad_launcher
python scripts/sync_plugin_skills.py --check
```

Expected: 全部 OK；check 退出码 0。

- [ ] **Step 4: 对照规格验收清单（手工勾选）**

对照 `docs/superpowers/specs/2026-11-14-cursor-codex-plugin-design.md` §6：目录/脚本/文档就绪；真正「空业务仓装插件」在有 Cursor/Codex UI 的环境由人点验（Agent 记录步骤与阻塞）。

---

## Spec coverage self-check

| Spec 项 | Task |
| --- | --- |
| 方案 A 布局 + 三清单 | Task 1 |
| 双 marketplace | Task 1 |
| 技能迁入单源 + `.cursor/skills` 同步 | Task 2 |
| Rules always lead | Task 3 |
| 精简 references | Task 3 |
| 技能改读 references / aad | Task 3 |
| `aad` 懒装（editable + git remote） | Task 4 |
| README 安装说明 | Task 5 |
| unittest 不破 | Task 5 |
| 不上公共市场 / 不打完整 modus | 全局约束（未做） |

## Placeholder scan

无 TBD；CLI 安装失败路径有明确环境变量与报错文案。

---

Plan complete and saved to `docs/superpowers/plans/2026-11-14-cursor-codex-plugin.md`.

**执行方式二选一：**

1. **Subagent-Driven（推荐）** — 每任务新开子代理，任务间复查  
2. **Inline Execution** — 本会话按 executing-plans 连续做完  

选哪一种？
