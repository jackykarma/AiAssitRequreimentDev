# 需求级技术方案（Epic Design）

本目录是整条需求的 **Epic Design**（对齐 AISDD `epic-design` 章节骨架），不是可有可无的草图。

| 文件 | 说明 |
| --- | --- |
| `architecture.md` | 人读总册（模板章节须齐全；`check-req` 校验 `##`） |
| `architecture.yaml` | 机器件：L0/L1 图、features 追溯、契约/风险 |
| `diagrams/` | Archify `.html` + `.png` |

## 与 Feature / Story

| 层级 | 文档 | 职责 |
| --- | --- | --- |
| Epic Design（本目录） | `architecture.md` | 整需求方案；`check-req` |
| Feature 薄 tech | `features/*/tech.md` | 交付落点 + 增量；G2T / 对 G4 负责 |
| Story | `stories/ST-*/story-tech.md` | 并行落码；不对独立交付负责 |

单 Feature 捷径未建 `requirements/` 时：由该 Feature 薄 tech **兼任** Epic 关键结论。

## 绘图

工具：[Archify](https://github.com/tt-a1i/archify)。`check-req` 要求 layer 0 与 1 的 architecture 图为正式产物（路径不得含 `PLACEHOLDER`）。
