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
| `ux.yaml` | 交互视觉 | G2：必填 `interactionRules` + `visual.baseline`（catalog：`ui-kit`\|`painless`\|`midoo`\|`custom`…）；可选 `motion`；验收映射；Pencil/Figma→`artifacts`；或 `skip` |
| `research/ui-kits/catalog.yaml` | 共享注册 | UX 人选视觉基线目录；apk-uikit 新 kit 须登记 id/path/prefix |
| `research/ui-kits/MOTION.md` | 共享合同 | 各 kit 动效/特效令牌与行为标准 |
| `prototype/ux/` | 交互视觉 | 可交互 UX HTML（规则+视觉；`ui-kit` 须引 kit，`custom` 可自建；与产品原型分工见 UX 技能） |
| `tech.md` / `tech-spec.md` / KD·NFR·接口·库表·埋点 | 架构师 | 人读：feature 级 `templates/feature/tech.md` + `tech-spec.md`；展开件 `templates/design/` |
| `tech.yaml` | 架构师 | 给 AI/门禁：`aiConstraints`、`keyDesigns`、`interfaces`、`diagrams[]` |
| `tasks.md` | 主控/架构 | 人读拆解：按 `templates/feature/tasks.md`；机器件仍为 `tasks.yaml` |
| `diagrams/*` | 架构师 | [Archify](https://github.com/tt-a1i/archify) `finalize` 真出：`.html` + `.png`（HTML 须含 generator/archify 溯源；**禁止 svg 预览合同**）；**并在 `tech.md` 用 `![](…png)` 内嵌预览** |
| `tasks.yaml` | 主控 | G2T 之后的任务图：依赖、写集、验收、验证命令 |
| `change.yaml` | 主控 | 变更台账：发起人、原因、级别、影响文件/门禁、时间、状态 |
| `review.yaml` | Review | `findings[]`：`blocking` / `dispute` / `nit` |
| `evidence.yaml` | 测试 | 每条验收的 command 与 `exitCode`；command 须对应 `spec.verify`，禁止空转成功 |
| `deploy.yaml` | 部署 | 环境、命令、回滚；不代执行上线 |

大需求另有 `requirements/REQ-…/`：`prd.md`、`split.yaml`、**`architecture/` Epic Design**（对齐 AISDD epic-design；`check-req` 硬门槛）。  
Feature **薄** `tech.md`（交付落点 + 相对 Epic 增量；G2T）。可选 `stories.yaml` + `stories/ST-*/story-tech.md`。`tasks.yaml` 可带 `storyId`。

`prd.md` 给人读，`spec.yaml` 给 Agent 与门禁，**同一套编号、一套事实源**（贯穿 UX/tech/dev/review/test/deploy）。禁止只交其中一份或另起平行口径。改规格必须同步 PRD 及受影响原型。
