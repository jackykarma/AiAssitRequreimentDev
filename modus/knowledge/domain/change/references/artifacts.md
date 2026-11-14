# feature 工件合同

目录：`features/<id>/`。只保留正式交付，不保留 `intent.md` 等对话草稿。

| 文件 | 作者 | 要点 |
| --- | --- | --- |
| `state.json` | 主控 | `stage`、`path`、`pathConfirmed`、`actorRole`、`gates`、`specHash`、`runId` |
| `BOARD.md` | 主控/`aiassitrequreimentdev board` | 共仓产物索引 |
| `prd.md` | 产品 | 给人评审的 PRD：核心用户旅程/功能/非功能/主流程/异常边界/验收；与 `spec.yaml` 同口径 |
| `prototype/index.html` | 产品 | 可交互 HTML 产品原型（G1；无 UI 时 `uiRequired=false` + `uiNoneReason`） |
| `spec.yaml` | 产品 | 机器合同与 G1/`seal`；`UJ*`/`FR*`/`NFR*`/`S*`/`E*`/`A*`；`uiRequired` |
| `ux.yaml` | 交互视觉 | 覆盖需 UI 的验收 + `htmlPrototype`；或 `skip: true` + `reason` |
| `prototype/ux/` | 交互视觉 | 可交互 UX HTML 原型（G2；入口默认 `index.html`） |
| `tech.md` | 技术方案 | 给人读：一页纸、L0/L1 架构、关键设计（含判定原则）、可多张流程/时序/类图 |
| `tech.yaml` | 技术方案 | 给 AI/门禁：`aiConstraints`、`keyDesigns`、`interfaces`、`diagrams[]`（含 layer/scope） |
| `diagrams/*` | 技术方案 | Archify：仅 `.html` + `.svg`；同类型可多张 |
| `tasks.yaml` | 主控 | 任务图：依赖、写集、验收、验证命令 |
| `review.yaml` | Review | `findings[]` |
| `evidence.yaml` | 测试 | 每条验收的 command 与 exitCode |
| `deploy.yaml` | 部署 | 清单、命令、回滚 |
| `usage.yaml` | 主控 | 各角色阶段 token 用量（`usage record` / 看板汇总） |

## `prd.md` 与 `spec.yaml`

两者都要，不是重复填两张表：

- `prd.md`：给人读（背景、用户、核心用户旅程、功能/非功能、主流程、异常边界、验收）
- `spec.yaml`：给 Agent 与门禁（`UJ*`/`FR*`/`NFR*`/`S*`/`E*`/`A*`、`seal` 哈希）

同一套编号；改规格必须同步 PRD（及受影响原型）。禁止只交其中一份就宣称产品完成。

禁止角色越权改写他人工件。
