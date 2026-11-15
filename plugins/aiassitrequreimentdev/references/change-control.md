# 变更控制（Change Control）

产品 / UX / 技术方案 / 任务图变更是常态。本流程要求：**先记账，再改合同，再回退门禁**。

落盘：`features/<id>/change.yaml`（主控维护；各角色提议，主控代记）。  
需求级变更可另记在 `requirements/<REQ>/change.yaml`（可选，字段同构）。

## 必填字段（每条变更）

| 字段 | 说明 |
| --- | --- |
| `id` | `CHG-*`，本 feature 内唯一 |
| `at` | ISO8601 时间（含时区），变更发起/入账时间 |
| `initiatedBy.role` | 发起角色：`product` / `ux` / `architect` / `developer` / `tester` / `deployer` / `lead` / `human` |
| `initiatedBy.name` | 人名或账号（可空，私人项目可填自己） |
| `reason` | 变更原因（为何改，禁止空话） |
| `level` | `C0`～`C4`（见下） |
| `category` | `product` / `ux` / `tech` / `tasks` / `split` / `other` |
| `summary` | 一句话变更摘要 |
| `impacts.artifacts` | 将改动的文件列表 |
| `impacts.gatesRollback` | 须重过的门禁 |
| `status` | `proposed` →（C3/C4 须）`approved` → `applied` |

建议字段：`impacts.acceptanceIds`、`impacts.features`、`confirmedBy`（role/name/at）。

## 分级与回退

| 级别 | 含义 | 典型 | 回退 | 是否须人确认 |
| --- | --- | --- | --- | --- |
| **C0** | 局部实现，不改合同 | 写集内实现细节 | 不回退门禁 | 否；仍建议记账 |
| **C1** | 技术方案合同 | `tech.yaml` 接口/KD/约束 | → **G2T**；重评 **G3** | 对外契约/迁移时打断 |
| **C2** | 交互视觉 | `ux.yaml` / `prototype/ux`，不改 A* | → **G2** | 风格多选时打断 |
| **C3** | 产品合同 | FR/NFR/E/A/UJ、产品原型 | → **G1** 重 seal；下游作废重做 | **是** |
| **C4** | 范围/拆分 | 需求级 PRD、`split.yaml`、新开/合并 feature | 需求级决策 + 相关 feature 门禁 | **是** |

原则：上游合同变 → 下游门禁与证据失效；只改下游不必无故打回产品。

## 主控操作顺序

1. `change … record` 写入台账（`status=proposed` 或直接 `approved`）  
2. C3/C4：人确认后把 `status` 改为 `approved`（打断码 `I_CHANGE_CONFIRM`）  
3. 按 `gatesRollback` 把 `state.gates.*` 退回 `pending`（G1 须清/重 seal）  
4. 派对应角色改工件  
5. 改完将条目 `status=applied`，再 `check` 从回退点往下走  

```bash
python <本插件>/scripts/aad.py change <feature目录> record \
  --initiated-by product \
  --name "张三" \
  --reason "业务确认成功态口径" \
  --level C3 \
  --category product \
  --summary "调整 A1 then" \
  --artifacts spec.yaml,prd.md,prototype/index.html \
  --gates G1,G2,G2T,G3 \
  --acceptance A1 \
  --status approved

python <本插件>/scripts/aad.py change <feature目录> show
```

## 与现有规则的关系

- G1 冻结后改 `spec.yaml`：必须先有 **C3** 台账，再退回 G1 并 `seal`（`specHash` 仍生效）。  
- 开发不得私自改规格/tech 合同；发现契约问题 → 提议变更，主控记账后回退。  
- Review `blocking` 修复若不动合同，可记 **C0** 或不记；一旦改 A*/接口则升到对应级别。
