# AiAssitRequreimentDev

做需求开发时：启用 `aiassitrequreimentdev-lead`。若已装团队插件，技能来自 `plugins/aiassitrequreimentdev/`；本仓请保持 `sync_plugin_skills` 无漂移。

1. 主控在对话内弹窗/选项选角色 → `adopt`（HTML picker 仅备用）
2. 主控在对话内推荐并确认路径 → `path`（`full` / `light` / `light-auto`；`recommend` 可选）
3. 进入对应技能；产物共仓在 `features/<id>/`（`BOARD.md`）。产品输入不完整时：`aiassitrequreimentdev-brainstorm` → `aiassitrequreimentdev-grill` → `aiassitrequreimentdev-product`

**需求 ≠ feature**：一条需求 → 1..N 个 feature。feature 须对本切片 `A*` 可独立交付（可 G4），不是半成品，也不等于整需求零依赖大包；可有 `dependsOnFeatures`。大需求：产品先写需求级 PRD，再在 `split.yaml` 决定拆几个；主控建目录。小需求可直开单个 feature。feature 内的 `tasks.yaml` 更晚才拆。

主控代跑 `start` / `init` / `init-req` / `check`（可 `--accept`）/ `check-req` / `tasks scaffold` / `seal` / `board` / `usage` / `change`（approved 默认可回退门禁）/ `recommend` / `path`。角色结束阶段后记 token：`usage record --role … --stage … --input … --output …`。

先读 `docs/architecture.md` 和 `constitution.md`。知识从 `modus/knowledge/architecture-overview.md` 进入。

角色只写自己的工件。门禁：`python -m aiassitrequreimentdev check <feature目录> --gate <G0|G1|G2|G2T|G3|GR|G4|GD>`。

竞品/对标 App 视觉：提供包名时启用 `aiassitrequreimentdev-apk-uikit`（ADB 抓页 → `research/<app>-ui/ui-kit/`），完成后登记 `research/ui-kits/catalog.yaml`；动效对齐 `research/ui-kits/MOTION.md`。G2 视觉：若 `projectStyle.locked=true` 则遵循项目自有 UI（不强制三选一）；否则人选 `ui-kit` / `painless` / `midoo`（可选 `custom`）。
