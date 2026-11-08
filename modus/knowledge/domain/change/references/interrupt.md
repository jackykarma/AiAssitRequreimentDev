# 打断策略

默认自动推进。下列情况主控必须停下来问人；其余结构问题只跑检查器。

| 码 | 条件 |
| --- | --- |
| I_ROLE_SELECT | 启动或换会话时 `state.actorRole` 为空；必须先选产品经理/架构师SE/开发/测试/部署 |
| I_PATH_SELECT | `pathConfirmed` 不为 true；须先根据需求推荐并确认全量（full）或轻量（light） |
| I_FEATURE_SPLIT | 需求级 `split.yaml` 为 `multi` 且尚未 `confirmedByHuman`；或拆分方案与 PRD 对不上 |
| I_PRODUCT_OPEN | `spec.openQuestions` 非空，或产品 grill 无法闭合 |
| I_UX_CHOICE | 需要人选视觉方案/风格，或用户要贴 Figma/图片 |
| I_TECH_RISK | 技术方案触及对外契约、数据迁移、权限安全、跨多领域 |
| I_REVIEW_DISPUTE | `review.yaml` 存在 `severity=dispute` 且未 `resolved` |
| I_TEST_STUCK | 测试失败且超过约定重试仍无法在写集内修复 |
| I_DEPLOY_CONFIRM | 部署清单已齐，上线前确认环境/窗口/回滚 |

`blocking` Review 项：**不**走打断码；主控直接退回 `implement` 派修并复审。
