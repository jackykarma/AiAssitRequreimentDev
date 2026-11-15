# 全量 / 轻量 / 轻量自动路径

`state.path`：`full` | `light` | `light-auto`。启动时根据需求推荐，并由人确认后写入 `pathConfirmed=true`。

## 怎么选

| 路径 | 适用 | 差异 |
| --- | --- | --- |
| `full` 全量（重） | 新能力、跨模块、改状态机/对外契约、需要 PRD/原型 | 完整角色链；可多任务 |
| `light` 轻量（小需求） | 单模块缺陷、已有验收的小行为修正 | 可无 ux 文件；`affected` 一项；只能一个任务；阶段仍逐步推进 |
| `light-auto` 轻量自动（无 UI） | 无 UX/UI 的小需求，希望 seal 后连跑 | 同 light 结构约束，且须 `uiRequired=false`；G1 seal 后 goal 连跑至 G4；部署仍打断 |

命令：

```bash
python -m aiassitrequreimentdev recommend --text "修复单模块崩溃，无UI"
python -m aiassitrequreimentdev paths --text "新功能跨模块状态机"
python -m aiassitrequreimentdev path features/FEAT-001 --path 轻量自动 --recommended light-auto
```

主控确认路径时优先在对话内弹选项（AskQuestion 或 `paths`/`recommend` 菜单）；`docs/path-picker.html` 仅备用可视化。

推荐只是建议；人确认优先。`light` / `light-auto` 改选后仍须通过 G0/G1/G3 对轻量族的结构约束。
