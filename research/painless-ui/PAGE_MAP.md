# 无痛单词页面抓取图（仅 tech.xiangzi.painless）

包名：`tech.xiangzi.painless` · 版本：4.6.3 · 入口：`SplashActivity` → `MainActivity`

## 有效页面（包名已校验）

| 预览 | 页面 | Activity / 形态 |
| --- | --- | --- |
| `previews/50_tab_words.jpg` | 单词 Tab · 语境名言卡 | MainActivity |
| `previews/51_tab_read.jpg` | 阅读 Tab · 文章列表 | MainActivity |
| `previews/52_tab_search.jpg` | 搜索 Tab · 随身听 | MainActivity |
| `previews/53_tab_stat.jpg` | 图表 Tab · 统计 | MainActivity |
| `previews/54_tab_setting.jpg` | 设置 Tab | MainActivity |
| `previews/71_read_article.jpg` | 文章正文 + 朗读/生词表/翻译 | ArticleDetailActivity |
| `previews/20_read_explore.jpg` | 单词详情（Mnemonic 等） | WordDetailActivity |
| `previews/61_words_tag_tap.jpg` / `01_tab_words` dump | 词气泡 Popup | PopupWindow |
| `previews/100_setting.jpg` | 设置列表文案完整 | MainActivity |

## 作废（误入其他 App，勿用）

以下截图/XML **不是**无痛单词，已识别为微信读书等，分析与 ui-kit **不采用**：

- `120_setting_base*`
- `121_setting_y*`
- `122_setting_scrolled2*`
- `123_theme_or_row*`（若存在）

原因：设置页曾用屏幕 Y 坐标盲点，焦点离开 `tech.xiangzi.painless`。

## 抓取约束（后续）

1. 每次 tap 前：`mCurrentFocus` / `mFocusedApp` 必须含 `tech.xiangzi.painless`
2. 只通过本包 `resource-id`（如 `tab_home` / `tag_tv`）点击
3. 禁止盲点系统手势区、通知、最近任务
4. 若焦点丢失：立刻停止，重新 `monkey -p tech.xiangzi.painless -c LAUNCHER 1`
