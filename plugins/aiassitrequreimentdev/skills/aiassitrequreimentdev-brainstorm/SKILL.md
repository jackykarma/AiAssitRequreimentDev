---
name: aiassitrequreimentdev-brainstorm
description: 产品 Brainstorm Agent。输入只有一句话或模糊想法时，先探索意图、约束与 2～3 种方案取舍，再交给 grill/产品出 PRD。不要在此阶段写代码或冻规格。
---

# Brainstorm（意图与方案探索）

在 `aiassitrequreimentdev-grill` / `aiassitrequreimentdev-product` **之前**使用。本技能只做探索与对齐，**不**写 `spec.yaml`、不改源码、不声称 G1 通过。

也可参考仓库外 Superpowers 的 `brainstorming` 习惯（一次一问、先设计后实现）；本仓库正式产物仍落在 `requirements/` 或 `features/*/prd.md`，不要把设计稿当成门禁合同。

## 何时启用

- 只有一句话、口号或模糊痛点
- 多个可能方向尚未选型
- 大需求还不知道该不该拆、往哪拆

## 流程

1. 扫一眼 `BOARD.md`、插件 `references/`（若业务仓有 `modus/knowledge/` 可作域补充）、邻近 feature（若有）。
2. 一次一个问题，弄清：目的、用户、约束、成功标准。
3. 给出 **2～3 个方案**（含取舍与推荐），等人选或改。
4. 按块陈述「当前理解的设计」（问题、用户、范围草图、主旅程草图），每块等人点头。
5. 自检：无占位糊弄、无自相矛盾、范围是否过大（过大则先帮拆成可讨论的能力块）。
6. **交接**：启用 `aiassitrequreimentdev-grill` 把草图压成可编号清单，再由 `aiassitrequreimentdev-product` 写 PRD/原型/spec。

## 禁止

- 未获人认可就写死 `spec.yaml` 或清空 `openQuestions`
- 跳过 grill 直接实现或拆 `tasks.yaml`
- 用长篇一次性问卷淹没产品经理
