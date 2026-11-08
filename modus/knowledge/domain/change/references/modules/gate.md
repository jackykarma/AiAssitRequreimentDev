# 门禁模块

实现：`specforge/gates.py`。

| 门禁 | 主要条件 |
| --- | --- |
| G0 | `path` 为 full/light；light 的 affected 恰好一项 |
| G1 | spec 字段齐、openQuestions 空、验收可执行；已接受则哈希一致 |
| G2 | ux 覆盖需 UI 的验收，或 `skip: true`；light 可无 ux 文件视为 skip |
| G2T | tech.md 存在；tech.yaml 含变更文件/选型/风险/快稳省/数据设计/埋点；验收落点全覆盖 |
| G3 | 任务无环、写集不交；light 仅一任务 |
| GR | 无未关闭 blocking；无未裁决 dispute |
| G4 | evidence 覆盖验收且 exitCode=0；且 GR 结构通过 |
| GD | deploy 含 environment、commands、rollback |
