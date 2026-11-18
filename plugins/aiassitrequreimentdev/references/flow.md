# 流程：G0 → GD

启动：主控在**对话内**弹选项选角色 → 确认 `full` / `light` / `light-auto`（须 `pathConfirmed`）→ 产品 PRD。HTML picker 仅备用。大需求先写需求级 PRD + **整需求 architecture** + `split.yaml`，`check-req` 通过后再创建各 feature；小需求直接一个 feature。可选 Story 仅并行落码，G4 只认 Feature。

`stage`：`intake` → `clarify` → `ux` → `tech` → `plan` → `implement` → `review` → `verify` → `release` → `done`。门禁 `check --gate … --accept` 通过后自动推进（light / 无 UI 时 G1 后可跳到 `tech`）。

## 门禁与角色顺序

| 顺序 | 门禁 | 阶段 | 谁写出 / 谁判定 |
| --- | --- | --- | --- |
| 1 | G0 | intake，进入 clarify 前 | 主控 `check`：path 合法 |
| 2 | G1 | clarify 结束，随后 `seal` | 产品：prd / 原型 / spec |
| 3 | G2 | ux | 交互视觉；无 UI 或轻量族可 skip |
| 4 | G2T | tech | 架构师：`tech.md` + `tech.yaml` |
| 5 | G3 | plan | G2T 后主控写 `tasks.yaml`，再 `check G3`（检查器判定任务图） |
| 6 | — | implement | 开发只改任务写集 |
| 7 | GR | review | Review 写 `review.yaml`；blocking 未清零禁止测试 |
| 8 | G4 | verify | 测试写 `evidence.yaml`，命令 `exitCode` 为 0 |
| 9 | GD | release | 部署写清单与命令；上线前人确认 |

全量角色链：产品（可先 brainstorm → grill）→ 交互视觉 → 架构师 → 主控拆任务 → 开发 → Code Review → 测试 → 部署。

启动菜单含上述角色（含 UX / Review）；无 UI 时可跳过 UX，`light-auto` 连跑时主控按阶段 `adopt`。轻量族（`light` / `light-auto`）可无 ux 文件，`affected` 恰好一项，且只能一个任务。

需求拆分后：`check-req <requirements/REQ-…>` 校验 `split.yaml`；`multi` 须 `confirmedByHuman=true` 再 `init`。

**`light-auto`**：须 `uiRequired=false`；G1 `seal` 后主控 goal 式连跑 tech→单任务→开发→Review→测试至 G4；`I_TECH_RISK` / dispute / 测试卡死 / 部署仍打断。详见 lead 技能。

主控代跑 CLI，优先 `python <本插件>/scripts/aad.py`（或 PATH 上的 `aad`）：`start` / `adopt` / `path` / `init` / `init-req` / `check` / `seal` / `board` / `usage` / `change`。与 `python -m aiassitrequreimentdev` 语义相同。变更控制见 `change-control.md`。

改某 feature 验收：回该 feature 的 G1 重 seal。范围外新目标：回到需求级 PRD 与 `split.yaml`，或新开 feature。
