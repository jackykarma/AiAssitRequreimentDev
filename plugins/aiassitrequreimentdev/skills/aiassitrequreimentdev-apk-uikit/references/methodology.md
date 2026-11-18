# APK → UI Kit 方法论

## 目标

从**用户手机上已安装的 App 包名**，用 ADB 拿到足够页面证据，归纳成 HTML 原型可用的 ui-kit（令牌 + 组件 + 橱窗），而不是还原官方设计系统源文件。

## 步骤心智模型

```text
包名 → 合法前台 → 页面图鉴 → 视觉事实 → 令牌/组件 → 橱窗验收
```

1. **合法前台**：所有自动化操作必须发生在目标 package 焦点内。
2. **页面图鉴**：截图 + uiautomator XML + 预览图 + PAGE_MAP。
3. **视觉事实**：色板采样只是起点；圆角、模糊、材质、双语层级要靠读图。
4. **令牌/组件**：先 scaffold，再按事实精修（blur、FAB、dock…）。
5. **橱窗验收**：关键屏可切换；防剧透模糊可点揭晓。

## 抓取策略

| 优先级 | 做法 |
| --- | --- |
| 1 | 用 `content-desc` / `resource-id`（含 `tab_*`）点底栏 |
| 2 | 本包 clickable 节点一层下钻（每 Tab 限次数） |
| 3 | 用户手动打开深层页 + `--once <name>` |
| 禁止 | 固定 Y 盲扫整屏、点系统手势区、跨 App |

启动：优先 `monkey -p <pkg> -c LAUNCHER 1`（MainActivity 常不 exported）。

截图：Python 二进制写 PNG；PowerShell `>` 会损坏文件。

## 分析清单（读预览时勾选）

- [ ] 画布色（是否护眼米绿/纯白/深色）
- [ ] 卡片圆角与阴影
- [ ] 主色 / 功能软彩（收藏黄、移除红、信息蓝）
- [ ] 底栏线图标 vs 选中色
- [ ] 标题字重与正文字号层级
- [ ] **模糊防剧透**（翻译/答案）强度与揭晓方式
- [ ] 毛玻璃 / scrim / 底部 sheet
- [ ] 列表卡结构（标题/摘要/tag/badge）

## 失败教训（必记）

1. **盲点 Y 坐标**易跳出目标 App（曾误入微信读书）→ 必须包名锁 + 失败即停。
2. **PopupWindow** 挡在 MainActivity 上时，Tab resource-id 可能 dump 不到 → 先 BACK 关掉。
3. **ADB unauthorized** 重启 server 后需手机再点允许。
4. 同图 hash 重复不要当成「新页面已覆盖」。

## 与需求流水线

- 产出默认在 `research/<app>-ui/`，不直接改 feature 门禁工件。
- 完成后登记 `research/ui-kits/catalog.yaml`，动效对齐 `research/ui-kits/MOTION.md`。
- UX 人选：`visual.baseline: <catalog.id>`；原型引用该 kit 的 tokens/components/phone。
