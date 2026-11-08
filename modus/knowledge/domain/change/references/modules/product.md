# 产品模块

技能：`aiassitrequreimentdev-product`。由产品经理用自然语言驱动；输入可以不完整。

## 辅助技能

| 技能 | 何时 |
| --- | --- |
| `aiassitrequreimentdev-brainstorm` | 一句话 / 方向未定：探索意图与方案取舍 |
| `aiassitrequreimentdev-grill` | 系统追问，闭合旅程与 FR/NFR/S/E/A |
| （可选）仓库外 `brainstorming` | 习惯对齐；正式产物仍落本仓 PRD/spec |

链：`brainstorm` → `grill` → `product` 出稿。

## 职责

通过对话澄清后交付：

1. `prd.md`：给人评审（**核心用户旅程**、功能、非功能、主流程、异常边界、验收）
2. `prototype/**/*.html`：可本地打开的点击原型（无 UI 须在 PRD 声明）
3. `spec.yaml`：`UJ*` / `FR*` / `NFR*` / `S*` / `E*` / `A*`（G1 / 下游 Agent）

大需求另写需求级 `requirements/<REQ>/prd.md` + `split.yaml`。

`prd.md` 与 `spec.yaml` 同源同口径，都要；不要用对话草稿文件代替。

## 边界

- 不改源码，不改 `state.json`
- 不写 `ux.yaml` / `tech.yaml`；视觉精修交给交互视觉
- 不编造答不出的业务决策；写入 `openQuestions`

## 完成

`python -m aiassitrequreimentdev check <feature 目录> --gate G1` 输出 `G1 ready`，且 PRD 与原型约定已齐。
