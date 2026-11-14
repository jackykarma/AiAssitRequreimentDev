# Cursor / Codex 插件分发设计

日期：2026-11-14  
状态：已批准（2026-11-14）  
范围：将 AiAssitRequreimentDev 打成团队私有 Git marketplace 插件，业务仓与本仓通用；Cursor 与 Codex 同一套源。

## 1. 目标与非目标

### 目标

- 任意业务仓库可安装本插件，用角色技能跑需求开发流水线（产物落在业务仓 `features/`）。
- **同一套源**：Cursor（团队 Git marketplace）与 Codex（`/plugins`）都能安装。
- 使用体验对齐 Codex 插件：**安装 → 新会话 → 直接用**，不要求用户先手拷 skills 或先理解 `pip install`。
- 插件自带跑通流水线所需的**精简知识与模板引用**；业务仓不必自带完整 `modus/`。

### 非目标（首期）

- 公共 Cursor Marketplace / OpenAI 公共插件目录正式提审。
- 将完整 `modus/`、Archify 整仓打进插件。
- MCP、hooks 自动化（可留空目录占位）。
- 用非 Python 重写门禁检查器。

## 2. 已确认决策

| 项 | 选择 |
| --- | --- |
| 使用场景 | 装到任意业务仓做需求开发 |
| 分发 | 团队/私有 Git marketplace（先于公共上架） |
| 知识与模板 | 插件自带精简 references；模板权威在 Python 包内 |
| 打包结构 | 方案 A：双清单 + 单插件根 |
| CLI | 插件 `scripts` 懒装并转调仓库根 `aiassitrequreimentdev` 包 |

## 3. 方案 A：仓库与插件布局

本仓库同时是流水线源码仓与团队 marketplace 源。

```text
AiAssitRequreimentDev/
├── aiassitrequreimentdev/           # Python 包：门禁 / 模板 / CLI（权威实现）
├── plugins/
│   └── aiassitrequreimentdev/       # 可安装插件（Cursor + Codex 共用）
│       ├── plugin.json              # Agent Plugins 标准清单
│       ├── .cursor-plugin/plugin.json
│       ├── .codex-plugin/plugin.json
│       ├── skills/                  # 角色技能（单源）
│       ├── rules/                   # always：需求开发启用 lead
│       ├── scripts/                 # aad：懒装 + 转调 CLI
│       ├── references/              # 精简 constitution + change 域
│       └── assets/                  # 可选说明资源；模板不双份维护
├── .cursor-plugin/marketplace.json  # Cursor 团队 marketplace
└── .agents/plugins/marketplace.json # Codex /plugins 团队源
```

### 约定

| 项 | 规则 |
| --- | --- |
| 技能源 | 只在 `plugins/aiassitrequreimentdev/skills/` 维护；根目录 `.cursor/skills` 同步或改为指向该处，禁止长期双改 |
| 知识 | 插件 `references/` = 最小可跑集；完整 `modus/` 可留本仓供本仓演进 |
| 业务仓 | 安装后只写 `features/`（大需求可有 `requirements/`），不要求自带 modus |
| 本仓 | 装同一插件或直接用仓库内同步 skills，行为一致 |
| 模板 | `init` / `init-req` 仍从 Python 包 `templates/` 读取，避免插件与包双份模板 |

## 4. 安装体验与 CLI 自包含

### 人侧安装

| 端 | 步骤 |
| --- | --- |
| Codex | 配置本仓为 marketplace → `/plugins` 安装 `aiassitrequreimentdev` → **新开会话** |
| Cursor | Customize → 从 Git / 团队 marketplace 安装同名插件 → 新开 Agent 会话 |
| 环境 | 业务仓机器需 Python ≥ 3.11；其余由脚本处理 |

### Agent 侧使用

1. Rules / 技能：需求开发 → `aiassitrequreimentdev-lead`。
2. 门禁与脚手架：技能调用插件 `scripts/aad`（或 `python …/aad.py`），**不**要求用户先手装包。
3. 产物只写入业务仓工作区。

### `scripts/aad` 行为

1. 解析插件根目录。
2. 若当前环境尚未可 `import aiassitrequreimentdev`，按序尝试懒装：
   1. **源仓开发**：若插件位于完整 clone 的 `…/plugins/aiassitrequreimentdev/`，对仓库根 `pip install -e <repo-root>`。
   2. **marketplace 安装**：插件副本通常**不含**仓库根 Python 包 → 从同一 Git remote 执行  
      `pip install "git+<remote>@<ref>#egg=aiassitrequreimentdev"`（ref 与插件版本/文档约定一致），或安装插件内 `python/` 镜像包（若发布流水线已同步拷贝）。
   3. 均失败：打印可复制修复命令（Python 版本、公司 PyPI、离线 wheel），不静默吞错。
3. 转调：`python -m aiassitrequreimentdev <args>`（`start` / `init` / `check` / `seal` / `board` / `usage` 等）。

权威实现仍是仓库根 `aiassitrequreimentdev/`；插件不长期手改第二份业务逻辑。若需「纯插件目录可离线跑」，由发布步骤把包同步进 `plugins/…/python/`（生成物，非手维）。

技能文案调整：读「插件 `references/` + 业务仓 `BOARD.md` / `features/`」，不再假定业务仓存在完整 `modus/knowledge/`。

## 5. 首期交付清单

| 项 | 内容 |
| --- | --- |
| 插件包 | `plugins/aiassitrequreimentdev/` + 三份 manifest（标准 + cursor + codex） |
| Marketplace | `.cursor-plugin/marketplace.json`、`.agents/plugins/marketplace.json` |
| Skills | lead / product / ux / tech / dev / review / test / deploy / brainstorm / grill |
| Rules | 一条 always：做需求开发启用 lead |
| Scripts | `aad` 懒装 + 转调 |
| References | constitution 摘要、change 流程、门禁表、产物表、拆分原则 |
| 文档 | README「团队安装（Cursor / Codex）」 |
| 同步 | `.cursor/skills` ↔ 插件 skills 单源策略（脚本或文档约定） |

## 6. 验收标准

1. 空业务仓：经 Cursor / Codex 从本 Git marketplace 安装后，新会话能发现 lead 等技能。
2. 业务仓执行 `aad start FEAT-demo`（或等价）生成 `features/FEAT-demo/` 且含模板文件。
3. `aad check … --gate G1` 在缺规格时能报违规（证明 CLI 通路）。
4. 只改插件 skills 一处，Cursor 与 Codex 所见文案一致（无分叉）。
5. 本仓现有 `unittest`（至少 gates/roles/paths/usage）仍通过。

## 7. 风险与缓解

| 风险 | 缓解 |
| --- | --- |
| marketplace 只安装插件子目录，不含仓库根 Python 包 | `aad` 优先 `pip install git+…`；可选发布同步 `plugins/…/python/`；文档写明 remote/ref |
| Cursor / Codex manifest 字段差异 | 保留标准 `plugin.json` + 两端兼容目录 |
| 技能路径仍写死 `modus/` | 迁移时批量改为 `references/` 相对插件说明 |
| 懒装 pip 需网络/权限 | 失败信息含离线/公司源说明；可后续加 wheels 缓存（非首期） |

## 8. 后续（非首期）

- 公共市场上架材料与提审。
- 按需扩充 references / 可选 MCP。
- 评估将精简 gate 以插件 scripts 子模块 vendoring，彻底脱离「必须 clone 源仓」假设（若 marketplace 只发插件子树）。
