# feature 工件

目录：`features/<id>/`。只保留正式交付，不保留对话草稿。角色只写自己的文件。

| 文件 | 作者 | 要点 |
| --- | --- | --- |
| `state.json` | 主控 | `stage`、`path`、`pathConfirmed`、`actorRole`、`requirementId`、`dependsOnFeatures`、`gates`、`specHash` |
| `BOARD.md` | 主控（`board`） | 共仓索引 |
| `usage.yaml` | 主控（`usage record`） | 各角色阶段 token 用量 |
| `prd.md` | 产品 | 给人读：旅程、功能、非功能、主流程、异常边界、验收；与 spec 同口径 |
| `prototype/index.html` | 产品 | 可交互产品原型（G1）；无 UI 时不交，改 `uiRequired=false` + `uiNoneReason` |
| `spec.yaml` | 产品 | 机器合同与 G1/`seal`：`UJ*`/`FR*`/`NFR*`/`S*`/`E*`/`A*`、`uiRequired` |
| `ux.yaml` | 交互视觉 | 覆盖需 UI 的验收 + `htmlPrototype`；或 `skip: true` + `reason` |
| `prototype/ux/` | 交互视觉 | 可交互 UX HTML（G2；入口默认 `index.html`） |
| `tech.md` | 架构师 | 给人读：一页纸、L0/L1、关键设计 |
| `tech.yaml` | 架构师 | 给 AI/门禁：`aiConstraints`、`keyDesigns`、`interfaces`、`diagrams[]` |
| `diagrams/*` | 架构师 | Archify，仅 `.html` + `.svg` |
| `tasks.yaml` | 主控 | G2T 之后的任务图：依赖、写集、验收、验证命令 |
| `review.yaml` | Review | `findings[]`：`blocking` / `dispute` / `nit` |
| `evidence.yaml` | 测试 | 每条验收的 command 与 `exitCode` |
| `deploy.yaml` | 部署 | 环境、命令、回滚；不代执行上线 |

大需求另有 `requirements/<REQ-id>/`：需求级 `prd.md`、`split.yaml`，可选 `architecture/`（Archify 草图，不进 G2T）。

`prd.md` 给人读，`spec.yaml` 给 Agent 与门禁，同一套编号。禁止只交其中一份。改规格必须同步 PRD 及受影响原型。
