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

若想法还很发散，先用 `aiassitrequreimentdev-brainstorm`（或仓库外的 `brainstorming`）探索意图与方案取舍，再回到本技能。

## 追问原则

1. **一次只问一个问题**；优先选择题，必要时开放题。
2. 不编造业务决策；答不出 → 记入开放问题，标明阻塞级别。
3. 先边界后细节：问题 → 用户 → 成功标准 → 范围/非目标 → 旅程 → 功能 → 非功能 → 异常 → 验收。
4. 与现有 `modus/knowledge/`、源码冲突时以源码为准并点名冲突。

## 必问清单（闭合前逐项打勾）

| 项 | 要问清什么 | 落入 |
| --- | --- | --- |
| 问题与成功 | 谁痛、做成什么样算成功 | PRD 背景 / 成功标准 |
| 用户与旅程 | 核心用户、端到端主路径（`UJ*`） | PRD 用户旅程；`spec.userJourneys` |
| 范围 | 做 / 不做 | `nonGoals` |
| 功能 | 可编号的能力（`FR*`） | `functionalRequirements` |
| 非功能 | 性能/功耗/稳定/安全等（`NFR*`）或明确无 | `nonFunctionalRequirements` / `nfrNoneReason` |
| 主流程 | 正常场景（`S*`）含失败时 | `scenarios` |
| 异常边界 | 超时、空态、权限、并发等（`E*`）或明确无 | `edgeCases` / `edgeNoneReason` |
| 验收 | 可执行 given/when/then/verify（`A*`） | `acceptance` |
| 原型 | 有无 UI、关键屏与异常示意 | `prototype/` 或 PRD 声明无 UI |

## 输出给产品技能的摘要

澄清够用后，用简短摘要交给 `aiassitrequreimentdev-product` 出稿，至少含：

- 已闭合项与编号草稿（`UJ*`/`FR*`/`NFR*`/`S*`/`E*`/`A*`）
- 仍开放的问题（须进 `openQuestions`）
- 建议：需求级 PRD + split，或小需求直开单个 feature

然后由产品技能写正式文件并跑 G1。
