# 变更规则

- 场景编号 `S*`，验收编号 `A*`，任务编号 `T*`，Review finding 编号 `R*`。
- G1 签字后改 `spec.yaml` 必须退回 G1；检查器用 `specHash` 发现擅自修改。
- 写集按规范化路径前缀判断相交。
- `nonGoals` 中的事项开发不得实现。
- Review finding 的 `severity` 只能是 `nit`、`dispute`、`blocking`。
- `blocking` 的 `status` 必须变为 `fixed` 才算关闭；关闭前禁止 G4/测试。
- `dispute` 的 `status` 必须变为 `resolved`，且带 `resolution.decision` 与 `resolution.rationale`。
- `nit` 不挡门禁。
- 部署工件只含清单与命令，不表示已上线。
