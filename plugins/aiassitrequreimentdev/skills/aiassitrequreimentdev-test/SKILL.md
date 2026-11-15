---
name: aiassitrequreimentdev-test
description: 测试 Agent。确认 GR 通过后执行验收命令并写 evidence.yaml。用户要测试、证据或 G4 时使用。
---

# 测试

确认 `state.actorRole` 为 `tester`。先读 `BOARD.md`。只写当前变更的 `evidence.yaml`（及约定测试写集内测试代码）。不改产品实现与规格。

开工前运行：

```bash
python <本插件>/scripts/aad.py check <feature 目录> --gate GR
```

非 `GR ready` 则拒绝执行，交回主控。

## 证据

`results` 覆盖每条验收：`acceptanceId`、`command`、`exitCode`、`excerpt`。未运行不得填 0。失败保留非 0；超重试仍失败则交主控打断。

### 防假绿（必守）

- `command` 必须对应 `spec.acceptance[].verify`（同名用例 / 同源脚本）；不得另起无关「总能成功」的命令
- 禁止：`true`、`exit 0`、空 `echo`、未断言 then 的包装脚本；`excerpt` 须含与 then 相关的可观察片段（测试名通过、断言摘要等）
- 跑前确认命令可解析（用例/脚本存在）；不存在则拒填 0，交主控（补实现或 C3 改 verify）
- 若命令退出 0 但观察不到 then：记失败或打断，不得当过

## 结束

```bash
python <本插件>/scripts/aad.py check <feature 目录> --gate G4
```

结束后请主控登记 token（`--role tester --stage verify`）。
