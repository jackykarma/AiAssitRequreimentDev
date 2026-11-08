# SpecForge

从意图出发，用结构化规格把产品、交互视觉、技术方案、开发、Review、测试、部署串起来。

你只需对主控说需求；文档与门禁命令由 Agent 代写代跑。有问题才打断，否则自动推进。

架构见 [docs/architecture.md](docs/architecture.md)。角色边界见 [constitution.md](constitution.md)。知识从 [modus/knowledge/architecture-overview.md](modus/knowledge/architecture-overview.md) 进入。

## 开始一个 feature

在 Cursor 中启用 `specforge-lead`，描述需求即可。一条需求可拆成一个或多个 feature。底层等价于：

```bash
python -m pip install -e .
python -m specforge init FEAT-001
```

角色技能：`specforge-lead`、`specforge-product`、`specforge-ux`、`specforge-tech`、`specforge-dev`、`specforge-review`、`specforge-test`、`specforge-deploy`。

```bash
python -m specforge check features/FEAT-001 --gate G1
python -m unittest tests.test_gates
```

## Review 要点

- `blocking`：先修复并复审，禁止进入测试
- `dispute`：打断等人裁决
- `nit`：不挡门禁
