# AiAssitRequreimentDev

AI 辅助需求开发流水线。从意图出发，用结构化规格把产品、交互视觉、技术方案、开发、Review、测试、部署串起来。

你只需对主控说需求；文档与门禁命令由 Agent 代写代跑。有问题才打断，否则自动推进。

- 仓库：https://github.com/jackykarma/AiAssitRequreimentDev
- 架构：[docs/architecture.md](docs/architecture.md)
- 角色边界：[constitution.md](constitution.md)
- Agent 入口：[AGENTS.md](AGENTS.md)
- 知识层：[modus/knowledge/architecture-overview.md](modus/knowledge/architecture-overview.md)

## 需求与 feature

| 概念 | 含义 |
| --- | --- |
| 需求 | 业务问题 / 史诗；大需求可建 `requirements/<REQ-id>/`（需求级 PRD + `split.yaml`） |
| feature | 可关门禁的交付切片（对本切片验收可独立交付；可有 feature 间依赖）；产物在 `features/<id>/`；一条需求 → 1..N 个 feature |
| task | feature 内实现单元；该 feature 的 `tasks.yaml`（G2T 之后再拆） |

小需求可直开单个 feature。大需求：产品先写需求级 PRD，再在 `split.yaml` 决定拆几个；主控建目录。

## 开始

在 Cursor 中启用 `aiassitrequreimentdev-lead`：

1. 选角色（[docs/role-picker.html](docs/role-picker.html) + `adopt`）
2. 确认路径全量/轻量（[docs/path-picker.html](docs/path-picker.html) + `recommend` / `path`）
3. 进入对应技能；共仓产物见各 feature 的 `BOARD.md`

底层等价于：

```bash
python -m pip install -e .
python -m aiassitrequreimentdev init-req REQ-001          # 大需求（可选）
python -m aiassitrequreimentdev init FEAT-001             # feature
python -m aiassitrequreimentdev check features/FEAT-001 --gate G1
python -m unittest tests.test_gates tests.test_roles tests.test_paths
```

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

## 角色技能（只写自己的工件）

| 技能 | 只写 |
| --- | --- |
| `aiassitrequreimentdev-lead` | `state.json`、`tasks.yaml`、代跑 CLI |
| `aiassitrequreimentdev-brainstorm` | 一句话需求时探索意图与方案（不出正式 spec） |
| `aiassitrequreimentdev-grill` | 系统追问，闭合旅程与规格清单 |
| `aiassitrequreimentdev-product` | `prd.md`、可交互 `prototype/index.html`、`spec.yaml`（用户旅程/功能/非功能/场景/异常/验收；大需求另写需求级 PRD / `split.yaml`） |
| `aiassitrequreimentdev-ux` | `ux.yaml`、可交互 `prototype/ux/` |
| `aiassitrequreimentdev-tech` | `tech.md`（人审）+ `tech.yaml`（AI 约束/接口/验收）；图用 [Archify](https://github.com/tt-a1i/archify) 仅 html+svg |
| `aiassitrequreimentdev-dev` | 任务写集内源码 |
| `aiassitrequreimentdev-review` | `review.yaml` |
| `aiassitrequreimentdev-test` | `evidence.yaml` |
| `aiassitrequreimentdev-deploy` | `deploy.yaml` |

门禁：`G0` → `G1` → `G2` → `G2T` → `G3` → `GR` → `G4` → `GD`。

## Review 要点

- `blocking`：先修复并复审，禁止进入测试
- `dispute`：打断等人裁决
- `nit`：不挡门禁
