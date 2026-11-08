# Feature 共仓看板

目录：`D:/Jacky/AndroidProjects/AiAssitRequreimentDev/features/FEAT-001`

各角色只写自己的工件，其余文件只读共享。一条需求可对应多个 feature。切换角色前先刷新本看板。

## 研发路径

- 当前：全量模式（重）（`full`）· 未确认（模板默认）
- 说明：新产品能力、跨模块、改状态/契约时走完整门禁与角色链。

## 当前角色

尚未选择。启动时请先选定：产品经理 / 架构师SE / 开发 / 测试 / 部署。

## 产物状态

| 文件 | 说明 | 状态 |
| --- | --- | --- |
| `prd.md` | 产品 PRD（给人） | 已有 |
| `prototype/index.html` | 产品 HTML 原型（给人） | 已有 |
| `spec.yaml` | 结构化规格（给 Agent/门禁） | 已有 |
| `ux.yaml` | 交互视觉 | 已有 |
| `tech.yaml` | 技术方案 | 已有 |
| `tasks.yaml` | 任务图 | 已有 |
| `review.yaml` | 代码评审 | 已有 |
| `evidence.yaml` | 测试证据 | 已有 |
| `deploy.yaml` | 部署清单 | 已有 |

## 角色入口

| 角色 | 技能 | 写出 |
| --- | --- | --- |
| 产品经理 | `aiassitrequreimentdev-product` | `prd.md`, `prototype/`, `spec.yaml` |
| 架构师SE | `aiassitrequreimentdev-tech` | `tech.yaml` |
| 开发 | `aiassitrequreimentdev-dev` | `<任务写集内源码>` |
| 测试 | `aiassitrequreimentdev-test` | `evidence.yaml` |
| 部署 | `aiassitrequreimentdev-deploy` | `deploy.yaml` |
