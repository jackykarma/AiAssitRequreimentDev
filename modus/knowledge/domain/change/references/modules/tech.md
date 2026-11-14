# 技术方案模块

| 文件 | 受众 | 用途 |
| --- | --- | --- |
| `tech.md` | 人 | 一页纸、L0/L1、关键设计判定与正文、多图说明 |
| `tech.yaml` | AI + G2T | `aiConstraints`、`keyDesigns`、`diagrams`、接口与验收 |
| `diagrams/*.{html,svg}` | 人 | Archify 图 |

## 关键设计

`keyDesigns`：`cornerstone` / `highlight` / `difficulty`；必含 `coreScheme`（链路闭环叙述）。判定原则见 `tech.md` §3.1。

## 接口 / 数据 / 埋点 / NFR

`interfaces`（provided/consumed + request/response/errors）、`dataDesign.tables` 字段级、`tracking.*.fields`、`nfr`（快稳省必填，扩展按需）。人读详版：`aiassitrequreimentdev/templates/design/`。

## 图

- 架构：分 0 层 / 1 层；可各多张
- 流程 / 时序 / 类图：可多张，必填 `scope`
- 详见 [diagrams.md](../diagrams.md)
