import json
import tempfile
import unittest
from pathlib import Path

from aiassitrequreimentdev.gates import evaluate, init_feature, init_requirement, seal_spec


def write_yaml(path: Path, text: str) -> None:
    path.write_text(text.strip() + "\n", encoding="utf-8")


def write_tech_doc(path: Path) -> None:
    path.write_text("# 技术方案\n\n测试用文档正文。\n", encoding="utf-8")


def write_interactive_html(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"/><title>proto</title></head>
<body>
<button type="button" data-go="home">首页</button>
<button type="button" data-go="detail">详情</button>
<section id="home">首页内容</section>
<section id="detail" hidden>详情内容</section>
<script>
document.querySelectorAll("[data-go]").forEach(function (btn) {
  btn.addEventListener("click", function () {
    document.querySelectorAll("section").forEach(function (el) { el.hidden = true; });
    document.getElementById(btn.getAttribute("data-go")).hidden = false;
  });
});
</script>
</body></html>
""",
        encoding="utf-8",
    )


def valid_spec() -> str:
    return """
id: CH-014
problem: 重复的支付回调会把订单推进两次
nonGoals:
  - 不改支付渠道协议
uiRequired: false
uiNoneReason: 本切片为支付回调幂等，无用户界面
userJourneys:
  - id: UJ1
    persona: 已下单用户
    entry: 支付渠道回调
    steps: "1. 收到通知 2. 幂等校验 3. 更新订单为已支付"
    success: 订单已支付且重复通知不二次推进
functionalRequirements:
  - id: FR1
    description: 相同通知只推进一次订单状态
    scenarios: [S1]
  - id: FR2
    description: 迟到通知不改变已支付订单
    scenarios: [S1]
nonFunctionalRequirements:
  - id: NFR1
    category: stability
    requirement: 写库失败可安全重试
    measure: 失败后状态保持待支付且可再次回调
nfrNoneReason: ""
scenarios:
  - id: S1
    trigger: 同一通知到达两次
    outcome: 订单仍为已支付
    failure: 写库失败时保持未支付
edgeCases:
  - id: E1
    trigger: 已支付后迟到通知到达
    expected: 返回已处理且状态不变
    userVisible: 订单详情仍显示已支付
edgeNoneReason: ""
acceptance:
  - id: A1
    given: 订单处于待支付
    when: 相同通知投递两次
    then: 状态只迁移一次
    verify: CallbackIdempotencyTest
    covers: [FR1, S1]
  - id: A2
    given: 订单处于已支付
    when: 迟到通知到达
    then: 响应为已处理且状态不变
    verify: LateCallbackTest
    covers: [FR2, E1]
constraints:
  - modus/knowledge/domain/order/references/state_machine.md
affected:
  - modus/knowledge/domain/order/references/modules/callback.md
openQuestions: []
"""


def valid_ux() -> str:
    return """
skip: false
reason: ""
htmlPrototype:
  entry: prototype/ux/index.html
  pages: []
acceptance:
  - id: A1
    flow: 回调两次仍显示已支付
    surface: 订单详情状态区
  - id: A2
    flow: 迟到通知不改变展示
    surface: 订单详情状态区
artifacts: []
"""


def valid_tech() -> str:
    return """
summary: 支付回调幂等
aiConstraints:
  mustFollow:
    - 以 notificationId 做幂等键，命中则短路成功 ack
    - 写库失败时保持待支付并返回可重试码
  mustNot:
    - 不得按订单金额哈希替代 notificationId
    - 不得引入后台轮询补单
  mustNotNoneReason: ""
  invariants:
    - 同一 notificationId 至多产生一次支付成功副作用
  invariantsNoneReason: ""
keyDesigns:
  - id: KD1
    title: 回调幂等
    kinds: [cornerstone, difficulty]
    judgment: 不做对则支付成功副作用可能重复；存在并发双写窗口
    problem: 渠道可能重放同一 notificationId
    decision: DB 唯一键 + 事务内读改写
    coreScheme: >
      渠道回调进入 Handler 后先按 notificationId 查重表；命中则直接成功 ack；
      未命中则在同一事务写入去重行并推进订单已支付；写库失败保持待支付并返回可重试。
    mustFollow:
      - 以 notificationId 为幂等键，命中则短路成功 ack
    pitfalls:
      - 不要用订单金额哈希替代 notificationId
    relatedDiagrams: []
    relatedAcceptance: [A1, A2]
keyDesignsNoneReason: ""
interfaces:
  - name: PaymentCallback
    kind: api
    direction: provided
    contract: POST /payments/callback; 幂等键 notificationId; 失败可重试
    request: POST /payments/callback body.notificationId:String, orderId:String
    response: 200 ack 或 5xx 可重试
    errors:
      - code: RETRY
        meaning: 写库失败
        action: 渠道重试
    concurrencyNotes: 同 notificationId 并发依赖 DB 唯一键
    consumers: [ChannelGateway]
    providers: [CallbackHandler]
interfacesNoneReason: ""
diagrams: []
diagramsNoneReason: 本切片沿用现有回调链路，无新模块边界，评审以文字约束与接口契约为准
architectureLayerGaps: ""
changedFiles:
  - path: app/src/order/callback/CallbackHandler.kt
    action: modify
    note: 幂等去重
  - path: app/src/order/callback/IdempotencyStore.kt
    action: add
    note: 通知去重存储
techChoices:
  - topic: 幂等键
    decision: notificationId 唯一约束
    alternatives: [订单号+金额哈希]
    rationale: 与支付渠道通知主键一致
risks:
  - id: R1
    description: 渠道重放窗口内并发双写
    impact: 订单状态抖动
    mitigation: DB 唯一键 + 事务内读改写
risksNoneReason: ""
nfr:
  performance:
    assessment: 单次回调多一次唯一键查询
    mitigations: 索引覆盖 notificationId
  stability:
    assessment: 写库失败需可重试
    mitigations: 保持待支付并返回可重试码
  power:
    assessment: 无常驻轮询，功耗影响可忽略
    mitigations: 不引入后台定时任务
  memory:
    involved: false
    noneReason: 无新增常驻缓存
  security:
    involved: false
    noneReason: 不新增敏感字段存储
  compatibility:
    involved: false
    noneReason: 不变更最低 API 与迁移
  romSize:
    involved: false
    noneReason: 仅少量业务代码
  algorithm:
    involved: false
    noneReason: 无算法模型
dataDesign:
  involved: true
  tables:
    - name: t_payment_notification
      change: add
      purpose: 回调去重
      fields:
        - name: notificationId
          type: TEXT
          description: 渠道通知主键
          required: true
          constraints: PRIMARY KEY
        - name: orderId
          type: TEXT
          description: 订单号
          required: true
      indexes: []
      migration: vN 新建表
  models:
    - name: NotificationRecord
      path: app/src/order/callback/NotificationRecord.kt
      note: 去重实体
  consistencyNotes: 以 notificationId 为 SoR 去重键
  noneReason: ""
tracking:
  product:
    - event: pay_callback_success
      trigger: 回调确认支付成功
      fields:
        - id: orderId
          description: 订单号
          type: String
          example: "O1"
  technical:
    - event: callback_idempotent_hit
      trigger: 幂等命中短路
      fields:
        - id: notificationId
          description: 通知主键
          type: String
  noneReason: ""
acceptance:
  - id: A1
    architecture: 回调入口幂等键去重
    interface: POST /payments/callback
    data: 以 notificationId 唯一约束
    failureRecovery: 写库失败保持待支付并可重试
    constraints:
      - modus/knowledge/domain/order/references/state_machine.md
  - id: A2
    architecture: 已支付短路返回
    interface: POST /payments/callback
    data: 读取订单状态后直接 ack
    failureRecovery: 读失败返回可重试
    constraints: []
"""


def valid_tasks() -> str:
    return """
tasks:
  - id: T1
    blockedBy: []
    writeScopes:
      - app/src/order/callback/
    acceptance: [A1]
    verify:
      - ./gradlew :app:testDebugUnitTest --tests CallbackIdempotencyTest
  - id: T2
    blockedBy: [T1]
    writeScopes:
      - app/src/order/late/
    acceptance: [A2]
    verify:
      - ./gradlew :app:testDebugUnitTest --tests LateCallbackTest
"""


def valid_review() -> str:
    return """
findings: []
"""


def valid_evidence() -> str:
    return """
results:
  - acceptanceId: A1
    command: ./gradlew :app:testDebugUnitTest --tests CallbackIdempotencyTest
    exitCode: 0
    excerpt: BUILD SUCCESSFUL
  - acceptanceId: A2
    command: ./gradlew :app:testDebugUnitTest --tests LateCallbackTest
    exitCode: 0
    excerpt: BUILD SUCCESSFUL
"""


def valid_deploy() -> str:
    return """
environment: staging
commands:
  - ./scripts/deploy.sh staging
rollback: ./scripts/rollback.sh staging
notes: []
"""


def state(path: str = "full", gates: dict | None = None, spec_hash: str | None = None) -> dict:
    base = {
        "stage": "intake",
        "path": path,
        "gates": {
            "G0": "pending",
            "G1": "pending",
            "G2": "pending",
            "G2T": "pending",
            "G3": "pending",
            "GR": "pending",
            "G4": "pending",
            "GD": "pending",
        },
        "openQuestions": [],
        "runId": None,
        "specHash": spec_hash,
    }
    if gates:
        base["gates"].update(gates)
    return base


class GateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.change = Path(self.tmp.name) / "CH-014"
        self.change.mkdir()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def put_state(self, **kwargs) -> None:
        (self.change / "state.json").write_text(
            json.dumps(state(**kwargs), ensure_ascii=False),
            encoding="utf-8",
        )

    def codes(self, gate: str) -> set[str]:
        report = evaluate(self.change)
        return {item.code for item in report.violations if item.gate == gate}

    def test_g1_rejects_open_questions(self) -> None:
        self.put_state()
        write_yaml(
            self.change / "spec.yaml",
            valid_spec().replace("openQuestions: []", "openQuestions:\n  - 超时后是否退款"),
        )
        self.assertIn("SPEC_OPEN_QUESTIONS", self.codes("G1"))

    def test_g1_accepts_closed_spec(self) -> None:
        self.put_state()
        write_yaml(self.change / "spec.yaml", valid_spec())
        self.assertEqual(self.codes("G1"), set())

    def test_g1_requires_interactive_product_prototype(self) -> None:
        self.put_state()
        write_yaml(
            self.change / "spec.yaml",
            valid_spec()
            .replace("uiRequired: false", "uiRequired: true")
            .replace("uiNoneReason: 本切片为支付回调幂等，无用户界面", "uiNoneReason: \"\""),
        )
        self.assertIn("PROTO_MISSING", self.codes("G1"))
        write_interactive_html(self.change / "prototype" / "index.html")
        self.assertEqual(self.codes("G1"), set())

    def test_g1_rejects_non_interactive_product_prototype(self) -> None:
        self.put_state()
        write_yaml(
            self.change / "spec.yaml",
            valid_spec()
            .replace("uiRequired: false", "uiRequired: true")
            .replace("uiNoneReason: 本切片为支付回调幂等，无用户界面", "uiNoneReason: \"\""),
        )
        proto = self.change / "prototype" / "index.html"
        proto.parent.mkdir(parents=True, exist_ok=True)
        proto.write_text(
            "<!DOCTYPE html><html><body><p>" + ("静态说明 " * 40) + "</p></body></html>\n",
            encoding="utf-8",
        )
        self.assertIn("PROTO_NOT_INTERACTIVE", self.codes("G1"))

    def test_g1_requires_ui_none_reason(self) -> None:
        self.put_state()
        write_yaml(
            self.change / "spec.yaml",
            valid_spec().replace(
                "uiNoneReason: 本切片为支付回调幂等，无用户界面",
                "uiNoneReason: \"\"",
            ),
        )
        self.assertIn("PROTO_SKIP_REASON", self.codes("G1"))

    def test_accepted_g1_detects_spec_edit(self) -> None:
        self.put_state()
        spec_path = self.change / "spec.yaml"
        write_yaml(spec_path, valid_spec())
        seal_spec(self.change)
        sealed = json.loads((self.change / "state.json").read_text(encoding="utf-8"))
        sealed["gates"]["G1"] = "accepted"
        (self.change / "state.json").write_text(json.dumps(sealed), encoding="utf-8")
        spec_path.write_text(spec_path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        self.assertIn("SPEC_HASH_MISMATCH", self.codes("G1"))

    def test_g2_requires_every_acceptance(self) -> None:
        self.put_state()
        write_yaml(self.change / "spec.yaml", valid_spec())
        write_yaml(
            self.change / "ux.yaml",
            """
skip: false
reason: ""
acceptance:
  - id: A1
    flow: 仅一条
    surface: 详情页
""",
        )
        self.assertIn("UX_UNMAPPED", self.codes("G2"))

    def test_g2_accepts_skip_with_reason(self) -> None:
        self.put_state()
        write_yaml(self.change / "spec.yaml", valid_spec())
        write_yaml(
            self.change / "ux.yaml",
            """
skip: true
reason: 无 UI，仅服务端幂等
acceptance: []
artifacts: []
""",
        )
        self.assertEqual(self.codes("G2"), set())

    def test_g2_accepts_complete_map(self) -> None:
        self.put_state()
        write_yaml(self.change / "spec.yaml", valid_spec())
        write_yaml(self.change / "ux.yaml", valid_ux())
        write_interactive_html(self.change / "prototype" / "ux" / "index.html")
        self.assertEqual(self.codes("G2"), set())

    def test_g2_requires_interactive_ux_prototype(self) -> None:
        self.put_state()
        write_yaml(self.change / "spec.yaml", valid_spec())
        write_yaml(self.change / "ux.yaml", valid_ux())
        self.assertIn("UX_PROTO_MISSING", self.codes("G2"))
        write_interactive_html(self.change / "prototype" / "ux" / "index.html")
        self.assertEqual(self.codes("G2"), set())

    def test_light_path_skips_missing_ux(self) -> None:
        self.put_state(path="light")
        write_yaml(self.change / "spec.yaml", valid_spec())
        self.assertEqual(self.codes("G2"), set())

    def test_g2t_requires_every_acceptance(self) -> None:
        self.put_state()
        write_yaml(self.change / "spec.yaml", valid_spec())
        write_tech_doc(self.change / "tech.md")
        write_yaml(
            self.change / "tech.yaml",
            """
summary: partial
aiConstraints:
  mustFollow: [x]
  mustNot: []
  mustNotNoneReason: 无
  invariants: []
  invariantsNoneReason: 无
keyDesigns: []
keyDesignsNoneReason: 无关键设计
interfaces: []
interfacesNoneReason: 沿用
diagrams: []
diagramsNoneReason: 无新图
architectureLayerGaps: ""
changedFiles:
  - path: app/src/a.kt
    action: modify
techChoices:
  - topic: x
    decision: y
    rationale: z
risks: []
risksNoneReason: 无额外风险
performancePower:
  performance:
    assessment: a
    mitigations: m
  stability:
    assessment: a
    mitigations: m
  power:
    assessment: a
    mitigations: m
dataDesign:
  involved: false
  noneReason: 不涉及
tracking:
  product: []
  technical: []
  noneReason: 无埋点
acceptance:
  - id: A1
    architecture: a
    interface: i
    data: d
    failureRecovery: f
""",
        )
        self.assertIn("TECH_UNMAPPED", self.codes("G2T"))

    def test_g2t_requires_changed_files(self) -> None:
        self.put_state()
        write_yaml(self.change / "spec.yaml", valid_spec())
        write_tech_doc(self.change / "tech.md")
        incomplete = valid_tech().replace(
            "changedFiles:\n  - path: app/src/order/callback/CallbackHandler.kt\n"
            "    action: modify\n    note: 幂等去重\n"
            "  - path: app/src/order/callback/IdempotencyStore.kt\n"
            "    action: add\n    note: 通知去重存储\n",
            "changedFiles: []\n",
        )
        write_yaml(self.change / "tech.yaml", incomplete)
        self.assertIn("TECH_FILES", self.codes("G2T"))

    def test_g2t_accepts_complete_map(self) -> None:
        self.put_state()
        write_yaml(self.change / "spec.yaml", valid_spec())
        write_tech_doc(self.change / "tech.md")
        write_yaml(self.change / "tech.yaml", valid_tech())
        self.assertEqual(self.codes("G2T"), set())

    def test_g2t_diagram_requires_archify_html_svg(self) -> None:
        self.put_state()
        write_yaml(self.change / "spec.yaml", valid_spec())
        write_tech_doc(self.change / "tech.md")
        diagrams = self.change / "diagrams"
        diagrams.mkdir(parents=True, exist_ok=True)
        for name in (
            "pay.L0.architecture",
            "pay.L1.architecture",
            "callback.sequence",
        ):
            (diagrams / f"{name}.html").write_text("<html></html>", encoding="utf-8")
            (diagrams / f"{name}.svg").write_text("<svg></svg>", encoding="utf-8")
        tech = valid_tech().replace(
            "diagrams: []\n"
            "diagramsNoneReason: 本切片沿用现有回调链路，无新模块边界，评审以文字约束与接口契约为准\n"
            "architectureLayerGaps: \"\"\n",
            "diagrams:\n"
            "  - id: D-L0\n"
            "    type: architecture\n"
            "    layer: 0\n"
            "    title: 支付域上下文\n"
            "    scope: 渠道与订单服务边界\n"
            "    tool: archify\n"
            "    html: diagrams/pay.L0.architecture.html\n"
            "    svg: diagrams/pay.L0.architecture.svg\n"
            "  - id: D-L1\n"
            "    type: architecture\n"
            "    layer: 1\n"
            "    title: 回调模块\n"
            "    scope: CallbackHandler 与 IdempotencyStore\n"
            "    tool: archify\n"
            "    html: diagrams/pay.L1.architecture.html\n"
            "    svg: diagrams/pay.L1.architecture.svg\n"
            "  - id: D-seq\n"
            "    type: sequence\n"
            "    title: 回调主路径\n"
            "    scope: 单次支付回调成功\n"
            "    tool: archify\n"
            "    html: diagrams/callback.sequence.html\n"
            "    svg: diagrams/callback.sequence.svg\n"
            "diagramsNoneReason: \"\"\n"
            "architectureLayerGaps: \"\"\n",
        )
        write_yaml(self.change / "tech.yaml", tech)
        self.assertEqual(self.codes("G2T"), set())

    def test_g2t_architecture_requires_both_layers_or_gaps(self) -> None:
        self.put_state()
        write_yaml(self.change / "spec.yaml", valid_spec())
        write_tech_doc(self.change / "tech.md")
        diagrams = self.change / "diagrams"
        diagrams.mkdir(parents=True, exist_ok=True)
        (diagrams / "pay.L1.architecture.html").write_text("<html></html>", encoding="utf-8")
        (diagrams / "pay.L1.architecture.svg").write_text("<svg></svg>", encoding="utf-8")
        bad = valid_tech().replace(
            "diagrams: []\n"
            "diagramsNoneReason: 本切片沿用现有回调链路，无新模块边界，评审以文字约束与接口契约为准\n"
            "architectureLayerGaps: \"\"\n",
            "diagrams:\n"
            "  - id: D-L1\n"
            "    type: architecture\n"
            "    layer: 1\n"
            "    title: 仅一层\n"
            "    scope: 内部模块\n"
            "    tool: archify\n"
            "    html: diagrams/pay.L1.architecture.html\n"
            "    svg: diagrams/pay.L1.architecture.svg\n"
            "diagramsNoneReason: \"\"\n"
            "architectureLayerGaps: \"\"\n",
        )
        write_yaml(self.change / "tech.yaml", bad)
        self.assertIn("TECH_DIAGRAM", self.codes("G2T"))

    def test_g2t_diagram_rejects_non_archify_or_missing_files(self) -> None:
        self.put_state()
        write_yaml(self.change / "spec.yaml", valid_spec())
        write_tech_doc(self.change / "tech.md")
        bad = valid_tech().replace(
            "diagrams: []\n"
            "diagramsNoneReason: 本切片沿用现有回调链路，无新模块边界，评审以文字约束与接口契约为准\n"
            "architectureLayerGaps: \"\"\n",
            "diagrams:\n"
            "  - id: D1\n"
            "    type: architecture\n"
            "    layer: 0\n"
            "    title: x\n"
            "    scope: x\n"
            "    tool: mermaid\n"
            "    html: diagrams/a.html\n"
            "    svg: diagrams/a.svg\n"
            "diagramsNoneReason: \"\"\n"
            "architectureLayerGaps: 缺 1 层，仅测 tool\n",
        )
        write_yaml(self.change / "tech.yaml", bad)
        codes = self.codes("G2T")
        self.assertIn("TECH_DIAGRAM", codes)

    def test_g2t_requires_ai_constraints(self) -> None:
        self.put_state()
        write_yaml(self.change / "spec.yaml", valid_spec())
        write_tech_doc(self.change / "tech.md")
        incomplete = valid_tech().replace(
            "aiConstraints:\n"
            "  mustFollow:\n"
            "    - 以 notificationId 做幂等键，命中则短路成功 ack\n"
            "    - 写库失败时保持待支付并返回可重试码\n"
            "  mustNot:\n"
            "    - 不得按订单金额哈希替代 notificationId\n"
            "    - 不得引入后台轮询补单\n"
            "  mustNotNoneReason: \"\"\n"
            "  invariants:\n"
            "    - 同一 notificationId 至多产生一次支付成功副作用\n"
            "  invariantsNoneReason: \"\"\n",
            "aiConstraints:\n  mustFollow: []\n  mustNot: []\n  invariants: []\n",
        )
        write_yaml(self.change / "tech.yaml", incomplete)
        self.assertIn("TECH_AI", self.codes("G2T"))

    def test_g3_rejects_cycle(self) -> None:
        self.put_state()
        write_yaml(self.change / "spec.yaml", valid_spec())
        write_yaml(
            self.change / "tasks.yaml",
            """
tasks:
  - id: T1
    blockedBy: [T2]
    writeScopes: [app/src/order/callback/]
    acceptance: [A1]
    verify: [CallbackIdempotencyTest]
  - id: T2
    blockedBy: [T1]
    writeScopes: [app/src/order/late/]
    acceptance: [A2]
    verify: [LateCallbackTest]
""",
        )
        self.assertIn("TASK_CYCLE", self.codes("G3"))

    def test_g3_rejects_overlapping_write_scopes(self) -> None:
        self.put_state()
        write_yaml(self.change / "spec.yaml", valid_spec())
        write_yaml(
            self.change / "tasks.yaml",
            """
tasks:
  - id: T1
    blockedBy: []
    writeScopes: [app/src/order/]
    acceptance: [A1]
    verify: [CallbackIdempotencyTest]
  - id: T2
    blockedBy: []
    writeScopes: [app/src/order/late/]
    acceptance: [A2]
    verify: [LateCallbackTest]
""",
        )
        self.assertIn("TASK_SCOPE_OVERLAP", self.codes("G3"))

    def test_g3_accepts_disjoint_dag(self) -> None:
        self.put_state()
        write_yaml(self.change / "spec.yaml", valid_spec())
        write_yaml(self.change / "tasks.yaml", valid_tasks())
        self.assertEqual(self.codes("G3"), set())

    def test_g3_light_path_rejects_two_tasks(self) -> None:
        self.put_state(path="light")
        write_yaml(self.change / "spec.yaml", valid_spec())
        write_yaml(self.change / "tasks.yaml", valid_tasks())
        self.assertIn("TASK_LIGHT_COUNT", self.codes("G3"))

    def test_gr_blocks_open_blocking(self) -> None:
        self.put_state()
        write_yaml(self.change / "spec.yaml", valid_spec())
        write_yaml(
            self.change / "review.yaml",
            """
findings:
  - id: R1
    severity: blocking
    status: open
    summary: 幂等键未落库
""",
        )
        self.assertIn("REVIEW_BLOCKING_OPEN", self.codes("GR"))

    def test_gr_blocks_open_dispute(self) -> None:
        self.put_state()
        write_yaml(self.change / "spec.yaml", valid_spec())
        write_yaml(
            self.change / "review.yaml",
            """
findings:
  - id: R2
    severity: dispute
    status: open
    summary: 是否允许静默丢弃迟到通知
""",
        )
        self.assertIn("REVIEW_DISPUTE_OPEN", self.codes("GR"))

    def test_gr_accepts_fixed_and_resolved(self) -> None:
        self.put_state()
        write_yaml(self.change / "spec.yaml", valid_spec())
        write_yaml(
            self.change / "review.yaml",
            """
findings:
  - id: R1
    severity: blocking
    status: fixed
    summary: 幂等键未落库
  - id: R2
    severity: dispute
    status: resolved
    summary: 迟到通知策略
    resolution:
      decision: accept
      rationale: 产品确认静默 ack
  - id: R3
    severity: nit
    status: open
    summary: 命名风格
""",
        )
        self.assertEqual(self.codes("GR"), set())

    def test_g4_requires_review_clean(self) -> None:
        self.put_state()
        write_yaml(self.change / "spec.yaml", valid_spec())
        write_yaml(
            self.change / "review.yaml",
            """
findings:
  - id: R1
    severity: blocking
    status: open
    summary: 阻塞
""",
        )
        write_yaml(self.change / "evidence.yaml", valid_evidence())
        self.assertIn("REVIEW_BLOCKING_OPEN", self.codes("G4"))

    def test_g4_requires_zero_exit_for_every_acceptance(self) -> None:
        self.put_state()
        write_yaml(self.change / "spec.yaml", valid_spec())
        write_yaml(self.change / "review.yaml", valid_review())
        write_yaml(
            self.change / "evidence.yaml",
            """
results:
  - acceptanceId: A1
    command: CallbackIdempotencyTest
    exitCode: 1
    excerpt: FAILED
""",
        )
        codes = self.codes("G4")
        self.assertIn("EVIDENCE_EXIT", codes)
        self.assertIn("EVIDENCE_GAP", codes)

    def test_g4_accepts_full_evidence(self) -> None:
        self.put_state()
        write_yaml(self.change / "spec.yaml", valid_spec())
        write_yaml(self.change / "review.yaml", valid_review())
        write_yaml(self.change / "evidence.yaml", valid_evidence())
        self.assertEqual(self.codes("G4"), set())

    def test_gd_requires_commands_and_rollback(self) -> None:
        self.put_state()
        write_yaml(self.change / "spec.yaml", valid_spec())
        write_yaml(
            self.change / "deploy.yaml",
            """
environment: staging
commands: []
rollback: ""
""",
        )
        self.assertIn("DEPLOY_SHAPE", self.codes("GD"))

    def test_gd_accepts_checklist(self) -> None:
        self.put_state()
        write_yaml(self.change / "spec.yaml", valid_spec())
        write_yaml(self.change / "deploy.yaml", valid_deploy())
        self.assertEqual(self.codes("GD"), set())

    def test_init_feature_copies_template(self) -> None:
        root = Path(self.tmp.name) / "repo"
        destination = init_feature(root, "FEAT-100", requirement_id="REQ-100")
        self.assertTrue((destination / "state.json").is_file())
        self.assertTrue((destination / "spec.yaml").is_file())
        self.assertTrue((destination / "ux.yaml").is_file())
        self.assertTrue((destination / "prototype" / "index.html").is_file())
        self.assertTrue((destination / "prototype" / "ux" / "index.html").is_file())
        self.assertTrue((destination / "tech.yaml").is_file())
        self.assertTrue((destination / "review.yaml").is_file())
        self.assertTrue((destination / "deploy.yaml").is_file())
        self.assertTrue(str(destination).endswith(str(Path("features") / "FEAT-100")))
        created = json.loads((destination / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(created["path"], "full")
        self.assertEqual(created["requirementId"], "REQ-100")
        self.assertEqual(created["gates"]["GR"], "pending")
        self.assertEqual(created["gates"]["GD"], "pending")

    def test_init_requirement_copies_template(self) -> None:
        root = Path(self.tmp.name) / "repo"
        destination = init_requirement(root, "REQ-200")
        self.assertTrue((destination / "prd.md").is_file())
        self.assertTrue((destination / "split.yaml").is_file())
        split_doc = (destination / "split.yaml").read_text(encoding="utf-8")
        self.assertIn("REQ-200", split_doc)


if __name__ == "__main__":
    unittest.main()
