# Feature 方案图（按需，可多张）

[Archify](https://github.com/tt-a1i/archify)。只保留 `.html` + `.svg`。

命名建议：

- `*.L0.architecture.html` / `.svg` — 0 层（可多张，文件名加 scope）
- `*.L1.architecture.html` / `.svg` — 1 层（可多张）
- `*.workflow.html` / `.svg`、`*.sequence.html` / `.svg`、`*.class.html` / `.svg` — 同类型可多张

每张在 `tech.yaml` → `diagrams[]` 登记，并填写 `scope`；架构图还须 `layer: 0|1`。
