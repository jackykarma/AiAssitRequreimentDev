# AiAssitRequreimentDev 架构

对话编排 + 规格门禁多智能体。启动时先选角色，再确认全量/轻量；合同落在 `features/<id>/`，长期知识在 `modus/knowledge/`。门禁用 `python -m specforge check`（主控代跑）。

## 需求与 feature

| 概念 | 含义 |
| --- | --- |
| 需求 | 业务问题 / 史诗；目录可选 `requirements/<REQ-id>/`（需求级 PRD + `split.yaml`） |
| feature | 可 G4 的交付切片；`features/<id>/`；一条需求 → 1..N 个 feature |
| task | feature 内实现单元；该 feature 门禁中后期的 `tasks.yaml` |

**谁拆 feature**：产品主责，依据需求级 PRD 写 `split.yaml`；主控执行创建目录；架构师可建议；开发不拆。  
**何时拆**：需求级 PRD 之后（小需求可直开单个 feature）。  
**一还是多**：默认少拆；PRD 出现可独立上线批次、跨域异节奏、探路依赖等信号才拆多。详见 `modus/knowledge/domain/change/references/decomposition.md`。

旧称「change」已统一为 **feature**。

## 四层

| 层 | 所有者 | 留下的东西 |
| --- | --- | --- |
| 控制层 | 主控 | `features/<id>/state.json` |
| 知识层 | 人持有约束与业务 | `modus/knowledge/` |
| 交付层 | 阶段角色 | prd / prototype / spec / ux / tech / tasks / review / evidence / deploy |
| 执行层 | 开发与测试 | 补丁、命令输出 |

## 目录

```text
requirements/<REQ-id>/     # 大需求：需求级 PRD + split.yaml
features/<FEAT-id>/        # 交付切片
  state.json               # requirementId、dependsOnFeatures、actorRole、path…
  BOARD.md
  prd.md / prototype / spec.yaml
  ux.yaml / tech.md / tech.yaml / tasks.yaml / review.yaml / evidence.yaml / deploy.yaml
```

启动：选角色 → 确认全量/轻量 → 产品 PRD。大需求先 `init-req` 再按 `split.yaml` 建 feature；小需求直接一个 feature。

## 状态与门禁

`path`：`full` | `light`（须 `pathConfirmed`）。`stage`：`intake` → `clarify` → `ux` → `tech` → `plan` → `implement` → `review` → `verify` → `release` → `done`。

| 门禁 | 条件 |
| --- | --- |
| G0 | path 合法；light 的 affected 一项 |
| G1 | spec 齐、openQuestions 空；已接受则哈希一致 |
| G2 | ux 覆盖或 skip；light 可无 ux 文件 |
| G2T | tech.md + tech.yaml；变更文件/选型/风险/快稳省/数据/埋点齐全；验收落点全覆盖 |
| G3 | 任务无环、写集不交；light 仅一任务 |
| GR | 无未关闭 blocking；无未裁决 dispute |
| G4 | evidence 全覆盖且 exitCode 0 |
| GD | deploy 含 environment/commands/rollback |

## 角色

| 技能 | 只写 |
| --- | --- |
| `specforge-lead` | `state.json`、`tasks.yaml`、代跑 CLI |
| `specforge-product` | `prd.md`、`prototype/`、`spec.yaml` |
| `specforge-ux` | `ux.yaml` |
| `specforge-tech` | `tech.md`、`tech.yaml` |
| `specforge-dev` | 任务写集 |
| `specforge-review` | `review.yaml` |
| `specforge-test` | `evidence.yaml` |
| `specforge-deploy` | `deploy.yaml` |

## 检查器

```bash
python -m pip install -e .
python -m specforge init FEAT-001
python -m specforge check features/FEAT-001 --gate G1
python -m unittest tests.test_gates tests.test_roles tests.test_paths
```
