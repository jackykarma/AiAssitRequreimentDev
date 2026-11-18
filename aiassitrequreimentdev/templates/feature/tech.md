# 切片技术方案（薄合同）：FEAT-[序号]-[kebab名称]

> **定位**：本 **Feature 交付切片** 的技术落点合同（对人 + `tech.yaml` 门禁）。**对 G4 负责**。  
> **禁止**：把整需求 Epic Design 再抄一遍。整图 / 领域 / 跨切片 KD·NFR·接口总册在需求级 `architecture/architecture.md`。  
> **详细落码**：有并行/复杂实现时写 `stories/ST-*/story-tech.md`；无 Story 时本节「增量」须写到可开发。  
> **单 Feature 捷径**（无 `requirements/`）：本节须**兼任** Epic 关键结论（或在 §三声明「无 REQ，L0/L1 以本节为准」并出齐图）。  
> **绘图**：增量图用 Archify；引用 Epic 图时可内嵌副本或填 `architectureLayerGaps`。  
> **Lite**：仍保留下列全部 `##`；`full` 另须强制 `###`。

**Feature**：FEAT-[序号]-[kebab名称]  
**关联需求**：`requirementId` 或「单 feature 捷径」  
**Epic Design**：`requirements/…/architecture/architecture.md` 或「本文件兼任」  
**Version**：v0.1.0  
**日期**：[YYYY-MM-DD]

---

## 变更记录

| 版本 | 日期 | 摘要 | 影响 |
| --- | --- | --- | --- |
| v0.1.0 | [YYYY-MM-DD] | 初版 | — |

---

## 设计前置检查

- [ ] 已读本切片 `prd.md` / `spec.yaml`（及有 UI 时原型）
- [ ] 已读 `tech-spec.md`
- [ ] 若有 `requirementId`：已读 Epic Design（`architecture/`）与 `split.yaml`
- [ ] P0 `A*` 均有落点（§二 + `tech.yaml` acceptance）
- [ ] 未重复开写 Epic 已定契约；冲突须先改 Epic / 变更台账

---

## 一、简介与交付范围

| 项 | 内容 |
| --- | --- |
| 问题 | [对齐 spec.problem] |
| 本切片交付 | [对本切片 A* 可独立验收；Feature 对交付负责] |
| 非目标 | [对齐 nonGoals] |
| path | full / light / light-auto |
| Story | 未启用 / 见 `stories.yaml`（Story 不对 G4 负责） |

---

## 二、验收追溯

| ID | 摘要 | 技术落点（Epic 章节 / 本切片 § / Story / 接口） |
| --- | --- | --- |
| UJ1 / FR1 / A1 | … | Epic §七 KD-… / §五 / ST-… |

> 每条 P0 `A*` 必须可追溯；禁止只写在 Story 却不在本表出现。

---

## 三、Epic 引用与本切片增量

| 类型 | 引用（Epic / 其它 Feature） | 本切片增量（只写差异） |
| --- | --- | --- |
| L0/L1 | architecture.md §四/§五 | [无增量 / 补丁说明] |
| KD | KD-… | [本刀新增 KD-… / 无] |
| 接口/数据/埋点 | Epic §九～§十一 | [本刀增删] |
| 风险/NFR | Epic §六/§八 | [本刀增补] |

> 无 `requirementId`：上表「引用」列填「本文件兼任 Epic」，并在 §四出齐整图。

---

## 四、本切片架构增量

### 4.1 相对 Epic 的架构说明

> 有 REQ：说明本切片改动落在哪些模块、依赖方向是否变化。  
> 无 REQ：在此写清整需求上下文边界（兼任 Epic L0 文字说明）。

### 4.2 本切片架构图（增量或引用内嵌）

![本切片架构](diagrams/PLACEHOLDER.3.architecture.png)

> `full`：须在 `tech.yaml` diagrams 登记；可 L0+L1，或仅增量图 + `architectureLayerGaps` 指向 Epic。  
> 另需主路径协作时保留流程/时序/类图（见 `tech.yaml`；可下沉 Story）。

### 4.3 模块改动面

| 模块 | 本切片改动 | 说明 |
| --- | --- | --- |
| … | 新增 / 修改 / 无 | … |

---

## 五、本切片关键设计

> **仅本刀新增或必须本地细化的 KD**。Epic 已有 KD 只引用，不重写。  
> 展开件：`templates/design/key-design-kd.md`。无则 `keyDesignsNoneReason`。

| KD | 标题 | 相对 Epic | mustFollow 摘要 |
| --- | --- | --- | --- |
| KD-F01 | … | 新增 / 细化 KD-001 | … |

### KD-F01：[标题]

- **问题**：…
- **决策**：…
- **核心链路**：…
- **必须遵守**：…
- **坑**：…

---

## 六、本切片约束与风险增量

> 工程硬约束见 `tech-spec.md`。此处只写相对 Epic 的增量；详表可链 `templates/design/`。

| 维度 | 增量结论 | tech.yaml 字段 |
| --- | --- | --- |
| 风险 | … / 无（risksNoneReason） | `risks` |
| NFR | … | `nfr` |
| 接口 | … | `interfaces` |
| 数据 | … | `dataDesign` |
| 埋点 | … | `tracking` |

---

## 七、Story 与任务指引

> G2T 后主控写 `tasks.yaml`。启用 Story 时任务可带 `storyId`；验证命令对齐 Feature `A*` verify。

| Story / 任务 | 写集 | 覆盖 A* | 说明 |
| --- | --- | --- | --- |
| （无 Story）T1 | path/… | A1 | … |
| ST-001 → T… | … | A1 | 详见 stories/ST-001-…/story-tech.md |

---

## 附录：与 tech.yaml / Epic / Story 对应

| 本文 | 下游 |
| --- | --- |
| §二 | `tech.yaml` acceptance → evidence / G4 |
| §三 / §四 | Epic `architecture/`；`diagrams` / `architectureLayerGaps` |
| §五 | `keyDesigns` / `aiConstraints` |
| §六 | `risks` / `nfr` / `interfaces` / `dataDesign` / `tracking` |
| §七 | `stories.yaml` / `tasks.yaml` |
