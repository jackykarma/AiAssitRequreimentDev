# 变更控制（Change Control）

产品 / UX / 技术方案 / 任务图 / **拆分范围**变更是常态。要求：**先记账，再改合同，再回退门禁**。

## 两层台账

| 范围 | 落盘 | 典型级别 | CLI |
| --- | --- | --- | --- |
| **单个 feature** | `features/<id>/change.yaml` | C0–C3（实现/UX/tech/产品合同） | `change record features/FEAT-001-move-album …` |
| **整条需求（拆分）** | `requirements/<REQ>/change.yaml` | **C4**（增删改 feature、改 split） | `change record requirements/REQ-… …` |

字段同构。`impacts.features` 列出受影响的 feature id；需求级回退时会对这些目录（或 `split.yaml` 里全部已存在 feature）执行门禁回退。

## 必填字段（每条变更）

| 字段 | 说明 |
| --- | --- |
| `id` | `CHG-*`，本目录内唯一 |
| `at` | ISO8601 时间（含时区） |
| `initiatedBy.role` / `.name` | 发起角色 / 可选人名 |
| `reason` / `summary` | 原因与一句话摘要 |
| `level` | `C0`～`C4` |
| `category` | `product` / `ux` / `tech` / `tasks` / `split` / `other` |
| `impacts.artifacts` | 将改动的文件 |
| `impacts.gatesRollback` | 须重过的门禁（C1–C3 必填；C4 仅新增空切片时可空） |
| `impacts.features` | 受影响 feature id 列表（**C4 强烈建议**） |
| `status` | `proposed` →（C3/C4）`approved` → `applied` |

## 分级与回退

| 级别 | 含义 | 典型 | 回退 | 人确认 |
| --- | --- | --- | --- | --- |
| **C0** | 局部实现 | 写集细节 | 不回退 | 否 |
| **C1** | 技术方案 | `tech.yaml` | → G2T，重评 G3 | 契约/迁移时 |
| **C2** | UX/UI | `ux.yaml` / UX 原型 | → G2 | 风格多选时 |
| **C3** | 产品合同 | 切片 FR/A*/原型 | → G1 重 seal | **是** |
| **C4** | 范围/拆分 | 需求级 PRD、`split.yaml`、增删合并 feature | 需求决策 + 相关 feature 门禁 | **是** |

原则：上游合同变 → 下游失效；只改下游不必无故打回产品。

## C4 场景怎么记（整需求）

| 场景 | 记在哪 | 动作 |
| --- | --- | --- |
| **新增** feature | `requirements/<REQ>/change.yaml` · C4 · `category=split` | 改 `split.yaml` → 人确认 → `init FEAT-<序号>-<slug> --requirement REQ-…` → 新产品切片 PRD/spec |
| **移除** feature | 同上；`--features` 含被移除 id | 改 split；对该 feature 回退/停做；目录可保留并在 BOARD 标明废弃 |
| **改某 feature 范围**（仍同一 id） | 需求台账 C4 + 该 feature 上再记 **C3**（若动 A*） | 先改 split/需求级 PRD 边界，再改切片 spec 并回 G1 |
| **合并 / 拆开** | C4 | 改 split；旧 feature 停做或回退；新 feature `init` |

```bash
# 需求级：拆出第二刀，并回退仍共享契约的 FEAT-001-move-album
python -m aiassitrequreimentdev change requirements/REQ-001-move-album-20220305 record \
  --initiated-by product --level C4 --category split \
  --reason "埋点可独立上线" --summary "拆出 FEAT-002-move-tracking" \
  --artifacts split.yaml,prd.md \
  --features FEAT-001-move-album,FEAT-002-move-tracking \
  --gates G1 \
  --status approved --confirmed-by human --confirmed-name "负责人"

python -m aiassitrequreimentdev check-req requirements/REQ-001-move-album-20220305
python -m aiassitrequreimentdev init FEAT-002-move-tracking --requirement REQ-001-move-album-20220305
```

单 feature 内改验收（不改拆分）→ 仍用 **feature 台账 C3**，不必升 C4。

## 主控操作顺序

1. `change … record`（`proposed` 或直接 `approved`）  
2. C3/C4：人确认（打断码 `I_CHANGE_CONFIRM`）  
3. **`approved|applied` + `gatesRollback`**：默认回退列出的 feature（需求级可多目录）；含 G1 清 `specHash`。`--no-rollback` / `--rollback` 可覆盖。  
4. 改工件（需求级：`split` / 需求 PRD；切片：spec/tech/…）  
5. `status=applied`，再 `check --accept`  

## 与现有规则

- G1 冻结后改切片 `spec.yaml`：先 **C3**（feature 台账），再回 G1。  
- 增删切片 / 改拆分：先 **C4**（需求台账），再改 `split.yaml`，`check-req`，再 `init` 或停做。  
- 开发不得私自改合同；发现契约问题 → 提议变更，主控记账后回退。
