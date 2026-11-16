---
name: aiassitrequreimentdev-archify
description: 为本仓 feature 技术方案用 Archify 出架构/流程/时序/类图（html+png）。用户或 tech 阶段要画图、替换 Mermaid、过 G2T 图门禁时使用。
---

# Archify 绘图（本仓封装）

正式图**唯一工具**：[Archify](https://github.com/tt-a1i/archify)。禁止手写 HTML/PNG 冒充或 Mermaid 过门禁。

本技能是**调用入口**：先读并遵循本仓已安装的 Archify 技能 `.agents/skills/archify/SKILL.md`（schema / finalize / 修复），再按下表把产物落到当前 feature。

## 类型映射

| 用途 | Archify type | 建议文件名 |
| --- | --- | --- |
| 0/1 层架构 | `architecture` | `diagrams/*.L0.architecture.*` / `*.L1.architecture.*` |
| 流程图 | `workflow` | `diagrams/*.workflow.*` |
| 时序图 | `sequence` | `diagrams/*.sequence.*` |
| 类图 | `class` | `diagrams/*.class.*` |
| 其它 | dataflow / erd / lifecycle / … | 按 type 命名 |

## 产物合同（重要）

| 文件 | 用途 |
| --- | --- |
| `.html` | Archify 可交互原稿（门禁验溯源） |
| `.png` | **Markdown / `tech.md` 预览**（门禁验内嵌） |

**不再产出或登记 `.svg`。** Archify 内联 SVG 依赖页面 CSS 变量，Cursor/多数 Markdown 预览不可见。

## 标准步骤

1. 确认 feature 目录与 `diagrams/` 存在；读 `prd.md` / `tech.md` / `spec.yaml` 确定图意与 `scope`。
2. **启用** `.agents/skills/archify`：按 type 写完整 `candidate.json`（质量 `showcase`，除非用户要求 `standard`）。
3. Finalize：

```bash
node .agents/skills/archify/bin/archify.mjs finalize <type> <candidate.json> <feature目录>/diagrams/<stem>.html --quality showcase --json
```

4. 导出同 stem PNG（插件脚本，需本机 Chrome/puppeteer）：

```bash
node <插件>/scripts/export_diagram_png.mjs <feature目录>/diagrams/<stem>.html
# 可选：--chrome "C:/Path/to/chrome.exe"
```

5. HTML 须含 Archify 溯源（`generator=archify`、`archify-reader-contract`、`#archify-fonts`）。
6. 在 `tech.md` 用 `![说明](diagrams/<stem>.png)` **内嵌**；`tech.yaml` → `diagrams[]` 填 `id/type/title/scope/tool: archify/html/png`（architecture 另填 `layer`）。**禁止 `svg` 字段。**
7. `python <插件>/scripts/aad.py check <feature目录> --gate G2T`。

## 模板里的占位

`templates/feature/tech.md`、`templates/design/*` 中图位为 `diagrams/PLACEHOLDER.*.png`。  
出图后用真实 stem 的 png/html **覆盖或改链**；**禁止**把占位 PNG 登记进 `tech.yaml` 过 G2T。勿再写回 Mermaid / svg。

## 不要做

- 不改 `spec.yaml` / 源码（除非用户另派开发）
- 不用 Mermaid / 手绘 SVG / 空壳 PNG 充当 `diagrams[]` 正式产物
