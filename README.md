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

## 角色技能（只写自己的工件）

| 技能 | 只写 |
| --- | --- |
| `aiassitrequreimentdev-lead` | `state.json`、`tasks.yaml`、代跑 CLI |
| `aiassitrequreimentdev-product` | `prd.md`、`prototype/`、`spec.yaml`（大需求另写需求级 PRD / `split.yaml`） |
| `aiassitrequreimentdev-ux` | `ux.yaml` |
| `aiassitrequreimentdev-tech` | `tech.md`、`tech.yaml`（按 feature；架构图可选，变更文件/选型/风险/快稳省/数据/埋点必含） |
| `aiassitrequreimentdev-dev` | 任务写集内源码 |
| `aiassitrequreimentdev-review` | `review.yaml` |
| `aiassitrequreimentdev-test` | `evidence.yaml` |
| `aiassitrequreimentdev-deploy` | `deploy.yaml` |

门禁：`G0` → `G1` → `G2` → `G2T` → `G3` → `GR` → `G4` → `GD`。

## Review 要点

- `blocking`：先修复并复审，禁止进入测试
- `dispute`：打断等人裁决
- `nit`：不挡门禁
