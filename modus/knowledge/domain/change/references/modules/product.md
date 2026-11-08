# 产品模块

技能：`aiassitrequreimentdev-product`。由产品经理用自然语言驱动。

## 职责

通过对话 grill 澄清需求，交付：

1. `prd.md`：给人评审的产品需求文档
2. `prototype/**/*.html`：可本地打开的点击原型（无 UI 须在 PRD 声明）
3. `spec.yaml`：带 `S*` / `A*` 的结构化规格（G1 / 下游 Agent）

`prd.md` 与 `spec.yaml` 同源同口径，都要；不要用对话草稿文件代替。

## 边界

- 不改源码，不改 `state.json`
- 不写 `ux.yaml` / `tech.yaml`；视觉精修交给交互视觉
- 不编造答不出的业务决策；写入 `openQuestions`

## 完成

`python -m aiassitrequreimentdev check <feature 目录> --gate G1` 输出 `G1 ready`，且 PRD 与原型约定已齐。
