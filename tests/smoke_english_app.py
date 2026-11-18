"""
/*********************************************************************************
 ** Copyright (C), 2019-2029, OPLUS Mobile Comm Corp., Ltd
 ** All rights reserved.
 **
 ** File: - smoke_english_app.py
 ** Description: 大需求烟测：无痛单词风格「今日复习队列」（全程自动，无人值守）
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
from tests.smoke_support import (
    write_req_architecture_expands,
    write_scenario_readme,
    write_yaml,
)
from tests.test_gates import valid_deploy, valid_review

# 对标 research/painless-ui（tech.xiangzi.painless）语境：生词本 → 今日复习
REQ_ID = "REQ-910-vocab-daily-review-20261118"
FEATURE_ID = "FEAT-910-daily-review-queue"
SCENARIO = "03-large-req"


def vocab_spec_yaml(feature_id: str) -> str:
    return f"""
id: {feature_id}
problem: 英语学习者打开 App 后不知道今天该复习哪些生词，容易漏复习或反复点开已会词
nonGoals:
  - 不做整站阅读器改版
  - 不改会员订阅与支付
  - 不做社交分享
uiRequired: true
uiNoneReason: ""
userJourneys:
  - id: UJ1
    persona: 每日打开无痛单词的英语学习者
    entry: 单词 Tab / 今日复习入口
    steps: "1. 进入今日复习 2. 按队列看语境卡 3. 点「认识/不认识」打卡 4. 看完今日队列"
    success: 今日待复习词全部处理完毕，进度可感知
functionalRequirements:
  - id: FR1
    description: 系统必须按生词本与复习算法生成「今日复习队列」
    scenarios: [S1]
  - id: FR2
    description: 用户必须能对当前词标记认识或不认识并进入下一词
    scenarios: [S1]
nonFunctionalRequirements:
  - id: NFR1
    category: performance
    requirement: 打开今日复习到首词可见 ≤ 500ms（本机冷数据可放宽到 1s）
    measure: 首帧词卡渲染完成时间
nfrNoneReason: ""
scenarios:
  - id: S1
    trigger: 生词本有 ≥1 个到期词
    outcome: 生成有序队列并可逐词打卡
    failure: 无到期词时展示空态引导去背新词
edgeCases:
  - id: E1
    trigger: 今日队列中途杀进程再进
    expected: 从上次未完成位置继续，不重复已打卡词
    userVisible: 进度条反映剩余词数
edgeNoneReason: ""
acceptance:
  - id: A1
    given: 生词本有到期词
    when: 进入今日复习
    then: 展示非空队列且释义默认防剧透模糊
    verify: DailyReviewQueueTest
    covers: [FR1, S1]
  - id: A2
    given: 队列中有当前词
    when: 用户点认识或不认识
    then: 记录结果并切到下一词或完成页
    verify: ReviewCheckInTest
    covers: [FR2, E1]
constraints:
  - research/painless-ui/ui-kit/THEME.md
affected:
  - app/src/vocab/review/
  - app/src/vocab/notebook/
openQuestions: []
"""


def vocab_ux_yaml() -> str:
    return """
skip: false
reason: ""
uiKit:
  baseline: research/painless-ui/ui-kit
interactionRules:
  - id: IR1
    when: 进入今日复习且队列非空
    behavior: 展示当前词语境卡；释义默认模糊，点击才展开
    states: queue_ready
    feedback: 顶部进度 n/N
    coversAcceptance: [A1]
  - id: IR2
    when: 用户点「认识」或「不认识」
    behavior: 记录结果；短反馈后切下一词；末词进入完成页
    states: checking_in, completed
    feedback: 按钮短暂禁用防连点
    coversAcceptance: [A2]
visual:
  baseline: painless
  notes: "烟测对标无痛单词 tech.xiangzi.painless 护眼纸感 + 防剧透模糊"
  motion:
    - id: M1
      trigger: 用户打卡后切下一词
      effect: 卡片横向短位移 + 淡入（对齐 research/ui-kits/MOTION.md）
htmlPrototype:
  entry: prototype/ux/index.html
  pages:
    - id: review
      file: prototype/ux/index.html
acceptance:
  - id: A1
    flow: 进入今日复习见模糊释义词卡
    surface: 单词 Tab · 今日复习
  - id: A2
    flow: 打卡后进入下一词或完成
    surface: 复习操作区
artifacts: []
"""


def vocab_tech_yaml() -> str:
    return """
summary: 无痛单词风格「今日复习队列」— 生词本到期词生成有序队列并支持打卡
aiConstraints:
  mustFollow:
    - 队列只包含到期且未在今日完成打卡的词
    - 释义默认模糊（防剧透），用户主动点开才清晰
    - 打卡结果须持久化，杀进程后可续跑
  mustNot:
    - 不得在首屏明文展示全部释义
    - 不得把会员墙插入复习主路径
  mustNotNoneReason: ""
  invariants:
    - 同一 wordId 在同一自然日内至多一次「完成」态打卡
  invariantsNoneReason: ""
keyDesigns:
  - id: KD-F01
    title: 今日队列生成与续跑
    kinds: [cornerstone, difficulty]
    judgment: 漏复习与重复打卡会直接伤害学习节奏
    problem: 到期词集合变化 + 进程被杀导致进度丢失
    decision: ReviewQueueRepository 按自然日快照队列；打卡写 CheckInStore
    coreScheme: >
      进入今日复习时若无当日快照则从 Notebook 拉取到期词排序写入队列快照；
      有快照则从首个未打卡位置继续；认识/不认识写入 CheckInStore 并推进游标。
    mustFollow:
      - 以自然日 + wordId 作为打卡幂等键
    pitfalls:
      - 不要每次进入都打乱已生成的当日队列顺序
    relatedDiagrams: [D-WF, D-SEQ]
    relatedAcceptance: [A1, A2]
keyDesignsNoneReason: ""
interfaces:
  - name: ReviewQueueApi
    kind: api
    direction: provided
    contract: 本地模块 API；getTodayQueue / checkIn
    request: getTodayQueue()；checkIn(wordId, result)
    response: QueueSnapshot；CheckInResult
    errors:
      - code: EMPTY
        meaning: 无到期词
        action: 展示空态
    concurrencyNotes: 打卡写串行，避免双击双记
    consumers: [DailyReviewFragment]
    providers: [ReviewQueueRepository]
interfacesNoneReason: ""
diagrams:
  - id: D-L0
    type: architecture
    layer: 0
    title: L0 学习 App 上下文
    scope: 用户 / 无痛单词客户端 / 本地生词本
    tool: archify
    html: diagrams/vocab.L0.architecture.html
    png: diagrams/vocab.L0.architecture.png
  - id: D-L1
    type: architecture
    layer: 1
    title: L1 复习模块
    scope: DailyReview / QueueRepo / CheckInStore / Notebook
    tool: archify
    html: diagrams/vocab.L1.architecture.html
    png: diagrams/vocab.L1.architecture.png
  - id: D-WF
    type: workflow
    title: 今日复习主流程
    scope: 进入→队列→打卡→完成/空态
    tool: archify
    html: diagrams/vocab.review.workflow.html
    png: diagrams/vocab.review.workflow.png
  - id: D-SEQ
    type: sequence
    title: 打开复习与打卡时序
    scope: UI → Repository → Store
    tool: archify
    html: diagrams/vocab.checkin.sequence.html
    png: diagrams/vocab.checkin.sequence.png
  - id: D-CL
    type: class
    title: 复习领域类型
    scope: QueueSnapshot / CheckInRecord
    tool: archify
    html: diagrams/vocab.review.class.html
    png: diagrams/vocab.review.class.png
diagramsNoneReason: ""
architectureLayerGaps: ""
changedFiles:
  - path: app/src/vocab/review/DailyReviewFragment.kt
    action: add
    note: 今日复习 UI
  - path: app/src/vocab/review/ReviewQueueRepository.kt
    action: add
    note: 日队列快照与续跑
  - path: app/src/vocab/review/CheckInStore.kt
    action: add
    note: 打卡持久化
techChoices:
  - topic: 队列稳定性
    decision: 自然日快照，当日不重排
    alternatives: [每次进入重新 SRS 排序]
    rationale: 避免用户感觉「词在跳」
risks:
  - id: R1
    description: 杀进程后游标恢复错误导致重复打卡
    impact: 进度不准、挫败感
    mitigation: 自然日+wordId 幂等；启动校验已完成集合
risksNoneReason: ""
nfr:
  performance:
    assessment: 首词可见目标 ≤500ms
    mitigations: 队列快照本地读取，避免进页现算
  stability:
    assessment: 打卡须可恢复
    mitigations: CheckInStore 持久化
  power:
    assessment: 无后台常驻拉取
    mitigations: 仅用户进入时计算
  memory:
    involved: false
    noneReason: 队列分页/单卡展示，无大图缓存新增
  security:
    involved: false
    noneReason: 无新增账号敏感字段
  compatibility:
    involved: false
    noneReason: 不降低 minSdk
  romSize:
    involved: false
    noneReason: 少量业务代码
  algorithm:
    involved: true
    assessment: 到期词筛选沿用现有 SRS 阈值，本切片不改公式
    mitigations: 只消费 Notebook 到期集合
dataDesign:
  involved: true
  tables:
    - name: t_review_queue_day
      change: add
      purpose: 当日队列快照
      fields:
        - name: day
          type: TEXT
          description: yyyy-MM-dd
          required: true
        - name: wordIds
          type: TEXT
          description: 有序 wordId 列表 JSON
          required: true
    - name: t_review_checkin
      change: add
      purpose: 打卡记录
      fields:
        - name: day
          type: TEXT
          description: 自然日
          required: true
        - name: wordId
          type: TEXT
          description: 词 ID
          required: true
        - name: result
          type: TEXT
          description: known / unknown
          required: true
      indexes: []
      migration: vN 新建表
  models:
    - name: QueueSnapshot
      path: app/src/vocab/review/QueueSnapshot.kt
      note: 日队列
  consistencyNotes: 打卡与游标同事务或等价串行写
  noneReason: ""
tracking:
  product:
    - event: review_session_start
      trigger: 进入今日复习且队列非空
      fields:
        - id: queueSize
          description: 队列长度
          type: Int
  technical:
    - event: review_checkin_write
      trigger: 打卡落盘
      fields:
        - id: wordId
          description: 词 ID
          type: String
  noneReason: ""
acceptance:
  - id: A1
    architecture: ReviewQueueRepository 日快照
    interface: getTodayQueue
    data: t_review_queue_day
    failureRecovery: 无到期词空态
    constraints:
      - research/painless-ui/ui-kit/THEME.md
  - id: A2
    architecture: CheckInStore + 游标推进
    interface: checkIn
    data: t_review_checkin
    failureRecovery: 写失败保留当前词可重试
    constraints: []
"""


def vocab_evidence_yaml() -> str:
    return """
results:
  - acceptanceId: A1
    command: ./gradlew :app:testDebugUnitTest --tests DailyReviewQueueTest
    exitCode: 0
    excerpt: BUILD SUCCESSFUL
  - acceptanceId: A2
    command: ./gradlew :app:testDebugUnitTest --tests ReviewCheckInTest
    exitCode: 0
    excerpt: BUILD SUCCESSFUL
"""


def write_painless_review_html(path: Path, *, title: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # 相对路径指向仓内 research kit；门禁主要认 pk-* 类名
    path.write_text(
        f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{title}</title>
  <link rel="stylesheet" href="../../../../../../research/painless-ui/ui-kit/tokens.css" />
  <style>
    body {{ margin: 0; font-family: "Songti SC", "Noto Serif SC", serif; background: #f3efe6; color: #2c2a26; }}
    .pk-app {{ max-width: 420px; margin: 0 auto; min-height: 100vh; padding: 16px; }}
    .pk-card {{ background: #faf7f0; border-radius: 16px; padding: 20px; box-shadow: 0 1px 0 rgba(0,0,0,.04); }}
    .pk-word-tag {{ display: inline-block; padding: 4px 10px; border-radius: 999px; background: #e7efdf; color: #3d5a3a; }}
    .pk-soft-btn {{ border: 0; border-radius: 12px; padding: 12px 16px; margin-right: 8px; background: #dce8d4; }}
    .pk-blur {{ filter: blur(6px); user-select: none; }}
    .pk-progress {{ margin: 8px 0 16px; color: #6b675f; font-size: 14px; }}
    [hidden] {{ display: none !important; }}
  </style>
</head>
<body class="pk-app">
  <header class="pk-progress" id="progress">今日复习 1/3 · 对标无痛单词</header>
  <section id="card" class="pk-card">
    <span class="pk-word-tag">serendipity</span>
    <p id="context">A fortunate serendipity brought the phrase into today's queue.</p>
    <p id="meaning" class="pk-blur" data-blurred="1">意外发现珍奇事物的能力；巧遇</p>
    <p>
      <button type="button" class="pk-soft-btn" id="reveal">点按查看释义</button>
    </p>
    <p>
      <button type="button" class="pk-soft-btn" id="known" data-go="next">认识</button>
      <button type="button" class="pk-soft-btn" id="unknown" data-go="next">不认识</button>
    </p>
  </section>
  <section id="done" class="pk-card" hidden>
    <h2>今日复习完成</h2>
    <p>已处理本队列全部生词。</p>
    <button type="button" class="pk-soft-btn" id="back" data-go="card">再看一词</button>
  </section>
  <script>
    var blurred = true;
    document.getElementById("reveal").addEventListener("click", function () {{
      var el = document.getElementById("meaning");
      if (blurred) {{ el.classList.remove("pk-blur"); blurred = false; }}
      else {{ el.classList.add("pk-blur"); blurred = true; }}
    }});
    document.querySelectorAll("[data-go]").forEach(function (btn) {{
      btn.addEventListener("click", function () {{
        var target = btn.getAttribute("data-go");
        document.getElementById("card").hidden = target !== "card";
        document.getElementById("done").hidden = target !== "next" && target !== "done";
        if (target === "next") {{
          document.getElementById("done").hidden = false;
          document.getElementById("card").hidden = true;
          document.getElementById("progress").textContent = "今日复习 3/3 · 完成";
        }}
        if (target === "card") {{
          document.getElementById("card").hidden = false;
          document.getElementById("done").hidden = true;
          document.getElementById("progress").textContent = "今日复习 1/3 · 对标无痛单词";
        }}
      }});
    }});
  </script>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_vocab_feature_prd(path: Path) -> None:
    path.write_text(
        f"""# Feature：今日复习队列（无痛单词风格烟测）

> 对标真机包 `tech.xiangzi.painless` 的学习节奏：生词本到期词 → 今日复习。  
> 烟测自动生成，无人值守；请人工打开核对章节与原型。

| 字段 | 值 |
| --- | --- |
| Feature ID | {FEATURE_ID} |
| 关联需求 | {REQ_ID} |
| 状态 | 冻结 |
| 有无 UI | 有（`prototype/` + painless UX） |
| path | full |

## 背景与目标

- **问题**：学习者不知道今天该复习哪些词，漏复习或反复刷已会词。
- **目标**：一键进入「今日复习」，按队列打卡至完成，释义默认防剧透。
- **价值**：稳定每日复习节奏，贴近无痛单词体验。

## 范围与非目标

- **In Scope**：今日队列生成、语境卡展示、认识/不认识打卡、空态与续跑。
- **Out of Scope / 非目标**：阅读器改版、会员支付、社交分享。
- **约束**：视觉 baseline=`painless`；释义默认模糊。

## 核心用户旅程（UJ*）

| ID | 角色 | 入口 | 步骤（1…n） | 成功结果 |
| --- | --- | --- | --- | --- |
| UJ1 | 英语学习者 | 单词 Tab / 今日复习 | 1. 进复习 2. 看语境卡 3. 打卡 4. 完成 | 今日队列处理完毕 |

## 功能需求（FR*）

| ID | 描述 | 关联 UJ/E |
| --- | --- | --- |
| FR1 | 系统必须生成今日复习队列 | UJ1 / S1 |
| FR2 | 用户必须能标记认识/不认识并前进 | UJ1 / E1 |

## 非功能需求（NFR*）

| ID | 类别 | 要求 | 度量 |
| --- | --- | --- | --- |
| NFR1 | performance | 首词可见尽量 ≤500ms | 首帧词卡 |

## 边界与异常（E*）

| ID | 触发 | 期望 | 用户可见 |
| --- | --- | --- | --- |
| E1 | 中途杀进程再进 | 从末完成处续跑 | 进度反映剩余 |

## 验收标准（A*）

| ID | Given | When | Then | verify |
| --- | --- | --- | --- | --- |
| A1 | 有到期词 | 进入今日复习 | 非空队列且释义默认模糊 | DailyReviewQueueTest |
| A2 | 队列有当前词 | 点认识/不认识 | 记录并切下一词或完成页 | ReviewCheckInTest |

## 产品原型

见 `prototype/index.html`（产品）与 `prototype/ux/index.html`（交互，painless/`pk-*`）。

## 补充场景（S*，可选）

| ID | 触发 | 结果 | 失败 |
| --- | --- | --- | --- |
| S1 | 有到期词 | 有序队列可打卡 | 无到期词 → 空态 |

## 开放问题

无。
""",
        encoding="utf-8",
    )


def write_vocab_req_prd(path: Path) -> None:
    bodies = {
        "背景与目标": (
            "- **问题**：英语学习 App（对标无痛单词）用户缺少清晰的「今日复习」闭环。\n"
            "- **目标**：生词本到期词能稳定进入每日复习队列并完成打卡。\n"
            "- **价值**：提升留存与复习完成率。"
        ),
        "范围与非目标": (
            "- **In Scope**：今日复习队列、打卡、防剧透释义、续跑。\n"
            "- **Out of Scope**：阅读 Tab 改版、会员体系、听读随身听改造。\n"
            "- **约束与假设**：沿用现有生词本与 SRS 到期字段。"
        ),
        "核心用户旅程总览": (
            "| 旅程 | 角色 | 端到端成功结果 | 建议落入 feature |\n"
            "| --- | --- | --- | --- |\n"
            f"| 今日复习 | 英语学习者 | 打卡完今日队列 | {FEATURE_ID} |"
        ),
        "功能与非功能总览": (
            "- **功能要点**：队列生成、打卡、空态、杀进程续跑。\n"
            "- **非功能要点**：首词可见性能；无后台常驻。\n"
            "- **明确无 / 延后**：社交、支付。"
        ),
        "边界与异常总览": "- 无到期词空态；中途退出后续跑；防连点。",
        "验收总览": (
            "| 验收 | 摘要 | Feature |\n"
            "| --- | --- | --- |\n"
            f"| A1/A2 | 队列 + 打卡 | {FEATURE_ID} |"
        ),
        "Feature 拆分依据": (
            f"单 Feature 即可独立交付 G4；`split.yaml` decision=single → `{FEATURE_ID}`。"
        ),
        "整需求架构": "见 `architecture/architecture.md`（Epic Design）。对标客户端模块边界，非支付类后台。",
        "开放问题": "无。",
    }
    lines = [
        "# 需求：英语学习 App · 今日复习（无痛单词风格）",
        "",
        "> 大需求烟测：对标 `tech.xiangzi.painless` / research/painless-ui。全程自动生成。",
        "",
        "| 字段 | 值 |",
        "| --- | --- |",
        f"| Requirement ID | {REQ_ID} |",
        "| 状态 | 可拆分 |",
        "| 建议 path | full |",
        "",
    ]
    for title in REQ_PRD_H2:
        lines += [f"## {title}", "", bodies[title], ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_vocab_architecture(req_dir: Path) -> None:
    """按 templates/requirement/architecture/architecture.md 全结构写满（含 ### 与表格）。"""
    arch = req_dir / "architecture"
    diagrams = arch / "diagrams"
    install_req_architecture_diagrams(diagrams)
    kd_dir = arch / "key-func-design"
    kd_dir.mkdir(parents=True, exist_ok=True)
    (kd_dir / "KD_001_daily_queue.md").write_text(
        f"""# KD-001：日队列快照与打卡幂等

> 需求级关键设计。Owner Feature：`{FEATURE_ID}`。

**Requirement**：{REQ_ID}  
**KD 编号**：KD-001  
**日期**：2026-11-18

---

## 依赖的其他 KD

| 前置 KD | 对应文件 | 本 KD 如何建立在其上 |
| --- | --- | --- |
| — | — | 无前置依赖 |

---

- **类型**：疑难点
- **背景/亮点说明**：到期词集合每日变化，且用户可能杀进程；若每次进入重排队列或重复打卡，会破坏「今日复习」节奏并污染进度。
- **方案选型与取舍**：候选 A 每次进入按 SRS 重排；候选 B 自然日快照 + 打卡幂等。选 B：当日顺序稳定、续跑简单，与无痛单词「一次刷完今日」心智一致。
- **核心方案**：进入今日复习时，若无当日 `QueueSnapshot` 则从 Notebook 拉取到期 `wordId` 有序写入快照；若已有快照则从首个未打卡位置继续。用户点「认识/不认识」时以 `自然日 + wordId` 为幂等键写入 `CheckInRecord`；冲突视为已打卡并推进游标。释义默认模糊，点击才展开，避免剧透。
- **关联决策**：L1 中 ReviewQueueRepository 为队列权威；CheckInStore 为打卡权威。
- **边界条件与注意事项**：无到期词走空态；连点打卡依赖唯一键；不在本 KD 改 SRS 公式。

### 方案架构图（涉及多组件/跨模块协作时推荐；可省略）

N/A：协作已由 Epic §五 L1 与 Feature 时序图覆盖。

### 关键类图

见 Feature `diagrams/vocab.review.class.png`（Epic 索引到 Owner Feature）。

### 核心调用链时序图

见 Feature `diagrams/vocab.checkin.sequence.png`。
""",
        encoding="utf-8",
    )

    md = f"""# 需求级技术方案（Epic Design）：{REQ_ID}

> **定位**：整条需求的技术方案总册（对人评审 + 约束 Feature）。结构对齐 AISDD epic-design / 仓内模板。  
> **不对 G4 交付负责**；可执行验收在 `features/*/spec.yaml`。  
> **下游**：Feature 薄 `tech.md`；本需求不启用 Story。  
> **绘图**：Archify finalize → html+png；正文内嵌 png。  
> **机器件**：`architecture.yaml`（check-req）。

**Requirement**：{REQ_ID}  
**设计 Version**：v0.1.0  
**日期**：2026-11-18

**本需求设计文件组成**：

| 文件 / 目录 | 对应章节 | 内容 |
| --- | --- | --- |
| `architecture.md`（本文件） | 全部 | Epic 级技术方案总览与索引 |
| `architecture.yaml` | 门禁 / Agent | diagrams、contracts、risks、features 追溯 |
| `diagrams/` | §四 / §五 | Archify html+png（真图） |
| `key-func-design/KD_001_daily_queue.md` | §七 | 日队列快照 KD |
| 各 Feature `stories/ST-*/` | §十二 / §十三 | 本需求不启用 |

---

## 变更记录（增量变更）

| 版本 | 日期 | 变更范围（REQ/Feature/Story） | 摘要 | 影响模块 | 是否回滚设计 |
| --- | --- | --- | --- | --- | --- |
| v0.1.0 | 2026-11-18 | REQ | 今日复习 Epic 初版（对标无痛单词） | vocab/review | 否 |

---

## 设计前置检查

### 前置检查清单

- [x] 已读需求级 `prd.md`、`split.yaml`
- [x] 跨 Feature 共享能力已明确 Owner Feature（本需求仅单 Feature）
- [x] 已对照 painless 生词本 / 复习节奏校准模块边界
- [x] P0 验收 A1/A2 在架构 / KD / Feature tech 中有覆盖策略

### 跨 Feature 共享能力登记

| 共享能力 | Owner Feature | 消费方 | 设计/契约位置 |
| --- | --- | --- | --- |
| 生词本到期集合只读 | {FEATURE_ID} | 仅本 Feature | §五 Notebook；不改 SRS |
| 今日复习队列与打卡 | {FEATURE_ID} | — | §七 KD-001 / Owner tech |

### P0 覆盖快照（与各 Feature spec 对照）

| Feature | 验收/场景 | 覆盖的设计章节/图 | 状态 |
| --- | --- | --- | --- |
| {FEATURE_ID} | A1 非空队列+防剧透 | §五 / §七 KD-001 / L1 图 | 已覆盖 |
| {FEATURE_ID} | A2 打卡推进/完成 | §六 / KD-001 / 协作流程图 | 已覆盖 |

### 前置检查结论

- **日期**：2026-11-18 / **结论**：通过

---

## 一、简介

### 1.1 目的和对象

| 项 | 内容 |
| --- | --- |
| 阅读对象 | 设计 / 开发 / 测试 / 评审 |
| 文档目的 | 锁定无痛单词风格「今日复习」的整需求技术方案与 Feature 边界 |

### 1.2 范围

| 来源 | 相对路径 | 要点 |
| --- | --- | --- |
| 需求 PRD | [`../prd.md`](../prd.md) | 到期词→日队列→打卡；Out：阅读器/会员 |
| 拆分 | [`../split.yaml`](../split.yaml) | decision=single，path=full |
| UX | `features/{FEATURE_ID}/prototype/ux/` | painless / pk-* 词卡 |

---

## 二、需求概述

### 2.1 需求背景

| 来源 | 要点 |
| --- | --- |
| PRD | 学习者不知道今天该复习哪些词，漏复习或反复刷已会词；对标 tech.xiangzi.painless |

### 2.2 需求范围及限制（按 Feature 索引）

| Feature ID | In Scope 摘要 | Out of Scope 摘要 | 关键 NFR |
| --- | --- | --- | --- |
| {FEATURE_ID} | 日队列、防剧透词卡、打卡、空态、杀进程续跑 | 阅读器改版、会员墙、社交 | 首词可见 ≤500ms；无后台轮询 |

> 禁止在此复述各 Feature FR/NFR/A* 全文。

---

## 三、领域模型

### 3.1 领域概念

本需求引入「日队列快照」与「打卡记录」，消费既有「生词本到期词」，不改 SRS 计分公式本身。

### 3.2 领域概念词汇表（必须）

| 概念（中文） | 名称（英文/代码） | 定义 | 关键属性/状态 | 不变量 | 关联概念 |
| --- | --- | --- | --- | --- | --- |
| 生词 | Word | 可被复习的词条 | wordId | wordId 全局唯一 | NotebookEntry |
| 生词本条目 | NotebookEntry | 用户收藏的词及到期信息 | wordId, dueAt | 一词一条 | Word |
| 日队列快照 | QueueSnapshot | 某自然日待复习有序词表 | day, wordIds, cursor | 同日仅一份快照 | CheckInRecord |
| 打卡记录 | CheckInRecord | 某日对某词的认识结果 | day, wordId, result | 同日同词至多一条 | QueueSnapshot |

### 3.3 概念关系图（推荐，可选）

N/A：概念少，词汇表已足够；技术类图见 Feature `vocab.review.class.png`。

---

## 四、零层架构（L0）

### 4.1 边界说明

- **需求边界**：仅客户端本地复习闭环；不新增云端同步依赖。
- **主要子系统**：无痛单词风格客户端 UI、今日复习模块、生词本、本地 SQLite。

### 4.2 零层架构图（必须）

![L0 架构图](diagrams/req.L0.architecture.png)

### 4.3 架构设计说明（必须）

- **边界与职责**：学习者只与客户端交互；复习模块读写本地库；生词本提供到期集合只读接口。
- **分层与依赖方向**：UI → 复习领域 → Notebook/SQLite；禁止 UI 直写库表。
- **关键数据流**：进入复习 → 建/取日快照 → 展示词卡 → 打卡落盘 → 推进或完成。
- **外部依赖策略**：无新增三方服务；SRS 到期字段沿用现网 Notebook。
- **可演进性**：后续若加云同步，以 day+wordId 打卡记录为同步单元，不改当日快照语义。

### 4.4 外部依赖清单

| 依赖项 | 类型 | 能力 | 通信 | 故障模式 | 策略 |
| --- | --- | --- | --- | --- | --- |
| Notebook（生词本） | 模块 | 到期词列表 | 进程内 API | 读失败 | 空态或可重试提示 |
| SQLite | 存储 | 队列/打卡持久化 | 本地 | 写失败 | 返回可重试，不推进游标 |

---

## 五、一层架构（L1）

### 5.1 一层框架图（必须）

![L1 架构图](diagrams/req.L1.architecture.png)

> 图上 Feature `{FEATURE_ID}` 归属 `app/src/vocab/review` 与 Notebook 只读依赖。

### 5.2 组件清单与职责（必须）

| 模块/组件 | 职责 | 归属 Feature | 本需求改动 |
| --- | --- | --- | --- |
| DailyReviewFragment | 词卡 UI、防剧透、打卡操作 | {FEATURE_ID} | 新增 |
| ReviewQueueRepository | 日快照生成与续跑 | {FEATURE_ID} | 新增 |
| CheckInStore | 打卡持久化与幂等 | {FEATURE_ID} | 新增 |
| Notebook | 到期词只读 | {FEATURE_ID} | 无（只读消费） |

### 5.3 组件协作流程图（必须）

![主路径协作](diagrams/req.overview.workflow.png)

### 5.4 技术方案选型

| 决策点 | 候选 | 选择 | 理由 |
| --- | --- | --- | --- |
| 队列稳定性 | 每次重排 / 日快照 | 日快照 | 避免「词在跳」 |
| 打卡幂等 | 内存游标 / day+wordId | day+wordId | 杀进程可恢复 |
| 释义展示 | 默认明文 / 默认模糊 | 默认模糊 | 对标 painless 防剧透 |

---

## 六、技术风险与边界场景

### 6.1 技术风险与消解策略（绑定 Feature / Story）

| ID | 风险 | 影响 | 落在 Feature / Story | 对策 |
| --- | --- | --- | --- | --- |
| RISK-1 | 杀进程后游标恢复错误 | 重复打卡、进度不准 | {FEATURE_ID} | day+wordId 幂等 + 启动校验已完成集合 |
| RISK-2 | 连点打卡双写 | 状态抖动 | {FEATURE_ID} | 写串行 + UNIQUE(day, wordId) |
| RISK-3 | 无到期词体验断裂 | 用户不知下一步 | {FEATURE_ID} | 空态引导去背新词 |

### 6.2 边界与异常场景枚举

| 场景 | 类别 | 对策落点 |
| --- | --- | --- |
| 中途杀进程再进 | 生命周期 | §七 KD-001；Feature E1 |
| 空队列 | 数据 | §五 空态分支；Feature S1 failure |
| 连点「认识」 | 并发/用户 | RISK-2；Feature IR2 按钮短暂禁用 |

---

## 七、关键功能与疑难点/亮点设计

### 7.1 关键设计清单

| KD | 名称 | 类型 | 前置 KD | 影响 Feature | 文件 |
| --- | --- | --- | --- | --- | --- |
| KD-001 | 日队列快照与打卡幂等 | 疑难 | — | {FEATURE_ID} | `./key-func-design/KD_001_daily_queue.md` |

### 7.2 详细设计引用

见 `key-func-design/KD_001_daily_queue.md`：核心方案、与 Feature 类图/时序互证。切片内细化见 `{FEATURE_ID}/tech.md` KD-F01。

---

## 八、技术评估（NFR）

> **强制**：详表见 [`nfr.md`](./nfr.md)。本节只保留结论。

| 维度 | 结论 / 预算 | 缓解 | 详表 |
| --- | --- | --- | --- |
| 性能 | 首词可见目标 ≤500ms（冷数据可放宽到 1s） | 日快照本地读取，避免进页现算 | [./nfr.md](./nfr.md) |
| 稳定性 | 打卡可恢复；写失败不丢当前词 | CheckInStore 持久化 + 可重试 | [./nfr.md](./nfr.md) |
| 功耗 | 无后台常驻拉取 | 仅用户进入时计算 | [./nfr.md](./nfr.md) |
| 其它 | 不降 minSdk；无新增敏感字段 | — | [./nfr.md](./nfr.md) |

---

## 九、接口设计

> **强制**：字段级详表见 [`interface-design.md`](./interface-design.md)。本需求单 Feature，契约为模块内 API。

| ID | 方向 | 类型 | 提供方 | 消费方 | 摘要 | 冻结时机 |
| --- | --- | --- | --- | --- | --- | --- |
| IF-1 | provided | api | {FEATURE_ID} | DailyReview UI | `getTodayQueue()` → QueueSnapshot | Owner G2T 前 |
| IF-2 | provided | api | {FEATURE_ID} | DailyReview UI | `checkIn(wordId, result)` → Advance | Owner G2T 前 |

详表：[./interface-design.md](./interface-design.md)。`contractsNoneReason`：无跨切片契约。

---

## 十、数据库设计

> **强制**：库表详表见 [`database-design.md`](./database-design.md)。

| 存储 | 变更 | 目的 | Owner Feature |
| --- | --- | --- | --- |
| t_review_queue_day | add | 当日队列快照（day, wordIds JSON） | {FEATURE_ID} |
| t_review_checkin | add | 打卡幂等（day, wordId, result） | {FEATURE_ID} |

详表：[./database-design.md](./database-design.md)。

---

## 十一、埋点技术方案

> **强制**：埋点字段规约见 [`analytics-tracking.md`](./analytics-tracking.md)。

| 事件 | 触发 | 关键字段 | Owner |
| --- | --- | --- | --- |
| review_session_start | 进入今日复习且队列非空 | queueSize:Int | {FEATURE_ID} |
| review_checkin_write | 打卡落盘成功 | wordId:String | {FEATURE_ID} |

详表：[./analytics-tracking.md](./analytics-tracking.md)。

---

## 十二、Feature 与 Story 拆解索引

> **Feature = 交付单元（对 G4 负责）；Story = 技术实现/并行（不对独立交付负责）。**

### 12.1 拆解策略与约束

- 默认少拆 Story；本需求体量单 Feature 可闭环，不启用 Story
- Story 不得自造交付验收；只引用 Feature `A*`

### 12.2 Feature 列表（与 split 对齐）

| Feature | 范围摘要 | dependsOn | 建议 path | 是否启用 Story |
| --- | --- | --- | --- | --- |
| {FEATURE_ID} | 今日复习队列 + 打卡 + 防剧透 | — | full | 否 |

### 12.3 Story 列表（按 Feature 分组，可选）

本需求不启用 Story；细节在各 Feature 薄 tech / tasks。

### 12.4 Story 依赖与并行度

N/A（未启用 Story）。

### 12.5 Feature → 设计覆盖矩阵

| Feature | Epic 章节/KD | Story（若有） | Feature 薄 tech |
| --- | --- | --- | --- |
| {FEATURE_ID} | §五 / KD-001 | — | features/{FEATURE_ID}/tech.md |

---

## 十三、Story 详细设计索引

> 正文在各 `features/<FEAT>/stories/ST-*/story-tech.md`。本节只做总索引。

### 13.1 索引表

| Story | 路径 | 关联 KD | 状态 |
| --- | --- | --- | --- |
| — | — | — | 本需求不启用 Story |

### 13.2 依赖总览

与 `stories.yaml` 一致：`storiesEnabled=false`。

### 13.3 覆盖度检查

- [x] 未启用 Story，无 Story 级 `coversAcceptance` 越权
- [x] 无 Story 目录下的 `evidence.yaml`（G4 只认 Feature）

---

## 附录：与 Feature tech / Story / tasks 的对应关系

| 层级 | 文档 | 职责 |
| --- | --- | --- |
| 本文（Epic Design） | `architecture.md` | 整需求方案；`check-req` |
| Feature 薄 tech | `features/*/tech.md` + `tech.yaml` | 本刀交付落点 + 增量；G2T |
| Story | `stories/ST-*/story-tech.md` | 并行落码细化（本需求未启用） |
| Task | `tasks.yaml` | 写集与验证 |
"""
    (arch / "architecture.md").write_text(md, encoding="utf-8")
    write_req_architecture_expands(
        arch,
        req_id=REQ_ID,
        feature_ids=[FEATURE_ID],
        domain="english-learning",
    )
    doc = {
        "requirementId": REQ_ID,
        "summary": "无痛单词风格今日复习：生词本到期词 → 日队列 → 打卡",
        "features": [FEATURE_ID],
        "contracts": [],
        "contractsNoneReason": "单 Feature，无跨切片契约；模块 API 在 Owner Feature tech.yaml",
        "keyDesigns": [
            {
                "id": "KD-001",
                "title": "日队列快照与打卡幂等",
                "summary": "自然日快照 + day+wordId；详见 key-func-design/KD_001_daily_queue.md",
            }
        ],
        "keyDesignsNoneReason": "",
        "risks": [
            {
                "id": "RISK-1",
                "description": "杀进程续跑错误",
                "impact": "重复打卡",
                "mitigation": "幂等键 + 游标校验",
            },
            {
                "id": "RISK-2",
                "description": "连点打卡双写",
                "impact": "状态抖动",
                "mitigation": "UNIQUE(day, wordId) + 写串行",
            },
        ],
        "risksNoneReason": "",
        "openTechQuestions": [],
        "diagrams": [
            {
                "id": "D-L0",
                "type": "architecture",
                "layer": 0,
                "title": "L0 学习 App 上下文",
                "scope": "学习者 / 客户端 / 生词本 / 复习模块",
                "tool": "archify",
                "html": "diagrams/req.L0.architecture.html",
                "png": "diagrams/req.L0.architecture.png",
            },
            {
                "id": "D-L1",
                "type": "architecture",
                "layer": 1,
                "title": "L1 复习模块",
                "scope": "DailyReview / QueueRepo / CheckIn / Notebook",
                "tool": "archify",
                "html": "diagrams/req.L1.architecture.html",
                "png": "diagrams/req.L1.architecture.png",
            },
            {
                "id": "D-WF",
                "type": "workflow",
                "title": "主路径协作",
                "scope": "进入→队列→打卡→完成/空态",
                "tool": "archify",
                "html": "diagrams/req.overview.workflow.html",
                "png": "diagrams/req.overview.workflow.png",
            },
        ],
        "diagramsNoneReason": "",
    }
    (arch / "architecture.yaml").write_text(
        yaml.safe_dump(doc, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


def write_vocab_feature_tech(feature_dir: Path) -> None:
    install_feature_vocab_diagrams(feature_dir / "diagrams")

    (feature_dir / "tech.md").write_text(
        f"""# 切片技术方案（薄合同）：{FEATURE_ID}

> 英语学习 App · 今日复习队列。引用 Epic，只写本切片增量。path=`full`。

**Feature**：{FEATURE_ID}  
**关联需求**：{REQ_ID}  
**Epic Design**：`requirements/{REQ_ID}/architecture/architecture.md`  
**Version**：v0.1.0  
**日期**：2026-11-18

---

## 变更记录

| 版本 | 日期 | 摘要 | 影响 |
| --- | --- | --- | --- |
| v0.1.0 | 2026-11-18 | 烟测初版 | — |

---

## 设计前置检查

- [x] 已读本切片 prd / spec / UX（painless）
- [x] 已读 tech-spec.md
- [x] 已读 Epic Design 与 split.yaml
- [x] P0 A* 均有落点
- [x] 未重抄 Epic 总册

---

## 一、简介与交付范围

| 项 | 内容 |
| --- | --- |
| 问题 | 今日该复习哪些词不清晰 |
| 本切片交付 | A1/A2：队列 + 打卡；Feature 对 G4 负责 |
| 非目标 | 阅读器/会员/社交 |
| path | full |
| Story | 未启用 |

---

## 二、验收追溯

| ID | 摘要 | 技术落点 |
| --- | --- | --- |
| A1 | 非空队列 + 释义模糊 | Epic KD-001 / §五 / getTodayQueue |
| A2 | 打卡推进 | §五 / checkIn / CheckInStore |

---

## 三、Epic 引用与本切片增量

| 类型 | 引用 | 本切片增量 |
| --- | --- | --- |
| L0/L1 | Epic §四/§五 | 落地 DailyReview UI 与仓库 |
| KD | KD-001 | 本刀 KD-F01 细化续跑 |
| 接口/数据/埋点 | Epic §九～§十一 | 本刀表结构与埋点事件 |
| 风险/NFR | Epic §六/§八 | 首词性能与连点防护 |

---

## 四、本切片架构增量

### 4.1 相对 Epic 的架构说明

本切片实现 Epic 复习闭环的 UI 与本地仓库；不新增外部系统。

### 4.2 本切片架构图（增量或引用内嵌）

![L0](diagrams/vocab.L0.architecture.png)

![L1](diagrams/vocab.L1.architecture.png)

![复习流程](diagrams/vocab.review.workflow.png)

![打卡时序](diagrams/vocab.checkin.sequence.png)

![类图](diagrams/vocab.review.class.png)

### 4.3 模块改动面

| 模块 | 本切片改动 | 说明 |
| --- | --- | --- |
| DailyReviewFragment | 新增 | 词卡 + 打卡 |
| ReviewQueueRepository | 新增 | 日快照 |
| CheckInStore | 新增 | 打卡持久化 |

---

## 五、本切片关键设计

| KD | 标题 | 相对 Epic | mustFollow 摘要 |
| --- | --- | --- | --- |
| KD-F01 | 今日队列生成与续跑 | 细化 KD-001 | 自然日+wordId 幂等 |

### KD-F01：今日队列生成与续跑

- **问题**：到期集合变化与杀进程导致进度丢失。
- **决策**：日快照 + CheckInStore。
- **核心链路**：进页取/建快照 → 展示未打卡词 → checkIn → 推进或完成。
- **必须遵守**：以自然日 + wordId 作为打卡幂等键。
- **坑**：不要每次进入重排当日队列。

---

## 六、本切片约束与风险增量

| 维度 | 增量结论 | tech.yaml 字段 |
| --- | --- | --- |
| 风险 | 续跑错误 → 幂等键 | `risks` |
| NFR | 首词性能 | `nfr` |
| 接口 | ReviewQueueApi | `interfaces` |
| 数据 | 两张新表 | `dataDesign` |
| 埋点 | session_start / checkin_write | `tracking` |

---

## 七、Story 与任务指引

| Story / 任务 | 写集 | 覆盖 A* | 说明 |
| --- | --- | --- | --- |
| T1 | app/src/vocab/review/ | A1 | 队列 |
| T2 | app/src/vocab/review/ | A2 | 打卡 |

---

## 附录：与 tech.yaml / Epic / Story 对应

| 本文 | 下游 |
| --- | --- |
| §二 | tech.yaml acceptance |
| §四 图 | diagrams/* |
| §五 | keyDesigns |
| §七 | tasks.yaml |
""",
        encoding="utf-8",
    )
    (feature_dir / "tech-spec.md").write_text(
        f"""# 技术约束（Tech Spec）：{FEATURE_ID}

## Tech Spec 前置检查

- [x] 与 tech.md / tech.yaml 一致
- [x] 视觉与交互遵循 painless（pk-*）

## 变更记录

| 版本 | 日期 | 摘要 |
| --- | --- | --- |
| v0.1.0 | 2026-11-18 | 烟测初版 |

## 一、工程与运行时约束

- 复习主路径禁止插入会员墙。
- 打卡写须串行，防止双击双记。

## 二、模块边界与依赖

- UI 只依赖 ReviewQueueRepository / CheckInStore。
- 到期集合只读 Notebook，不在本切片改 SRS 公式。

## 三、数据与存储约束

- 队列快照与打卡表按自然日分区语义；打卡幂等键 day+wordId。

## 四、安全与合规约束

- 无新增账号敏感字段；学习数据仅本地库。

## 五、共享能力与外部依赖

- 视觉：research/painless-ui/ui-kit（baseline=painless）
- 无新增三方 SDK
""",
        encoding="utf-8",
    )
    write_yaml(feature_dir / "tech.yaml", vocab_tech_yaml())


def run_english_learning_large_requirement(
    scenario_root: Path,
) -> tuple[Path, list[Path]]:
    """无人值守：无痛学环 1 REQ × 3 Feature，每切片完整产物至 GD。"""
    from tests.smoke_english_multi import (
        run_english_learning_large_requirement as _run_multi,
    )

    return _run_multi(scenario_root)
