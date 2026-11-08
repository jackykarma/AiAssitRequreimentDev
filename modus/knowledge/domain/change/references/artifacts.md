# feature 工件合同

目录：`features/<id>/`。只保留正式交付，不保留 `intent.md` 等对话草稿。

| 文件 | 作者 | 要点 |
| --- | --- | --- |
| `state.json` | 主控 | `stage`、`path`、`pathConfirmed`、`actorRole`、`gates`、`specHash`、`runId` |
| `BOARD.md` | 主控/`aiassitrequreimentdev board` | 共仓产物索引 |
| `prd.md` | 产品 | 给人评审的 PRD：核心用户旅程/功能/非功能/主流程/异常边界/验收；与 `spec.yaml` 同口径 |
| `prototype/` | 产品 | 可点击 HTML 原型 |
| `spec.yaml` | 产品 | 机器合同与 G1/`seal`；`UJ*`/`FR*`/`NFR*`/`S*`/`E*`/`A*` |
| `ux.yaml` | 交互视觉 | 覆盖需 UI 的验收；或 `skip: true` + `reason` |
| `tech.md` | 技术方案 | 给人读：架构图（可选）、变更文件、选型、风险、快稳省、数据设计、埋点 |
| `tech.yaml` | 技术方案 | 机器合同：同上结构化字段 + 每条验收的架构/接口/数据/约束 |
| `tasks.yaml` | 主控 | 任务图：依赖、写集、验收、验证命令 |
| `review.yaml` | Review | `findings[]` |
| `evidence.yaml` | 测试 | 每条验收的 command 与 exitCode |
| `deploy.yaml` | 部署 | 清单、命令、回滚 |

## `prd.md` 与 `spec.yaml`

两者都要，不是重复填两张表：

- `prd.md`：给人读（背景、用户、核心用户旅程、功能/非功能、主流程、异常边界、验收）
- `spec.yaml`：给 Agent 与门禁（`UJ*`/`FR*`/`NFR*`/`S*`/`E*`/`A*`、`seal` 哈希）

同一套编号；改规格必须同步 PRD（及受影响原型）。禁止只交其中一份就宣称产品完成。

禁止角色越权改写他人工件。
