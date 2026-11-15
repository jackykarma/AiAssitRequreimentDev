# UI Kit 主题规范 · Apple Music–inspired

两套**对等标准**：`light` 与 `dark`。结构令牌（字号/间距/圆角/动效）共用；色彩令牌分主题。

强调色（共用）：`#FF2D55`（`--uk-accent`），主按钮字色 `--uk-on-accent: #fff`。

## 切换方式

```html
<html data-uk-theme="dark">   <!-- 或 light -->
```

也可在容器上加 `.uk-theme-dark` / `.uk-theme-light`。  
未写 `data-uk-theme`：默认 **dark**；若系统 `prefers-color-scheme: light` 则用 light。

橱窗：`showcase.html` 顶部可切换。原型页建议显式写死主题，避免评审时随系统跳变。

## Light 标准

| 令牌 | 值 | 用途 |
| --- | --- | --- |
| `--uk-bg` | `#F2F2F7` | 页面底 |
| `--uk-surface` | `#FFFFFF` | 顶栏/卡片/列表底 |
| `--uk-surface-muted` | `#F9F9FB` | 次级面、分段轨 |
| `--uk-ink` | `#1C1C1E` | 主文字 |
| `--uk-ink-secondary` | `#3A3A3C` | 次文字 |
| `--uk-muted` | `#8E8E93` | 辅助/未选中 |
| `--uk-line` | `rgba(60,60,67,.12)` | 分隔 |
| `--uk-accent` | `#FF2D55` | 强调/选中/主按钮 |
| `--uk-dock-bg` | 白半透明 | 底栏 |

气质：浅色系统列表、大标题、品红点缀，少描边靠层次。

## Dark 标准

| 令牌 | 值 | 用途 |
| --- | --- | --- |
| `--uk-bg` | `#000000` | 页面底（Music 近黑） |
| `--uk-surface` | `#1C1C1E` | 顶栏/卡片 |
| `--uk-surface-muted` | `#2C2C2E` | 次级面 |
| `--uk-ink` | `#F5F5F7` | 主文字 |
| `--uk-ink-secondary` | `#D1D1D6` | 次文字 |
| `--uk-muted` | `#8E8E93` | 辅助 |
| `--uk-line` | `rgba(84,84,88,.65)` | 分隔 |
| `--uk-accent` | `#FF2D55` | 同 light |
| `--uk-dock-bg` | 深色半透明 | 底栏 |

气质：近黑底、大白字、品红强调；可叠专辑色氛围（页面自行加背景模糊，不进公共令牌）。

## 产品 / UX 约定

- 默认视觉基线仍是本 ui-kit；`ux.yaml` → `visual.baseline: ui-kit`。
- 交付原型须可切换或标明主题；关键验收屏建议 **亮暗各一帧**（或工具栏一键切）。
- 禁止页面内另起色板；例外用 `visual.baseline: custom` + notes。
