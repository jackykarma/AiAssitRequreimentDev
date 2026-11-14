# 宪法要点

对话编排 + 规格门禁。角色技能与检查器服从下列规则。本仓全文见 `constitution.md`；装到业务仓时以本摘要为最小集。

1. 先选人角色（产品 / 架构师SE / 开发 / 测试 / 部署），再确认路径 `full` 或 `light`，写入 `actorRole` 与已确认的 `path` 后派技能。工件与 CLI 由主控代跑。
2. 产物共仓于 `features/<id>/`，索引为 `BOARD.md`。**角色只写自己的文件**，其余只读。一条需求可对应 1..N 个 feature。
3. 产品交付：`prd.md`、可交互 `prototype/index.html`（无 UI 则 `uiRequired=false` + `uiNoneReason`）、`spec.yaml`。输入不完整先 brainstorm/grill。须覆盖旅程、功能、非功能、主流程、异常边界、验收；prd 与 spec 同源同口径。禁止用对话草稿代替。
4. 一个 feature 只有一份机器规格 `spec.yaml`（`UJ*`/`FR*`/`NFR*`/`S*`/`E*`/`A*`）。其他角色按编号引用，不改写规格正文。
5. **G1 冻结后改 `spec.yaml` 必须先把 `gates.G1` 改回 `pending` 并重新 `seal`。** 检查器用 `specHash` 发现未经退回的修改。改规格须同步 PRD 及受影响原型。不要手改 `gates.*.accepted`。
6. 交互视觉写 `ux.yaml` + 可交互 `prototype/ux/`（或 `skip`）。技术方案写 `tech.md` + `tech.yaml`（`aiConstraints` + `keyDesigns`，开发必遵）。绘图用 Archify，只留 html/svg。
7. 验收必须能被一条命令判断。`given` / `when` / `then` / `verify` 都要有内容。**通过与否看命令退出码**（记入 `evidence.yaml` 的 `exitCode`）。
8. `nonGoals` 里的事项开发不得实现。主控直接拒绝。
9. 知识与源码冲突时以当前源码为准。规格与技术方案只保存链接。长期事实在业务仓 `modus/knowledge/`（可选）；插件内以本目录为准。
10. 写集相交的任务不得并行。检查器报告 `TASK_SCOPE_OVERLAP` 时，合并任务或改成 `blockedBy`。
11. 测试与开发不共享对话。测试开工前 GR 必须通过。
12. Review：`blocking` 必须修复并复审，清零前禁止测试；`dispute` 必须等人裁决；`nit` 不挡门禁。Review 不直接改业务代码。
13. 人打断含：未选角色、路径未确认、产品未决、视觉选型、技术高风险、Review 争议、测试卡死、部署确认。结构问题只由检查器报告。
14. 部署只写清单与命令，不代执行上线；上线前必须打断确认。
15. G3 只由检查器判断。主控不得把 `G3` 写成 `accepted` 来盖过 `TASK_CYCLE` 或 `TASK_SCOPE_OVERLAP`。
16. 一个 feature 须对本切片 `A*` 可独立验收并走到 G4，不是半成品，也不等于整条需求的零依赖大包，也不等于 `tasks.yaml` 里的任务。允许 `dependsOnFeatures`。拆 feature 在需求级 PRD 之后（`split.yaml`）；feature 内 `tasks.yaml` 更晚才拆。过程中改验收须回 G1 重 seal；范围外新目标开新 feature。细则见 `decomposition.md`。
