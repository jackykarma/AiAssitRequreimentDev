"""
/*********************************************************************************
 ** Copyright (C), 2019-2029, OPLUS Mobile Comm Corp., Ltd
 ** All rights reserved.
 **
 ** File: - smoke_english_multi.py
 ** Description: 大需求烟测「无痛学环」：1 REQ × 3 Feature，全程自动落齐产物
 ** Version: 1.0
 ** Date: 2026/11/18
 ** Author: limao2@Apps.Gallery
 **
 ** ------------------------------- Revision History: ----------------------------
 ** <author> <date> <version> <desc>
 ** ------------------------------------------------------------------------------
 ** limao2@Apps.Gallery 2026/11/18 1.0 INIT
 *********************************************************************************/
"""

from __future__ import annotations

from pathlib import Path

import yaml

from aiassitrequreimentdev.board import adopt_role, set_path
from aiassitrequreimentdev.gates import init_feature, init_requirement
from aiassitrequreimentdev.progress import accept_gate
from aiassitrequreimentdev.split import evaluate_requirement
from aiassitrequreimentdev.tasks_scaffold import scaffold_tasks
from aiassitrequreimentdev.template_headings import REQ_PRD_H2
from tests.smoke_diagrams import (
    install_feature_vocab_diagrams,
    install_req_architecture_diagrams,
)
from tests.smoke_english_app import (
    vocab_evidence_yaml,
    vocab_spec_yaml,
    vocab_tech_yaml,
    vocab_ux_yaml,
    write_painless_review_html,
    write_vocab_feature_prd,
    write_vocab_feature_tech,
)
from tests.smoke_small_vocab import _run_small
from tests.smoke_support import (
    write_req_architecture_expands,
    write_scenario_readme,
    write_yaml,
)
from tests.test_gates import valid_deploy, valid_review

# 需求名：无痛学环 —— 收藏 → 今日复习 → 连续学习进度
REQ_ID = "REQ-920-painless-study-loop-20261118"
FEAT_FAVORITE = "FEAT-920-notebook-favorite"
FEAT_REVIEW = "FEAT-921-daily-review-queue"
FEAT_STREAK = "FEAT-922-study-streak"
FEATURE_IDS = (FEAT_FAVORITE, FEAT_REVIEW, FEAT_STREAK)


def write_multi_req_prd(path: Path) -> None:
    bodies = {
        "背景与目标": (
            "- **问题**：英语学习者（对标无痛单词）缺一条「看见生词→入库→今日复习→看见进度」闭环，"
            "收藏摩擦高、复习无队列、打卡无反馈。\n"
            "- **目标**：三条可独立 G4 的 Feature 串成学环：收藏、今日复习、连续进度。\n"
            "- **价值**：提升入库率、复习完成率与留存。"
        ),
        "范围与非目标": (
            "- **In Scope**：语境卡收藏幂等、今日复习队列与打卡、连续学习天数统计展示。\n"
            "- **Out of Scope**：阅读器改版、会员支付、社交分享、云同步。\n"
            "- **约束与假设**：沿用生词本 wordId 与 SRS 到期字段；视觉 baseline=painless。"
        ),
        "核心用户旅程总览": (
            "| 旅程 | 角色 | 端到端成功结果 | 建议落入 feature |\n"
            "| --- | --- | --- | --- |\n"
            f"| 收藏入库 | 学习者 | 生词本有且仅一条 | {FEAT_FAVORITE} |\n"
            f"| 今日复习 | 学习者 | 打卡完今日队列 | {FEAT_REVIEW} |\n"
            f"| 看进度 | 学习者 | 看见连续天数更新 | {FEAT_STREAK} |"
        ),
        "功能与非功能总览": (
            "- **功能要点**：幂等收藏、日队列+防剧透打卡、连续天数。\n"
            "- **非功能要点**：首词可见性能；写失败可重试；无后台轮询。\n"
            "- **明确无 / 延后**：云同步、会员墙。"
        ),
        "边界与异常总览": (
            "- 收藏连点不双写；复习杀进程续跑；无到期词空态；连续天数跨日边界。"
        ),
        "验收总览": (
            "| 验收簇 | 摘要 | Feature |\n"
            "| --- | --- | --- |\n"
            f"| A* 收藏 | 写入/幂等 | {FEAT_FAVORITE} |\n"
            f"| A* 复习 | 队列/打卡 | {FEAT_REVIEW} |\n"
            f"| A* 进度 | 连续天数 | {FEAT_STREAK} |"
        ),
        "Feature 拆分依据": (
            "命中「可独立上线批次 + 异节奏」：收藏可先发为复习供词；复习主路径 UI 重；"
            "进度依赖打卡数据。故 `decision=multi`，三 Feature，人确认拆分。"
        ),
        "整需求架构": "见 `architecture/architecture.md`（Epic Design，覆盖三 Feature）。",
        "开放问题": "无。",
    }
    lines = [
        "# 需求：无痛学环（收藏 → 今日复习 → 连续进度）",
        "",
        "> 大需求烟测：对标 `tech.xiangzi.painless`。**3 个 Feature**，全程自动、产物不省略。",
        "",
        "| 字段 | 值 |",
        "| --- | --- |",
        f"| Requirement ID | {REQ_ID} |",
        "| 状态 | 可拆分 |",
        "| 建议 path | full（各 Feature 可再定） |",
        "",
    ]
    for title in REQ_PRD_H2:
        lines += [f"## {title}", "", bodies[title], ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_multi_split(req_dir: Path) -> None:
    split = {
        "requirementId": REQ_ID,
        "decision": "multi",
        "rationale": (
            "收藏 / 今日复习 / 连续进度可分批上线且节奏不同："
            "收藏先供词，复习主 UI，进度消费打卡；故拆 3 个可 G4 Feature。"
        ),
        "confirmedByHuman": True,
        "features": [
            {
                "id": FEAT_FAVORITE,
                "title": "语境卡收藏生词本",
                "scope": "词卡一键入库 + wordId 幂等；无独立新页",
                "path": "light-auto",
                "dependsOn": [],
            },
            {
                "id": FEAT_REVIEW,
                "title": "今日复习队列",
                "scope": "到期词日队列、防剧透词卡、打卡续跑",
                "path": "full",
                "dependsOn": [FEAT_FAVORITE],
            },
            {
                "id": FEAT_STREAK,
                "title": "连续学习进度",
                "scope": "基于打卡的连续天数展示与跨日结算",
                "path": "full",
                "dependsOn": [FEAT_REVIEW],
            },
        ],
    }
    (req_dir / "split.yaml").write_text(
        yaml.safe_dump(split, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


def write_multi_architecture(req_dir: Path) -> None:
    arch = req_dir / "architecture"
    install_req_architecture_diagrams(arch / "diagrams")
    kd_dir = arch / "key-func-design"
    kd_dir.mkdir(parents=True, exist_ok=True)
    (kd_dir / "KD_001_daily_queue.md").write_text(
        f"""# KD-001：日队列快照与打卡幂等

**Requirement**：{REQ_ID}  
**Owner Feature**：{FEAT_REVIEW}  
**日期**：2026-11-18

## 依赖的其他 KD

| 前置 KD | 对应文件 | 说明 |
| --- | --- | --- |
| — | — | 依赖 {FEAT_FAVORITE} 供词，非 KD 前置 |

- **类型**：疑难点
- **核心方案**：自然日 `QueueSnapshot` + 打卡键 `day+wordId`；当日不重排；杀进程可续跑。
- **边界**：无到期词空态；连点靠 UNIQUE；不改 SRS 公式。
""",
        encoding="utf-8",
    )
    (kd_dir / "KD_002_favorite_idempotent.md").write_text(
        f"""# KD-002：生词本收藏幂等

**Owner Feature**：{FEAT_FAVORITE}

- **核心方案**：`UNIQUE(wordId)`；命中返回 Already；写失败可重试。
""",
        encoding="utf-8",
    )
    (kd_dir / "KD_003_streak.md").write_text(
        f"""# KD-003：连续学习天数跨日结算

**Owner Feature**：{FEAT_STREAK}

- **核心方案**：以自然日是否存在至少一次成功打卡为「活跃日」；连续天数按日历向前累计。
""",
        encoding="utf-8",
    )

    md = f"""# 需求级技术方案（Epic Design）：{REQ_ID}

> **定位**：无痛学环整需求技术方案总册。对齐仓内 Epic Design 模板。  
> **Feature**：{FEAT_FAVORITE} / {FEAT_REVIEW} / {FEAT_STREAK}  
> **绘图**：Archify 真图内嵌。

**Requirement**：{REQ_ID}  
**设计 Version**：v0.1.0  
**日期**：2026-11-18

**本需求设计文件组成**：

| 文件 / 目录 | 对应章节 | 内容 |
| --- | --- | --- |
| `architecture.md` | 全部 | Epic 总览 |
| `architecture.yaml` | 门禁 | diagrams / risks / features |
| `diagrams/` | §四 / §五 | Archify html+png |
| `key-func-design/` | §七 | KD-001~003 |

---

## 变更记录（增量变更）

| 版本 | 日期 | 变更范围（REQ/Feature/Story） | 摘要 | 影响模块 | 是否回滚设计 |
| --- | --- | --- | --- | --- | --- |
| v0.1.0 | 2026-11-18 | REQ | 无痛学环三 Feature Epic | notebook/review/streak | 否 |

---

## 设计前置检查

### 前置检查清单

- [x] 已读需求级 `prd.md`、`split.yaml`（multi + 人确认）
- [x] 跨 Feature 共享能力已明确 Owner
- [x] 已对照 painless 生词本 / 复习节奏校准边界
- [x] 三 Feature P0 A* 均有覆盖策略

### 跨 Feature 共享能力登记

| 共享能力 | Owner Feature | 消费方 | 设计/契约位置 |
| --- | --- | --- | --- |
| 生词本条目 / wordId | {FEAT_FAVORITE} | {FEAT_REVIEW} | KD-002；Notebook |
| 日队列与打卡记录 | {FEAT_REVIEW} | {FEAT_STREAK} | KD-001；CheckInStore |
| 连续天数展示 | {FEAT_STREAK} | — | KD-003 |

### P0 覆盖快照（与各 Feature spec 对照）

| Feature | 验收/场景 | 覆盖的设计章节/图 | 状态 |
| --- | --- | --- | --- |
| {FEAT_FAVORITE} | 收藏写入/幂等 | §七 KD-002 / L1 | 已覆盖 |
| {FEAT_REVIEW} | 队列+打卡 | §五 / KD-001 / 协作图 | 已覆盖 |
| {FEAT_STREAK} | 连续天数 | §七 KD-003 / L1 | 已覆盖 |

### 前置检查结论

- **日期**：2026-11-18 / **结论**：通过

---

## 一、简介

### 1.1 目的和对象

| 项 | 内容 |
| --- | --- |
| 阅读对象 | 设计 / 开发 / 测试 / 评审 |
| 文档目的 | 锁定「无痛学环」三 Feature 边界、依赖与关键设计 |

### 1.2 范围

| 来源 | 相对路径 | 要点 |
| --- | --- | --- |
| 需求 PRD | [`../prd.md`](../prd.md) | 收藏→复习→进度 |
| 拆分 | [`../split.yaml`](../split.yaml) | multi，三 Feature |
| UX | 各 Feature `prototype/ux/` | painless（复习/进度有 UI） |

---

## 二、需求概述

### 2.1 需求背景

| 来源 | 要点 |
| --- | --- |
| PRD | 对标无痛单词，补齐入库-复习-进度闭环 |

### 2.2 需求范围及限制（按 Feature 索引）

| Feature ID | In Scope 摘要 | Out of Scope 摘要 | 关键 NFR |
| --- | --- | --- | --- |
| {FEAT_FAVORITE} | 收藏幂等写库 | 复习 UI | 写失败可重试 |
| {FEAT_REVIEW} | 日队列、防剧透打卡 | 会员墙 | 首词 ≤500ms |
| {FEAT_STREAK} | 连续天数展示 | 排行榜 | 跨日结算正确 |

---

## 三、领域模型

### 3.1 领域概念

学环共享 Word / NotebookEntry；复习引入 QueueSnapshot / CheckInRecord；进度引入 StudyStreak。

### 3.2 领域概念词汇表（必须）

| 概念（中文） | 名称（英文/代码） | 定义 | 关键属性/状态 | 不变量 | 关联概念 |
| --- | --- | --- | --- | --- | --- |
| 生词 | Word | 可收藏/复习词条 | wordId | 全局唯一 | NotebookEntry |
| 生词本条目 | NotebookEntry | 收藏记录 | wordId, dueAt | 一词一条 | Word |
| 日队列快照 | QueueSnapshot | 当日待复习序 | day, wordIds, cursor | 同日一份 | CheckInRecord |
| 打卡记录 | CheckInRecord | 某日对词结果 | day, wordId, result | 同日同词一条 | StudyStreak |
| 连续天数 | StudyStreak | 连续活跃自然日数 | current, best | current≥0 | CheckInRecord |

### 3.3 概念关系图（推荐，可选）

N/A：见各 Feature 类图；Epic 以词汇表为准。

---

## 四、零层架构（L0）

### 4.1 边界说明

- **需求边界**：本地客户端学环；无云同步。
- **主要子系统**：词卡收藏、今日复习、进度展示、生词本、SQLite。

### 4.2 零层架构图（必须）

![L0 架构图](diagrams/req.L0.architecture.png)

### 4.3 架构设计说明（必须）

- **边界与职责**：收藏供词 → 复习消费到期集合并写打卡 → 进度只读打卡算连续天数。
- **分层与依赖方向**：UI → 各 Feature 领域 → Notebook/SQLite；禁止进度写复习表。
- **关键数据流**：favorite → notebook；getTodayQueue/checkIn → queue/checkin；streak ← checkin。
- **外部依赖策略**：无新增三方服务。
- **可演进性**：云同步可按 wordId / day+wordId / streak 快照分域上线。

### 4.4 外部依赖清单

| 依赖项 | 类型 | 能力 | 通信 | 故障模式 | 策略 |
| --- | --- | --- | --- | --- | --- |
| Notebook | 模块 | 到期词/收藏 | 进程内 | 读失败 | 空态/重试 |
| SQLite | 存储 | 持久化 | 本地 | 写失败 | 可重试不丢意图 |

---

## 五、一层架构（L1）

### 5.1 一层框架图（必须）

![L1 架构图](diagrams/req.L1.architecture.png)

### 5.2 组件清单与职责（必须）

| 模块/组件 | 职责 | 归属 Feature | 本需求改动 |
| --- | --- | --- | --- |
| FavoriteAction / NotebookRepository | 收藏幂等 | {FEAT_FAVORITE} | 新增/修改 |
| DailyReviewFragment / ReviewQueueRepository / CheckInStore | 队列与打卡 | {FEAT_REVIEW} | 新增 |
| StreakFragment / StreakCalculator | 连续天数 | {FEAT_STREAK} | 新增 |

### 5.3 组件协作流程图（必须）

![主路径协作](diagrams/req.overview.workflow.png)

> 主图侧重复习闭环；收藏与进度在各自 Feature 薄 tech 补增量说明。

### 5.4 技术方案选型

| 决策点 | 候选 | 选择 | 理由 |
| --- | --- | --- | --- |
| 拆分 | 单 Feature / 三 Feature | 三 Feature | 可分批 G4 |
| 队列 | 每次重排 / 日快照 | 日快照 | 体验稳定 |
| 连续天数 | 会话计数 / 自然日活跃 | 自然日活跃 | 跨进程可恢复 |

---

## 六、技术风险与边界场景

### 6.1 技术风险与消解策略（绑定 Feature / Story）

| ID | 风险 | 影响 | 落在 Feature / Story | 对策 |
| --- | --- | --- | --- | --- |
| RISK-1 | 收藏双写 | 复习池重复 | {FEAT_FAVORITE} | UNIQUE(wordId) |
| RISK-2 | 复习续跑错误 | 重复打卡 | {FEAT_REVIEW} | day+wordId 幂等 |
| RISK-3 | 跨日 streak 错算 | 进度不信 | {FEAT_STREAK} | 以打卡表活跃日为准 |

### 6.2 边界与异常场景枚举

| 场景 | 类别 | 对策落点 |
| --- | --- | --- |
| 连点收藏 | 并发 | KD-002 |
| 杀进程复习 | 生命周期 | KD-001 |
| 时区/跨日 0 点 | 时间 | KD-003 |

---

## 七、关键功能与疑难点/亮点设计

### 7.1 关键设计清单

| KD | 名称 | 类型 | 前置 KD | 影响 Feature | 文件 |
| --- | --- | --- | --- | --- | --- |
| KD-001 | 日队列快照与打卡幂等 | 疑难 | — | {FEAT_REVIEW} | `./key-func-design/KD_001_daily_queue.md` |
| KD-002 | 生词本收藏幂等 | 疑难 | — | {FEAT_FAVORITE} | `./key-func-design/KD_002_favorite_idempotent.md` |
| KD-003 | 连续天数跨日结算 | 疑难 | KD-001 | {FEAT_STREAK} | `./key-func-design/KD_003_streak.md` |

### 7.2 详细设计引用

见 `key-func-design/` 三份 KD；切片细化在各 Feature 薄 tech。

---

## 八、技术评估（NFR）

> **强制**：详表见 [`nfr.md`](./nfr.md)（对齐 `templates/design/nfr.md`）。本节只保留结论。

| 维度 | 结论 / 预算 | 缓解 | 详表 |
| --- | --- | --- | --- |
| 性能 | 复习首词 ≤500ms；收藏/streak 本地查询 | 快照与索引 | [./nfr.md](./nfr.md) |
| 稳定性 | 写失败可重试；进度只读打卡 | 幂等键 | [./nfr.md](./nfr.md) |
| 功耗 | 无后台轮询 | 用户触发 | [./nfr.md](./nfr.md) |
| 其它 | 不降 minSdk | — | [./nfr.md](./nfr.md) |

---

## 九、接口设计

> **强制**：字段级详表见 [`interface-design.md`](./interface-design.md)。

| ID | 方向 | 类型 | 提供方 | 消费方 | 摘要 | 冻结时机 |
| --- | --- | --- | --- | --- | --- | --- |
| IF-F1 | provided | api | {FEAT_FAVORITE} | 词卡 UI | favorite(wordId) | 该 Feature G2T 前 |
| IF-R1 | provided | api | {FEAT_REVIEW} | 复习 UI | getTodayQueue / checkIn | 该 Feature G2T 前 |
| IF-S1 | provided | api | {FEAT_STREAK} | 进度 UI | getStreak() | 该 Feature G2T 前 |
| CTR-1 | consumed | data | {FEAT_FAVORITE} | {FEAT_REVIEW} | Notebook 到期集合 | 复习 G2T 前冻结契约 |
| CTR-2 | consumed | data | {FEAT_REVIEW} | {FEAT_STREAK} | 打卡活跃日 | 进度 G2T 前冻结契约 |

详表：[./interface-design.md](./interface-design.md)。

---

## 十、数据库设计

> **强制**：库表详表见 [`database-design.md`](./database-design.md)。

| 存储 | 变更 | 目的 | Owner Feature |
| --- | --- | --- | --- |
| t_notebook_entry | modify | 收藏 UNIQUE(wordId) | {FEAT_FAVORITE} |
| t_review_queue_day | add | 日队列快照 | {FEAT_REVIEW} |
| t_review_checkin | add | 打卡幂等 | {FEAT_REVIEW} |
| t_study_streak | add | 连续天数缓存（可重建） | {FEAT_STREAK} |

详表：[./database-design.md](./database-design.md)。

---

## 十一、埋点技术方案

> **强制**：埋点字段规约见 [`analytics-tracking.md`](./analytics-tracking.md)。

| 事件 | 触发 | 关键字段 | Owner |
| --- | --- | --- | --- |
| notebook_favorite | 收藏成功/已存在 | wordId | {FEAT_FAVORITE} |
| review_session_start | 进入非空队列 | queueSize | {FEAT_REVIEW} |
| review_checkin_write | 打卡落盘 | wordId | {FEAT_REVIEW} |
| study_streak_view | 打开进度页 | currentStreak | {FEAT_STREAK} |

详表：[./analytics-tracking.md](./analytics-tracking.md)。

---

## 十二、Feature 与 Story 拆解索引

### 12.1 拆解策略与约束

- multi：三 Feature 可独立 G4；依赖见 split
- 本需求不启用 Story

### 12.2 Feature 列表（与 split 对齐）

| Feature | 范围摘要 | dependsOn | 建议 path | 是否启用 Story |
| --- | --- | --- | --- | --- |
| {FEAT_FAVORITE} | 收藏幂等 | — | light-auto | 否 |
| {FEAT_REVIEW} | 今日复习 | {FEAT_FAVORITE} | full | 否 |
| {FEAT_STREAK} | 连续进度 | {FEAT_REVIEW} | full | 否 |

### 12.3 Story 列表（按 Feature 分组，可选）

本需求不启用 Story；细节在各 Feature 薄 tech / tasks。

### 12.4 Story 依赖与并行度

N/A。

### 12.5 Feature → 设计覆盖矩阵

| Feature | Epic 章节/KD | Story（若有） | Feature 薄 tech |
| --- | --- | --- | --- |
| {FEAT_FAVORITE} | KD-002 | — | features/{FEAT_FAVORITE}/tech.md |
| {FEAT_REVIEW} | §五 / KD-001 | — | features/{FEAT_REVIEW}/tech.md |
| {FEAT_STREAK} | KD-003 | — | features/{FEAT_STREAK}/tech.md |

---

## 十三、Story 详细设计索引

### 13.1 索引表

| Story | 路径 | 关联 KD | 状态 |
| --- | --- | --- | --- |
| — | — | — | 不启用 Story |

### 13.2 依赖总览

`storiesEnabled=false`。

### 13.3 覆盖度检查

- [x] 无 Story 越权验收
- [x] G4 只认各 Feature evidence

---

## 附录：与 Feature tech / Story / tasks 的对应关系

| 层级 | 文档 | 职责 |
| --- | --- | --- |
| Epic | `architecture.md` | 整需求；check-req |
| Feature 薄 tech | `features/*/tech.md` | 各刀交付；G2T |
| Story | — | 未启用 |
| Task | `tasks.yaml` | 写集与验证 |
"""
    (arch / "architecture.md").write_text(md, encoding="utf-8")
    write_req_architecture_expands(
        arch,
        req_id=REQ_ID,
        feature_ids=FEATURE_IDS,
        domain="english-learning",
    )
    (arch / "architecture.yaml").write_text(
        yaml.safe_dump(
            {
                "requirementId": REQ_ID,
                "summary": "无痛学环：收藏 → 今日复习 → 连续进度（三 Feature）",
                "features": list(FEATURE_IDS),
                "contracts": [
                    {
                        "id": "CTR-1",
                        "from": FEAT_FAVORITE,
                        "to": FEAT_REVIEW,
                        "summary": "Notebook 到期集合只读",
                    },
                    {
                        "id": "CTR-2",
                        "from": FEAT_REVIEW,
                        "to": FEAT_STREAK,
                        "summary": "打卡活跃日只读",
                    },
                ],
                "contractsNoneReason": "",
                "keyDesigns": [
                    {"id": "KD-001", "title": "日队列快照与打卡幂等", "summary": "day snapshot"},
                    {"id": "KD-002", "title": "收藏幂等", "summary": "UNIQUE wordId"},
                    {"id": "KD-003", "title": "连续天数", "summary": "自然日活跃累计"},
                ],
                "keyDesignsNoneReason": "",
                "risks": [
                    {
                        "id": "RISK-1",
                        "description": "收藏双写",
                        "impact": "复习池重复",
                        "mitigation": "UNIQUE(wordId)",
                    },
                    {
                        "id": "RISK-2",
                        "description": "复习续跑错误",
                        "impact": "重复打卡",
                        "mitigation": "day+wordId",
                    },
                    {
                        "id": "RISK-3",
                        "description": "streak 错算",
                        "impact": "进度不信",
                        "mitigation": "以打卡活跃日为准",
                    },
                ],
                "risksNoneReason": "",
                "openTechQuestions": [],
                "diagrams": [
                    {
                        "id": "D-L0",
                        "type": "architecture",
                        "layer": 0,
                        "title": "L0",
                        "scope": "学环上下文",
                        "tool": "archify",
                        "html": "diagrams/req.L0.architecture.html",
                        "png": "diagrams/req.L0.architecture.png",
                    },
                    {
                        "id": "D-L1",
                        "type": "architecture",
                        "layer": 1,
                        "title": "L1",
                        "scope": "三 Feature 模块",
                        "tool": "archify",
                        "html": "diagrams/req.L1.architecture.html",
                        "png": "diagrams/req.L1.architecture.png",
                    },
                    {
                        "id": "D-WF",
                        "type": "workflow",
                        "title": "复习主协作",
                        "scope": "今日复习主路径",
                        "tool": "archify",
                        "html": "diagrams/req.overview.workflow.html",
                        "png": "diagrams/req.overview.workflow.png",
                    },
                ],
                "diagramsNoneReason": "",
            },
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def _patch_review_ids() -> None:
    """让既有复习烟测文案挂到 FEAT-921 / REQ-920。"""
    import tests.smoke_english_app as eng

    eng.REQ_ID = REQ_ID
    eng.FEATURE_ID = FEAT_REVIEW


def run_review_feature(root: Path) -> Path:
    _patch_review_ids()
    feature = init_feature(root, FEAT_REVIEW, requirement_id=REQ_ID)
    set_path(feature, "full")
    adopt_role(feature, "product")
    write_yaml(feature / "spec.yaml", vocab_spec_yaml(FEAT_REVIEW))
    write_vocab_feature_prd(feature / "prd.md")
    # 修正 prd 内旧 ID（write 函数仍可能写常量）
    prd = (feature / "prd.md").read_text(encoding="utf-8")
    prd = prd.replace("FEAT-910-daily-review-queue", FEAT_REVIEW).replace(
        "REQ-910-vocab-daily-review-20261118", REQ_ID
    )
    (feature / "prd.md").write_text(prd, encoding="utf-8")
    write_painless_review_html(feature / "prototype" / "index.html", title="今日复习·产品")
    accept_gate(feature, "G0")
    accept_gate(feature, "G1")
    adopt_role(feature, "ux")
    write_yaml(feature / "ux.yaml", vocab_ux_yaml())
    write_painless_review_html(feature / "prototype" / "ux" / "index.html", title="今日复习·UX")
    accept_gate(feature, "G2")
    adopt_role(feature, "architect")
    write_vocab_feature_tech(feature)
    tech = (feature / "tech.md").read_text(encoding="utf-8")
    tech = tech.replace("FEAT-910-daily-review-queue", FEAT_REVIEW).replace(
        "REQ-910-vocab-daily-review-20261118", REQ_ID
    )
    (feature / "tech.md").write_text(tech, encoding="utf-8")
    accept_gate(feature, "G2T")
    scaffold_tasks(feature, mode="per-acceptance", force=True)
    accept_gate(feature, "G3")
    adopt_role(feature, "reviewer")
    write_yaml(feature / "review.yaml", valid_review())
    accept_gate(feature, "GR")
    adopt_role(feature, "tester")
    write_yaml(feature / "evidence.yaml", vocab_evidence_yaml())
    accept_gate(feature, "G4")
    adopt_role(feature, "deployer")
    write_yaml(feature / "deploy.yaml", valid_deploy())
    accept_gate(feature, "GD")
    return feature


def streak_spec(feature_id: str) -> str:
    return f"""
id: {feature_id}
problem: 学习者打卡后看不到连续学习反馈，难以形成每日打开习惯
nonGoals:
  - 不做排行榜与社交对比
  - 不改今日复习队列算法
uiRequired: true
uiNoneReason: ""
userJourneys:
  - id: UJ1
    persona: 完成或准备复习的英语学习者
    entry: 图表/我的 · 连续学习卡片
    steps: "1. 打开进度 2. 看见当前连续天数与最佳记录 3. 今日已打卡则高亮"
    success: 连续天数与打卡事实一致
functionalRequirements:
  - id: FR1
    description: 系统必须根据打卡活跃日计算当前连续天数
    scenarios: [S1]
  - id: FR2
    description: 用户必须能看到最佳连续记录
    scenarios: [S1]
nonFunctionalRequirements:
  - id: NFR1
    category: performance
    requirement: 打开进度页到数字可见 ≤300ms
    measure: 首帧 streak 数字渲染
nfrNoneReason: ""
scenarios:
  - id: S1
    trigger: 用户打开进度页
    outcome: 展示 current/best
    failure: 无打卡历史时展示 0 并引导去复习
edgeCases:
  - id: E1
    trigger: 中间空一日
    expected: current 归零，best 保留历史最大
    userVisible: 当前连续变为 0，最佳仍显示旧值
edgeNoneReason: ""
acceptance:
  - id: A1
    given: 连续两日均有打卡
    when: 打开进度页
    then: currentStreak≥2
    verify: StudyStreakCurrentTest
    covers: [FR1, S1]
  - id: A2
    given: 历史 best=5 且昨日未打卡
    when: 打开进度页
    then: current=0 且 best=5
    verify: StudyStreakBreakTest
    covers: [FR2, E1]
constraints:
  - research/painless-ui/ui-kit/THEME.md
affected:
  - app/src/vocab/streak/
  - app/src/vocab/review/
openQuestions: []
"""


def streak_ux() -> str:
    return """
skip: false
reason: ""
uiKit:
  baseline: research/painless-ui/ui-kit
interactionRules:
  - id: IR1
    when: 打开连续进度页
    behavior: 展示当前连续与最佳；无历史则 0 + 引导复习
    states: streak_ready
    feedback: 数字与简短文案
    coversAcceptance: [A1, A2]
visual:
  baseline: painless
  notes: "对标无痛单词图表/统计气质"
  motion:
    - id: M1
      trigger: 数字首次出现
      effect: 轻微上浮淡入
htmlPrototype:
  entry: prototype/ux/index.html
  pages: []
acceptance:
  - id: A1
    flow: 连续两日打卡后看见 current≥2
    surface: 连续学习卡片
  - id: A2
    flow: 断签后 current=0 best 保留
    surface: 连续学习卡片
artifacts: []
"""


def streak_tech_yaml() -> str:
    return """
summary: 连续学习天数——以打卡活跃自然日累计
aiConstraints:
  mustFollow:
    - 以 t_review_checkin 是否存在该日记录判定活跃日
    - 断日则 current 归零，best 取历史最大
  mustNot:
    - 不得只按 App 打开次数计连续天数
  mustNotNoneReason: ""
  invariants:
    - best >= current 恒成立
  invariantsNoneReason: ""
keyDesigns:
  - id: KD-F01
    title: 跨日 streak 结算
    kinds: [cornerstone]
    judgment: 错算会直接毁掉激励
    problem: 时区与断日
    decision: 自然日活跃集合向前扫描
    coreScheme: >
      从今天起向前找连续活跃日得到 current；扫描全部活跃日片段得 best；
      可选缓存 t_study_streak，打卡成功后失效重建。
    mustFollow:
      - 活跃日定义=当日至少一条 checkin
    pitfalls:
      - 不要用会话时长代替打卡
    relatedDiagrams: [D-L1]
    relatedAcceptance: [A1, A2]
keyDesignsNoneReason: ""
interfaces:
  - name: StreakApi
    kind: api
    direction: provided
    contract: getStreak() → current, best
    request: "getStreak()"
    response: "{current:Int, best:Int}"
    errors: []
    concurrencyNotes: 只读
    consumers: [StreakFragment]
    providers: [StreakCalculator]
interfacesNoneReason: ""
diagrams:
  - id: D-L0
    type: architecture
    layer: 0
    title: streak L0 上下文
    scope: 学习者 / 客户端 / 打卡数据
    tool: archify
    html: diagrams/vocab.L0.architecture.html
    png: diagrams/vocab.L0.architecture.png
  - id: D-L1
    type: architecture
    layer: 1
    title: streak 模块
    scope: Streak UI → Calculator → CheckIn 只读
    tool: archify
    html: diagrams/vocab.L1.architecture.html
    png: diagrams/vocab.L1.architecture.png
  - id: D-WF
    type: workflow
    title: 打开进度主流程
    scope: 进入→计算→展示/断日
    tool: archify
    html: diagrams/vocab.review.workflow.html
    png: diagrams/vocab.review.workflow.png
  - id: D-SEQ
    type: sequence
    title: getStreak 时序
    scope: UI → Calculator → CheckIn
    tool: archify
    html: diagrams/vocab.checkin.sequence.html
    png: diagrams/vocab.checkin.sequence.png
  - id: D-CL
    type: class
    title: streak 类型
    scope: StudyStreak / Calculator
    tool: archify
    html: diagrams/vocab.review.class.html
    png: diagrams/vocab.review.class.png
diagramsNoneReason: ""
architectureLayerGaps: ""
changedFiles:
  - path: app/src/vocab/streak/StreakFragment.kt
    action: add
    note: 进度 UI
  - path: app/src/vocab/streak/StreakCalculator.kt
    action: add
    note: 连续天数
techChoices:
  - topic: 数据源
    decision: 复用打卡表
    alternatives: [独立打开日志]
    rationale: 与复习激励一致
risks:
  - id: R1
    description: 跨日错算
    impact: 进度不信
    mitigation: 单测覆盖断日
risksNoneReason: ""
nfr:
  performance:
    assessment: 本地扫描可接受
    mitigations: 可缓存
  stability:
    assessment: 只读打卡
    mitigations: 打卡写失败不影响历史 best
  power:
    assessment: 无后台
    mitigations: 进入页计算
  memory:
    involved: false
    noneReason: 无大缓存
  security:
    involved: false
    noneReason: 无敏感字段
  compatibility:
    involved: false
    noneReason: 不降 minSdk
  romSize:
    involved: false
    noneReason: 少量代码
  algorithm:
    involved: true
    assessment: 线性扫描活跃日
    mitigations: 日级数据量小
dataDesign:
  involved: true
  tables:
    - name: t_study_streak
      change: add
      purpose: 可选缓存
      fields:
        - name: current
          type: INTEGER
          description: 当前连续
          required: true
        - name: best
          type: INTEGER
          description: 最佳连续
          required: true
  models:
    - name: StudyStreak
      path: app/src/vocab/streak/StudyStreak.kt
      note: 进度值对象
  consistencyNotes: 缓存失效以打卡写成功为信号
  noneReason: ""
tracking:
  product:
    - event: study_streak_view
      trigger: 打开进度页
      fields:
        - id: currentStreak
          description: 当前连续
          type: Int
  technical: []
  noneReason: ""
acceptance:
  - id: A1
    architecture: StreakCalculator 向前扫描
    interface: getStreak
    data: t_review_checkin
    failureRecovery: 无数据返回 0
    constraints:
      - research/painless-ui/ui-kit/THEME.md
  - id: A2
    architecture: best 保留历史最大片段
    interface: getStreak
    data: t_review_checkin
    failureRecovery: 断日 current=0
    constraints: []
"""


def streak_evidence() -> str:
    return """
results:
  - acceptanceId: A1
    command: ./gradlew :app:testDebugUnitTest --tests StudyStreakCurrentTest
    exitCode: 0
    excerpt: BUILD SUCCESSFUL
  - acceptanceId: A2
    command: ./gradlew :app:testDebugUnitTest --tests StudyStreakBreakTest
    exitCode: 0
    excerpt: BUILD SUCCESSFUL
"""


def write_streak_prd(path: Path) -> None:
    path.write_text(
        f"""# Feature：连续学习进度（无痛学环）

| 字段 | 值 |
| --- | --- |
| Feature ID | {FEAT_STREAK} |
| 关联需求 | {REQ_ID} |
| 状态 | 冻结 |
| 有无 UI | 有（painless 进度卡） |
| path | full |

## 背景与目标

- **问题**：打卡后缺少连续天数反馈，习惯难养成。
- **目标**：打开进度即见 current/best，且与打卡事实一致。
- **价值**：强化每日打开与复习动机。

## 范围与非目标

- **In Scope**：连续天数计算与展示、断日归零、最佳保留。
- **Out of Scope / 非目标**：排行榜、社交、改复习算法。
- **约束**：只读 {FEAT_REVIEW} 打卡表。

## 核心用户旅程（UJ*）

| ID | 角色 | 入口 | 步骤（1…n） | 成功结果 |
| --- | --- | --- | --- | --- |
| UJ1 | 学习者 | 图表/我的 | 1. 打开 2. 看数字 | current/best 正确 |

## 功能需求（FR*）

| ID | 描述 | 关联 UJ/E |
| --- | --- | --- |
| FR1 | 必须按活跃日算 current | UJ1 |
| FR2 | 必须展示 best | UJ1 / E1 |

## 非功能需求（NFR*）

| ID | 类别 | 要求 | 度量 |
| --- | --- | --- | --- |
| NFR1 | performance | 数字可见 ≤300ms | 首帧 |

## 边界与异常（E*）

| ID | 触发 | 期望 | 用户可见 |
| --- | --- | --- | --- |
| E1 | 中间空一日 | current=0，best 保留 | 文案提示已断签 |

## 验收标准（A*）

| ID | Given | When | Then | verify |
| --- | --- | --- | --- | --- |
| A1 | 连续两日打卡 | 打开进度 | current≥2 | StudyStreakCurrentTest |
| A2 | best=5 且昨日未打卡 | 打开进度 | current=0 best=5 | StudyStreakBreakTest |

## 产品原型

见 `prototype/index.html` 与 `prototype/ux/index.html`。

## 补充场景（S*，可选）

| ID | 触发 | 结果 | 失败 |
| --- | --- | --- | --- |
| S1 | 打开进度 | 展示数字 | 无历史 → 0 |

## 开放问题

无。
""",
        encoding="utf-8",
    )


def write_streak_html(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"/><title>连续学习</title>
<link rel="stylesheet" href="../../../../../../research/painless-ui/ui-kit/tokens.css"/>
<style>
body{margin:0;font-family:"Songti SC",serif;background:#f3efe6;color:#2c2a26}
.pk-app{max-width:420px;margin:0 auto;padding:20px}
.pk-card{background:#faf7f0;border-radius:16px;padding:24px}
.pk-soft-btn{border:0;border-radius:12px;padding:10px 14px;background:#dce8d4}
.pk-metric{font-size:40px;font-weight:700;color:#3d5a3a}
[hidden]{display:none!important}
</style></head>
<body class="pk-app">
<section id="main" class="pk-card">
  <h1>连续学习</h1>
  <p>当前连续</p>
  <div class="pk-metric" id="current">2</div>
  <p>最佳记录 <span id="best">5</span> 天</p>
  <button type="button" class="pk-soft-btn" id="break" data-go="broken">模拟断签</button>
</section>
<section id="broken" class="pk-card" hidden>
  <h1>连续学习</h1>
  <p>当前连续</p>
  <div class="pk-metric">0</div>
  <p>最佳记录仍为 5 天</p>
  <button type="button" class="pk-soft-btn" id="back" data-go="main">返回</button>
</section>
<script>
document.querySelectorAll("[data-go]").forEach(function(btn){
  btn.addEventListener("click", function(){
    var t=btn.getAttribute("data-go");
    document.getElementById("main").hidden = t!=="main";
    document.getElementById("broken").hidden = t!=="broken";
  });
});
</script>
</body></html>
""",
        encoding="utf-8",
    )


def write_streak_tech(feature_dir: Path) -> None:
    # full 路径须 architecture L0/L1 + workflow + sequence + class（真图，不省略）
    install_feature_vocab_diagrams(feature_dir / "diagrams")
    (feature_dir / "tech.md").write_text(
        f"""# 切片技术方案（薄合同）：{FEAT_STREAK}

**Feature**：{FEAT_STREAK}  
**关联需求**：{REQ_ID}  
**Epic Design**：`requirements/{REQ_ID}/architecture/architecture.md`  
**path**：full

---

## 变更记录

| 版本 | 日期 | 摘要 | 影响 |
| --- | --- | --- | --- |
| v0.1.0 | 2026-11-18 | 连续进度初版 | — |

---

## 设计前置检查

- [x] 已读 prd/spec/ux
- [x] 已读 tech-spec
- [x] 已读 Epic 与 split（依赖 {FEAT_REVIEW}）
- [x] A* 有落点
- [x] 未重抄 Epic

---

## 一、简介与交付范围

| 项 | 内容 |
| --- | --- |
| 问题 | 打卡无连续反馈 |
| 本切片交付 | A1/A2 连续天数 |
| 非目标 | 排行榜 |
| path | full |
| Story | 未启用 |

---

## 二、验收追溯

| ID | 摘要 | 技术落点 |
| --- | --- | --- |
| A1 | current≥2 | KD-F01 / getStreak |
| A2 | 断日 current=0 best 保留 | KD-F01 |

---

## 三、Epic 引用与本切片增量

| 类型 | 引用 | 本切片增量 |
| --- | --- | --- |
| L0/L1 | Epic §四/§五 | Streak UI + Calculator |
| KD | KD-003 | 本刀 KD-F01 |
| 接口/数据/埋点 | Epic §九～§十一 | StreakApi / t_study_streak |
| 风险/NFR | Epic §六/§八 | 跨日错算 |

---

## 四、本切片架构增量

### 4.1 相对 Epic 的架构说明

只读 {FEAT_REVIEW} 打卡表，不写队列；进度模块独立。L0/L1 与流程/时序/类图如下（Archify 真图）。

### 4.2 本切片架构图（增量或引用内嵌）

![L0](diagrams/vocab.L0.architecture.png)

![L1](diagrams/vocab.L1.architecture.png)

![流程](diagrams/vocab.review.workflow.png)

![时序](diagrams/vocab.checkin.sequence.png)

![类图](diagrams/vocab.review.class.png)

### 4.3 模块改动面

| 模块 | 本切片改动 | 说明 |
| --- | --- | --- |
| StreakFragment | 新增 | 进度 UI |
| StreakCalculator | 新增 | 连续天数 |

---

## 五、本切片关键设计

| KD | 标题 | 相对 Epic | mustFollow 摘要 |
| --- | --- | --- | --- |
| KD-F01 | 跨日 streak 结算 | 细化 KD-003 | 活跃日=有打卡 |

### KD-F01：跨日 streak 结算

- **问题**：断日与时区导致错算。
- **决策**：自然日活跃集合向前扫描。
- **核心链路**：读 checkin 活跃日 → current / best。
- **必须遵守**：不以打开次数计。
- **坑**：缓存不失效会显示旧值。

---

## 六、本切片约束与风险增量

| 维度 | 增量结论 | tech.yaml 字段 |
| --- | --- | --- |
| 风险 | 跨日错算 | risks |
| NFR | ≤300ms | nfr |
| 接口 | getStreak | interfaces |
| 数据 | t_study_streak 缓存 | dataDesign |
| 埋点 | study_streak_view | tracking |

---

## 七、Story 与任务指引

| Story / 任务 | 写集 | 覆盖 A* | 说明 |
| --- | --- | --- | --- |
| T1/T2 | app/src/vocab/streak/ | A1/A2 | per-acceptance |

---

## 附录：与 tech.yaml / Epic / Story 对应

| 本文 | 下游 |
| --- | --- |
| §二 | acceptance |
| §四 | diagrams |
| §五 | keyDesigns |
""",
        encoding="utf-8",
    )
    (feature_dir / "tech-spec.md").write_text(
        f"""# 技术约束（Tech Spec）：{FEAT_STREAK}

## Tech Spec 前置检查

- [x] 与 tech.md / tech.yaml 一致
- [x] 只读打卡，不改复习写路径

## 变更记录

| 版本 | 日期 | 摘要 |
| --- | --- | --- |
| v0.1.0 | 2026-11-18 | 初版 |

## 一、工程与运行时约束

- 进入页计算或读缓存；禁止后台轮询。

## 二、模块边界与依赖

- 依赖 {FEAT_REVIEW} 打卡表只读契约 CTR-2。

## 三、数据与存储约束

- t_study_streak 可丢，须能从打卡重建。

## 四、安全与合规约束

- 无新增敏感字段。

## 五、共享能力与外部依赖

- 视觉 painless；无新 SDK。
""",
        encoding="utf-8",
    )
    write_yaml(feature_dir / "tech.yaml", streak_tech_yaml())


def run_streak_feature(root: Path) -> Path:
    feature = init_feature(root, FEAT_STREAK, requirement_id=REQ_ID)
    set_path(feature, "full")
    adopt_role(feature, "product")
    write_yaml(feature / "spec.yaml", streak_spec(FEAT_STREAK))
    write_streak_prd(feature / "prd.md")
    write_streak_html(feature / "prototype" / "index.html")
    accept_gate(feature, "G0")
    accept_gate(feature, "G1")
    adopt_role(feature, "ux")
    write_yaml(feature / "ux.yaml", streak_ux())
    write_streak_html(feature / "prototype" / "ux" / "index.html")
    accept_gate(feature, "G2")
    adopt_role(feature, "architect")
    write_streak_tech(feature)
    accept_gate(feature, "G2T")
    scaffold_tasks(feature, mode="per-acceptance", force=True)
    accept_gate(feature, "G3")
    adopt_role(feature, "reviewer")
    write_yaml(feature / "review.yaml", valid_review())
    accept_gate(feature, "GR")
    adopt_role(feature, "tester")
    write_yaml(feature / "evidence.yaml", streak_evidence())
    accept_gate(feature, "G4")
    adopt_role(feature, "deployer")
    write_yaml(feature / "deploy.yaml", valid_deploy())
    accept_gate(feature, "GD")
    return feature


def run_english_learning_large_requirement(scenario_root: Path) -> tuple[Path, list[Path]]:
    """无人值守：1 REQ × 3 Feature，每切片完整产物至 GD。"""
    req_dir = init_requirement(scenario_root, REQ_ID)
    write_multi_req_prd(req_dir / "prd.md")
    write_multi_split(req_dir)
    write_multi_architecture(req_dir)
    errors = evaluate_requirement(req_dir)
    if errors:
        detail = "; ".join(f"{e.code}:{e.message}" for e in errors[:10])
        raise AssertionError(f"check-req 未通过: {detail}")

    # 1) 收藏（light-auto，完整门禁产物）
    f_favorite = _run_small(
        scenario_root,
        FEAT_FAVORITE,
        "light-auto",
        requirement_id=REQ_ID,
    )
    # 修正小需求 prd 关联需求行
    fav_prd = (f_favorite / "prd.md").read_text(encoding="utf-8")
    fav_prd = fav_prd.replace("—（小需求捷径）", REQ_ID)
    (f_favorite / "prd.md").write_text(fav_prd, encoding="utf-8")

    # 2) 今日复习（full + painless，完整产物）
    f_review = run_review_feature(scenario_root)

    # 3) 连续进度（full + painless，完整产物）
    f_streak = run_streak_feature(scenario_root)

    features = [f_favorite, f_review, f_streak]
    write_scenario_readme(
        scenario_root,
        "大需求 · 无痛学环（3 Feature）",
        [
            f"`requirements/{REQ_ID}/` — PRD + split(multi) + Epic（含 KD×3 + 真图）",
            f"`features/{FEAT_FAVORITE}/` — 收藏 light-auto 全套至 GD",
            f"`features/{FEAT_REVIEW}/` — 今日复习 full/painless 全套至 GD",
            f"`features/{FEAT_STREAK}/` — 连续进度 full/painless 全套至 GD",
            "依赖：920 → 921 → 922；全程自动，产物不省略",
        ],
    )
    return req_dir, features
