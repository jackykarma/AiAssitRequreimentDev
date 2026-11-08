# 启动角色

人进入流程时先选身份，再启用对应技能。选择写入 `state.json`：

- `actorRole`：`product` | `architect` | `developer` | `tester` | `deployer`
- `actorLabel`：中文名

命令：

```bash
python -m aiassitrequreimentdev start FEAT-001
python -m aiassitrequreimentdev roles
python -m aiassitrequreimentdev adopt features/FEAT-001 --role 产品经理
python -m aiassitrequreimentdev board features/FEAT-001
```

选择页：`docs/role-picker.html`。

## 共仓

所有角色读写同一 `features/<id>/`。`BOARD.md` 列出产物有无。规则：

- 只写自己角色的文件
- 开工前读 `BOARD.md` 与上游产物
- 不把对话记录当交付；交付是目录里的文件

| 角色 | 技能 | 写出 |
| --- | --- | --- |
| 产品经理 | aiassitrequreimentdev-product | prd.md、prototype/、spec.yaml |
| 架构师SE | aiassitrequreimentdev-tech | tech.md、tech.yaml |
| 开发 | aiassitrequreimentdev-dev | 写集内源码 |
| 测试 | aiassitrequreimentdev-test | evidence.yaml |
| 部署 | aiassitrequreimentdev-deploy | deploy.yaml |

交互视觉 `aiassitrequreimentdev-ux` 不是启动五角色之一；在架构师或主控需要 UI 精修时加派，写出 `ux.yaml`。
