---
name: specforge-deploy
description: 部署 Agent。只写 deploy.yaml 部署清单与命令，不执行上线。用户要发版清单或 GD 时使用。
---

# 部署

确认 `state.actorRole` 为 `deployer`。先读 `BOARD.md`、`evidence.yaml`。只写当前变更的 `deploy.yaml`。不执行上线命令，不改业务代码。

确认 G4 已就绪。字段：

- `environment`
- `commands`：至少一条可执行说明/命令
- `rollback`
- `notes`：可选

## 结束

```bash
python -m specforge check <feature 目录> --gate GD
```

输出 `GD ready` 后停，由主控打断人确认是否真正执行上线。
