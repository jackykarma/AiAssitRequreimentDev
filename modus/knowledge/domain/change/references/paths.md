# 全量 / 轻量路径

`state.path`：`full` | `light`。启动时根据需求推荐，并由人确认后写入 `pathConfirmed=true`。

## 怎么选

| 路径 | 适用 | 差异 |
| --- | --- | --- |
| `full` 全量（重） | 新能力、跨模块、改状态机/对外契约、需要 PRD/原型 | 完整角色链；可多任务 |
| `light` 轻量（小需求） | 单模块缺陷、已有验收的小行为修正 | 可无 ux 文件；`affected` 一项；只能一个任务 |

命令：

```bash
python -m specforge recommend --text "修复单模块崩溃"
python -m specforge paths --text "新功能跨模块状态机"
python -m specforge path features/FEAT-001 --path 轻量 --recommended light
```

选择页：`docs/path-picker.html`（可带 `?recommend=light&reason=...`）。

推荐只是建议；人确认优先。改选轻量后仍须通过 G0/G3 对轻量的结构约束。
