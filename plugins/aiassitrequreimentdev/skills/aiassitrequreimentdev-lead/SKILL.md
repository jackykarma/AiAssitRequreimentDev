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
**tasks.yaml** 只在单个 feature 的技术门禁之后拆，不是拆需求。G2T 通过后可用：

```bash
python <本插件>/scripts/aad.py tasks <feature目录> scaffold   # 或 tasks scaffold <目录>
```

按 `spec.acceptance` 生成骨架（轻量族自动单任务）；改 `writeScopes` 后 `check --gate G3`。任务的验证命令须与 `spec.acceptance[].verify` **同名/同源**（可补全可跑路径，不得另起总能成功的假命令）。

## 启动（单 feature 捷径）

1. `python <本插件>/scripts/aad.py start <FEAT-id> [--need "..."]`（可带 `--need` 供路径推荐）
2. **在对话内**选角色 → `adopt`（打断码 `I_ROLE_SELECT`）
3. **在对话内**确认路径 → `path`（`full` / `light` / `light-auto`；打断码 `I_PATH_SELECT`）
4. 派对应技能

### 角色 / 路径怎么问人（禁止要求先开 HTML）

主控遇到未选角色或未确认路径时，**必须在本会话内弹出选择**，等用户点选或回复后再写 state：

1. **优先**：宿主若提供结构化选择题（如 Cursor `AskQuestion`），用单选列出角色或路径；路径题须标出系统推荐项。
2. **否则**：直接在对话里贴 CLI 菜单（`roles` / `paths` / `recommend` 打印的编号列表），请用户回复编号或名称。
3. 用户确认后主控代跑 `adopt` / `path`，**不要**让用户自己去复制粘贴命令。

`docs/role-picker.html` / `docs/path-picker.html` **仅备用**（浏览器可视化、离线演示）；**不是**启动必经步骤。文档与 `start` 输出里若出现选择页链接，当作可选，不得写成「请先打开 HTML」。

## 路径与执行

| path | 适用 | 执行方式 |
| --- | --- | --- |
| `full` | 新能力 / 跨模块 / 改契约 | 完整角色链，按阶段推进 |
| `light` | 单模块小改（可有 UI） | 可跳 UX；单任务；阶段仍逐步派角色 |
| `light-auto` | **无 UX/UI** 的小需求 | 与 light 同门禁约束，且须 `uiRequired=false`；**G1 `seal` 后人闸，之后 goal 式连跑至 G4** |

### `light-auto` 连跑规则（主控必须遵守）

前置：`pathConfirmed` + G1 已 `seal` + `uiRequired=false` + `openQuestions=[]` + 单 `affected`。

seal **之后**不要停下来等人点「下一步」，连续完成：

1. 架构师 → `tech.md` / `tech.yaml` → `check G2T`（G2 无 ux 文件即视为 skip）
2. 主控写**一个**任务 → `check G3`
3. 开发 → Review →（blocking 清零后）测试写 `evidence.yaml` → `check G4`

仍须打断：`I_PRODUCT_OPEN`、`I_TECH_RISK`、`I_REVIEW_DISPUTE`、`I_TEST_STUCK`、`I_DEPLOY_CONFIRM`、`I_CHANGE_CONFIRM`（C3/C4）。  
部署（GD）**不要**自动上线确认。有 UI / 需逐步确认时改选 `light` 或 `full`，不要硬套 `light-auto`。

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

`check` → 结构通过再往下；通过后可用 `check <目录> --gate Gx --accept` 写入 `gates.Gx=accepted` 并推进 `stage`（**G1 的 --accept 会 seal**）。也可单独 `seal`。交付后 `board`（看板含 stage / 门禁表）。  
需求拆分：产品填完 `split.yaml` 后主控代跑 `check-req <需求目录>`；`decision: multi` 须人确认后再 `init`。

## 变更控制（必记台账）

产品 / UX / 技术方案 / 任务图变更：**先记账，再回退门禁，再改工件**。规范：`references/change-control.md`。

每条须含：发起人（角色+可选姓名）、原因、级别 C0–C4、影响文件与回退门禁、时间、状态。

- **单切片**（C0–C3）：`features/<id>/change.yaml`
- **整需求拆分**（C4 增删改 feature）：`requirements/<REQ>/change.yaml`，`--features` 列出受影响切片

```bash
# feature 级
python <本插件>/scripts/aad.py change <feature目录> record \
  --initiated-by product --level C3 --category product \
  --reason "…" --summary "…" --artifacts spec.yaml,prd.md --gates G1,G2,G2T \
  --status approved --confirmed-by human --confirmed-name "…"

# 需求级 C4（新增/移除/改拆分）
python <本插件>/scripts/aad.py change <requirements/REQ-…> record \
  --initiated-by product --level C4 --category split \
  --reason "…" --summary "…" --artifacts split.yaml,prd.md \
  --features FEAT-001,FEAT-002 --gates G1 \
  --status approved --confirmed-by human --confirmed-name "…"
```

| 级别 | 回退 |
| --- | --- |
| C0 实现细节 | 可不回退门禁，建议仍记账 |
| C1 技术方案 | → G2T，重评 G3 |
| C2 UX/UI | → G2 |
| C3 产品合同 | → G1 重 seal；下游重做（记在 **feature**） |
| C4 范围/拆分 | 需求级 PRD/`split.yaml` + 人确认；回退 **`--features` 所列**切片门禁 |

细则：`references/change-control.md`。C3/C4 打断码：`I_CHANGE_CONFIRM`。

## Token 用量（各角色阶段）

每个角色**结束本阶段写出**后，主控代跑记录（可从对话/平台拿到的 input/output；只有总数时用 `--total`）：

```bash
# 两种参数顺序均可：usage <目录> record … 或 usage record <目录> …
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
