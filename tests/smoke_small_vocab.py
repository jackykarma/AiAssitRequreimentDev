"""
/*********************************************************************************
 ** Copyright (C), 2019-2029, OPLUS Mobile Comm Corp., Ltd
 ** All rights reserved.
 **
 ** File: - smoke_small_vocab.py
 ** Description: 小需求烟测：无痛单词「语境卡收藏到生词本」（light / light-auto，真图）
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
from aiassitrequreimentdev.gates import init_feature
from aiassitrequreimentdev.progress import accept_gate
from aiassitrequreimentdev.tasks_scaffold import scaffold_tasks
from tests.smoke_diagrams import copy_diagram
from tests.smoke_support import write_scenario_readme, write_yaml
from tests.test_gates import valid_deploy, valid_review


def small_spec(feature_id: str) -> str:
    return f"""
id: {feature_id}
problem: 学习者在语境卡上看见生词时，收藏步骤过多，导致放弃入库、复习池缺词
nonGoals:
  - 不改今日复习算法
  - 不做阅读器全文搜索改版
uiRequired: false
uiNoneReason: 本切片为收藏写库与幂等，无独立新页面；沿用现有词卡入口
userJourneys:
  - id: UJ1
    persona: 正在刷语境卡的英语学习者
    entry: 单词 Tab 语境卡 / 词气泡
    steps: "1. 看见生词 2. 点收藏 3. 词进入生词本 4. 重复点不产生重复条目"
    success: 生词本出现该词且仅一条
functionalRequirements:
  - id: FR1
    description: 系统必须把当前词以幂等方式写入生词本
    scenarios: [S1]
  - id: FR2
    description: 已收藏词再次收藏须提示已在生词本且不重复插入
    scenarios: [S1]
nonFunctionalRequirements:
  - id: NFR1
    category: stability
    requirement: 弱网或写库失败时可重试，不丢用户意图
    measure: 失败后词卡仍可再次点收藏
nfrNoneReason: ""
scenarios:
  - id: S1
    trigger: 用户点收藏
    outcome: 生词本有且仅有一条该 wordId
    failure: 写库失败时保持未收藏可重试
edgeCases:
  - id: E1
    trigger: 同一 wordId 连续快速点两次收藏
    expected: 仍只有一条生词本记录
    userVisible: 第二次反馈「已在生词本」
edgeNoneReason: ""
acceptance:
  - id: A1
    given: 词未在生词本
    when: 用户点收藏
    then: 生词本新增该词
    verify: NotebookFavoriteTest
    covers: [FR1, S1]
  - id: A2
    given: 词已在生词本
    when: 用户再次点收藏
    then: 不重复插入并返回已收藏
    verify: NotebookFavoriteIdempotentTest
    covers: [FR2, E1]
constraints:
  - research/painless-ui/ui-kit/THEME.md
affected:
  - app/src/vocab/notebook/
openQuestions: []
"""


def small_tech_yaml() -> str:
    return """
summary: 无痛单词语境卡一键收藏到生词本（幂等写库）
aiConstraints:
  mustFollow:
    - 以 wordId 作为生词本唯一键，命中则短路已收藏
    - 写库失败保持未收藏并可重试
  mustNot:
    - 不得用词面字符串替代 wordId 做唯一约束
  mustNotNoneReason: ""
  invariants:
    - 同一 wordId 在生词本至多一条有效记录
  invariantsNoneReason: ""
keyDesigns:
  - id: KD-F01
    title: 收藏幂等
    kinds: [cornerstone]
    judgment: 重复插入会污染复习池
    problem: 用户连点或弱网重试导致双写
    decision: DB 唯一键 wordId + 事务内 upsert
    coreScheme: >
      收藏入口先按 wordId 查生词本；命中则返回已收藏；
      未命中则插入 NotebookEntry；唯一键冲突视为已收藏。
    mustFollow:
      - 以 wordId 为幂等键
    pitfalls:
      - 不要用展示用拼写当主键
    relatedDiagrams: [D-SMOKE-L1]
    relatedAcceptance: [A1, A2]
keyDesignsNoneReason: ""
interfaces:
  - name: NotebookFavoriteApi
    kind: api
    direction: provided
    contract: favorite(wordId) → Added | Already
    request: "favorite(wordId: String)"
    response: "Added | Already | Retry"
    errors:
      - code: RETRY
        meaning: 写库失败
        action: 可再点收藏
    concurrencyNotes: 唯一键防并发双插
    consumers: [WordCardActions]
    providers: [NotebookRepository]
interfacesNoneReason: ""
diagrams:
  - id: D-SMOKE-L1
    type: architecture
    layer: 1
    title: 收藏模块 L1
    scope: WordCard → NotebookRepository → SQLite
    tool: archify
    html: diagrams/vocab.L1.architecture.html
    png: diagrams/vocab.L1.architecture.png
diagramsNoneReason: ""
architectureLayerGaps: "小需求捷径无独立 REQ Epic；L0 见 tech.md §四文字（学习者↔客户端↔生词本），本切片登记 L1 真图。"
changedFiles:
  - path: app/src/vocab/notebook/NotebookRepository.kt
    action: modify
    note: favorite 幂等
  - path: app/src/vocab/notebook/FavoriteAction.kt
    action: add
    note: 词卡收藏入口
techChoices:
  - topic: 幂等键
    decision: wordId 唯一约束
    alternatives: [拼写+词性拼接]
    rationale: 与生词本主键一致
risks:
  - id: R1
    description: 并发双点收藏
    impact: 重复行
    mitigation: UNIQUE(wordId)
risksNoneReason: ""
nfr:
  performance:
    assessment: 多一次唯一键查询
    mitigations: wordId 索引
  stability:
    assessment: 写失败可重试
    mitigations: 返回 Retry
  power:
    assessment: 无后台任务
    mitigations: 仅点击触发
  memory:
    involved: false
    noneReason: 无新增缓存
  security:
    involved: false
    noneReason: 无新增敏感字段
  compatibility:
    involved: false
    noneReason: 不降 minSdk
  romSize:
    involved: false
    noneReason: 少量代码
  algorithm:
    involved: false
    noneReason: 不改 SRS
dataDesign:
  involved: true
  tables:
    - name: t_notebook_entry
      change: modify
      purpose: 生词本
      fields:
        - name: wordId
          type: TEXT
          description: 词主键
          required: true
          constraints: UNIQUE
  models:
    - name: NotebookEntry
      path: app/src/vocab/notebook/NotebookEntry.kt
      note: 生词本行
  consistencyNotes: wordId 为 SoR
  noneReason: ""
tracking:
  product:
    - event: notebook_favorite
      trigger: 收藏成功（含已存在短路）
      fields:
        - id: wordId
          description: 词 ID
          type: String
  technical:
    - event: notebook_favorite_conflict
      trigger: 唯一键冲突当已收藏
      fields:
        - id: wordId
          description: 词 ID
          type: String
  noneReason: ""
acceptance:
  - id: A1
    architecture: NotebookRepository.favorite 插入
    interface: favorite(wordId)
    data: t_notebook_entry
    failureRecovery: 写失败返回 Retry
    constraints:
      - research/painless-ui/ui-kit/THEME.md
  - id: A2
    architecture: 命中/冲突短路
    interface: favorite(wordId)
    data: UNIQUE(wordId)
    failureRecovery: 已收藏态可重入
    constraints: []
"""


def small_evidence() -> str:
    return """
results:
  - acceptanceId: A1
    command: ./gradlew :app:testDebugUnitTest --tests NotebookFavoriteTest
    exitCode: 0
    excerpt: BUILD SUCCESSFUL
  - acceptanceId: A2
    command: ./gradlew :app:testDebugUnitTest --tests NotebookFavoriteIdempotentTest
    exitCode: 0
    excerpt: BUILD SUCCESSFUL
"""


def write_small_prd(path: Path, *, feature_id: str, path_name: str) -> None:
    path.write_text(
        f"""# Feature：语境卡收藏到生词本（无痛单词）

> 对标 `tech.xiangzi.painless`：语境卡 / 词气泡一键入库。烟测自动生成。

| 字段 | 值 |
| --- | --- |
| Feature ID | {feature_id} |
| 关联需求 | —（小需求捷径） |
| 状态 | 冻结 |
| 有无 UI | 无独立新页（沿用词卡入口；`uiRequired=false`） |
| path | {path_name} |

## 背景与目标

- **问题**：看见生词时收藏路径长，用户放弃，复习池缺词。
- **目标**：词卡上一键收藏；重复点击不双写。
- **价值**：降低入库摩擦，保证后续今日复习有词可刷。

## 范围与非目标

- **In Scope**：收藏写库、幂等、失败可重试反馈。
- **Out of Scope / 非目标**：今日复习队列、阅读器改版、会员。
- **约束**：生词本主键为 wordId，与现网一致。

## 核心用户旅程（UJ*）

| ID | 角色 | 入口 | 步骤（1…n） | 成功结果 |
| --- | --- | --- | --- | --- |
| UJ1 | 英语学习者 | 语境卡 / 词气泡 | 1. 看词 2. 点收藏 3. 入库 | 生词本有且仅一条 |

## 功能需求（FR*）

| ID | 描述 | 关联 UJ/E |
| --- | --- | --- |
| FR1 | 未收藏词必须能写入生词本 | UJ1 / S1 |
| FR2 | 已收藏词再次收藏不得重复插入 | UJ1 / E1 |

## 非功能需求（NFR*）

| ID | 类别 | 要求 | 度量 |
| --- | --- | --- | --- |
| NFR1 | stability | 写失败可重试 | 词卡仍可再点 |

## 边界与异常（E*）

| ID | 触发 | 期望 | 用户可见 |
| --- | --- | --- | --- |
| E1 | 连点两次收藏 | 仍一条记录 | 第二次提示已在生词本 |

## 验收标准（A*）

| ID | Given | When | Then | verify |
| --- | --- | --- | --- | --- |
| A1 | 未收藏 | 点收藏 | 新增一条 | NotebookFavoriteTest |
| A2 | 已收藏 | 再点收藏 | 不重复插入 | NotebookFavoriteIdempotentTest |

## 产品原型

无独立产品原型页：沿用现有语境卡收藏入口；本切片无 `uiRequired`。

## 补充场景（S*，可选）

| ID | 触发 | 结果 | 失败 |
| --- | --- | --- | --- |
| S1 | 点收藏 | 生词本幂等入库 | 写库失败可重试 |

## 开放问题

无。
""",
        encoding="utf-8",
    )


def write_small_tech(feature_dir: Path, *, feature_id: str, path_name: str) -> None:
    copy_diagram(feature_dir / "diagrams", "vocab.L1.architecture")
    (feature_dir / "tech.md").write_text(
        f"""# 切片技术方案（薄合同）：{feature_id}

> 小需求捷径：本文件兼任 Epic 关键结论。对标无痛单词生词本收藏。

**Feature**：{feature_id}  
**关联需求**：单 feature 捷径  
**Epic Design**：本文件兼任  
**Version**：v0.1.0  
**日期**：2026-11-18  
**path**：{path_name}

---

## 变更记录

| 版本 | 日期 | 摘要 | 影响 |
| --- | --- | --- | --- |
| v0.1.0 | 2026-11-18 | 收藏幂等初版 | — |

---

## 设计前置检查

- [x] 已读 prd / spec
- [x] 已读 tech-spec.md
- [x] 无 requirementId：本文件兼任 Epic
- [x] A1/A2 有落点
- [x] 使用 Archify 真图（非空壳桩）

---

## 一、简介与交付范围

| 项 | 内容 |
| --- | --- |
| 问题 | 收藏摩擦高 + 易双写 |
| 本切片交付 | A1/A2 幂等收藏 |
| 非目标 | 今日复习 / 阅读器 |
| path | {path_name} |
| Story | 未启用 |

---

## 二、验收追溯

| ID | 摘要 | 技术落点 |
| --- | --- | --- |
| A1 | 首次收藏写入 | KD-F01 / favorite |
| A2 | 再次收藏短路 | UNIQUE(wordId) |

---

## 三、Epic 引用与本切片增量

| 类型 | 引用 | 本切片增量 |
| --- | --- | --- |
| L0/L1 | 本文件兼任 | L1 真图 diagrams/vocab.L1.architecture.* |
| KD | 本文件 KD-F01 | 收藏幂等 |
| 接口/数据/埋点 | tech.yaml | NotebookFavoriteApi |
| 风险/NFR | §六 | 并发双点 |

---

## 四、本切片架构增量

### 4.1 相对 Epic 的架构说明

无 REQ：学习者在客户端语境卡触发收藏；生词本落本地 SQLite；信任边界在 App 进程内。

### 4.2 本切片架构图（增量或引用内嵌）

![生词本收藏 L1](diagrams/vocab.L1.architecture.png)

### 4.3 模块改动面

| 模块 | 本切片改动 | 说明 |
| --- | --- | --- |
| FavoriteAction | 新增 | 词卡入口 |
| NotebookRepository | 修改 | favorite 幂等 |

---

## 五、本切片关键设计

| KD | 标题 | 相对 Epic | mustFollow 摘要 |
| --- | --- | --- | --- |
| KD-F01 | 收藏幂等 | 兼任 Epic | wordId 唯一键 |

### KD-F01：收藏幂等

- **问题**：连点/重试双写污染复习池。
- **决策**：UNIQUE(wordId) + upsert 语义。
- **核心链路**：查 → 未命中插入 → 冲突当已收藏。
- **必须遵守**：以 wordId 为幂等键。
- **坑**：不要用展示拼写当主键。

---

## 六、本切片约束与风险增量

| 维度 | 增量结论 | tech.yaml 字段 |
| --- | --- | --- |
| 风险 | 并发双点 → 唯一键 | `risks` |
| NFR | 写失败可重试 | `nfr` |
| 接口 | favorite | `interfaces` |
| 数据 | t_notebook_entry | `dataDesign` |
| 埋点 | notebook_favorite | `tracking` |

---

## 七、Story 与任务指引

| Story / 任务 | 写集 | 覆盖 A* | 说明 |
| --- | --- | --- | --- |
| T1 | app/src/vocab/notebook/ | A1,A2 | light 单任务 |

---

## 附录：与 tech.yaml / Epic / Story 对应

| 本文 | 下游 |
| --- | --- |
| §二 | acceptance → evidence |
| §四 | diagrams 真图 |
| §五 | keyDesigns |
""",
        encoding="utf-8",
    )
    (feature_dir / "tech-spec.md").write_text(
        f"""# 技术约束（Tech Spec）：{feature_id}

## Tech Spec 前置检查

- [x] 与 tech.md / tech.yaml 一致
- [x] 主键约束与生词本现网一致

## 变更记录

| 版本 | 日期 | 摘要 |
| --- | --- | --- |
| v0.1.0 | 2026-11-18 | 初版 |

## 一、工程与运行时约束

- 收藏仅在用户点击时触发；禁止后台批量刷库。
- 写库失败返回可重试，不吞掉错误。

## 二、模块边界与依赖

- UI 词卡只调 NotebookRepository.favorite。
- 不在本切片改 SRS / 今日复习。

## 三、数据与存储约束

- t_notebook_entry.wordId UNIQUE。
- 冲突视为 Already，不抛给用户未处理异常。

## 四、安全与合规约束

- 无新增账号敏感字段。

## 五、共享能力与外部依赖

- 对标 painless 生词本模型；无新三方 SDK。
""",
        encoding="utf-8",
    )
    write_yaml(feature_dir / "tech.yaml", small_tech_yaml())


def _run_small(
    root: Path,
    feature_id: str,
    path_name: str,
    *,
    requirement_id: str | None = None,
) -> Path:
    feature = init_feature(root, feature_id, requirement_id=requirement_id)
    set_path(feature, path_name)
    adopt_role(feature, "product")
    write_yaml(feature / "spec.yaml", small_spec(feature_id))
    write_small_prd(feature / "prd.md", feature_id=feature_id, path_name=path_name)
    accept_gate(feature, "G0")
    accept_gate(feature, "G1")
    adopt_role(feature, "architect")
    accept_gate(feature, "G2")
    write_small_tech(feature, feature_id=feature_id, path_name=path_name)
    accept_gate(feature, "G2T")
    scaffold_tasks(feature, mode="single", force=True)
    accept_gate(feature, "G3")
    adopt_role(feature, "reviewer")
    write_yaml(feature / "review.yaml", valid_review())
    accept_gate(feature, "GR")
    adopt_role(feature, "tester")
    write_yaml(feature / "evidence.yaml", small_evidence())
    accept_gate(feature, "G4")
    adopt_role(feature, "deployer")
    write_yaml(feature / "deploy.yaml", valid_deploy())
    accept_gate(feature, "GD")
    return feature


def run_small_light(root: Path, feature_id: str) -> Path:
    feature = _run_small(root, feature_id, "light")
    write_scenario_readme(
        root,
        "小需求 · light · 语境卡收藏",
        [
            f"`features/{feature_id}/prd.md` — 写满的真实收藏需求",
            f"`features/{feature_id}/tech.md` + Archify 真图 `diagrams/vocab.L1.architecture.*`",
            "path=light，全程自动",
        ],
    )
    return feature


def run_small_light_auto(root: Path, feature_id: str) -> Path:
    feature = _run_small(root, feature_id, "light-auto")
    write_scenario_readme(
        root,
        "小需求 · light-auto · 语境卡收藏",
        [
            f"`features/{feature_id}/` 全套产物",
            "单任务 + 真图；无需人选",
        ],
    )
    return feature
