---
name: specforge-tech
description: 技术方案 Agent。架构师与 AI 共写 tech.md + tech.yaml：架构图（可选）、变更文件路径、选型、风险、快稳省、数据设计、埋点与验收落点。用户要技术方案、接口/库表设计或 G2T 时使用。
---

# 技术方案

只写当前 feature 的 `tech.md`（给人）与 `tech.yaml`（给门禁/Agent）。不改规格、视觉与源码，不新增验收编号。

确认 `state.actorRole` 为 `architect`（或主控已 adopt 架构师SE）。先读 `BOARD.md`、`prd.md`、`prototype/`、`spec.yaml`。确认 G1 已就绪，G2 已通过或已 skip。再写方案。

## 必含章节（缺一不可）

| 章节 | 文件落点 | 说明 |
| --- | --- | --- |
| 架构图 | `architectureDiagram` + `tech.md` §2 | **可选**；有图则 `included: true` 且 `ref` 非空 |
| 变更文件 | `changedFiles` | 至少一条；`path` + `action`（add/modify/delete） |
| 技术方案选型 | `techChoices` | 至少一条；`topic` / `decision` / `rationale` |
| 技术风险点 | `risks` | 有则填 `id/description/impact/mitigation`；无则填 `risksNoneReason` |
| 快稳省 | `performancePower` | `performance` / `stability` / `power` 各写 `assessment` + `mitigations` |
| 数据设计 | `dataDesign` | 涉及则 `involved: true` 且 tables 或 models 非空；否则 `noneReason` |
| 埋点 | `tracking` | 产品埋点 `product` + 技术埋点 `technical`；都空则 `noneReason` |

`tech.md` 用同样章节写给人看的叙述，与 `tech.yaml` 同口径。

## 验收落点

`acceptance` 恰好覆盖每个 `A*` 一次。每项含：

- `architecture`
- `interface`
- `data`
- `failureRecovery`
- `constraints`：modus 路径列表

高风险写入 `risks`，供主控打断。

## 结束

```bash
python -m specforge check <feature 目录> --gate G2T
```
