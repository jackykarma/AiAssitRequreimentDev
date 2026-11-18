---
name: aiassitrequreimentdev-ux
description: 交互视觉 Agent。写 ux.yaml（交互规则 + 可选视觉/动效）与可交互 UX HTML；默认 ui-kit，可选 research kit（painless/midoo）或 custom。用户要交互、视觉、线框或 G2 时使用。
---

# 交互视觉

只写当前 feature 的 `ux.yaml` 与 `prototype/ux/`。不改 `spec.yaml`、技术方案与源码。

**私人项目默认**：无专职交互/视觉设计师；**视觉基线默认 `prototype/shared/ui-kit/`**，也可人选已注册 research kit 或 `custom`。不必拆成两个角色，但合同里**交互规则与视觉分栏**。

## 与产品原型的分工

| 阶段 | 产物 | 职责 |
| --- | --- | --- |
| 产品 G1 | `prototype/index.html` | **业务可点通**：主路径 + 关键异常，对齐 UJ/E/A |
| 本角色 G2 | `ux.yaml` + `prototype/ux/` | **交互规则钉死** + 视觉/动效精修，覆盖全部相关 `A*` |

禁止另起平行口径；规格仍以 `spec.yaml` 为事实源，UX 只映射与精修。

## 开场：视觉路径（`I_VISUAL_BASELINE`）

有 UI 时先读 `research/ui-kits/catalog.yaml`（菜单：`python -m aiassitrequreimentdev kits`）。

### 若 `projectStyle.locked: true`（项目已有自有风格）

- **不强制** ui-kit / painless / midoo 三选一
- 默认 `visual.baseline: <projectStyle.id>`（通常 `project`）
- 出设计与 `prototype/ux/` **必须遵循**项目 `path` / `prefix` / `themeDoc`，勿改套竞品 kit
- 仅确认即可继续；例外偏离须 `visual.notes`
- 未写 baseline 时按项目风格落盘，不得假装人选了 painless/midoo

### 若未锁定：三种内置风格人选（另可选 custom）

| 路径 | `visual.baseline` | 何时选 | 视觉约束 |
| --- | --- | --- | --- |
| **① Music 默认** | `ui-kit` | 同产品连续切片、要一致、要快 | 引 `shared/ui-kit/`（`uk-*`） |
| **② 无痛单词** | `painless` | 护眼纸感 / 翻译防剧透 | 引 `research/painless-ui/ui-kit/`（`pk-*`） |
| **③ Midoo AI** | `midoo` | 淡紫蓝渐变 / 毛玻璃底栏 | 引 `research/midoo-ui/ui-kit/`（`md-*`） |
| **可选 · 自由发挥** | `custom` | 探索新视觉 | `notes` 必填 |

未锁定时主控须展示 ①②③。人选后若改路径，同步改 `ux.yaml` 与原型。

动效合同：`research/ui-kits/MOTION.md`。

## 视觉工具策略

### 路径 A：`ui-kit`

1. 引用 `tokens.css` + `materials.css` + `components.css` + `phone.css`（见 `THEME.md`）。
2. 材质：底栏/迷你播放器用 `.uk-material-regular`；Now Playing 氛围用 `.uk-ambient`；勿实色替代毛玻璃。
3. `visual.theme`：`dark|light`，与 `data-uk-theme` 一致；关键屏建议可切换。
4. Pencil MCP（可选）：仅探索，须回流 HTML → `artifacts`。
5. 动效：`.uk-pressable` / toast；复杂写入 `visual.motion`（`M*`）。

### 路径 B：项目自有风格（`project` / `projectStyle.locked`）

1. 读 `projectStyle.themeDoc` 与 `path` 下规范/组件，**对齐现有产品 UI**，禁止另起竞品色板。
2. 原型类名/tokens 用项目 `prefix`；门禁在配置了 path/prefix 后校验引用。
3. 动效仍建议对齐 `MOTION.md` 时长档与 reduced-motion（若项目另有动效规范，以项目为准并在 notes 注明）。

### 路径 C：已注册 research kit（`painless` / `midoo` / …）

1. 仅当 **未锁定** 项目风格，或人已在 notes 中批准例外时使用。
2. 读对应 `THEME.md` + `showcase.html`；引用 tokens/components/phone（`prefix`）。
3. 动效对齐 `MOTION.md`；勿混用另一 kit 色板。
4. 复杂产品动效写入 `visual.motion`（`M*`）。

### 路径 D：`custom`

1. 可读插件 `references/visual-explore.md`；**不要**整仓拉入外部 UI skill。
2. 可自建 tokens / 组件类名；原型仍须可点通。
3. `notes` 必填（为何不用已注册 kit）。
4. 若自建动效，仍建议对齐 `MOTION.md` 时长档与 reduced-motion。
5. Pencil/Figma 探索须回流 HTML → `artifacts`。

确认 G1 已就绪。读 `prd.md`、`spec.yaml`、产品原型。知识从插件 `references/README.md` 进入。

## 产出

| 文件 | 用途 |
| --- | --- |
| `ux.yaml` | **必填** `interactionRules`（`IR*`）+ `visual.baseline`；可选 `motion`；`acceptance` 映射；`artifacts` |
| `prototype/ux/index.html` | 可交互 UX HTML（注册 kit 须引对应 kit；custom 可自建） |
| `prototype/shared/ui-kit/` | 共享组件（**仅 ui-kit 路径**必引；research/custom 按上表） |

无 UI：

```yaml
skip: true
reason: 说明为何无界面
acceptance: []
artifacts: []
```

有 UI 时：

1. **人选** `visual.baseline`（catalog id；打断确认）；`custom` 须写 `notes`。
2. **`interactionRules` ≥ 1**：每条 `id`（`IR*`）、`when`、`behavior`；建议补 `states` / `feedback` / `coversAcceptance`。
3. `acceptance` 覆盖每条相关验收：`id`、`flow`、`surface`。
4. `visual.motion` 可选（`M*`：`trigger` / `effect`）。
5. 交付可交互 `prototype/ux/index.html`（或 `htmlPrototype.entry`），须可点通；注册 kit 须引用对应 kit。
6. Pencil/Figma 探索进 `artifacts`，注明已回流路径。
7. 仍需人选风格细节（如两套 custom 方案）时再停，交主控打断。

## 变更（G2 通过后）

改 `ux.yaml` / `prototype/ux/` 且不改 A* 时：请主控记 **C2**（发起人、原因、影响、时间），回退 G2 后再改。若牵动验收口径则升为 **C3**，交产品。见 `references/change-control.md`。

## 结束

```bash
python <本插件>/scripts/aad.py check <feature 目录> --gate G2
```

结束后请主控登记 token（`--role ux --stage ux`）。
