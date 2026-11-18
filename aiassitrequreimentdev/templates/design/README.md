# 设计展开模板

与 `templates/feature/tech.md`、`tech.yaml` 配套。亦可用于**需求级 Epic Design**：复制到 `requirements/<REQ>/architecture/`，文件名见下表「REQ 落盘名」。

| 模板 | Feature 落盘 | REQ Epic 落盘名（§八～§十一 **强制**） | 机器字段 |
| --- | --- | --- | --- |
| [key-design-kd.md](key-design-kd.md) | `KD_*.md` | `architecture/key-func-design/` | `keyDesigns[]` |
| [nfr.md](nfr.md) | `nfr.md` | `architecture/nfr.md` | `nfr` / Epic 摘要表 |
| [interface.md](interface.md) | 自定 | `architecture/interface-design.md` | `interfaces[]` |
| [database.md](database.md) | 自定 | `architecture/database-design.md` | `dataDesign` |
| [analytics-tracking.md](analytics-tracking.md) | 自定 | `architecture/analytics-tracking.md` | `tracking` |

Epic `architecture.md` §八～§十一 **只保留结论/摘要表 + 相对链接**；详表必须在上表独立文件中按模板章节写满（`check-req` 硬校验标题）。

人读主文档模板在 `templates/feature/`（`prd.md` / **feature 级** `tech.md` / `tech-spec.md` / `tasks.md`）、`templates/requirement/`（`prd.md` + `architecture/`）与可选 `templates/story/`。章节标题须与这些文件完全对齐（门禁校验）。本目录是展开件；可借鉴 AISDD 文档结构，但**禁止**跑旧 `/aisdd.*` 命令或把 Story 做成可 G4 单元。绘图启用技能 `aiassitrequreimentdev-archify`（[Archify](https://github.com/tt-a1i/archify)）。
