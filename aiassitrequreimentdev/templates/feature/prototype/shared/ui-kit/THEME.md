# UI Kit 主题规范 · Apple Music–inspired（完善版）

参考来源（归纳用于 HTML 原型，非官方 SDK 还原）：

- [Apple HIG · Materials](https://developer.apple.com/design/human-interface-guidelines/materials)（ultraThin / thin / regular / thick + vibrancy）
- 业界拆解：[Apple Music iOS Design System Inspiration](https://www.uiskillbook.com/design-md/apple-music.md)
- Now Playing 专辑色氛围 / blur 实践（Mesh 渐变 + 高斯模糊）

本 kit 用 CSS 近似：**亮/暗两套对等标准** + **材质模糊** + **媒体组件**。真机 Liquid Glass / Metal shader 无法 1:1，以观感与可验收为准。

---

## 1. 气质原则

| 原则 | 做法 |
| --- | --- |
| 封面为王 | 大图、方封面、Now Playing 氛围来自专辑色 |
| 真黑 / 真白画布 | Dark `#000`；Light 主画布 `#FFF`（分组区 `#F2F2F7`） |
| 品牌红点缀 | `#FA2D48`（播放、进度、喜欢、选中） |
| 材质透叠 | 底栏 / 迷你播放器 / 顶栏用 material，不是实色一块 |
| 暗色靠色阶抬升 | Dark **少阴影**；Light 卡片可轻阴影 |
| SF 体系字体 | `-apple-system` / SF Pro；大标题 Display 气质 |

---

## 2. 主题切换

```html
<html data-uk-theme="dark">  <!-- 或 light -->
```

未指定：默认 dark；`prefers-color-scheme: light` 时跟系统。  
橱窗 `showcase.html` 可切换。原型建议显式写死。

---

## 3. 色彩标准

### 共用

| 令牌 | 值 | 用途 |
| --- | --- | --- |
| `--uk-accent` | `#FA2D48` | 播放、进度、喜欢、Tab 选中 |
| `--uk-accent-press` | `#D4213B` | 按下 |
| `--uk-on-accent` | `#FFFFFF` | 红底上的字/图标 |
| `--uk-link` | `#007AFF` | 系统蓝链接 |
| `--uk-atmos` | `#D4A857` | Atmos 金标 |
| `--uk-radius-art` | `12px` | 专辑/歌单封面圆角（Music 签名） |
| `--uk-radius-art-sm` | `8px` | 列表缩略图 |

### Light

| 令牌 | 值 |
| --- | --- |
| `--uk-bg` | `#FFFFFF` 主画布 |
| `--uk-bg-grouped` | `#F2F2F7` 分组列表底 |
| `--uk-surface` | `#FFFFFF` |
| `--uk-surface-muted` | `#F2F2F7` |
| `--uk-surface-elevated` | `#E5E5EA` |
| `--uk-ink` | `#000000` |
| `--uk-ink-secondary` | `rgba(60,60,67,.60)` |
| `--uk-muted` | `rgba(60,60,67,.30)` |
| `--uk-line` | `rgba(60,60,67,.29)` |

### Dark

| 令牌 | 值 |
| --- | --- |
| `--uk-bg` | `#000000` |
| `--uk-bg-grouped` | `#000000` |
| `--uk-surface` | `#1C1C1E` |
| `--uk-surface-muted` | `#2C2C2E` |
| `--uk-surface-elevated` | `#3A3A3C` |
| `--uk-ink` | `#FFFFFF` |
| `--uk-ink-secondary` | `rgba(235,235,245,.60)` |
| `--uk-muted` | `rgba(235,235,245,.30)` |
| `--uk-line` | `#38383A` |

---

## 4. 材质与模糊（HIG Materials 近似）

| 类名 | 对应 | 用途 | CSS 近似 |
| --- | --- | --- | --- |
| `.uk-material-ultraThin` | ultraThin | 轻遮罩、保留强背景 | blur ~10px + 低不透明 |
| `.uk-material-thin` | thin | 轻浮层 | blur ~40–60px |
| `.uk-material-regular` | regular（默认） | 底栏、迷你播放器、多数浮层 | blur ~20px + 较高 tint |
| `.uk-material-thick` | thick | 强对比面板、告警感 | blur ~40–60px + 更不透明 |

规则：

- 材质上的字用 `--uk-ink` / `--uk-ink-secondary`（模拟 vibrancy 层级），勿手写灰死色。
- Dark 迷你播放器 / Dock：`.uk-material-regular`。
- 全屏遮罩：`.uk-scrim`（约 40% 黑）。
- Now Playing 氛围：`.uk-ambient`（放大模糊封面 + 渐变压暗），不是 solid 色块。

---

## 5. 层级 / 阴影

| 级别 | Light | Dark |
| --- | --- | --- |
| 0 列表行 | 无影 | 无影 |
| 1 小卡片/封面 | `0 2px 8px rgba(0,0,0,.05)` | 无影，靠 surface 台阶 |
| 2 标准封面 | `0 4px 16px rgba(0,0,0,.08)` | 无影 |
| 3 Hero / 大封面 | `0 8px 24px rgba(0,0,0,.10)` | 可选极弱 |
| 4 Now Playing 主封面 | `0 20px 40px rgba(0,0,0,.30)` | 同左（封面浮空） |
| Sheet | `0 -12px 32px rgba(0,0,0,.25)` | 更深 scrim |

工具类：`.uk-elev-1` … `.uk-elev-4`、`.uk-elev-art`。

---

## 6. 字体阶梯（SF Pro 近似）

| 角色 | 大小 | 字重 | 类名 |
| --- | --- | --- | --- |
| Large Title | 34 | 700 | `.uk-type-large-title` |
| Title 2 | 22 | 700 | `.uk-type-title2` |
| Title 3 / 区头 | 20 | 600 | `.uk-type-title3` |
| Headline（曲名列表） | 17 | 600 | `.uk-type-headline` |
| Body | 17 | 400 | `.uk-type-body` |
| Subhead（艺人） | 15 | 400 | `.uk-type-subhead` |
| Footnote | 13 | 400 | `.uk-type-footnote` |
| Caption | 11–12 | 400 | `.uk-type-caption` |
| Tab | 10 | 500 | Dock 标签 |

---

## 7. 组件清单（须用类名，勿另起皮）

| 组件 | 类名 | 要点 |
| --- | --- | --- |
| 顶栏 | `.uk-topbar` / `.uk-topbar--material` | 可毛玻璃 |
| 大标题页 | `.uk-large-title` | 34pt |
| 列表行 | `.uk-cell` / `.uk-track` | 曲目行含封面 |
| 封面 | `.uk-art` / `.uk-art--sm` / `.uk-art--hero` | 12px / 8px 圆角 |
| 横滑货架 | `.uk-shelf` | 封面+双行字 |
| Hero 卡 | `.uk-hero` | 大图+文案压底 |
| 圆播放钮 | `.uk-play` | 44 / 64 圆形红底 |
| 胶囊 CTA | `.uk-btn--primary` | 圆角约 8–12，非一味 pill |
| 进度条 | `.uk-scrubber` | 红填充 |
| 迷你播放器 | `.uk-mini-player` | material + 封面 + 播放 |
| 底栏 | `.uk-dock` + material | 选中用 accent |
| 半屏 | `.uk-sheet` | 圆角顶 + grab |
| 氛围底 | `.uk-ambient` | 模糊封面背景 |
| 徽章 | `.uk-badge` / `--atmos` / `--new` | Atmos 金 / NEW |

---

## 8. 动效 / 特效（对齐 `research/ui-kits/MOTION.md`）

| 令牌/类 | 值 | 用途 |
| --- | --- | --- |
| `--uk-duration` / `fast` / `slow` | 280 / 180 / 360ms | 通用 / 按压 / sheet |
| `--uk-ease` | `cubic-bezier(0.22,1,0.36,1)` | 标准 |
| `--uk-press-scale` | `0.96` | 按下 |
| `--uk-blur-glass` | `22px` | 材质玻璃近似 |
| Toast | 上浮淡入 | `.uk-toast.is-show` |
| `prefers-reduced-motion` | 关动画/过渡 | 无障碍 |

复杂 Mesh 专辑渐变：原型用 `.uk-ambient` 静态模糊即可；真机 Metal 不在本 kit 范围。

---

## 9. 产品 / UX 约定

- 有 UI 时须人选并写入 `visual.baseline`（见 `research/ui-kits/catalog.yaml`：`ui-kit` / `painless` / `midoo` / `custom`…）
- **ui-kit（默认）**：`visual.theme: dark|light`；禁止页面内另起色板；引用 `tokens.css` + `materials.css` + `components.css` + `phone.css`；关键屏建议可切换亮暗
- **已注册 research kit**（如 `painless` / `midoo`）：引用对应 `research/<app>-ui/ui-kit/`（前缀 `pk`/`md`），动效对齐 MOTION.md
- **custom**：不强制本 kit；`notes` 说明原因；可读插件 `references/visual-explore.md`
