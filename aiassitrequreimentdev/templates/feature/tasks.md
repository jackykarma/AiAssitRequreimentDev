# 任务拆解（人读）：FEAT-[序号]-[kebab名称]

> **定位**：给人看的任务说明；**门禁只认**同目录 `tasks.yaml`。  
> **时机**：本 feature **G2T 通过之后**由主控填写 `tasks.yaml`（可用 `aad tasks scaffold` 生成骨架），本文可作对照索引。  
> **规则**：任务验证命令须与 `spec.acceptance[].verify` **同名/同源**（可补全可跑路径，禁止总能成功的空转）。  
> **Story**：可选 `storyId`；Story 不对 G4 负责，验收仍归本 Feature `A*`。  
> **禁止**：在本文改写 `spec` / `tech` 合同；写集相交的任务不得标并行。

**Feature**：FEAT-[序号]-[kebab名称]  
**关联**：`spec.yaml` · `tech.md` / `tech.yaml` · `tasks.yaml` · `stories.yaml`（若启用）  
**Version**：v0.1.0  
**日期**：[YYYY-MM-DD]

---

## 与 tasks.yaml 对照

| tasks.yaml id | 标题 | 写集 | 覆盖 A* | storyId | blockedBy |
| --- | --- | --- | --- | --- | --- |
| T1 | … | `path/…` | A1 | — | [] |

> 轻量族（light / light-auto）**只能一个任务**。

---

## 拆任务检查单

- [ ] 每个 P0 `A*` 至少被一个任务的 `acceptance` 引用
- [ ] `verify` / 任务验证与证据命令同源，失败时非 0
- [ ] 写集不相交；有依赖用 `blockedBy`，无环
- [ ] 未实现 `nonGoals`
- [ ] 引用 `tech.yaml` 的 `aiConstraints` / `keyDesigns`（若有）

---

## 任务说明（可选展开）

### T1：[标题]

- **目的**：…
- **写集**：…
- **步骤**：1) … 2) …
- **验证**：与 A1 的 verify 同源
- **设计引用**：`tech.md` §七 / `tech.yaml` keyDesigns …

---

## 路径约定（按本仓工程）

- 以 `tech-spec.md` / 现有模块名为准（如 `:feature:xxx`）
- 测试路径写进任务验证或 `evidence.yaml` 的 `command`
