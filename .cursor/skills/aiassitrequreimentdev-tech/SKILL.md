---
name: aiassitrequreimentdev-tech
description: 技术方案 Agent。共写 tech.md（人审）+ tech.yaml（AI/门禁）：aiConstraints、关键设计、L0/L1 架构图、可多张流程/时序/类图（Archify html+svg）、接口、变更与验收落点。用户要技术方案或 G2T 时使用。
---

# 技术方案

只写当前 feature 的 `tech.md`、`tech.yaml`，以及 `diagrams/` 下 Archify 的 `.html`/`.svg`。不改规格、视觉与业务源码，不新增验收编号。

确认 `state.actorRole` 为 `architect`。先读 `BOARD.md`、`prd.md`、`prototype/`、`spec.yaml`；有 `requirementId` 时再读需求级 PRD / `architecture/` 与同需求其它 tech。G1 就绪且 G2 通过或 skip 后再写。

## 双受众

| 受众 | 读什么 | 目的 |
| --- | --- | --- |
| 人 | `tech.md` + 图 | 一页纸、L0/L1、关键设计、多图分范围审阅 |
| AI / 门禁 | `tech.yaml` | 遵守 `aiConstraints` 与每条 `keyDesigns.mustFollow` / `pitfalls` |

## 架构分层与多图

| 规则 | 说明 |
| --- | --- |
| 0 层 | 系统/上下文：外部系统、其它 feature、信任边界 |
| 1 层 | 本 feature 内部模块/组件与本切片改动 |
| 成对 | 有 architecture 图时须同时有 layer 0 与 1，或写 `architectureLayerGaps` |
| 多张 | 同一 `type` 可多条；每条必填 `scope`，feature 大时按子系统/场景拆分 |

流程 / 时序 / 类图同理：必要时多张，禁止一张塞满。

## 关键设计

对照 `tech.md` §3.1 写入 `keyDesigns`。每条至少：`judgment`、`problem`、`decision`、`coreScheme`（链路闭环）、`mustFollow`≥1、`pitfalls`。无则 `keyDesignsNoneReason`。

## 接口 / NFR / 数据 / 埋点

- `interfaces`：`direction` provided|consumed，及 `request`/`response`（`errors` 可选列表）
- `nfr`：performance/stability/power 必填；memory/security/compatibility/romSize/algorithm 按需 `involved`
- `dataDesign.tables`：涉及时 `name`/`change`/`purpose`；`fields[]` 有则校验 name/type/description
- `tracking`：event+trigger；`fields[]` 有则校验 id/description/type  
人读详版模板：`aiassitrequreimentdev/templates/design/`（按需复制到 feature 目录展开）。

## G2T 必含摘要

`summary`、`aiConstraints`、`keyDesigns`、`interfaces`、`diagrams`、`nfr`、变更/选型/风险、数据/埋点、`acceptance` 全覆盖 `A*`。

```bash
python <本插件>/scripts/aad.py check <feature 目录> --gate G2T
```

结束后请主控登记本阶段 token（`--role architect --stage tech`），见 lead 技能「Token 用量」。
