# AiAssitRequreimentDev 架构

对话编排 + 规格门禁多智能体。启动时先选角色，再确认全量/轻量；合同落在 `features/<id>/`，长期知识在 `modus/knowledge/`。门禁用 `python -m aiassitrequreimentdev check`（主控代跑）。团队插件入口：`plugins/aiassitrequreimentdev/`（Cursor / Codex marketplace 同一套源）。

## 需求与 feature

| 概念 | 含义 |
| --- | --- |
| 需求 | 业务问题 / 史诗；目录可选 `requirements/REQ-<序号>-<名称>-<YYYYMMDD>/`（如 `REQ-001-move-album-20220305`；需求级 PRD + `split.yaml`） |
| feature | 可 G4 的交付切片（对本切片 `A*` 可独立验收；≠ 整需求零依赖大包）；`features/<id>/`；一条需求 → 1..N 个 feature |
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
requirements/REQ-<序号>-<名称>-<YYYYMMDD>/  # 如 REQ-001-move-album-20220305；PRD + split + architecture/
features/FEAT-<序号>-<kebab>/  # 如 FEAT-001-move-album
  state.json               # requirementId、dependsOnFeatures、actorRole、path…
  BOARD.md
  prd.md / prototype / spec.yaml
  ux.yaml / tech.md / tech.yaml / diagrams/ / tasks.yaml / review.yaml / evidence.yaml / deploy.yaml
```

启动：选角色 → 确认全量/轻量 → 产品 PRD。大需求先 `init-req`（可含整需求 Archify 草图）再按 `split.yaml` 建 feature；每个 feature 各自写 tech（G2T）。小需求直接一个 feature。

绘图：一律 [Archify](https://github.com/tt-a1i/archify)，只保留 html + png。详见 `modus/knowledge/domain/change/references/diagrams.md`。

## 状态与门禁

`path`：`full` | `light` | `light-auto`（须 `pathConfirmed`）。`stage`：`intake` → `clarify` → `ux` → `tech` → `plan` → `implement` → `review` → `verify` → `release` → `done`。`light-auto`：无 UI 小需求，G1 seal 后连跑至 G4。

| 门禁 | 条件 |
| --- | --- |
| G0 | path 合法且 `pathConfirmed`；轻量族（light / light-auto）的 affected 一项 |
| G1 | spec 含 UJ/FR/NFR/E/A（S 可选）且形状合法、openQuestions 空；prd 章节对齐模板；有 UI 须可交互 `prototype/index.html`，无 UI 须 `uiRequired=false`+原因；light-auto 另须 `uiRequired=false`；`seal` 写哈希并 `G1=accepted` |
| G2 | `uiRequired=false` 跳过 UX；有 UI 须 `interactionRules` + `visual.baseline`（ui-kit\|custom）+ 可交互 `prototype/ux/`（或 `skip`）；轻量族可无 ux 文件 |
| G2T | tech.md + tech-spec.md + tech.yaml（feature 级模板）；aiConstraints/keyDesigns/interfaces/diagrams；full 强制 L0/L1 三级标题与 workflow/sequence/class；acceptance 全覆盖 |
| G3 | 任务无环、写集不交；轻量族仅一任务 |
| GR | 无未关闭 blocking；无未裁决 dispute |
| G4 | evidence 全覆盖且 exitCode 0 |
| GD | deploy 含 environment/commands/rollback |

## 角色

| 技能 | 只写 |
| --- | --- |
| `aiassitrequreimentdev-lead` | `state.json`、`tasks.yaml`、`usage.yaml`（经 CLI）、代跑 CLI |
| `aiassitrequreimentdev-product` | `prd.md`、`prototype/index.html`、`spec.yaml` |
| `aiassitrequreimentdev-ux` | `ux.yaml`（交互规则+可选视觉/动效）、`prototype/ux/` |
| `aiassitrequreimentdev-tech` | `tech.md`、`tech.yaml` |
| `aiassitrequreimentdev-dev` | 任务写集 |
| `aiassitrequreimentdev-review` | `review.yaml` |
| `aiassitrequreimentdev-test` | `evidence.yaml` |
| `aiassitrequreimentdev-deploy` | `deploy.yaml` |

## 检查器

```bash
python -m pip install -e .
python -m aiassitrequreimentdev init FEAT-001-move-album
python -m aiassitrequreimentdev check features/FEAT-001-move-album --gate G1
python -m aiassitrequreimentdev check features/FEAT-001-move-album --gate G1 --accept
python -m aiassitrequreimentdev tasks scaffold features/FEAT-001-move-album
python -m unittest discover -s tests
```



