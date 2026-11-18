# Story 模板（可选层）

**Feature = 可独立交付（对 G4 负责）；Story = 技术实现 / 并行开发视角（不对独立交付负责）。**

## 何时启用

满足任一条再从本目录复制到 `features/<FEAT>/stories/ST-…/`：

1. 同一 Feature 内需并行改不相交写集  
2. 存在 ≥2 条可独立落码的技术主链  
3. 需探路 Story 再铺开实现  
4. Feature tech 评审要求按实现单元拆并行  

否则保持 `stories.yaml` → `storiesEnabled: false`，直接 tasks。

## 文件

| 源模板 | 目标 |
| --- | --- |
| `story-tech.md` | `features/<id>/stories/ST-…/story-tech.md` |
| `story-tech.yaml` | 同目录（可选） |
| Feature 根 `stories.yaml` | 索引；`init` 时已带 `storiesEnabled: false` |

结构借鉴 AISDD L2 Story 详细设计；绘图与门禁遵循本仓 Archify / Feature G4 约定。
