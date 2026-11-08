# AiAssitRequreimentDev

做需求开发时：启用 `specforge-lead`（CLI / 技能目录仍用包名 `specforge`）。

1. 选角色（`docs/role-picker.html` + `adopt`）
2. 按需求推荐并确认路径（`recommend` / `docs/path-picker.html` + `path`）→ `full` 或 `light`
3. 进入对应技能；产物共仓在 `features/<id>/`（`BOARD.md`）

**需求 ≠ feature**：一条需求 → 1..N 个 feature。大需求：产品先写需求级 PRD，再在 `split.yaml` 决定拆几个；主控建目录。小需求可直开单个 feature。feature 内的 `tasks.yaml` 更晚才拆。

主控代跑 `start` / `init` / `check` / `seal` / `board` / `recommend` / `path`。

先读 `docs/architecture.md` 和 `constitution.md`。知识从 `modus/knowledge/architecture-overview.md` 进入。

角色只写自己的工件。门禁：`python -m specforge check <feature目录> --gate <G0|G1|G2|G2T|G3|GR|G4|GD>`。
