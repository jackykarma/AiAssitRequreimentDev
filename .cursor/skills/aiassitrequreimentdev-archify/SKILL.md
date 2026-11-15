---
name: aiassitrequreimentdev-archify
description: 为本仓 feature 技术方案用 Archify 出架构/流程/时序/类图（html+svg）。用户或 tech 阶段要画图、替换 Mermaid、过 G2T 图门禁时使用。
---

# Archify 绘图（本仓封装）

正式图**唯一工具**：[Archify](https://github.com/tt-a1i/archify)。禁止手写 HTML/SVG 或 Mermaid 冒充过门禁。

本技能是**调用入口**：先读并遵循本仓已安装的 Archify 技能 `.agents/skills/archify/SKILL.md`（schema / finalize / 修复），再按下表把产物落到当前 feature。

## 类型映射

| 用途 | Archify type | 建议文件名 |
| --- | --- | --- |
| 0/1 层架构 | `architecture` | `diagrams/*.L0.architecture.*` / `*.L1.architecture.*` |
| 流程图 | `workflow` | `diagrams/*.workflow.*` |
| 时序图 | `sequence` | `diagrams/*.sequence.*` |
| 类图 | `class` | `diagrams/*.class.*` |
| 其它 | dataflow / erd / lifecycle / … | 按 type 命名 |

## 标准步骤

1. 确认 feature 目录与 `diagrams/` 存在；读 `prd.md` / `tech.md` / `spec.yaml` 确定图意与 `scope`。
2. **启用** `.agents/skills/archify`：按 type 写完整 `candidate.json`（质量 `showcase`，除非用户要求 `standard`）。
3. Finalize（路径按本机；本仓技能包示例）：

```bash
node .agents/skills/archify/bin/archify.mjs finalize <type> <candidate.json> <feature目录>/diagrams/<stem>.html --quality showcase --json
```

4. 导出/另存同 stem 的 `.svg`；HTML 须含 Archify 溯源（`generator=archify`、`archify-reader-contract`、`#archify-fonts`）。
5. 在 `tech.md`（及 KD 等）用 `![说明](diagrams/<stem>.svg)` **内嵌**；`tech.yaml` → `diagrams[]` 填 `id/type/title/scope/tool: archify/html/svg`（architecture 另填 `layer`）。
6. `python <插件>/scripts/aad.py check <feature目录> --gate G2T`。

## 模板里的占位

`templates/feature/tech.md`、`templates/design/*` 中图位已是 Archify 占位（非 Mermaid）。出图时替换 `diagrams/PLACEHOLDER.*` 为真实 stem，勿再写回 Mermaid 代码块。

## 不要做

- 不改 `spec.yaml` / 源码（除非用户另派开发）
- 不用 Mermaid / 手绘 SVG 充当 `diagrams[]` 正式产物
