# 宪法要点

对话编排 + 规格门禁。角色技能与检查器服从下列规则。本仓全文见 `constitution.md`；装到业务仓时以本摘要为最小集。

1. 主控在对话内弹选项选角色（含产品 / UX / 架构 / 开发 / Review / 测试 / 部署）、确认路径 `full` / `light` / `light-auto`，写入 `actorRole` 与 `path` 后派技能；HTML picker 仅备用。工件与 CLI 由主控代跑。`light-auto` 仅无 UI 小需求：G1 seal 后连跑至 G4，部署仍打断。需求拆分用 `check-req` 校验 `split.yaml`。
2. 产物共仓于 `features/<id>/`，索引为 `BOARD.md`。**角色只写自己的文件**，其余只读。一条需求可对应 1..N 个 feature。
3. **有模板必须严格按模板**：`templates/` 已有底稿的人读产物（prd / architecture / tech / tech-spec / tasks / Story·design 展开件等）须与模板章节结构、标题原文、必填小节与填写要求完全对齐；禁止自创精简版、改名跳节、一行摘要冒充。无独立 md 模板的机器件按其 schema/技能字段表填写。
4. 产品交付：`prd.md`、可交互 `prototype/index.html`（无 UI 则 `uiRequired=false` + `uiNoneReason`）、`spec.yaml`。输入不完整先 brainstorm/grill。prd 与 spec 同源同口径。禁止用对话草稿代替正式工件。
5. 一个 feature 只有一份机器规格 `spec.yaml`（`UJ*`/`FR*`/`NFR*`/`S*`/`E*`/`A*`）。其他角色按编号引用，不改写规格正文。
6. **G1 冻结：`check G1` 通过后由主控 `seal`（写 `specHash` 并置 `gates.G1=accepted`）。** 之后改 `spec.yaml` 必须先记变更、把 `gates.G1` 改回 `pending` 并重新 `seal`。检查器用 `specHash` 发现未经退回的修改。改规格须同步 PRD 及受影响原型。见 `change-control.md`。不要手改其它门禁的 `accepted`。
7. 交互视觉写 `ux.yaml` + 可交互 `prototype/ux/`（或 `skip`）。技术方案写 `tech.md` + `tech.yaml`（`aiConstraints` + `keyDesigns`，开发必遵）。架构/流程/时序/类图须用 [Archify](https://github.com/tt-a1i/archify) `finalize` 真出图（禁止手写/Mermaid 冒充），只留 html/png。
8. 验收必须能被一条命令判断。`given` / `when` / `then` / `verify` 都要有内容。**通过与否看命令退出码**（记入 `evidence.yaml` 的 `exitCode`）。`verify`/证据命令禁止空转成功；G1 seal 前人过 A* 清单（见产品技能）。
9. `nonGoals` 里的事项开发不得实现。主控直接拒绝。
10. 知识与源码冲突时以当前源码为准。规格与技术方案只保存链接。长期事实在业务仓 `modus/knowledge/`（可选）；插件内以本目录为准。
11. 写集相交的任务不得并行。检查器报告 `TASK_SCOPE_OVERLAP` 时，合并任务或改成 `blockedBy`。
12. 测试与开发不共享对话。测试开工前 GR 必须通过。
13. Review：`blocking` 必须修复并复审，清零前禁止测试；`dispute` 必须等人裁决；`nit` 不挡门禁。Review 不直接改业务代码。
14. 人打断含：未选角色、路径未确认、产品未决、视觉路径（项目锁定则确认遵循，否则 catalog 三选一；可 custom）、视觉选型细节、技术高风险、Review 争议、测试卡死、部署确认。结构问题只由检查器报告。
15. 部署只写清单与命令，不代执行上线；上线前必须打断确认。
16. G3 只由检查器判断。主控不得把 `G3` 写成 `accepted` 来盖过 `TASK_CYCLE` 或 `TASK_SCOPE_OVERLAP`。
17. Feature 对本切片 `A*` **对交付负责**（可 G4）。大需求须需求级 PRD + **整需求 architecture**（`check-req`）再 `split.yaml`。可选 Story 只服务并行实现，不对独立交付负责。`tasks.yaml` 更晚才拆。细则见 `decomposition.md`。
