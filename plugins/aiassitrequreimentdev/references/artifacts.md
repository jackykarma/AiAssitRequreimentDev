# feature 工件

目录：`features/<id>/`。只保留正式交付，不保留对话草稿。角色只写自己的文件。

| 文件 | 作者 | 要点 |
| --- | --- | --- |
| `state.json` | 主控 | `stage`、`path`、`pathConfirmed`、`actorRole`、`requirementId`、`dependsOnFeatures`、`gates`、`specHash` |
| `BOARD.md` | 主控（`board`） | 共仓索引 |
| `usage.yaml` | 主控（`usage record`） | 各角色阶段 token 用量 |
| `prd.md` | 产品 | 人读事实源：严格按 `templates/feature/prd.md`（需求级 `templates/requirement/prd.md`）；与 spec 同编号 |
| `prototype/index.html` | 产品 | 可交互产品原型（G1；主路径+异常）；无 UI 时 `uiRequired=false` + `uiNoneReason` |
| `prototype/shared/ui-kit/` | 共享（模板） | Music 风亮/暗双主题（`THEME.md`）+ `showcase.html`；`data-uk-theme` |
| `spec.yaml` | 产品 | 全流程机器事实源与 G1/`seal`：必含 `UJ*`/`FR*`/`NFR*`/`E*`/`A*`；`S*` 可选；`uiRequired` |
| `ux.yaml` | 交互视觉 | G2：必填 `interactionRules`；可选 `visual`/`motion`；验收映射；Pencil/Figma→`artifacts`；或 `skip` |
| `prototype/ux/` | 交互视觉 | 可交互 UX HTML（规则+视觉精修；须引 ui-kit；与产品原型分工见 UX 技能） |
| `tech.md` / `tech-spec.md` / KD·NFR·接口·库表·埋点 | 架构师 | 人读：严格按 `templates/feature/tech.md` 等；展开件 `templates/design/` |
| `tech.yaml` | 架构师 | 给 AI/门禁：`aiConstraints`、`keyDesigns`、`interfaces`、`diagrams[]` |
| `tasks.md` | 主控/架构 | 人读拆解：按 `templates/feature/tasks.md`；机器件仍为 `tasks.yaml` |
| `diagrams/*` | 架构师 | [Archify](https://github.com/tt-a1i/archify) `finalize` 真出：`.html` + `.svg`（HTML 须含 generator/archify 溯源）；**并在 `tech.md` 用 `![](…svg)` 内嵌预览** |
| `tasks.yaml` | 主控 | G2T 之后的任务图：依赖、写集、验收、验证命令 |
| `review.yaml` | Review | `findings[]`：`blocking` / `dispute` / `nit` |
| `evidence.yaml` | 测试 | 每条验收的 command 与 `exitCode` |
| `deploy.yaml` | 部署 | 环境、命令、回滚；不代执行上线 |

大需求另有 `requirements/REQ-<序号>-<名称>-<YYYYMMDD>/`（如 `REQ-001-move-album-20220305`）：需求级 `prd.md`、`split.yaml`，可选 `architecture/`（Archify 草图，不进 G2T）。

`prd.md` 给人读，`spec.yaml` 给 Agent 与门禁，**同一套编号、一套事实源**（贯穿 UX/tech/dev/review/test/deploy）。禁止只交其中一份或另起平行口径。改规格必须同步 PRD 及受影响原型。
