# 交互视觉模块

技能：`aiassitrequreimentdev-ux`。角色 id：`ux`。

## 定位

私人项目通常无专职设计师：**一个角色**，合同内分栏。

| 栏 | 必填？ | 内容 |
| --- | --- | --- |
| 交互规则 `interactionRules`（`IR*`） | 有 UI 时必填 | when / behavior（状态、反馈） |
| 视觉 `visual` | 建议 | 默认 `baseline: ui-kit`（Music 亮/暗，见 `THEME.md`）；`theme: dark|light`；custom 须说明 |
| 动效 `visual.motion`（`M*`） | 可选 | trigger / effect |
| UX HTML | 有 UI 时必填 | `prototype/ux/`，须引 ui-kit |
| `artifacts` | 可选 | Pencil/Figma 探索稿；须回流 HTML |

与产品分工：`prototype/index.html`＝业务可点通；`prototype/ux/`＝规则与视觉精修。规格事实源仍是 `spec.yaml`。

无 UI：`skip: true` + `reason`。
