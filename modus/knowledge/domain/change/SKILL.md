# Feature 交付流程

一条**需求**拆成一个或多个 **feature**（`features/<id>/`），再走到部署清单。本领域不包含具体业务规则。

## 进入

| 要回答的问题 | 文件 |
| --- | --- |
| 阶段怎么迁移，哪一道门把任务堵住 | [references/state_machine.md](references/state_machine.md) |
| 全量还是轻量 | [references/paths.md](references/paths.md) |
| 大需求如何拆、过程中怎么改 | [references/decomposition.md](references/decomposition.md) |
| 绘图（Archify，仅 html/svg） | [references/diagrams.md](references/diagrams.md) |
| 设计展开模板（NFR/接口/库表/埋点/KD） | `aiassitrequreimentdev/templates/design/` |
| 启动选哪个角色 | [references/roles.md](references/roles.md) |
| 编号、哈希、写集、工件规则 | [references/rule.md](references/rule.md) |
| 打断策略何时停下来问人 | [references/interrupt.md](references/interrupt.md) |
| 各 yaml 字段合同 | [references/artifacts.md](references/artifacts.md) |
| 检查器读哪些字段 | [references/modules/gate.md](references/modules/gate.md) |
| 命令怎么调用 | [references/api.md](references/api.md) |
| 主控 / 产品 / 视觉 / 技术 / Review / 测试 / 部署 | [references/modules/](references/modules/) |

## 场景

全路径：意图 → G0 → 规格 G1 → 交互视觉 G2 → 技术方案 G2T → 任务 G3 → 实现 → Review GR → 证据 G4 → 部署清单 GD → 知识回写 → done。

轻路径：G0 确认只影响一个模块；可跳过 ux；tech 仍要覆盖验收；一个任务；Review 与证据同样适用。
