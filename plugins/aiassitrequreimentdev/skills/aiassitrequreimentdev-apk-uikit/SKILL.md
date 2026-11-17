---
name: aiassitrequreimentdev-apk-uikit
description: >-
  通过 Android 应用包名用 ADB 抓取页面截图与 UI 层级，归纳视觉风格并生成可复用 ui-kit
 （THEME/tokens/components/showcase）。用户提供包名、要竞品/对标 App 视觉规范、抓取全部页面做
  UI kit、或提到 adb/uiautomator/apk-uikit 时使用。
---

# APK → UI Kit

将**已安装且用户已授权 ADB 的 Android 应用**，从包名自动抓取页面并产出风格化 ui-kit。  
参考实现：`research/painless-ui/`（`tech.xiangzi.painless`）。

## 何时启用

- 用户给出包名（如 `tech.xiangzi.painless`）并要求抓页面 / 做 ui-kit
- 竞品视觉对标、自定义 `visual.baseline: custom` 前要先沉淀 kit
- 「把某某 App 的 UI 风格组件化」

## 输入

| 项 | 必填 | 说明 |
| --- | --- | --- |
| `package` | 是 | 应用包名 |
| `out` | 否 | 默认 `research/<short-name>-ui/` |
| `max_pages` | 否 | 默认 40 |
| `kit_prefix` | 否 | CSS 前缀，默认从包名末段生成（如 `pk`） |

用户只给包名时：先确认设备已 `adb devices` 为 `device`（非 unauthorized），再开跑。

## 硬约束（防误点其他 App）

1. **每次 tap / swipe 前后**校验 `mCurrentFocus` / `mFocusedApp` 含目标 `package`
2. 焦点丢失 → **立即停止**，勿继续盲点；可 `monkey -p <pkg> -c LAUNCHER 1` 拉回后再问人
3. **优先点本包 `resource-id` / `content-desc`**；禁止扫系统手势条、通知栏、最近任务
4. 非本包窗口（其它 App、桌面）的截图/XML → 移入 `_invalid_other_app/`，**禁止**写入 kit
5. 截图必须用二进制写出（Python `adb exec-out screencap -p`），禁止 PowerShell `>` 重定向 PNG
6. MainActivity 常 `exported=false`：用 `monkey -p <pkg> -c android.intent.category.LAUNCHER 1` 启动

## 标准流水线

技能根目录（脚本/参考）：

- 仓内：`plugins/aiassitrequreimentdev/skills/aiassitrequreimentdev-apk-uikit/`
- 同步后：`.cursor/skills/aiassitrequreimentdev-apk-uikit/`（以插件为准）

```text
Task Progress:
- [ ] 1. 探测：devices / pm path / versionName / LAUNCHER
- [ ] 2. 抓取：capture_app_ui.py → screens + ui + previews + pages_index.json
- [ ] 3. 清洗：PAGE_MAP.md；隔离非本包证据
- [ ] 4. 分析：analyze_palette.py + 读关键预览（模糊/材质/圆角等）
- [ ] 5. 脚手架：scaffold_uikit.py → ui-kit/
- [ ] 6. 精修：按真机补组件（blur spoiler、FAB、dock…）+ showcase 可点揭晓
- [ ] 7. 交付：路径 + 气质摘要 + 未覆盖页清单
```

### 1) 探测

```bash
adb devices -l
adb shell pm path <package>
adb shell dumpsys package <package> | findstr /i "versionName LAUNCHER Activity"
```

### 2) 抓取（执行脚本，勿手写脆弱循环）

```bash
python plugins/aiassitrequreimentdev/skills/aiassitrequreimentdev-apk-uikit/scripts/capture_app_ui.py \
  --package <package> \
  --out research/<short>-ui \
  --max-pages 40
```

脚本行为：启动 App → dump 层级 → 发现底栏 Tab / 可点控件 → **包名锁**下遍历 → `screens/*.png` + `ui/*.xml` + `previews/*.jpg` + `pages_index.json`。

深层页抓不全时：**请用户在本 App 内手动打开**，再跑：

```bash
python .../capture_app_ui.py --package <package> --out <out> --once <name>
```

### 3) 清洗

写 `PAGE_MAP.md`：有效页 vs `_invalid_other_app/`。只认焦点含包名的证据。

### 4) 分析

```bash
python .../scripts/analyze_palette.py --screens <out>/screens --out <out>/palette.json
```

人工必看（读预览图）：主色、圆角、卡片、底栏、**模糊防剧透**、毛玻璃、双语层级。细则见 [references/methodology.md](references/methodology.md)。

### 5) 脚手架

```bash
python .../scripts/scaffold_uikit.py \
  --out <out>/ui-kit \
  --prefix <kit_prefix> \
  --palette <out>/palette.json \
  --pages <out>/pages_index.json \
  --app-name "<显示名>" \
  --package <package>
```

产出合同见 [references/output-contract.md](references/output-contract.md)。

### 6) 精修（Agent 必做）

脚手架只给骨架。须对照截图补齐：

- 特殊交互：`filter: blur()` 翻译防剧透（`.{prefix}-blur-text` + `.is-revealed`）
- 浮层 dock / FAB / CEFR badge / 设置分组彩标等
- `showcase.html` 覆盖主要信息架构屏，模糊区可点击揭晓

### 7) 与本仓 UX 衔接

- 探索/竞品 kit：留在 `research/<short>-ui/ui-kit/`
- 若产品选用该风格：复制或软引到 feature 的 `prototype/shared/ui-kit/`，`ux.yaml` 中 `visual.baseline: custom`，`notes` 写明来源包名与路径

## 禁止

- 反编译 APK 偷资源/字体文件当「官方 kit」
- 焦点不在目标包时继续自动点击
- 把其它 App 截图写进 THEME/组件
- 宣称「已抓尽所有页面」却未列未覆盖项

## 额外参考

- [references/methodology.md](references/methodology.md) — 方法论与失败教训
- [references/output-contract.md](references/output-contract.md) — 目录与文件合同
- 范例：`research/painless-ui/ui-kit/`
