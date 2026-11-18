# AiAssitRequreimentDev

做需求开发时：启用 `aiassitrequreimentdev-lead`。若已装团队插件，技能来自 `plugins/aiassitrequreimentdev/`；本仓请保持 `sync_plugin_skills` 无漂移。

1. 主控在对话内弹窗/选项选角色 → `adopt`（HTML picker 仅备用）
2. 主控在对话内推荐并确认路径 → `path`（`full` / `light` / `light-auto`；`recommend` 可选）
3. 进入对应技能；产物共仓在 `features/<id>/`（`BOARD.md`）。产品输入不完整时：`aiassitrequreimentdev-brainstorm` → `aiassitrequreimentdev-grill` → `aiassitrequreimentdev-product`

**需求 ≠ feature ≠ story**：一条需求 → 1..N 个 feature。大需求：需求级 PRD + **整需求 `architecture/`（L0/L1，`check-req` 硬）** → `split.yaml` → 建 feature。feature 对本切片 `A*` **对交付负责**（可 G4）；可选 Story 仅技术实现/并行，挂在 Feature 下、不对独立交付负责。小需求可直开单个 feature。`tasks.yaml` 更晚才拆（可挂 `storyId`）。

主控代跑 `start` / `init` / `init-req` / `check`（可 `--accept`）/ `check-req` / `tasks scaffold` / `seal` / `board` / `usage` / `change`（approved 默认可回退门禁）/ `recommend` / `path`。角色结束阶段后记 token：`usage record --role … --stage … --input … --output …`。

先读 `docs/architecture.md` 和 `constitution.md`。知识从 `modus/knowledge/architecture-overview.md` 进入。

角色只写自己的工件。门禁：`python -m aiassitrequreimentdev check <feature目录> --gate <G0|G1|G2|G2T|G3|GR|G4|GD>`。

**模板硬约束（凡有底稿必遵）**：产物落盘时，若 `aiassitrequreimentdev/templates/`（或技能明示的底稿路径）已有对应模板，**必须**按该模板的章节结构、标题原文、必填小节与填写要求出内容——保留全部规定 `##`/`###`（及模板要求的表/清单），只替换占位，禁止自创精简版、改名跳节、只写一行摘要糊弄（门禁 `*_TEMPLATE` / `ARCH_MD_THIN` 等会拦）。无独立模板的机器件（如 `spec.yaml`）仍按其 schema/技能字段表填写。

竞品/对标 App 视觉：提供包名时启用 `aiassitrequreimentdev-apk-uikit`（ADB 抓页 → `research/<app>-ui/ui-kit/`），完成后登记 `research/ui-kits/catalog.yaml`；动效对齐 `research/ui-kits/MOTION.md`。G2 视觉：若 `projectStyle.locked=true` 则遵循项目自有 UI（不强制三选一）；否则人选 `ui-kit` / `painless` / `midoo`（可选 `custom`）。
