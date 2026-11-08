# 变更状态

实现锚点：`aiassitrequreimentdev/templates/feature/state.json` 的 `stage` 与 `gates`。

| 阶段 | 进入条件 | 离开条件 |
| --- | --- | --- |
| intake | feature 目录已创建；角色与路径已确认 | 进入 clarify（大需求若需先拆多 change，在此划切片） |
| clarify | 产品开始 grill | G0 与 G1 结构通过；人仅在未决问题时介入；G1 后 `seal` |
| ux | G1 已接受 | G2 通过；无 UI 时 `ux.skip=true` 可跳过 |
| tech | G2 通过或已跳过 | G2T 通过；高风险项打断确认后继续 |
| plan | G2T 通过 | G3 无违反项 |
| implement | G3 无违反项 | 任务补丁完成；或从 Review `blocking` 打回修复 |
| review | 实现完成或复审 | GR 通过：无未关闭 blocking、无未裁决 dispute |
| verify | GR 通过 | G4 通过；失败超重试则打断 |
| release | G4 通过 | GD 通过且人确认部署窗口 |
| done | GD 确认 | 若规则/状态/契约变了，修订对应知识 |

`gates.*` 取值 `pending` 或 `accepted`。检查失败保持 `pending`。

从 review/`blocking` 或用户要求改代码的 dispute 退回：`stage` 设为 `implement`，修复后必须再跑 Review。

规格/验收变更：回 `clarify`，`G1` 改 `pending` 并重 `seal`；受影响的后续门禁按 [decomposition.md](decomposition.md) 重置。范围外新目标：新开 change，不在本目录无限追加验收。
