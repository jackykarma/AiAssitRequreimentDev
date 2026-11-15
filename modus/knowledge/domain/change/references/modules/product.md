# 产品模块

技能：`aiassitrequreimentdev-product`。由产品经理用自然语言驱动；输入可以不完整。

## 辅助技能

| 技能 | 何时 |
| --- | --- |
| `aiassitrequreimentdev-brainstorm` | 一句话 / 方向未定：探索意图与方案取舍 |
| `aiassitrequreimentdev-grill` | 系统追问，闭合旅程与 FR/NFR/E/A（S 可选） |
| （可选）仓库外 `brainstorming` | 习惯对齐；正式产物仍落本仓 PRD/spec |

链：`brainstorm` → `grill` → `product` 出稿。

## 职责

通过对话澄清后交付**一套事实源**（全流程角色共用）：

1. `prd.md`：人审；严格按模板章节；UJ / FR / NFR / E / A 与 spec 同编号
2. `prototype/**/*.html`：可交互；主路径 + 异常/空态；引 `shared/ui-kit/`
3. `spec.yaml`：机器合同；必含 `UJ*`/`FR*`/`NFR*`/`E*`/`A*`；`S*` 可选

原则：清晰无歧义、验收可执行、边界尽量全面；不写实现细节。G1 seal 前过人审 A*/verify 清单（covers 矩阵、then 可观察、verify 失败须非 0）。

大需求另写需求级 `requirements/REQ-<序号>-<名称>-<YYYYMMDD>/prd.md` + `split.yaml`。

## 边界

- 不改源码，不改 `state.json`
- 不写 `ux.yaml` / `tech.yaml`；视觉精修交给交互视觉
- 不编造答不出的业务决策；写入 `openQuestions`

## 完成

`python -m aiassitrequreimentdev check <feature 目录> --gate G1` 输出 `G1 ready`。
