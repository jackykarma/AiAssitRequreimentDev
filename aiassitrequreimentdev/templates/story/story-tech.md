# Story 详细设计：`ST-001-<slug>`（技术实现 / 并行单元）

> **落盘**：复制到 `features/<FEAT-id>/stories/ST-001-<slug>/story-tech.md`。  
> **定位**：本 Story 的落码级实现方案。挂在 Feature 下；**不对独立交付负责**（G4 只认 Feature）。  
> **借鉴**：结构参考 AISDD L2 `story_detail_design_template`；绘图用 Archify（禁止 Mermaid 冒充合同）。  
> **上游**：Epic Design（`requirements/…/architecture/architecture.md`）+ 本 Feature 薄 `tech.md` / `tech.yaml`；关联 KD 只可细化不可另起炉灶。

**Feature**：FEAT-[序号]-[kebab名称]  
**Story**：ST-001-[slug]  
**日期**：[YYYY-MM-DD]

---

## 依赖与引用

| 类型 | 说明 |
| --- | --- |
| 关联 KD | — / `../../KD_001_….md`（继承哪些决策） |
| 前置 ST（本 Feature） | — / `../ST-000-…/story-tech.md` |
| 对外契约（本 Story 完成后可依赖） | [接口/模块边界摘要] |
| REQ 契约 | — / `requirements/…/architecture/` 中 CTR-\* |

---

## 一、范围与覆盖

- **本 Story 做什么**：[技术主链一句话]
- **不做什么**：[避免膨胀成半个 Feature]
- **覆盖验收**：只引用本 Feature `A*`（禁止自造交付验收）

| A* | 本 Story 覆盖的实现部分 |
| --- | --- |
| A1 | … |

---

## 二、实现方案

> 讲清怎么落地：入口、数据流、核心类、出口/副作用；关键决策须写「选 A 而非 B 的原因」。

- **核心实现思路**：…
- **继承 KD / REQ 决策**：[无则 N/A]
- **失败处理**：重试 / 降级 / 透传（各类由谁负责）

---

## 三、类图（按需）

![类图](diagrams/PLACEHOLDER.class.png)

> Deep：须覆盖本 Story 关键类与方法签名；与 KD 冲突时先改 KD。

---

## 四、时序图（按需）

![时序图](diagrams/PLACEHOLDER.sequence.png)

> 主路径 + 关键异常分支；图下用文字说明协作者与过程。

---

## 五、写集边界

| 路径 / 模块 | 本 Story | 并行 Story 不得改 |
| --- | --- | --- |
| … | 是 | … |

> 与 `stories.yaml` → `writeScopeHint` 及后续 `tasks.yaml` writeScopes 一致；并行 Story 写集不得相交。

---

## 六、任务指引

| 建议 Task | 写集 | 覆盖 A* | 验证对齐 |
| --- | --- | --- | --- |
| T… | … | A1 | spec.verify 同源 |

> 主控写 `tasks.yaml` 时可填 `storyId: ST-001-…`。Story `status=done` ≠ Feature G4。
