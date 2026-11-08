# 需求、feature 拆分与过程变更

## 名词

| 概念 | 含义 | 落盘 |
| --- | --- | --- |
| **需求** | 业务要解决的问题 / 史诗 | `requirements/<REQ-id>/`（需求级 PRD + 拆分决策） |
| **feature** | 可关门禁、可合并的交付切片 | `features/<FEAT-id>/` |
| **task** | feature 内实现单元 | `features/.../tasks.yaml` |

一条需求 → **1..N 个 feature**。先有需求级认知与 PRD，再决定拆几个 feature；**不是**先建一堆空 feature 目录再补故事。

## 谁来拆 feature

| 角色 | 职责 |
| --- | --- |
| **产品（PM + `aiassitrequreimentdev-product`）** | **主责**：写需求级 PRD，提出「一个还是多个」及每个 feature 的范围/验收边界，写入 `split.yaml` |
| **主控（`aiassitrequreimentdev-lead`）** | 按 `split.yaml` 执行 `init` 各 feature、写入 `requirementId` / `dependsOnFeatures`；多 feature 时向人确认拆分方案 |
| **架构师SE** | **顾问**：可对技术耦合、发布依赖提出合并/拆开建议，不代替产品定业务切片 |
| **开发 / 测试** | 不拆 feature；只在既定 feature 内改写集 / 写证据 |

`tasks.yaml` 的任务拆解是 **plan 阶段主控** 的事，发生在该 feature 的 G2T 之后，与「拆 feature」不是同一层。

## 顺序（先 PRD，后拆 feature）

```text
需求对话 / grill
    → 需求级 PRD（requirements/<REQ>/prd.md）
    → 拆分决策（requirements/<REQ>/split.yaml）  ← 根据 PRD 决定 1 或 N
    → 人确认（多 feature 时）
    → 创建 features/FEAT-*，写入 requirementId
    → 每个 feature：切片 PRD + 原型 + spec.yaml → 各自门禁
```

**小需求捷径**：明显只需一个 feature 时，可不建 `requirements/`，直接 `features/FEAT-xxx/`，该目录的 `prd.md` 同时充当需求级与 feature 级 PRD；`state.requirementId` 可等于 feature id 或单独 REQ id。

**大需求**：禁止跳过需求级 PRD 直接开多个空 feature。

## 一个还是多个：如何决策

依据是 **需求级 PRD** 里的目标、范围、验收与依赖，用下面清单。默认偏 **少拆**：能一个 feature 交付就不要拆。

### 保持为 1 个 feature（同时满足）

- 验收必须一起上线才有业务意义（拆开会留下不可用半成品）
- 同一主导用户旅程 / 同一发布窗口
- 主要改动落在可协同的模块集合，任务写集能划清
- 开放问题可在同一澄清周期内闭合
- 预估可在约两周内走到 G4

### 拆成多个 feature（命中任一条就拆）

| 信号 | 怎么拆 |
| --- | --- |
| PRD 里存在可独立交付的验收批次 | 每批一个 feature |
| 不同用户角色/端可先后上线 | 按上线批次拆 |
| 跨业务域且节奏或风险不同 | 按域拆，用 `dependsOnFeatures` 串依赖 |
| 前半是探路/实验，后半依赖结论 | 先 FEAT-A，再开 FEAT-B |
| 单目录 PRD 已过大、开放问题分区明显 | 按闭合的问题簇拆 |
| 架构师指出强耦合必须同发 | **合并**回一个 feature，或拆但仍强制同一发布列车并写明依赖 |

决策结果写入 `requirements/<REQ>/split.yaml`，至少包含：`decision`（`single`|`multi`）、`rationale`、`features[]`（id、标题、范围、建议 path、dependsOn）。

## feature 内再拆什么

feature 已创建且该 feature 的 spec 冻结后，主控才写 `tasks.yaml`。那是实现任务 DAG，不是第二轮「拆需求」。

## 过程中变更

| 变更类型 | 动作 |
| --- | --- |
| 需求级 PRD 未拆分 | 继续改 `requirements/.../prd.md` |
| 已拆分，改某 feature 验收 | 回该 feature 的 G1 重 seal |
| 发现应多拆 / 应合并 | 更新 `split.yaml`；多拆则新开 feature；合并则迁移验收并废弃空 feature（人确认） |
| 范围外新目标 | 更新需求级 PRD，再决定并入现 feature 或新开 feature |

规格变 → 门禁回退。feature 变大 → 回到需求级 PRD 与 `split.yaml` 重决策，不要无限追加 `A*`。
