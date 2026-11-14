# 门禁

实现：`aiassitrequreimentdev/gates.py`。主控代跑 `python <本插件>/scripts/aad.py check <feature目录> --gate <门禁>`（等价 `python -m aiassitrequreimentdev check`）。不要手改 `gates.*.accepted`。

`path`：`full` | `light`，且须 `pathConfirmed`。`gates.*` 取 `pending` 或 `accepted`；检查失败保持 `pending`。

| 门禁 | 主要条件 |
| --- | --- |
| G0 | `path` 为 full 或 light；light 的 `affected` 恰好一项 |
| G1 | `UJ*`/`FR*`/`NFR*`/`S*`/`E*`/`A*` 形状合法（NFR/E 可声明无）；`openQuestions` 为空。**有 UI**：可交互 `prototype/index.html`。**无 UI**：`uiRequired=false` 且 `uiNoneReason`。已接受则 `specHash` 与规格一致 |
| G2 | ux 覆盖需 UI 的验收，且可交互 `prototype/ux/`（入口 `htmlPrototype.entry`，默认 `index.html`）；或 `skip: true` + `reason`。light 可无 ux 文件，视为 skip |
| G2T | `tech.md` + `tech.yaml`：`summary`、`aiConstraints`、`keyDesigns`（或 noneReason）、`interfaces`、`diagrams`（架构 layer 0+1，或 `architectureLayerGaps`；同类型可多张且须 `scope`）。含变更、选型、风险、快稳省、数据、埋点；`acceptance` 全覆盖 |
| G3 | 任务无环、写集不相交；light 仅一个任务。主控不得手写 `accepted` 盖过 `TASK_CYCLE` / `TASK_SCOPE_OVERLAP` |
| GR | 无未关闭 `blocking`；无未裁决 `dispute`。`nit` 不挡门禁 |
| G4 | `evidence` 覆盖全部验收且 `exitCode` 为 0，并且 GR 结构通过 |
| GD | `deploy.yaml` 含 `environment`、`commands`、`rollback` |

G1 已接受后改 `spec.yaml`：先将 `gates.G1` 退回 `pending`，同步 PRD 与受影响原型，再 `seal`。检查器用 `specHash` 发现未经退回的修改。
