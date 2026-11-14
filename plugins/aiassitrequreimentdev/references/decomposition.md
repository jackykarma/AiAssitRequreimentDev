# 需求、feature 与 task

| 概念 | 含义 | 落盘 |
| --- | --- | --- |
| 需求 | 业务问题 / 史诗 | `requirements/<REQ-id>/`（需求级 PRD + `split.yaml`） |
| feature | 可 G4 的交付切片 | `features/<FEAT-id>/` |
| task | feature 内实现单元 | `tasks.yaml`，在该 feature **G2T 通过之后**由主控拆 |

一条需求 → **1..N 个 feature**。先有需求级 PRD，再决定拆几个。不要先建一堆空 feature 再补故事。

## feature 必须可独立交付

对本切片声明的 `A*`：可独立验收、可写证据、合入后不留下不可用半成品。它可以是整条需求里的一个上线批次，并允许 `dependsOnFeatures`。

它不是整条需求的零依赖大包，不是 `tasks.yaml` 里的任务，也不是写到一半的中间态。拆开后没有下游就完全不可用：合并回一个 feature，或仍拆但强制同一发布列车并写明依赖。

## 谁拆、何时拆

| 角色 | 职责 |
| --- | --- |
| 产品 | 主责。需求级 PRD 之后写 `split.yaml`（一个还是多个、范围与验收边界） |
| 主控 | 按 `split.yaml` 执行 `init`，写入 `requirementId` / `dependsOnFeatures`；多 feature 时向人确认 |
| 架构师 | 可建议技术耦合与发布依赖，不代替产品定业务切片 |
| 开发 / 测试 | 不拆 feature |

`tasks.yaml` 是 plan 阶段的任务 DAG，发生在该 feature 的 G2T 之后，与拆 feature 不是同一层。

顺序：澄清 → 需求级 PRD → 可选整需求架构草图 → `split.yaml` → 人确认（多 feature）→ 创建 feature → 各切片 PRD / 原型 / spec → 各自门禁（含各自 tech）。

小需求可不建 `requirements/`，直接一个 feature，其 `prd.md` 兼任两级。大需求禁止跳过需求级 PRD 直接开多个空 feature。

## 一个还是多个

默认少拆。同时满足则保持 1 个：验收必须一起上线才有业务意义、同一主导旅程与发布窗口、写集能划清、开放问题能在同一澄清周期闭合。

命中任一条则拆多：PRD 里有可独立上线的验收批次、不同角色或端可先后上线、跨域且节奏或风险不同、前半是探路后半依赖结论、开放问题分区明显。架构师指出强耦合必须同发：合并，或拆开仍强制同一发布列车。

写入 `split.yaml`：`decision`（`single`|`multi`）、`rationale`、`features[]`（id、标题、范围、建议 path、dependsOn）。`decision: multi` 时主控打断人确认。

## 过程中变更

| 变更 | 动作 |
| --- | --- |
| 尚未拆分 | 继续改需求级 PRD |
| 改某 feature 的验收 | 回该 feature 的 G1，重新 seal |
| 应多拆或应合并 | 更新 `split.yaml`；多拆则新开 feature；合并须人确认 |
| 范围外新目标 | 先改需求级 PRD，再并入现 feature 或新开 feature（可挂同一 requirementId） |

规格变化则门禁回退。feature 变大时回到需求级 PRD 与 `split.yaml` 重决策，不要在同一 feature 上无限追加 `A*`。
