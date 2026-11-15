# 设计展开模板

与 `templates/feature/tech.md`、`tech.yaml` 配套。Feature 内按需复制到 `features/<id>/` 展开；机器字段仍以 `tech.yaml` 为准。

| 模板 | 用途 | 对应 tech.yaml |
| --- | --- | --- |
| [key-design-kd.md](key-design-kd.md) | 单条关键设计（KD） | `keyDesigns[]` |
| [nfr.md](nfr.md) | 快稳省等量化 | `nfr` |
| [interface.md](interface.md) | 接口详述 | `interfaces[]` |
| [database.md](database.md) | 库表 / 迁移 | `dataDesign` |
| [analytics-tracking.md](analytics-tracking.md) | 埋点 | `tracking` |

人读主文档模板在 `templates/feature/`（`prd.md` / **feature 级** `tech.md` / `tech-spec.md` / `tasks.md`）与 `templates/requirement/prd.md`。章节标题须与这些文件完全对齐（门禁校验）。本目录是展开件，不是旧 AISDD EPIC/Story 命令产物。绘图启用技能 `aiassitrequreimentdev-archify`（[Archify](https://github.com/tt-a1i/archify)）。
