# 门禁

实现：`aiassitrequreimentdev/gates.py`。主控代跑 `python <本插件>/scripts/aad.py check <feature目录> --gate <门禁>`（等价 `python -m aiassitrequreimentdev check`）。通过后加 `--accept` 写入该门禁 `accepted` 并推进 `stage`（G1 的 `--accept` 等同 seal）。不要手改 `gates.*.accepted` 绕过检查器。

`path`：`full` | `light` | `light-auto`，且须 `pathConfirmed`。`gates.*` 取 `pending` 或 `accepted`；检查失败保持 `pending`。`light` 与 `light-auto` 同属轻量族（单 `affected`、单任务、可无 ux）。

| 门禁 | 主要条件 |
| --- | --- |
| G0 | `path` 为 full / light / light-auto；**`pathConfirmed=true`**；轻量族的 `affected` 恰好一项 |
| G1 | `UJ*`/`FR*`/`NFR*`/`S*`/`E*`/`A*` 形状合法（NFR/E 可声明无）；`openQuestions` 为空。**有 UI**：可交互 `prototype/index.html`。**无 UI**：`uiRequired=false` 且 `uiNoneReason`。**light-auto** 另须 `uiRequired=false`。已接受则 `specHash` 与规格一致 |
| G2 | **`uiRequired=false`**：跳过 UX 精修（init 模板 `ux.yaml` 不挡门禁；若显式 `skip: true` 须写 `reason`）。有 UI：须 `interactionRules` + `visual.baseline`（`ui-kit`\|`custom`）+ 可交互 `prototype/ux/`（或 `skip`）。轻量族可无 ux 文件，视为 skip |
| G2T | `tech.md` + `tech-spec.md` + `tech.yaml`（章节对齐 **feature 级**模板，非旧 EPIC/Story）。`summary`、`aiConstraints`、`keyDesigns`、`interfaces`、`diagrams`。架构 layer 0+1（或 gaps）。**full** 另强制 tech.md 三级标题 4.2/5.1/5.3，且 diagrams 含 workflow+sequence+class。**`tech.md` 用 `![](…svg)` 内嵌**。含变更、选型、风险、快稳省、数据、埋点；`acceptance` 全覆盖 |
| G3 | 任务无环、写集不相交；轻量族仅一个任务。主控不得手写 `accepted` 盖过 `TASK_CYCLE` / `TASK_SCOPE_OVERLAP` |
| GR | 无未关闭 `blocking`；无未裁决 `dispute`。`nit` 不挡门禁 |
| G4 | `evidence` 覆盖全部验收且 `exitCode` 为 0，并且 GR 结构通过 |
| GD | `deploy.yaml` 含 `environment`、`commands`、`rollback` |

G1 已接受后改 `spec.yaml`：先记 **C3** 到 `change.yaml`，再将 `gates.G1` 退回 `pending`，同步 PRD 与受影响原型，再 `seal`。检查器用 `specHash` 发现未经退回的修改。UX/技术变更见 `change-control.md`（C2/C1）。
