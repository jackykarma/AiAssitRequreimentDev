# AiAssitRequreimentDev 总览

本知识库描述 AiAssitRequreimentDev 研发系统。业务项目接入时，在 `modus/knowledge/domain/` 下按 `_template/` 合同增加自己的领域，不要把业务规则写进 `domain/change/`。

## 怎么读

1. 先判断问题属于变更流程，还是某个业务领域。
2. 变更流程进入 [domain/change/SKILL.md](domain/change/SKILL.md)。
3. 底线在 [constraint/global-standard.md](constraint/global-standard.md) 与 [constraint/team-standard.md](constraint/team-standard.md)。
4. 读到规则后回到当前源码核对。流程实现锚点是 `aiassitrequreimentdev/gates.py`。

## 四层

| 层 | 所有者 | 留下的东西 |
| --- | --- | --- |
| 控制层 | 主控 Agent | `features/<id>/state.json` |
| 知识层 | 人持有约束与业务所有权；Agent 按规则修订 | `modus/knowledge/` |
| 变更层 | 阶段角色 | `spec` / `ux` / `tech` / `tasks` / `review` / `evidence` / `deploy` |
| 执行层 | 开发与测试工人 | 补丁、命令输出 |

## 运行单元

| 单元 | 路径 | 职责 |
| --- | --- | --- |
| 门禁检查 | `aiassitrequreimentdev/gates.py` | G0–G1、G2(ux)、G2T(tech)、G3、GR、G4、GD |
| 命令入口 | `aiassitrequreimentdev/__main__.py` | `init`、`check`、`seal`（由主控代跑） |
| 角色技能 | `.cursor/skills/aiassitrequreimentdev-*` | 约束每个 Agent 能写的文件 |
| feature 工件 | `features/<id>/` | 一个 feature 的冻结合同 |

架构说明在 `docs/architecture.md`。接入业务域见 [README.md](README.md)。
