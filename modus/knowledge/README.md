# modus 知识库

长期事实只写在这里。feature 目录里的 yaml 用路径链接进来，禁止复制规则正文。

## 布局

- `architecture-overview.md`：总入口
- `constraint/`：全局与团队底线（人持有，Agent 不得覆盖）
- `domain/change/`：AiAssitRequreimentDev 变更流程域
- `domain/_template/`：业务域接入模板（复制后改名，填真实规则）

## 新增业务域

1. 复制 `domain/_template/` 为 `domain/<name>/`。
2. 填写 `SKILL.md` 与 `references/` 下的规则、状态、API、模块。
3. 人持有的业务叙述放进 `business/`。
4. 产品规格的 `constraints` / `affected` 写这些路径。

## 与 Agent 的关系

每个角色 Skill 开场：`architecture-overview` → 相关域 `SKILL.md` → 所需 references；引用前核对源码。源码与知识冲突时以源码为准，再在原定义处修订知识。
