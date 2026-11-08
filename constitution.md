# 工程宪法

本仓库用对话编排 + 规格门禁多智能体做需求开发。角色技能、modus 知识库和门禁检查器都服从下面这些规则。

1. 启动流程必须先选择人角色（产品经理 / 架构师SE / 开发 / 测试 / 部署），再根据需求推荐并确认研发路径（`full` 全量 / `light` 轻量）。写入 `actorRole` 与已确认的 `path` 后再派对应技能。工件与 CLI 由 Agent 代跑。
2. 同一 feature 的产物共仓于 `features/<id>/`，以 `BOARD.md` 为共享索引。角色只写自己的文件，其余只读。一条**需求**可对应一个或多个 feature。
3. 产品阶段交付：`prd.md`（给人）、`prototype/`（给人）、`spec.yaml`（给 Agent 与门禁）。输入不完整时须先 brainstorm/grill 再出稿。须覆盖核心用户旅程、功能需求、非功能需求、主流程、异常与边界、验收标准；`prd` 与 `spec` 都要，同源同口径；禁止用对话草稿文件代替。
4. 一个 feature 只有一份机器规格：`features/<id>/spec.yaml`（`UJ*`/`FR*`/`NFR*`/`S*`/`E*`/`A*`）。其他 Agent 按编号引用，不改写规格正文。
5. G1 冻结后修改 `spec.yaml` 必须先把 `gates.G1` 改回 `pending` 并重新签字。检查器用 `specHash` 发现未经退回的修改。改规格须同步 PRD（及受影响原型）。
6. 交互视觉写 `ux.yaml`，技术方案写 `tech.yaml`。旧 `design.yaml` 退役。产品先出 HTML 原型；视觉精修由交互视觉承接（可从架构师路径加派）。
7. 验收必须能被一条命令判断。`given` / `when` / `then` / `verify` 都要有内容。
8. `nonGoals` 里的事项，开发工人不得实现。主控直接拒绝。
9. 知识库中的规则以当前源码为准。规格与技术方案只保存链接。长期事实只定义在 `modus/knowledge/`。
10. 写集相交的任务不得并行。检查器报告 `TASK_SCOPE_OVERLAP` 时，合并任务或改成 `blockedBy`。
11. 测试与开发不共享对话。通过与否看 `evidence.yaml` 的退出码。测试开工前 GR 必须通过。
12. Review：`blocking` 必须修复并复审，清零前禁止测试；`dispute` 必须等人裁决；`nit` 不挡门禁。Review 不直接改业务代码。
13. 人打断含：启动未选角色、路径未确认、产品未决、视觉选型、技术高风险、Review 争议、测试卡死、部署确认。结构问题只由检查器报告。
14. 部署一期只写清单与命令，不代执行上线；上线前必须打断确认。
15. G3 只由检查器判断，主控不得把 `G3` 写成 `accepted` 来盖过 `TASK_CYCLE` 或 `TASK_SCOPE_OVERLAP`。`constraint/` 与各域 `business/` 由人持有所有权。
16. 一个 feature 是可 G4 的交付切片：对本切片 `A*` 可独立验收与举证，合入后不留下不可用半成品；不等于整条需求的零依赖「完整大功能」，也不等于 `tasks.yaml` 任务。允许 `dependsOnFeatures`。拆 feature 由产品依据需求级 PRD 决策（`split.yaml`），主控创建目录；须在 PRD 之后。单 feature 内再用 `tasks.yaml` 拆任务。过程中改验收须回 G1 重 seal；范围外新目标开新 feature（可挂同一 requirementId）。细则见 `modus/knowledge/domain/change/references/decomposition.md`。
