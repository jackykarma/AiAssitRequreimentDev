---
name: aiassitrequreimentdev-lead
description: AiAssitRequreimentDev 主控。选角色与路径；大需求先让产品产出需求级 PRD 与 split.yaml，再创建一个或多个 feature。产物共仓于 features/<id>/。
---

# 主控

只改 `state.json`、`BOARD.md`（经 CLI）、以及 G3 后的 `tasks.yaml`。不写各角色专属工件。

先读 `docs/architecture.md`、`constitution.md`。拆分细则：`modus/knowledge/domain/change/references/decomposition.md`。

## 需求 → feature（先 PRD，后拆）

| 步骤 | 谁 | 做什么 |
| --- | --- | --- |
| 1 | 产品 | 需求级 PRD（大需求用 `init-req`） |
| 2 | 产品 | 填 `split.yaml`（1 或 N） |
| 3 | 主控 | `decision: multi` 时打断人确认拆分 |
| 4 | 主控 | `init` 各 feature，带 `--requirement` |
| 5 | 产品 | 各 feature 切片 PRD/原型/spec |
| 6 | 主控 | 之后才按 feature 推进门禁；G3 再拆 tasks |

小需求：直接 `start FEAT-xxx`，一个 feature 到底。

```bash
python -m aiassitrequreimentdev init-req REQ-001
# 产品写完 prd + split 后：
python -m aiassitrequreimentdev init FEAT-001 --requirement REQ-001
python -m aiassitrequreimentdev init FEAT-002 --requirement REQ-001
```

**不要**在没有需求级 PRD（或未确认的单 feature 捷径）时批量空建 feature。  
**tasks.yaml** 只在单个 feature 的技术门禁之后拆，不是拆需求。

## 启动（单 feature 捷径）

1. `python -m aiassitrequreimentdev start <FEAT-id> [--need "..."]`
2. 角色弹窗 → `adopt`
3. 路径推荐弹窗 → `path`
4. 派对应技能

## 角色写出

| 角色 | 技能 | 写出 |
| --- | --- | --- |
| 产品经理 | product | 需求级 prd/split；或 feature 的 prd/prototype/spec |
| 架构师SE | tech | tech.md + tech.yaml（可建议拆分，不拍板） |
| 开发 | dev | 写集内源码 |
| 测试 | test | evidence.yaml |
| 部署 | deploy | deploy.yaml |

## 推进门禁

`check` → 结构通过再往下；G1 后 `seal`；交付后 `board`。  
改验收回 G1；范围外新目标回到需求级 PRD/`split.yaml` 或新开 feature。

## Review

blocking → implement 复审；dispute → 人裁决；nit → verify。
