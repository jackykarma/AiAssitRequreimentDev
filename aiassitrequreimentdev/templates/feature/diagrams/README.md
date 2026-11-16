# diagrams/

工具唯一：[Archify](https://github.com/tt-a1i/archify)。启用技能 `aiassitrequreimentdev-archify`。

正式产物：

| 文件 | 用途 |
| --- | --- |
| `*.html` | Archify 可交互原稿（门禁验溯源） |
| `*.png` | Markdown / `tech.md` 预览（门禁验内嵌） |

**不再要求、不再登记 `.svg`。** Cursor 等预览器对 Archify SVG（CSS 变量）支持差，统一用 PNG。

模板里的 `PLACEHOLDER.*.png` **仅供 Markdown 预览**（避免裂图），**不能**登记进 `tech.yaml` 过 G2T。正式出图：

1. `finalize` → `diagrams/<stem>.html`
2. `node plugins/aiassitrequreimentdev/scripts/export_diagram_png.mjs diagrams/<stem>.html`
3. 在 `tech.md` 内嵌 `![](diagrams/<stem>.png)`，`tech.yaml` → `diagrams[]` 填 `html` + `png`

建议命名：

- `*.L0.architecture.html` / `.png`
- `*.L1.architecture.html` / `.png`
- `*.workflow.html` / `.png`、`*.sequence.html` / `.png`、`*.class.html` / `.png`
