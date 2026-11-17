# 产出目录合同

```text
research/<short>-ui/
  app_meta.json
  pages_index.json
  discovered_tabs.json
  PAGE_MAP.md
  palette.json
  screens/*.png
  previews/*.jpg
  ui/*.xml
  _invalid_other_app/          # 非目标包证据隔离
  ui-kit/
    THEME.md
    tokens.css
    components.css
    phone.css
    showcase.html
```

## 文件职责

| 路径 | 职责 |
| --- | --- |
| `app_meta.json` | 包名、versionName |
| `pages_index.json` | 每次 capture 的 focus/sha1/文件名 |
| `PAGE_MAP.md` | 人读图鉴：有效页 / 作废页 / 未覆盖 |
| `palette.json` | 自动色采 + roles 启发式 |
| `ui-kit/THEME.md` | 气质、令牌表、组件清单、模糊规则 |
| `ui-kit/tokens.css` | `--{prefix}-*` |
| `ui-kit/components.css` | `.{prefix}-*`（含 blur-text） |
| `ui-kit/showcase.html` | 可切换/可点揭晓橱窗 |

## 命名

- 抓取：`00_home`、`10x_tab_*`、`2xx_*` 子页、`--once` 自定义名
- CSS 前缀：短小写，如 `pk`、`nm`；勿与本仓默认 `uk-`（Apple Music kit）混淆
- 类名：`{prefix}-blur-text`、`is-revealed` 为防剧透约定

## 完成定义

- [ ] 至少覆盖全部底栏 Tab（若有）
- [ ] PAGE_MAP 标明未覆盖深层页
- [ ] showcase 能体现主色/卡片/底栏
- [ ] 若真机有翻译模糊，kit 必须有 blur 组件与演示
- [ ] `_invalid_other_app` 不参与 THEME
