# AiAssitRequreimentDev 对话编排 + modus 设计规格

Date: 2026/11/03

## 目标

对话优先的多智能体流水线：主控编排；产品 grill；交互视觉与技术方案分离；开发 → Review → 测试 → 部署清单。modus 为一等知识层。默认自动推进，打断策略 G；Review 的 blocking 必修复审，dispute 打断。

## 门禁

G0 / G1 / G2(ux) / G2T(tech) / G3 / GR / G4 / GD。

## 工件

`spec.yaml`、`ux.yaml`、`tech.yaml`、`tasks.yaml`、`review.yaml`、`evidence.yaml`、`deploy.yaml`。`design.yaml` 退役。

## modus

`architecture-overview`、`constraint/`、`domain/change/` 全套 references 与 modules、`domain/_template/`、`README.md`。

## 非目标（一期）

部署 Agent 不执行上线；不内置多环境 CD；不虚构业务域内容。
