# Feature 方案图（按需，可多张）

工具唯一：[Archify](https://github.com/tt-a1i/archify)。启用技能 `aiassitrequreimentdev-archify`。架构 / 流程 / 时序 / 类图均用 Archify；只保留 `.html` + `.svg`。

模板里的 `PLACEHOLDER.*.svg` **仅供 Markdown 预览**（避免裂图），**不能**登记进 `tech.yaml` 过 G2T。正式出图后用 finalize 产物**覆盖同名或换成真实 stem**，再内嵌到 `tech.md`。

**禁止**手写 HTML/SVG 或 Mermaid 冒充。须 `finalize`；HTML 须含 `generator=archify`、`archify-reader-contract`、`#archify-fonts`（G2T 检查）。

命名建议：

- `*.L0.architecture.html` / `.svg` — 0 层（可多张，文件名加 scope）
- `*.L1.architecture.html` / `.svg` — 1 层（可多张）
- `*.workflow.html` / `.svg`、`*.sequence.html` / `.svg`、`*.class.html` / `.svg` — 同类型可多张

每张在 `tech.yaml` → `diagrams[]` 登记，并填写 `scope`；架构图还须 `layer: 0|1`。`tool` 固定 `archify`。
