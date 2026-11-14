# 绘图约定（Archify）

统一使用 [Archify](https://github.com/tt-a1i/archify)。仓库内只保留 `.html` + `.svg`。

## 架构分层

| layer | 含义 |
| --- | --- |
| `0` | 系统/上下文：外部依赖、同需求其它 feature、信任边界 |
| `1` | 本 feature 内部模块与本切片改动 |

`type: architecture` 时 **必须** 填 `layer: 0` 或 `1`。有架构图时须 **0 与 1 都有**（可各多张），否则填 `architectureLayerGaps` 说明缺层原因。

## 多图

`sequence` / `workflow` / `class` 等 **允许同类型多条**。每条必填：

- `id`、`title`、`scope`（范围：场景/子系统/写集）
- `tool: archify`、`html`、`svg`

Feature 很大时按 scope 拆开，不要一张图画完全部。

## `diagrams[]` 示例

```yaml
diagrams:
  - id: D-L0
    type: architecture
    layer: 0
    title: 支付域上下文
    scope: 渠道与订单服务边界
    tool: archify
    html: diagrams/pay.L0.architecture.html
    svg: diagrams/pay.L0.architecture.svg
  - id: D-L1-a
    type: architecture
    layer: 1
    title: 回调模块
    scope: Callback 写集
    tool: archify
    html: diagrams/pay.L1.callback.architecture.html
    svg: diagrams/pay.L1.callback.architecture.svg
  - id: D-seq-ok
    type: sequence
    title: 回调成功
    scope: 单次成功路径
    tool: archify
    html: diagrams/callback.ok.sequence.html
    svg: diagrams/callback.ok.sequence.svg
diagramsNoneReason: ""
architectureLayerGaps: ""
```

## 安装

本仓库：`.agents/skills/archify`（`node .agents/skills/archify/bin/archify.mjs doctor`）。
