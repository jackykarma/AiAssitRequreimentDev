# Painless UI Kit · 无痛单词风格归纳

> 来源：真机 `tech.xiangzi.painless` v4.6.3（PMA110）截图 + `uiautomator` 层级。  
> 用途：HTML 原型视觉基线（竞品风格参考，非官方 SDK / 资源还原）。  
> 抓取包名约束：**仅** `tech.xiangzi.painless`。

---

## 1. 气质原则

| 原则 | 做法 |
| --- | --- |
| 护眼纸感画布 | 主背景浅橄榄米白 `#F0F5E7`，少用纯白满屏 |
| 大圆角白卡片 | 内容落在白卡片上，圆角约 20–28px，轻阴影或无阴影 |
| 苔藓绿主色 | 选中 Tab / 播放 / 返回箭头 / 词高亮 ≈ `#7BA23A`–`#8FBC4A` |
| 软彩点缀 | 橙（难度/强调）、黄（收藏）、蓝（翻译/搜索）、粉红（移除）低饱和底 |
| 双语层级 | 英文主文深色；中文翻译明显变淡（灰） |
| 翻译防剧透 | 不想先看的中译/释义用 **高斯模糊盖住**，点按揭晓（非马赛克、非纯隐藏） |
| 呼吸留白 | 卡片间距大，信息块垂直堆叠，避免密列表压迫感 |
| 线型图标 | 底栏未选中细线灰图标；选中实心/着色绿 |

---

## 2. 信息架构（已证实页面）

底栏 5 Tab（`bottomNav`）：

| Tab | id | 主界面 |
| --- | --- | --- |
| 单词 | `tab_home` | 名言/语境卡片 + 词 tag + 右列 FAB（分享/发音/图表） |
| 阅读 | `tab_read` | 文章卡片列表（标题/摘要/词 tag/Public Reads/CEFR） |
| 搜索 | `tab_search` | 搜索框 +「随身听」播放卡片 |
| 图表 | `tab_stat` | 统计/进度/分布/今日/连胜卡片；子 Tab「统计」「榜单」 |
| 设置 | `tab_setting` | 会员卡 + 分组列表（学习/外观/帮助） |

关键子页：

- 词气泡 `PopupWindow`：词头、音标、释义、移除/收藏  
- `WordDetailActivity`：词频/难度、CEFR/TOP、Mnemonic、Root and Affix  
- `ArticleDetailActivity`：双语阅读 + 浮层工具「朗读 / 生词表 / 翻译」

证据目录：`research/painless-ui/screens/`、`previews/`、`ui/`。

---

## 3. 色彩令牌（采样归纳）

### 画布与表面

| 令牌 | 值 | 用途 |
| --- | --- | --- |
| `--pk-bg` | `#F0F5E7` | 主画布（多页稳定采样） |
| `--pk-bg-stat-top` | `#F1F9FC` | 统计页顶部偏冷渐变起点 |
| `--pk-surface` | `#FFFFFF` | 卡片 |
| `--pk-surface-recessed` | `#F5F5F3` | 随身听内凹展示区 |
| `--pk-scrim` | `rgba(0,0,0,.45)` | 词气泡遮罩 |

### 墨色

| 令牌 | 值 | 用途 |
| --- | --- | --- |
| `--pk-ink` | `#1C1C1E` | 主标题/英文正文 |
| `--pk-ink-secondary` | `#8E8E93` | 摘要、元信息 |
| `--pk-ink-muted` | `#A8A8A0` | 中文翻译、placeholder |
| `--pk-ink-inverse` | `#FFFFFF` | 深色徽章上的字 |

### 品牌与功能色

| 令牌 | 值 | 用途 |
| --- | --- | --- |
| `--pk-accent` | `#7BA23A` | 主绿（Tab 选中、播放、返回） |
| `--pk-accent-soft` | `#E4F0D4` | 绿底按钮/词高亮 |
| `--pk-accent-press` | `#62862E` | 按下 |
| `--pk-warn` | `#F5A623` | B2 / 强调橙 |
| `--pk-warn-deep` | `#E86A2A` | C1 深橙 |
| `--pk-warn-soft` | `#FDE8D4` | 橙 tag 底 |
| `--pk-ok` | `#8BC34A` | A2 / 已掌握 |
| `--pk-info` | `#5B9BD5` | 翻译/信息蓝 |
| `--pk-info-soft` | `#E3F0FA` | 蓝软底 |
| `--pk-danger-soft` | `#F8E0DE` | 移除 |
| `--pk-star-soft` | `#F8F0C8` | 收藏 |
| `--pk-line` | `rgba(60,60,67,.12)` | 分割线 |

### CEFR / 掌握度

| 级别/状态 | 色 |
| --- | --- |
| A2 | `#8BC34A` |
| B2 | `#F5A623` |
| C1+ | `#E86A2A` |
| Mastered / Known / Fuzzy / Stranger / ToLearn | 深绿 → 浅绿 → 黄 → 橙 → 灰 |

---

## 4. 字体与间距

- 字体：系统无衬线（中文优先 PingFang / 思源；英文 SF / Roboto 回退）  
- 词头可略偏展示感（大号 semibold/bold）  
- 字号阶梯：11 / 13 / 15 / 17 / 20 / 28 / 34  
- 间距：4 / 8 / 12 / 16 / 20 / 24 / 32  
- 圆角：8（小控件）/ 12（按钮）/ 16（tag）/ 24（卡片）/ 999（pill）

---

## 5. 组件清单（`pk-*`）

| 组件 | 说明 |
| --- | --- |
| `pk-app` | 护眼画布壳 |
| `pk-topbar` | 居中标题 + 左返回（绿色线箭头） |
| `pk-card` | 大圆角白卡片 |
| `pk-quote-card` | 名言语境卡（大引号 + 双语 + 作者） |
| `pk-word-tag` | 当前词 chip |
| `pk-fab-col` | 右侧圆形 FAB 列 |
| `pk-bottom-nav` | 5 Tab 线图标底栏 |
| `pk-search` | 圆角搜索框 |
| `pk-player-card` | 随身听播放卡 |
| `pk-article-card` | 阅读列表卡 + CEFR badge + 词 tags |
| `pk-level-badge` | A2/B2/C1 pill |
| `pk-stat-grid` | 统计小指标软彩 pill |
| `pk-settings-group` | 设置分组列表 + 左彩标图标 |
| `pk-word-sheet` | 底部词气泡 |
| `pk-tool-dock` | 阅读页浮层三按钮（朗读/生词表/翻译） |
| `pk-hl` | 文内词高亮/下划线 |
| `pk-blur-text` | 翻译/释义防剧透模糊；`.is-revealed` 揭晓 |
| `pk-label-pill` | 小节标签（如 italic `translation` / `adverb` 黑底白字） |

### 模糊规则（必对齐真机）

| 场景 | 类名 | 模糊强度 | 交互 |
| --- | --- | --- | --- |
| 例句下方中文整句 | `pk-blur-text` | `--pk-blur-spoiler` ≈ 7px | 点击该行揭晓 |
| `translation` 下的词性释义（如 adv. 智力上） | `pk-blur-text pk-blur-text--strong` | ≈ 10px | 点击揭晓 |
| 首页名言卡中译（可选更轻） | `pk-blur-text pk-blur-text--soft` | ≈ 4px | 点击揭晓 |

实现要点：

- 用 CSS `filter: blur(...)` 盖在**真实文字**上（隐约可见字形轮廓，不是 `visibility:hidden`）
- `user-select: none`；揭晓后加 `.is-revealed`（`filter: none`）
- 过渡：`filter` + 约 220ms
- 真机证据：`20_read_explore.png` 例句中译与 `translation` 释义区

---

## 6. 动效 / 特效（对齐 `research/ui-kits/MOTION.md`）

| 令牌/类 | 值 | 用途 |
| --- | --- | --- |
| `--pk-ease` | `cubic-bezier(0.22,1,0.36,1)` | 标准缓动 |
| `--pk-duration` / `fast` / `slow` | 240 / 160 / 360ms | 通用 / 按压 / sheet |
| `--pk-press-scale` | `0.96` | `.pk-pressable:active` |
| `--pk-blur-glass` | `18px` | 可选玻璃表面 |
| `--pk-blur-spoiler*` | 4 / 7 / 10px | 防剧透 |
| `.pk-fade-up` | 入场 | 列表卡可选 |
| `prefers-reduced-motion` | 关动画/过渡 | 无障碍必含 |

- 底栏切换：图标着色，无夸张动效  
- 词气泡：自下而上 sheet + scrim（`--pk-duration-slow`）  
- **翻译模糊揭晓**：blur → sharp，约 `--pk-duration`

人选 id：`visual.baseline: painless`（见 `research/ui-kits/catalog.yaml`）。

---

## 7. 使用方式

```html
<html data-pk-theme="light">
  <link rel="stylesheet" href="tokens.css" />
  <link rel="stylesheet" href="components.css" />
  <link rel="stylesheet" href="phone.css" />
```

橱窗：`showcase.html`。  
正式 feature：人选 `visual.baseline: painless`，复制或软引本目录；勿再仅用 `custom` + notes 代替已注册 kit。
