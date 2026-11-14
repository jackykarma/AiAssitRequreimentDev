# 流程：G0 → GD

启动：选角色 → 确认 `full` 或 `light`（须 `pathConfirmed`）→ 产品 PRD。大需求先写需求级 PRD 与 `split.yaml`，再创建各 feature；小需求直接一个 feature。

`stage`：`intake` → `clarify` → `ux` → `tech` → `plan` → `implement` → `review` → `verify` → `release` → `done`。

## 门禁与角色顺序

| 顺序 | 门禁 | 阶段 | 谁写出 / 谁判定 |
| --- | --- | --- | --- |
| 1 | G0 | intake，进入 clarify 前 | 主控 `check`：path 合法 |
| 2 | G1 | clarify 结束，随后 `seal` | 产品：prd / 原型 / spec |
| 3 | G2 | ux | 交互视觉；无 UI 或 light 可 skip |
| 4 | G2T | tech | 架构师：`tech.md` + `tech.yaml` |
| 5 | G3 | plan | G2T 后主控写 `tasks.yaml`，再 `check G3`（检查器判定任务图） |
| 6 | — | implement | 开发只改任务写集 |
| 7 | GR | review | Review 写 `review.yaml`；blocking 未清零禁止测试 |
| 8 | G4 | verify | 测试写 `evidence.yaml`，命令 `exitCode` 为 0 |
| 9 | GD | release | 部署写清单与命令；上线前人确认 |

全量角色链：产品（可先 brainstorm → grill）→ 交互视觉 → 架构师 → 主控拆任务 → 开发 → Review → 测试 → 部署。

交互视觉不是启动五角色之一，需要 UI 精修时加派。轻量路径可无 ux 文件，`affected` 恰好一项，且只能一个任务。

主控代跑 CLI，优先 `python <本插件>/scripts/aad.py`（或 PATH 上的 `aad`）：`start` / `adopt` / `path` / `init` / `init-req` / `check` / `seal` / `board` / `usage`。与 `python -m aiassitrequreimentdev` 语义相同。

改某 feature 验收：回该 feature 的 G1 重 seal。范围外新目标：回到需求级 PRD 与 `split.yaml`，或新开 feature。
