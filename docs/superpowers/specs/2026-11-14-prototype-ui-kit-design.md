# 产品/UX 共享 Prototype UI Kit 设计

**日期**: 2026-11-14  
**状态**: 已批准（视觉基准：偏 ColorOS / 相册类系统应用）

## 目标

为产品 G1 与 UX G2 的可交互 HTML 原型提供统一、美观的手机端组件规范，减少「每页手写杂色 CSS」导致的观感漂与丑。

## 决策

- **落点**：`aiassitrequreimentdev/templates/feature/prototype/shared/ui-kit/`（随 `init` copytree 进入各 feature 的 `prototype/shared/ui-kit/`）。
- **视觉**：浅色系统风、克制强调色、大圆角、弱阴影；非运营落地页、非紫渐变 AI 滥调。
- **分工**：产品/UX HTML 均引用 kit；Pencil 可选，不阻塞门禁。
- **模式**：产品模板保留 patch（截图+热区）与 new（组件拼页）；组件 class 前缀 `uk-`。

## 交付物

| 文件 | 职责 |
| --- | --- |
| `tokens.css` | 色板、字号、间距、圆角、动效 |
| `components.css` | 顶栏、列表、卡片、按钮、半屏、空态、分段、开关、标签、底栏、Toast |
| `phone.css` | 手机框、热区 |
| `showcase.html` | 组件橱窗 |

## 非目标

深色主题、插画体系、拷贝真实 ColorOS 私有源码、替代 G1/G2 可交互要求。
