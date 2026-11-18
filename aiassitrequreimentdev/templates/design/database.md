# 数据库设计：FEAT-[序号]-[kebab名称] / REQ-[…]

> **定位**：数据表/存储展开件；Feature 约束在 `tech-spec.md`，摘要在 `tech.md` §十 / `dataDesign`。  
> **REQ Epic**：必须落盘 `architecture/database-design.md`；`architecture.md` §十只摘要 + 链接。  
> **适用**：Room/SQLite/DataStore/云端等；无则整文 N/A（仍须保留章节标题）。  
> **绘图**：Archify `erd` → `diagrams/`，并在 yaml diagrams 登记。

**Feature / Requirement**：[ID]  
**关联**：Epic `architecture.md` §十 · `tech-spec.md` · `tech.yaml`  
**日期**：[YYYY-MM-DD]

---

### 10.1 数据库概览

#### 10.1.1 数据存储清单


| 存储ID   | 存储名称       | 存储类型                                   | 所属 Feature | 表/集合数量 | 规约位置                   |
| ------ | ---------- | -------------------------------------- | ---------- | ------ | ---------------------- |
| DB-001 | [数据库/存储名称] | [Room/SQLite/SharedPrefs/DataStore/云端] | FEAT-001-example   | [N 张表] | tech-spec.md FEAT-001-example · 四 |


#### 10.1.2 数据库 ER 图（推荐）

> 用 ER 图展示关键数据表之间的关系，便于评审者理解整体数据模型。

> **绘图（Archify，强制）**：启用技能 `aiassitrequreimentdev-archify`（底层 `.agents/skills/archify`）。类型：`erd`。写 candidate → `finalize` → 产出 html+png；**禁止**用 Mermaid 作正式图。
>
> 建议路径：`diagrams/PLACEHOLDER.1.erd.html` + `diagrams/PLACEHOLDER.1.erd.png`；在 `tech.yaml` → `diagrams[]` 登记（`tool: archify`）。

![Archify erd 占位（请替换为 finalize 产物）](diagrams/PLACEHOLDER.1.erd.png)




### 10.2 数据表详细设计

> 每张表一节，完整描述字段含义、类型、约束和索引。

#### 10.2.1 [表名 / TABLE_A]

- **所属模块**：[模块名称]
- **所属 Feature**：FEAT-001-example
- **用途描述**：[一句话说明该表存储什么数据、用于什么场景]

##### 字段设计


| 字段名     | 类型                       | 是否必填 | 默认值     | 说明       | 约束                        |
| ------- | ------------------------ | ---- | ------- | -------- | ------------------------- |
| `id`    | INTEGER                  | 是    | 自增      | 主键       | PRIMARY KEY AUTOINCREMENT |
| `[字段名]` | [TEXT/INTEGER/REAL/BLOB] | 是/否  | [默认值/-] | [字段含义说明] | [UNIQUE/NOT NULL/外键等]     |


##### 索引设计


| 索引名             | 索引字段  | 索引类型          | 用途说明     |
| --------------- | ----- | ------------- | -------- |
| `idx_[表名]_[字段]` | [字段名] | UNIQUE / 普通索引 | [查询场景说明] |


##### 版本迁移


| 版本号 | 变更内容        | 迁移策略                   |
| --- | ----------- | ---------------------- |
| v1  | 初始建表        | 创建表                    |
| v2  | [新增字段/修改字段] | [ALTER TABLE / 数据迁移脚本] |


- **约束来源**：→ `tech-spec.md FEAT-001-example · 四`

#### 10.2.2 [表名 / TABLE_B]

（结构同 10.2.1）

### 10.3 数据设计说明

> 说明关键的数据设计决策，包括数据一致性策略、缓存策略、数据生命周期管理等。

- **数据一致性**：[本地与远端数据的一致性策略，如 Single Source of Truth、乐观锁、最终一致性等]
- **缓存策略**：[缓存失效机制、缓存大小上限、LRU 策略等]
- **数据生命周期**：[数据保留策略、过期清理机制、用户注销后的数据处理]
- **数据迁移策略**：[版本升级时的 Migration 策略，与 `nfr.md` §8.6 兼容性评估中数据库升级项对应]
- **敏感数据处理**：[加密字段、脱敏策略，与 `nfr.md` §8.5 安全评估对应]

### 10.4 数据库设计一致性自检

- 所有数据表均可追溯到对应 Feature 的 `tech-spec.md` §四数据硬约束
- §10.1 ER 图中的表关系与需求级 / Feature 领域概念及 dataDesign 一致
- 所有外键关联已在字段约束中明确标注
- 数据库版本迁移策略已在 `nfr.md` §8.6 兼容性评估中覆盖
- 敏感字段已在 `nfr.md` §8.5 安全评估中标注加密/脱敏要求
