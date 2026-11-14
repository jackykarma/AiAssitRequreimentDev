# 设计展开模板（本仓自有）

与 `templates/feature/tech.md` / `tech.yaml` 配套。Feature 技术方案可在 `tech.md` 写摘要，细节按需展开为同目录或 `features/<id>/` 下独立文件；机器字段仍以 `tech.yaml` 为准，G2T 校验 yaml。

| 模板 | 用途 | 对应 tech.yaml |
| --- | --- | --- |
| [key-design-kd.md](key-design-kd.md) | 单条关键设计（KD）详述 | `keyDesigns[]` |
| [nfr.md](nfr.md) | 快稳省及内存/安全/兼容/包体/算法量化 | `nfr` |
| [interface.md](interface.md) | 对外提供 / 依赖外部接口详述 | `interfaces[]` |
| [database.md](database.md) | 库表字段、索引、迁移 | `dataDesign` |
| [analytics-tracking.md](analytics-tracking.md) | 产品/技术埋点字段规约 | `tracking` |

绘图一律 [Archify](https://github.com/tt-a1i/archify)，只保留 `.html` + `.svg`。见 `modus/knowledge/domain/change/references/diagrams.md`。
