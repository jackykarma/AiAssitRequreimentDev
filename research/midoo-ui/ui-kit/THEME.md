# Midoo UI Kit · com.midoo.ai 风格归纳

> 来源：真机 `com.midoo.ai` v1.5.27（PMA110）截图 + `uiautomator` 层级。  
> 用途：HTML 原型视觉基线（对标视觉参考，非官方 SDK / 资源还原）。  
> 抓取包名约束：**仅** `com.midoo.ai`。  
> 动效合同：`research/ui-kits/MOTION.md`（前缀 `md`）。  
> 人选 id：`visual.baseline: midoo`（见 `research/ui-kits/catalog.yaml`）。

---

## 1. 气质原则

| 原则 | 做法 |
| --- | --- |
| 淡紫蓝渐变画布 | 全屏 soft gradient（紫 → 米白 → 浅蓝），忌纯灰底 |
| 毛玻璃浮层 | 底栏 / 步骤条 / chip 用 `backdrop-filter` + 半透明白 |
| 大圆角友好卡 | 主卡 ≈ 28px；按钮 / 底栏 pill |
| 手写感标题 | Plan / Chat / Play 用 display 手写体；正文无衬线 |
| 渐变 CTA | 浅蓝 → 淡紫横向渐变胶囊按钮 |
| 3D 吉祥物点缀 | 模式卡 / VIP 用插画占位，勿改成扁平图标唯一风格 |
| 中心品牌 Tab | 底栏 5 项，中间为 Midoo 品牌位 |

---

## 2. 信息架构（已证实）

| Tab | 主界面 |
| --- | --- |
| 课程 | 阶段进度 + 讲解/练习/情景对话 + 步骤列表 |
| 对话 | 角色大卡轮播 + 标签 +「去聊聊」 |
| Midoo | 中心品牌入口（深层未全覆盖） |
| 趣玩 | 分类 pill + 双列瀑布 |
| 我的 | 头像统计 + VIP + 学习概览 |

证据：`research/midoo-ui/screens/`、`previews/`、`PAGE_MAP.md`。

---

## 3. 令牌摘要

| 令牌 | 值 | 用途 |
| --- | --- | --- |
| `--md-bg` / gradient | `#E8E6F6` + 多停靠渐变 | 画布 |
| `--md-surface` | `rgba(255,255,255,.88)` | 毛玻璃卡 |
| `--md-accent` | `#6B8CFF` | 选中描边 / 小徽章 |
| `--md-accent-2` | `#9B7BFF` | 渐变尾 |
| `--md-cta-gradient` | `#7EB6FF → #B49CFC` | 主按钮 |
| `--md-blur-glass` | `20px` | 底栏/玻璃 |
| `--md-press-scale` | `0.96` | 按压 |
| `--md-duration*` | 170 / 260 / 360ms | 动效合同 |

---

## 4. 组件（`md-*`）

| 组件 | 说明 |
| --- | --- |
| `md-app` | 渐变画布壳 |
| `md-topbar` | 手写标题 + 侧按钮 |
| `md-card` / `md-glass` | 白卡 / 毛玻璃 |
| `md-progress` | 胶囊进度 |
| `md-mode` | 三模式选择卡 |
| `md-cta` | 渐变主按钮 |
| `md-step` | 课程步骤条 |
| `md-hero-card` | 对话角色大卡 |
| `md-chip` / `md-pill` | 玻璃标签 / 分类 |
| `md-masonry` | 趣玩瀑布 |
| `md-vip` / `md-metric` | 会员与学习概览 |
| `md-bottom-nav` | 浮层毛玻璃 5 Tab |
| `md-blur-text` | 防剧透（合同保留；真机少见） |
| `md-pressable` / `md-fade-up` / `md-sheet` | 标准化动效 |

---

## 5. 动效 / 特效（对齐 MOTION.md）

| 行为 | 实现 |
| --- | --- |
| 按压 | `.md-pressable:active` → `scale(var(--md-press-scale))`，`--md-duration-fast` |
| 入场 | `.md-fade-up` |
| Sheet | `.md-sheet.is-open` + `.md-scrim`，`--md-duration-slow` |
| 玻璃 | `--md-blur-glass` + saturate |
| 无障碍 | `prefers-reduced-motion: reduce` 关闭动画/过渡 |

---

## 6. 使用方式

```html
<html data-md-theme="light">
  <link rel="stylesheet" href="tokens.css" />
  <link rel="stylesheet" href="components.css" />
  <link rel="stylesheet" href="phone.css" />
```

橱窗：`showcase.html`。  
正式 feature：人选 `visual.baseline: midoo`，复制或软引本目录到原型可解析路径。
