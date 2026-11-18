# 门禁

实现：`aiassitrequreimentdev/gates.py`。主控代跑 `python <本插件>/scripts/aad.py check <feature目录> --gate <门禁>`（等价 `python -m aiassitrequreimentdev check`）。通过后加 `--accept` 写入该门禁 `accepted` 并推进 `stage`（G1 的 `--accept` 等同 seal）。不要手改 `gates.*.accepted` 绕过检查器。

`path`：`full` | `light` | `light-auto`，且须 `pathConfirmed`。`gates.*` 取 `pending` 或 `accepted`；检查失败保持 `pending`。`light` 与 `light-auto` 同属轻量族（单 `affected`、单任务、可无 ux）。

| 门禁 | 主要条件 |
| --- | --- |
| G0 | `path` 为 full / light / light-auto；**`pathConfirmed=true`**；轻量族的 `affected` 恰好一项 |
| G1 | `UJ*`/`FR*`/`NFR*`/`S*`/`E*`/`A*` 形状合法（NFR/E 可声明无）；`openQuestions` 为空。**有 UI**：可交互 `prototype/index.html`。**无 UI**：`uiRequired=false` 且 `uiNoneReason`。**light-auto** 另须 `uiRequired=false`。已接受则 `specHash` 与规格一致 |
| G2 | **`uiRequired=false`**：跳过 UX 精修（init 模板 `ux.yaml` 不挡门禁；若显式 `skip: true` 须写 `reason`）。有 UI：须 `interactionRules` + `visual.baseline`。`projectStyle.locked` 时默认项目自有风格（偏离须 notes）；否则 `ui-kit`\|`painless`\|`midoo`\|`custom`。可交互 `prototype/ux/`（注册/项目 kit 须引对应前缀/path；或 `skip`）。轻量族可无 ux 文件，视为 skip |
| G2T | **薄** `tech.md` + `tech-spec.md` + `tech.yaml`（交付落点；整册在 REQ Epic Design）。`summary`、`aiConstraints`、`keyDesigns`、`interfaces`、`diagrams`（或 `architectureLayerGaps` 引 Epic）。**full** 强制 tech.md `###` 4.1/4.2，且 diagrams 含 workflow+sequence+class。Archify html+png；tech.md 内嵌 png。`storiesEnabled=true` 时校验 Story。`acceptance` 全覆盖 |
| G3 | 任务无环、写集不相交；轻量族仅一个任务。主控不得手写 `accepted` 盖过 `TASK_CYCLE` / `TASK_SCOPE_OVERLAP` |
| GR | 无未关闭 `blocking`；无未裁决 `dispute`。`nit` 不挡门禁 |
| G4 | `evidence` 覆盖全部验收且 `exitCode` 为 0，并且 GR 结构通过 |
| GD | `deploy.yaml` 含 `environment`、`commands`、`rollback` |

G1 已接受后改 `spec.yaml`：先记 **C3** 到 `change.yaml`，再将 `gates.G1` 退回 `pending`，同步 PRD 与受影响原型，再 `seal`。检查器用 `specHash` 发现未经退回的修改。UX/技术变更见 `change-control.md`（C2/C1）。

`check-req`（需求目录）：`split.yaml` + `architecture/`。`architecture.md` 须对齐 Epic Design 模板的全部 `##` 与关键 `###`（如 4.1–4.4、5.1–5.4、6.1–6.2、7.1–7.2…）；§六～§十一 禁止只写一行摘要（须表格 / 清单结构，`ARCH_MD_THIN`）。**§八～§十一 详表强制独立落盘** `nfr.md` / `interface-design.md` / `database-design.md` / `analytics-tracking.md`（标题对齐 `templates/design/`，`ARCH_EXPAND_*`）；对应章须引用相对路径。L0/L1（及协作流程图）须为 Archify 真图 html+png。
