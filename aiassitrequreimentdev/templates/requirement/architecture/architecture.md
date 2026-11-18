# 需求级技术方案（Epic Design）：REQ-[序号]-[kebab名称]-[YYYYMMDD]

> **定位**：整条需求的**技术方案总册**（对人评审 + 约束各 Feature / Story）。结构对齐 AISDD `epic-design`，落盘于本目录。  
> **不对 G4 交付负责**；可执行验收在各 `features/*/spec.yaml`。  
> **下游**：Feature 写**薄** `tech.md`（交付落点 + 增量）；复杂/并行落码写 `stories/ST-*/story-tech.md`。  
> **绘图**：[Archify](https://github.com/tt-a1i/archify) `finalize` → `.html` + `.png`；正文用 `![](…png)` 内嵌（禁止仅列路径；禁止 svg 作合同预览）。  
> **展开件**：KD / NFR / 接口 / 库表 / 埋点可复制 `templates/design/` 到本目录或 Owner Feature。  
> **机器件**：`architecture.yaml`（`check-req`）。

**Requirement**：REQ-[序号]-[kebab名称]-[YYYYMMDD]  
**设计 Version**：v0.1.0  
**日期**：[YYYY-MM-DD]

**本需求设计文件组成**：

| 文件 / 目录 | 对应章节 | 内容 |
| --- | --- | --- |
| `architecture.md`（本文件） | 全部 | Epic 级技术方案总览与索引 |
| `architecture.yaml` | 门禁 / Agent | diagrams、contracts、risks、features 追溯 |
| `diagrams/` | §四 / §五 等 | Archify html+png |
| `key-func-design/KD_*_*.md`（按需） | §七 | 跨 Feature 或整需求级 KD |
| `nfr.md` / `interface-design.md` 等（按需） | §八～§十一 | 详表；本节保留摘要 + 链接 |
| 各 Feature `stories/ST-*/` | §十二 / §十三 | Story 详细设计（挂在 Feature 下） |

---

## 变更记录（增量变更）

| 版本 | 日期 | 变更范围（REQ/Feature/Story） | 摘要 | 影响模块 | 是否回滚设计 |
| --- | --- | --- | --- | --- | --- |
| v0.1.0 | [YYYY-MM-DD] | REQ | 初版 | — | 否 |

---

## 设计前置检查

### 前置检查清单

- [ ] 已读需求级 `prd.md`、`split.yaml`（可同步定稿）
- [ ] 跨 Feature 共享能力已明确 Owner Feature
- [ ] 已对照现有工程代码校准模块边界
- [ ] P0 验收总览在后续架构 / KD / Story 中有覆盖策略

### 跨 Feature 共享能力登记

| 共享能力 | Owner Feature | 消费方 | 设计/契约位置 |
| --- | --- | --- | --- |
| … | FEAT-… | FEAT-… | 本文 §五 / Owner tech |

### P0 覆盖快照（与各 Feature spec 对照）

| Feature | 验收/场景 | 覆盖的设计章节/图 | 状态 |
| --- | --- | --- | --- |
| FEAT-… | A1 / … | §七 KD-… / §五 | 已覆盖 / 未覆盖 |

### 前置检查结论

- **日期** / **结论**：通过 / 阻塞（原因）

---

## 一、简介

### 1.1 目的和对象

| 项 | 内容 |
| --- | --- |
| 阅读对象 | 设计 / 开发 / 测试 / 评审 |
| 文档目的 | [一句话：本需求技术方案用途] |

### 1.2 范围

| 来源 | 相对路径 | 要点 |
| --- | --- | --- |
| 需求 PRD | [`../prd.md`](../prd.md) | In/Out 摘要 |
| 拆分 | [`../split.yaml`](../split.yaml) | single / multi |
| UX（若有） | 各 Feature `prototype/ux/` | 摘要或 N/A |

---

## 二、需求概述

### 2.1 需求背景

| 来源 | 要点 |
| --- | --- |
| PRD | [一行或「见原文」] |

### 2.2 需求范围及限制（按 Feature 索引）

| Feature ID | In Scope 摘要 | Out of Scope 摘要 | 关键 NFR |
| --- | --- | --- | --- |
| FEAT-… | … | … | … |

> 禁止在此复述各 Feature FR/NFR/A\* 全文。

---

## 三、领域模型

### 3.1 领域概念

> 统一命名权威；只写本需求涉及或新引入的概念。

### 3.2 领域概念词汇表（必须）

| 概念（中文） | 名称（英文/代码） | 定义 | 关键属性/状态 | 不变量 | 关联概念 |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

### 3.3 概念关系图（推荐，可选）

> 业务概念关系（非技术类图）。简单 CRUD 可写 N/A。

![领域概念关系](diagrams/PLACEHOLDER.domain.png)

---

## 四、零层架构（L0）

### 4.1 边界说明

- **需求边界**：[本需求内 / 复用现有]
- **主要子系统**：[高层能力块，可与 Feature 对应]

### 4.2 零层架构图（必须）

![L0 架构图](diagrams/PLACEHOLDER.L0.architecture.png)

### 4.3 架构设计说明（必须）

- **边界与职责**：…
- **分层与依赖方向**：…
- **关键数据流**：…
- **外部依赖策略**：…
- **可演进性**：…

### 4.4 外部依赖清单

| 依赖项 | 类型 | 能力 | 通信 | 故障模式 | 策略 |
| --- | --- | --- | --- | --- | --- |
| … | 服务/OS/模块 | … | … | … | … |

无则 N/A。

---

## 五、一层架构（L1）

### 5.1 一层框架图（必须）

![L1 架构图](diagrams/PLACEHOLDER.L1.architecture.png)

> 图上须能追溯各 Feature 归属模块（与 `split.yaml` 一致）。

### 5.2 组件清单与职责（必须）

| 模块/组件 | 职责 | 归属 Feature | 本需求改动 |
| --- | --- | --- | --- |
| … | … | FEAT-… | 新增 / 修改 / 无 |

### 5.3 组件协作流程图（必须）

![主路径协作](diagrams/PLACEHOLDER.overview.workflow.png)

### 5.4 技术方案选型

| 决策点 | 候选 | 选择 | 理由 |
| --- | --- | --- | --- |
| … | A / B | … | … |

---

## 六、技术风险与边界场景

### 6.1 技术风险与消解策略（绑定 Feature / Story）

| ID | 风险 | 影响 | 落在 Feature / Story | 对策 |
| --- | --- | --- | --- | --- |
| RISK-1 | … | … | FEAT-… / ST-… | … |

无则写明，并在 `architecture.yaml` → `risksNoneReason`。

### 6.2 边界与异常场景枚举

| 场景 | 类别 | 对策落点 |
| --- | --- | --- |
| … | 数据/状态/生命周期/并发/用户 | §七 / Feature E* |

---

## 七、关键功能与疑难点/亮点设计

### 7.1 关键设计清单

| KD | 名称 | 类型 | 前置 KD | 影响 Feature | 文件 |
| --- | --- | --- | --- | --- | --- |
| KD-001 | … | 疑难/亮点 | — | FEAT-… | `./key-func-design/KD_001_….md` |

### 7.2 详细设计引用

> 各 KD 独立文件须含：核心方案、关键类图、核心时序（Archify）；模板见 `templates/design/key-design-kd.md`。  
> 无需求级 KD 时写「无」并填 `keyDesignsNoneReason`；切片内 KD 可只出现在 Feature 薄 tech。

---

## 八、技术评估（NFR）

> 必须量化；详表可展开本目录 `nfr.md`（`templates/design/nfr.md`）。本节保留结论表。

| 维度 | 结论 / 预算 | 缓解 | 详表 |
| --- | --- | --- | --- |
| 性能 | … | … | ./nfr.md 或 N/A |
| 稳定性 | … | … | |
| 功耗 | … | … | |
| 其它 | … | … | |

---

## 九、接口设计

> 跨 Feature / 对外契约摘要；字段级详表 → `interface-design.md` 或 Owner Feature。

| ID | 方向 | 类型 | 提供方 | 消费方 | 摘要 | 冻结时机 |
| --- | --- | --- | --- | --- | --- | --- |
| CTR-1 / IF-1 | provided/consumed | api/event/… | FEAT-… | FEAT-… | … | 先发 G2T 前 |

无则 N/A + `contractsNoneReason`。

---

## 十、数据库设计

> 摘要 + 链接；详表 → `database-design.md`（`templates/design/database.md`）。

| 存储 | 变更 | 目的 | Owner Feature |
| --- | --- | --- | --- |
| … | add/alter/none | … | FEAT-… |

不涉及则 N/A。

---

## 十一、埋点技术方案

> 摘要 + 链接；详表 → `analytics-tracking.md`。

| 事件 | 触发 | 关键字段 | Owner |
| --- | --- | --- | --- |
| … | … | … | FEAT-… |

无则 N/A。

---

## 十二、Feature 与 Story 拆解索引

> **Feature = 交付单元（对 G4 负责）；Story = 技术实现/并行（不对独立交付负责）。**  
> 业务拆分以 `split.yaml` 为准；此处补技术并行视角。

### 12.1 拆解策略与约束

- 默认少拆 Story；触发条件见 `templates/story/README.md`
- Story 不得自造交付验收；只引用 Feature `A*`

### 12.2 Feature 列表（与 split 对齐）

| Feature | 范围摘要 | dependsOn | 建议 path | 是否启用 Story |
| --- | --- | --- | --- | --- |
| FEAT-… | … | — | full | 否 / 是 |

### 12.3 Story 列表（按 Feature 分组，可选）

| Story | 所属 Feature | 目的 | 覆盖 A* | 并行组 |
| --- | --- | --- | --- | --- |
| ST-… | FEAT-… | … | A1 | G1 |

无 Story 时整表写「本需求不启用 Story；细节在各 Feature 薄 tech / tasks」。

### 12.4 Story 依赖与并行度

> 推荐：依赖图或表格；写集相交的 Story 不得并行。

### 12.5 Feature → 设计覆盖矩阵

| Feature | Epic 章节/KD | Story（若有） | Feature 薄 tech |
| --- | --- | --- | --- |
| FEAT-… | §五 / KD-001 | ST-… | features/…/tech.md |

---

## 十三、Story 详细设计索引

> 正文在各 `features/<FEAT>/stories/ST-*/story-tech.md`（模板 `templates/story/`）。本节只做总索引。

### 13.1 索引表

| Story | 路径 | 关联 KD | 状态 |
| --- | --- | --- | --- |
| ST-… | `../../features/…/stories/ST-…/story-tech.md` | KD-… | planned/ready/done |

### 13.2 依赖总览

> 与各 Feature `stories.yaml` 一致。

### 13.3 覆盖度检查

- [ ] 每个启用 Story 的 `coversAcceptance` ⊆ 所属 Feature `A*`
- [ ] 无 Story 目录下的 `evidence.yaml`（G4 只认 Feature）

---

## 附录：与 Feature tech / Story / tasks 的对应关系

| 层级 | 文档 | 职责 |
| --- | --- | --- |
| 本文（Epic Design） | `architecture.md` | 整需求方案；`check-req` |
| Feature 薄 tech | `features/*/tech.md` + `tech.yaml` | 本刀交付落点 + 增量；G2T |
| Story | `stories/ST-*/story-tech.md` | 并行落码细化 |
| Task | `tasks.yaml` | 写集与验证；可挂 `storyId` |
