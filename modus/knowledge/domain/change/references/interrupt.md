# 打断策略

默认自动推进。下列情况主控必须停下来问人；其余结构问题只跑检查器。

| 码 | 条件 |
| --- | --- |
| I_ROLE_SELECT | 启动或换会话时 `state.actorRole` 为空；主控须在**本会话内**弹选项（AskQuestion 或编号菜单）选角色，再 `adopt`；禁止要求用户先打开 HTML |
| I_PATH_SELECT | `pathConfirmed` 不为 true；主控须在**本会话内**展示推荐并弹选项确认 full / light / light-auto，再 `path`；HTML picker 仅备用 |
| I_FEATURE_SPLIT | 需求级 `split.yaml` 为 `multi` 且尚未 `confirmedByHuman`；或拆分方案与 PRD 对不上 |
| I_PRODUCT_OPEN | `spec.openQuestions` 非空，或产品 grill 无法闭合 |
| I_UX_CHOICE | 需要人选视觉方案/风格，或用户要贴 Figma/图片 |
| I_TECH_RISK | 技术方案触及对外契约、数据迁移、权限安全、跨多领域 |
| I_REVIEW_DISPUTE | `review.yaml` 存在 `severity=dispute` 且未 `resolved` |
| I_TEST_STUCK | 测试失败且超过约定重试仍无法在写集内修复 |
| I_DEPLOY_CONFIRM | 部署清单已齐，上线前确认环境/窗口/回滚 |
| I_CHANGE_CONFIRM | 变更级别为 C3/C4（产品合同或范围拆分），或 C1 触及对外契约/迁移；须人确认后再 `approved` 并回退门禁；台账见 `change.yaml` |

`blocking` Review 项：**不**走打断码；主控直接退回 `implement` 派修并复审。

变更台账：`change.yaml` / `references/change-control.md`。
