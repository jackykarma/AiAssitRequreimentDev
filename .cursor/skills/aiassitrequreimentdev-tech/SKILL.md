---
name: aiassitrequreimentdev-tech
description: 技术方案 Agent。写 REQ Epic Design（architecture/）与/或 Feature 薄 tech.md+tech.yaml；可选 Story 详细设计。Archify 出图。用户要技术方案、G2T 或 check-req 架构时使用。
---

# 技术方案

大需求先写 **Epic Design**（`requirements/…/architecture/`）；各 Feature 只写**薄** `tech.md` + `tech.yaml`（交付落点与增量）及按需 Story。不改规格、视觉与业务源码，不新增验收编号。

**人读模板（必须与 `templates/feature/` 章节完全对齐；按需展开 `templates/design/`）**：

1. **Epic Design**（整需求）：`templates/requirement/architecture/architecture.md`（对齐 AISDD epic-design）→ `requirements/…/architecture/`。
2. **Feature 薄 tech**：`templates/feature/tech.md` + `tech-spec.md` + `tech.yaml`；只写交付落点与相对 Epic 的增量，禁止重抄 Epic 总册。
3. **保留薄 tech 全部 `##`**；`full` 还须强制 `###`（4.1 / 4.2）。展开件：`templates/design/`。
4. G2T 校验薄 tech 标题 + `tech.yaml`；`light` 不强制 4.1/4.2，但仍须 `##` + yaml。
5. 可借鉴 AISDD 结构，**禁止**跑 `/aisdd.*`；Story 不可 G4。
6. 并行/复杂落码：`stories.yaml` + `templates/story/`；验收只认 Feature `A*`。
7. 无 `requirementId`（单 Feature 捷径）：薄 tech **兼任** Epic 关键结论并出齐必要图。

确认 `state.actorRole` 为 `architect`。先读 Epic Design（若有）、`BOARD.md`、`prd`/`spec`。G1 就绪且 G2 通过或 skip 后再写。

## 绘图工具（强制 Archify）

工具唯一：[Archify](https://github.com/tt-a1i/archify)。类型映射：

| 图 | Archify type |
| --- | --- |
| 架构图 L0/L1 | `architecture` |
| 流程图 | `workflow` |
| 时序图 | `sequence` |
| 类图 | `class` |

**必须真正用 Archify 绘制**，禁止手写 HTML/PNG、Mermaid 直出、或随便画图冒充：

1. **启用**本仓技能 `aiassitrequreimentdev-archify`（封装入口；底层遵循 `.agents/skills/archify/SKILL.md`）。
2. 按 type 写 `candidate.json` 并 `finalize`（详见 archify 技能）：

```bash
node .agents/skills/archify/bin/archify.mjs finalize <type> <candidate.json> <diagrams/xxx.html> --quality showcase --json
```

3. **导出同 stem `.png`**（供 Markdown 预览；**不要再交 svg**）：

```bash
node <插件>/scripts/export_diagram_png.mjs <diagrams/xxx.html>
```

4. `tech.yaml` → `diagrams[].tool` 必须为 `archify`；字段为 `html` + `png`（禁止 `svg`）。
5. 模板中的图位已是 Archify 占位 PNG；替换 `diagrams/PLACEHOLDER.*` 为真实产物。
6. G2T 检查 HTML 溯源：`generator=archify`、`archify-reader-contract`、`#archify-fonts`；PNG 须为有效且足够大的预览图。缺一则失败。

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

## 流程 / 时序 / 类图（full 路径强制）

`path: full` 且 `diagrams[]` 非空时，**除 L0/L1 架构图外**，还必须各至少一张：

| type | 中文 | 要求 |
| --- | --- | --- |
| `workflow` | 流程图 | 主路径 + 分支/失败出口 |
| `sequence` | 时序图 | 参与者与调用关系（以 Archify HTML 为准；PNG 为预览） |
| `class` | 类图 | 关键类型与依赖 |

同类型可多张，禁止一张塞满。light 或 `diagramsNoneReason` 说明无新图时可跳过。

## tech.md 内嵌图（强制）

- `tech.md` 对 `tech.yaml` → `diagrams[].png` **每一张**必须用 Markdown 图片语法直接内嵌，例如：`![流程图](diagrams/xxx.workflow.png)`。
- **禁止**仅用表格列出 html/png 路径、禁止「见某某文件 / 点击链接」代替预览。
- **禁止**再内嵌 `.svg` 作为预览合同。
- 章节上须能直接看到：**流程图、时序图、类图**（以及 L0/L1）。
- `diagrams/*.html` 可保留供交互探索；人审以 `tech.md` 内嵌 PNG 为准。

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

## 变更（G2T 通过后）

改 `tech.yaml` / `tech.md` 合同（接口、KD、约束等）：请主控记 **C1**（发起人、原因、影响、时间），回退 G2T 并重评 G3。牵动 A* 则升 **C3**。见 `references/change-control.md`。

```bash
python <本插件>/scripts/aad.py check <feature 目录> --gate G2T
```

结束后请主控登记本阶段 token（`--role architect --stage tech`），见 lead 技能「Token 用量」。
