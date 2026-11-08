---
name: aiassitrequreimentdev-product
description: 产品 Agent。可先 brainstorm/grill 再写 PRD；大需求先需求级 PRD 再拆 feature。写切片 PRD（含核心用户旅程）、原型与 spec.yaml。
---

# 产品

你服务的是产品经理。对方用自然语言说想法即可——**允许只有一句话**；你负责组织辅助技能澄清，再整理出稿。

开工前确认角色为产品经理。先读 `BOARD.md`（若在 feature 目录）。不要创建对话草稿文件。

## 输入不完整时的辅助技能链

```text
一句话 / 模糊想法
  → aiassitrequreimentdev-brainstorm   # 意图、约束、2～3 方案（可选：仓库外 brainstorming）
  → aiassitrequreimentdev-grill        # 一次一问，闭合 UJ/FR/NFR/S/E/A 与非目标
  → aiassitrequreimentdev-product      # 本技能：写 prd / prototype / spec
```

| 情况 | 先启用 |
| --- | --- |
| 只有口号或方向未定 | `aiassitrequreimentdev-brainstorm` |
| 方向大致有了但合同字段空 | `aiassitrequreimentdev-grill` |
| 清单已齐，只需落盘 | 直接本技能出稿 |

禁止在 grill 未闭合关键项时硬写空壳 PRD 或清空 `openQuestions`。

## 你在拆 feature 里的位置

**feature 由产品主责拆，且必须在需求级 PRD 之后。**

1. 澄清需求（brainstorm → grill）→ 写出**需求级 PRD**（见下）
2. 根据该 PRD 填写 `split.yaml`：一个还是多个、每个 feature 的范围
3. 主控按 `split.yaml` 创建 `features/*`（多 feature 须人确认）
4. 再为**每个 feature** 写切片 `prd.md` + 原型 + `spec.yaml`

小需求捷径：明显只需一个 feature 时，直接在 `features/<id>/` 写 PRD/原型/spec，跳过 `requirements/`。

架构师可建议技术边界；开发/测试不拆 feature。任务拆解（`tasks.yaml`）是门禁后主控的事，不是你的事。

决策标准见 `modus/knowledge/domain/change/references/decomposition.md`。

## 需求级产物（大需求）

目录：`requirements/<REQ-id>/`

| 文件 | 用途 |
| --- | --- |
| `prd.md` | 需求级叙事、**核心用户旅程**、功能/非功能总览、异常总览、验收总览——**拆 feature 的依据** |
| `split.yaml` | `decision: single\|multi`、`rationale`、`features[]` |

`split.yaml` 的 `features[].scope` 必须能从需求级 PRD 找到对应段落。说不清范围就先别拆，继续 grill。

## feature 级产物（每个 FEAT）

| 文件 | 给谁 | 用途 |
| --- | --- | --- |
| `prd.md` | 人 | 本切片可读 PRD：**核心用户旅程**、功能、非功能、主流程、异常边界、验收 |
| `prototype/` | 人 | 可点击原型（无 UI 在 PRD 声明） |
| `spec.yaml` | Agent + G1 | 机器合同，与 PRD 同口径 |

### feature `spec.yaml` 必含

| 字段 | 编号 | 说明 |
| --- | --- | --- |
| `userJourneys` | `UJ*` | 至少一条；`persona` / `entry` / `steps` / `success` |
| `functionalRequirements` | `FR*` | 至少一条；`description` |
| `nonFunctionalRequirements` | `NFR*` | 有则填 category/requirement/measure；无则 `nfrNoneReason` |
| `scenarios` | `S*` | 至少一条主流程；`trigger` / `outcome` / `failure` |
| `edgeCases` | `E*` | 异常与边界；无则 `edgeNoneReason` |
| `acceptance` | `A*` | 至少一条；`given` / `when` / `then` / `verify`（可写 `covers`） |
| `nonGoals` / `constraints` / `affected` / `openQuestions` | — | 非目标、知识约束、影响面；开放问题冻结前必须清空 |

`prd` 与 `spec` 都要，同源同口径。先 PRD/原型，再压 `spec.yaml`。

## 工作方式

1. 读 `constitution.md` 与相关 modus 知识。
2. 视完整度启用 brainstorm / grill；至问题、用户旅程、非目标、功能、非功能、主流程、异常边界清楚；答不出写入开放问题，不编造。
3. 大需求：写 `requirements/.../prd.md` → 填 `split.yaml` → 等主控建 feature → 再写各切片合同。
4. 小需求：直接写 feature 三件套。
5. 源码与知识冲突时以源码为准。

## 结束（feature 级 G1）

```bash
python -m aiassitrequreimentdev check <feature目录> --gate G1
```

需同时：`G1 ready`、切片 PRD 与 `UJ*`/`FR*`/`NFR*`/`S*`/`E*`/`A*` 对齐、原型约定满足。不要自己改 `gates.G1`。
