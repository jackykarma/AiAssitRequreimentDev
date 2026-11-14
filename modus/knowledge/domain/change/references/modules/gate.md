# 门禁模块

实现：`aiassitrequreimentdev/gates.py`。

| 门禁 | 主要条件 |
| --- | --- |
| G0 | `path` 为 full/light；light 的 affected 恰好一项 |
| G1 | UJ/FR/NFR/S/E/A 齐备（NFR/E 可声明无）、openQuestions 空；有 UI 须可交互 `prototype/index.html`，无 UI 须 `uiRequired=false`+`uiNoneReason`；已接受则哈希一致 |
| G2 | ux 覆盖需 UI 的验收 + 可交互 `prototype/ux/`，或 `skip: true`；light 可无 ux 文件视为 skip |
| G2T | tech.md；tech.yaml 含 summary、aiConstraints、keyDesigns（或 noneReason）、interfaces、diagrams；architecture 须 layer 0+1 或 architectureLayerGaps；图可多张且须 scope；变更/选型/风险/快稳省/数据/埋点；acceptance 全覆盖 |
| G3 | 任务无环、写集不交；light 仅一任务 |
| GR | 无未关闭 blocking；无未裁决 dispute |
| G4 | evidence 覆盖验收且 exitCode=0；且 GR 结构通过 |
| GD | deploy 含 environment、commands、rollback |
