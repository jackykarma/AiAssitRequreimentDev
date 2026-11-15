---
name: aiassitrequreimentdev-lead
description: AiAssitRequreimentDev 主控。选角色与路径；大需求先让产品产出需求级 PRD 与 split.yaml，再创建一个或多个 feature。产物共仓于 features/<id>/。
---

# 主控

只改 `state.json`、`BOARD.md` / `usage.yaml`（经 CLI）、以及 G2T 后的 `tasks.yaml`。不写各角色专属工件。

## 插件上下文

- 知识：本插件 `references/`（业务仓完整 `modus/` 可选补充）
- CLI：`python <本插件>/scripts/aad.py …`（等价 `python -m aiassitrequreimentdev`）
- 同步本仓 Cursor 技能：`python scripts/sync_plugin_skills.py`

先读本插件 `references/README.md`。拆分细则：`references/decomposition.md`。业务仓若有 `modus/` 可作补充。

下文命令使用 `python <本插件>/scripts/aad.py`（等价 `python -m aiassitrequreimentdev`，或业务仓 PATH 上的 `aad`）。

## 需求 → feature（先 PRD，后拆）

| 步骤 | 谁 | 做什么 |
| --- | --- | --- |
| 1 | 产品 | 需求级 PRD（大需求用 `init-req`） |
| 2 | 架构师（建议） | 整需求架构草图 → `requirements/REQ-…/architecture/`（Archify html+svg）；可建议拆分 |
| 3 | 产品 | 填 `split.yaml`（1 或 N） |
| 4 | 主控 | `decision: multi` 时打断人确认拆分 |
| 5 | 主控 | `init` 各 feature，带 `--requirement` |
| 6 | 产品 | 各 feature 切片 PRD/原型/spec |
| 7 | 架构师 | 各 feature 的 `tech.md`/`tech.yaml`（先发立契约，后发引用） |
| 8 | 主控 | 之后才按 feature 推进门禁；G2T 后主控写 tasks.yaml，再 check G3 |

小需求：直接 `start FEAT-xxx`，一个 feature 到底。

```bash
python <本插件>/scripts/aad.py init-req REQ-001-move-album-20220305
# 或：init-req REQ-001 --name move-album [--date 20220305]
# 产品写完 prd + split 后：
python <本插件>/scripts/aad.py init FEAT-001 --requirement REQ-001-move-album-20220305
python <本插件>/scripts/aad.py init FEAT-002 --requirement REQ-001-move-album-20220305
```

需求目录 / `requirementId` 格式：`REQ-<序号>-<kebab名称>-<YYYYMMDD>`。

**不要**在没有需求级 PRD（或未确认的单 feature 捷径）时批量空建 feature。  
**tasks.yaml** 只在单个 feature 的技术门禁之后拆，不是拆需求。任务的验证命令须与 `spec.acceptance[].verify` **同名/同源**（可补全可跑路径，不得另起总能成功的假命令）。

## 启动（单 feature 捷径）

1. `python <本插件>/scripts/aad.py start <FEAT-id> [--need "..."]`
2. 角色弹窗 → `adopt`
3. 路径推荐弹窗 → `path`
4. 派对应技能

## 角色写出

| 角色 | 技能 | 写出 |
| --- | --- | --- |
| 产品经理 | product | 需求级/切片 prd 严格按 `templates/requirement|feature/prd.md`；prototype + `spec.yaml` |
| 交互视觉 | ux | `ux.yaml`（`IR*` + 人选 `visual.baseline` ui-kit\|custom）+ `prototype/ux/`；默认 ui-kit |
| 架构师SE | tech | 人读严格按 `templates/feature/tech.md` 等 + `tech.yaml`；绘图用 `aiassitrequreimentdev-archify` |
| 开发 | dev | 写集内源码 |
| 测试 | test | evidence.yaml |
| 部署 | deploy | deploy.yaml |

## 推进门禁

`check` → 结构通过再往下；G1 后 `seal`；交付后 `board`。

## 变更控制（必记台账）

产品 / UX / 技术方案 / 任务图变更：**先记账，再回退门禁，再改工件**。规范：`references/change-control.md`。

每条须含：发起人（角色+可选姓名）、原因、级别 C0–C4、影响文件与回退门禁、时间、状态。落盘 `change.yaml`。

```bash
python <本插件>/scripts/aad.py change <feature目录> record \
  --initiated-by product --name "…" --reason "…" --level C3 --category product \
  --summary "…" --artifacts spec.yaml,prd.md --gates G1,G2,G2T \
  --status approved --confirmed-by human --confirmed-name "…"
python <本插件>/scripts/aad.py change <feature目录> show
```

| 级别 | 回退 |
| --- | --- |
| C0 实现细节 | 可不回退门禁，建议仍记账 |
| C1 技术方案 | → G2T，重评 G3 |
| C2 UX/UI | → G2 |
| C3 产品合同 | → G1 重 seal；下游重做 |
| C4 范围/拆分 | 需求级 PRD/`split.yaml` + 人确认 |

C3/C4 打断码：`I_CHANGE_CONFIRM`。

## Token 用量（各角色阶段）

每个角色**结束本阶段写出**后，主控代跑记录（可从对话/平台拿到的 input/output；只有总数时用 `--total`）：

```bash
python <本插件>/scripts/aad.py usage <feature目录> record \
  --role product|architect|developer|tester|deployer|lead|ux|reviewer \
  --stage clarify|ux|tech|plan|implement|review|verify|release \
  --input <N> --output <N> [--model "..."] [--gate G1] [--note "..."]
python <本插件>/scripts/aad.py usage <feature目录> show
python <本插件>/scripts/aad.py board <feature目录>   # 看板含按角色/阶段汇总
```

落盘：`features/<id>/usage.yaml`。切换角色前进门禁前尽量补记当前阶段用量。

## Review

blocking → implement 复审；dispute → 人裁决；nit → verify。
