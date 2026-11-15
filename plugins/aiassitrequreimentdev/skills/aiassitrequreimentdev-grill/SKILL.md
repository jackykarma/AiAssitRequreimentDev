---
name: aiassitrequreimentdev-grill
description: 产品 Grill Agent。在输入不完整时系统追问，补齐功能/非功能/用户旅程/异常边界/验收与非目标，直至可写 PRD。用户只丢一段话、开放问题未闭合或产品澄清卡壳时使用。
---

# Grill（需求澄清）

配合 `aiassitrequreimentdev-product` 使用。本技能**只负责追问与清单闭合**，不改源码；正式落盘仍由产品技能写 `prd.md` / `prototype/` / `spec.yaml`。

输入可能只有一句话或零散要点。禁止在关键项未闭合时宣称「规格已齐」。

## 何时启用

- 产品经理只给了概要 / 一句话需求
- `openQuestions` 非空或 PRD 仍有大片「待填写」
- Brainstorm 已定方向，需要压成可验收合同

若想法还很发散，先用 `aiassitrequreimentdev-brainstorm`，再回到本技能。

## 追问原则

1. **一次只问一个问题**；优先选择题。
2. 不编造业务决策；答不出 → 开放问题 + 是否阻塞。
3. 先边界后细节：问题 → 成功标准 → 范围/非目标 → 旅程 → **功能 → 非功能 → 异常（全面）→ 验收**。
4. 规格须**无歧义、可验收**；含糊词继续追问直到可写成 FR/A。
5. 与插件 `references/`、业务仓 `modus/`（若有）、源码冲突时以源码为准。

## 必问清单（闭合前逐项打勾）

| 项 | 要问清什么 | 落入 |
| --- | --- | --- |
| 问题与成功 | 谁痛、做成什么样算成功 | PRD 背景；`problem` |
| 用户与旅程 | 核心用户、端到端主路径（`UJ*`） | `userJourneys` |
| 范围 | 做 / 不做 | `nonGoals` |
| 功能 | 可编号、可测试（`FR*`） | `functionalRequirements` |
| 非功能 | 性能/功耗/稳定/安全等（`NFR*`）或明确无 | `nonFunctionalRequirements` / `nfrNoneReason` |
| 异常边界 | 空态/权限/弱网/重复/并发/生命周期/依赖失败等（`E*`） | `edgeCases` / `edgeNoneReason` |
| 验收 | given/when/then/verify（`A*`），覆盖 P0 的 FR/NFR/E | `acceptance` |
| 原型 | 有无 UI、主路径与异常屏 | `prototype/` 或无 UI 原因 |
| 补充场景 | 仅当多条并列主流程且 UJ 不够（`S*`，可选） | `scenarios` 可 `[]` |

## 输出给产品技能的摘要

澄清够用后，用简短摘要交给 `aiassitrequreimentdev-product`，至少含：

- 已闭合编号草稿（`UJ*`/`FR*`/`NFR*`/`E*`/`A*`，可选 `S*`）
- **covers 矩阵**：每条 P0 的 FR/NFR/E → 覆盖它的 `A*`；每条 A 的草稿 `verify`（具名用例/命令意向，禁止「待定」）
- 仍开放的问题（进 `openQuestions`）
- 建议：需求级 PRD + split，或小需求直开单个 feature

A 草稿自检：given/when/then 可观察；`verify` 须能回答「失败时谁非 0」。未闭合则不要宣称可写 PRD。

然后由产品技能写正式文件并跑 G1。
