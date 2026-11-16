# 技术方案：FEAT-[序号]-[kebab名称]

> **定位**：本 **feature 切片** 的技术方案人读件。与 `tech.yaml`（AI/门禁）、`tech-spec.md`（工程约束）同源。  
> **输入**：本切片 `prd.md` / `spec.yaml` / 原型；若有 `requirementId` 再读需求级 PRD 与同需求其它 tech。  
> **绘图**：正式图须用 [Archify](https://github.com/tt-a1i/archify) `finalize` 出 `.html`，再导出同 stem `.png` 入 `diagrams/`；本文用 `![](…png)` **直接内嵌**（禁止仅表格列路径；**不再使用 svg**）。  
> **展开件**（按需复制）：`templates/design/`（KD / NFR / 接口 / 库表 / 埋点）。  
> **Lite**：轻量路径可将详表收成索引 + 链接，但仍须保留下列全部 `##` 标题；`full` 还须保留强制 `###`。

**Feature**：FEAT-[序号]-[kebab名称]  
**关联需求**：`requirementId` 或「单 feature 捷径」  
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
- [ ] 已读 `tech-spec.md` 工程约束
- [ ] 若有 `requirementId`：已读需求级 PRD / `split.yaml` / 可选 `architecture/`
- [ ] 已对照现有工程代码校准模块边界
- [ ] P0 的 `A*` 均有技术落点计划（写入 §二 与 `tech.yaml` acceptance）

---

## 一、简介与范围

| 项 | 内容 |
| --- | --- |
| 问题 | [一句话，对齐 spec.problem] |
| 本切片交付 | [对本切片 A* 可独立验收的能力] |
| 非目标 | [对齐 nonGoals] |
| 建议 path | full / light / light-auto |

---

## 二、需求与验收追溯

| ID | 摘要 | 技术落点（章节 / KD / 接口） |
| --- | --- | --- |
| UJ1 / FR1 / A1 | … | §七 / §九 / … |

> 每条 P0 `A*` 须能在本文件或 `tech.yaml` 找到覆盖。

---

## 三、关键设计判定

> 对照原则决定是否立 KD：跨模块契约、状态机、并发/幂等、安全、性能预算、不可逆数据变更等。  
> 无则在 `tech.yaml` 写 `keyDesignsNoneReason`，本节说明「无关键设计」。

| 判定 | 结论 |
| --- | --- |
| 是否需要 KD | 是 / 否（原因） |

---

## 四、零层架构（L0）

> 本 feature 与外部系统、其它 feature、信任边界。无新边界可写「沿用现有工程」并在 `architectureLayerGaps` 说明。

### 4.1 外部与依赖

| 系统 / Feature | 关系 | 说明 |
| --- | --- | --- |
| … | 提供 / 消费 | … |

### 4.2 零层架构图（必须）

![L0 架构图](diagrams/PLACEHOLDER.2.architecture.png)

> 替换为 Archify HTML 截出的真实 png；`tech.md` 必须内嵌，禁止只写路径。可交互原稿为同 stem `.html`。

---

## 五、一层架构（L1）

> 本 feature 内部模块/组件与本切片改动面。

### 5.1 一层框架图（必须）

![L1 架构图](diagrams/PLACEHOLDER.3.architecture.png)

### 5.2 模块职责

| 模块 | 职责 | 本切片改动 |
| --- | --- | --- |
| … | … | 新增 / 修改 / 无 |

### 5.3 组件协作流程（必须）

![主路径协作](diagrams/PLACEHOLDER.4.workflow.png)

> `full` 路径还须在 `tech.yaml` diagrams 中具备 workflow / sequence / class（可多张，`scope` 区分）。

---

## 六、技术风险与边界

| ID | 风险 | 影响 | 对策 |
| --- | --- | --- | --- |
| RISK-1 | … | … | … |

无风险时写明，并在 `tech.yaml` 填 `risksNoneReason`。

---

## 七、关键设计

> 每条 KD 至少：问题、决策、核心链路、`mustFollow`、`pitfalls`。复杂 KD 可复制 `templates/design/key-design-kd.md` 展开。

### KD-001：[标题]

- **问题**：…
- **决策**：…
- **核心链路**：…
- **必须遵守**：…
- **坑**：…

无则写「无关键设计」并与 `keyDesignsNoneReason` 一致。

---

## 八、NFR 评估

| 维度 | 评估 | 缓解 |
| --- | --- | --- |
| 性能 | … | … |
| 稳定性 | … | … |
| 功耗 | … | … |

> 与 `tech.yaml` → `nfr` 一致；详表可展开 `templates/design/nfr.md`。

---

## 九、接口设计

| ID | 方向 | 类型 | 说明 |
| --- | --- | --- | --- |
| IF-1 | provided / consumed | api / function / event / db | … |

详版可展开 `templates/design/interface.md`。

---

## 十、数据设计

| 表/存储 | 变更 | 目的 |
| --- | --- | --- |
| … | add / alter / none | … |

不涉及则写 N/A，并在 `tech.yaml` → `dataDesign.noneReason` 说明。

---

## 十一、埋点

| 事件 | 触发 | 字段 |
| --- | --- | --- |
| … | … | … |

无则写 N/A + `tracking.noneReason`。

---

## 十二、实现与任务指引

> G2T 通过后由主控写 `tasks.yaml`。此处只给拆任务约束：写集建议、验收命令同源、禁止实现 nonGoals。

| 建议任务 | 写集 | 覆盖 A* |
| --- | --- | --- |
| T1 | path/… | A1 |

---

## 附录：与 tech.yaml / tasks 对应

| 本文章节 | tech.yaml / 下游 |
| --- | --- |
| §三 / §七 | `keyDesigns` / `aiConstraints` |
| §四 / §五 | `diagrams`（L0/L1） |
| §八～§十一 | `nfr` / `interfaces` / `dataDesign` / `tracking` |
| §二 / §十二 | `acceptance` → `tasks.yaml` |
