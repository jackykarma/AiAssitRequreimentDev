# 插件知识索引

本目录是跑通需求流水线的最小知识集。业务仓若有完整 `modus/knowledge/`，可作域补充；与源码或门禁冲突时以当前源码和检查器为准。

| 文件 | 内容 |
| --- | --- |
| [constitution-summary.md](constitution-summary.md) | 宪法要点：角色只写自己的件、G1 seal、验收看命令退出码 |
| [flow.md](flow.md) | G0→GD 与角色顺序 |
| [gates.md](gates.md) | 门禁表（含原型 G1/G2） |
| [artifacts.md](artifacts.md) | `features/<id>/` 产物表 |
| [decomposition.md](decomposition.md) | 需求 ≠ feature；`tasks.yaml` 在 G2T 之后 |

CLI 优先 `python <本插件>/scripts/aad.py …`（或 PATH 上的 `aad`），等价 `python -m aiassitrequreimentdev`。不要手改 `gates.*.accepted`。
