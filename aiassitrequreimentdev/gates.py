"""
/*********************************************************************************
 ** Copyright (C), 2019-2029, OPLUS Mobile Comm Corp., Ltd
 ** All rights reserved.
 **
 ** File: - gates.py
 ** Description: 规格门禁检查。门禁是否通过由工件结构决定，不由模型判断。
 ** Version: 1.2
 ** Date: 2026/11/14
 ** Author: limao2@Apps.Gallery
 **
 ** ------------------------------- Revision History: ----------------------------
 ** <author> <date> <version> <desc>
 ** ------------------------------------------------------------------------------
 ** limao2@Apps.Gallery 2026/11/03 1.0 INIT
 ** limao2@Apps.Gallery 2026/11/03 1.1 ux/tech/review/deploy gates
 ** limao2@Apps.Gallery 2026/11/14 1.2 archify html+svg diagram contract
 ** limao2@Apps.Gallery 2026/11/14 1.3 dual-audience tech + diagrams[]
 ** limao2@Apps.Gallery 2026/11/14 1.4 L0/L1 arch + keyDesigns + multi diagrams
 ** limao2@Apps.Gallery 2026/11/14 1.5 nfr/iface/data/tracking + design templates
 ** limao2@Apps.Gallery 2026/11/14 1.6 interactive HTML prototype G1/G2
 *********************************************************************************/
"""

from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import dataclass
from pathlib import Path

import yaml

GATES = ("G0", "G1", "G2", "G2T", "G3", "GR", "G4", "GD")
PATHS = ("full", "light")
REVIEW_SEVERITIES = ("nit", "dispute", "blocking")
DIAGRAM_TYPES = (
    "architecture",
    "sequence",
    "workflow",
    "class",
    "dataflow",
    "lifecycle",
    "erd",
    "tree",
    "timeline",
    "waterfall",
)
INTERFACE_KINDS = ("api", "function", "event", "db")
INTERFACE_DIRECTIONS = ("provided", "consumed")
ARCHITECTURE_LAYERS = (0, 1)
KEY_DESIGN_KINDS = ("cornerstone", "highlight", "difficulty")
NFR_CORE = ("performance", "stability", "power")
NFR_OPTIONAL = ("memory", "security", "compatibility", "romSize", "algorithm")


@dataclass(frozen=True)
class Violation:
    gate: str
    code: str
    message: str


@dataclass(frozen=True)
class Report:
    violations: list[Violation]

    def codes(self, gate: str) -> list[str]:
        return [item.code for item in self.violations if item.gate == gate]


def template_dir() -> Path:
    return Path(__file__).resolve().parent / "templates" / "feature"


def requirement_template_dir() -> Path:
    return Path(__file__).resolve().parent / "templates" / "requirement"


def init_requirement(root: Path, requirement_id: str) -> Path:
    destination = root / "requirements" / requirement_id
    if destination.exists():
        raise FileExistsError(f"requirement 已存在: {destination}")
    shutil.copytree(requirement_template_dir(), destination)
    split_path = destination / "split.yaml"
    split_doc = yaml.safe_load(split_path.read_text(encoding="utf-8"))
    split_doc["requirementId"] = requirement_id
    if isinstance(split_doc.get("features"), list) and split_doc["features"]:
        first = split_doc["features"][0]
        if isinstance(first, dict):
            first["id"] = "FEAT-000"
    split_path.write_text(
        yaml.safe_dump(split_doc, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return destination


def init_feature(root: Path, feature_id: str, *, requirement_id: str | None = None) -> Path:
    destination = root / "features" / feature_id
    if destination.exists():
        raise FileExistsError(f"feature 已存在: {destination}")
    shutil.copytree(template_dir(), destination)
    spec_path = destination / "spec.yaml"
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    spec["id"] = feature_id
    spec_path.write_text(
        yaml.safe_dump(spec, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    if requirement_id:
        state_path = destination / "state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["requirementId"] = requirement_id
        state_path.write_text(
            json.dumps(state, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return destination


def init_change(root: Path, change_id: str) -> Path:
    # 兼容旧名；新代码请用 init_feature
    return init_feature(root, change_id)


def seal_spec(feature_dir: Path) -> str:
    digest = hashlib.sha256((feature_dir / "spec.yaml").read_bytes()).hexdigest()
    state_path = feature_dir / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["specHash"] = digest
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return digest


def evaluate(feature_dir: Path) -> Report:
    violations: list[Violation] = []
    state = _read_state(feature_dir, violations)
    if state is None:
        return Report(violations)
    spec = _read_yaml(feature_dir / "spec.yaml", "G1", "SPEC_MISSING", "缺少 spec.yaml", violations)
    _check_g0(state, spec, violations)
    if spec is not None:
        _check_g1(feature_dir, state, spec, violations)
        _check_g2(feature_dir, state, spec, violations)
        _check_g2t(feature_dir, state, spec, violations)
        _check_g3(feature_dir, state, spec, violations)
        _check_gr(feature_dir, violations)
        _check_g4(feature_dir, spec, violations)
        _check_gd(feature_dir, violations)
    return Report(violations)


def _read_state(change_dir: Path, violations: list[Violation]) -> dict | None:
    path = change_dir / "state.json"
    if not path.is_file():
        violations.append(Violation("G0", "STATE_MISSING", "缺少 state.json"))
        return None
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        violations.append(Violation("G0", "STATE_PARSE", f"state.json 无法解析: {error}"))
        return None
    if not isinstance(state, dict):
        violations.append(Violation("G0", "STATE_PARSE", "state.json 必须是对象"))
        return None
    return state


def _read_yaml(
    path: Path,
    gate: str,
    code: str,
    missing: str,
    violations: list[Violation],
) -> dict | None:
    if not path.is_file():
        violations.append(Violation(gate, code, missing))
        return None
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        violations.append(Violation(gate, code, f"{path.name} 无法解析: {error}"))
        return None
    if loaded is None:
        return {}
    if not isinstance(loaded, dict):
        violations.append(Violation(gate, code, f"{path.name} 必须是映射"))
        return None
    return loaded


def _check_g0(state: dict, spec: dict | None, violations: list[Violation]) -> None:
    path = state.get("path")
    if path not in PATHS:
        violations.append(Violation("G0", "STATE_PATH", "path 只能是 full 或 light"))
        return
    if path == "light" and spec is not None:
        affected = spec.get("affected")
        if not isinstance(affected, list) or len(affected) != 1:
            violations.append(
                Violation("G0", "G0_LIGHT_AFFECTED", "轻路径只能影响一个知识模块")
            )


def _check_g1(change_dir: Path, state: dict, spec: dict, violations: list[Violation]) -> None:
    for field in (
        "id",
        "problem",
        "nonGoals",
        "userJourneys",
        "functionalRequirements",
        "nonFunctionalRequirements",
        "scenarios",
        "edgeCases",
        "acceptance",
        "constraints",
        "affected",
        "openQuestions",
    ):
        if field not in spec:
            violations.append(Violation("G1", "SPEC_MISSING_FIELD", f"spec.yaml 缺少 {field}"))
    problem = spec.get("problem")
    if not isinstance(problem, str) or not problem.strip():
        violations.append(Violation("G1", "SPEC_MISSING_FIELD", "problem 不能为空"))
    questions = spec.get("openQuestions")
    if not isinstance(questions, list):
        violations.append(Violation("G1", "SPEC_OPEN_QUESTIONS", "openQuestions 必须是列表"))
    elif questions:
        violations.append(Violation("G1", "SPEC_OPEN_QUESTIONS", "开放问题未清空，不能冻结规格"))

    journeys = spec.get("userJourneys")
    if not isinstance(journeys, list) or not journeys:
        violations.append(Violation("G1", "SPEC_JOURNEY", "userJourneys 至少一条核心用户旅程"))
    else:
        _check_id_items(
            journeys,
            "UJ",
            ("persona", "entry", "steps", "success"),
            "G1",
            "SPEC_JOURNEY",
            violations,
        )

    functional = spec.get("functionalRequirements")
    if not isinstance(functional, list) or not functional:
        violations.append(
            Violation("G1", "SPEC_FUNCTIONAL", "functionalRequirements 至少一条功能需求")
        )
    else:
        _check_id_items(
            functional,
            "FR",
            ("description",),
            "G1",
            "SPEC_FUNCTIONAL",
            violations,
        )

    nfr = spec.get("nonFunctionalRequirements")
    if not isinstance(nfr, list):
        violations.append(
            Violation("G1", "SPEC_NFR", "nonFunctionalRequirements 必须是列表")
        )
    elif not nfr:
        reason = spec.get("nfrNoneReason")
        if not isinstance(reason, str) or not reason.strip():
            violations.append(
                Violation("G1", "SPEC_NFR", "无非功能需求时须填写 nfrNoneReason")
            )
    else:
        _check_id_items(
            nfr,
            "NFR",
            ("category", "requirement", "measure"),
            "G1",
            "SPEC_NFR",
            violations,
        )

    scenarios = spec.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        violations.append(Violation("G1", "SPEC_SCENARIO", "scenarios 至少一条主流程场景"))
    else:
        _check_unique(scenarios, "S", "G1", "SPEC_DUPLICATE_ID", violations)
        for item in scenarios:
            if not isinstance(item, dict):
                violations.append(Violation("G1", "SPEC_SCENARIO", "场景条目必须是映射"))
                continue
            identifier = item.get("id")
            for key in ("trigger", "outcome", "failure"):
                value = item.get(key)
                if not isinstance(value, str) or not value.strip():
                    violations.append(
                        Violation("G1", "SPEC_SCENARIO", f"{identifier} 缺少 {key}")
                    )

    edges = spec.get("edgeCases")
    if not isinstance(edges, list):
        violations.append(Violation("G1", "SPEC_EDGE", "edgeCases 必须是列表"))
    elif not edges:
        reason = spec.get("edgeNoneReason")
        if not isinstance(reason, str) or not reason.strip():
            violations.append(
                Violation("G1", "SPEC_EDGE", "无异常边界时须填写 edgeNoneReason")
            )
    else:
        _check_id_items(
            edges,
            "E",
            ("trigger", "expected"),
            "G1",
            "SPEC_EDGE",
            violations,
        )

    acceptance = spec.get("acceptance")
    if not isinstance(acceptance, list) or not acceptance:
        violations.append(Violation("G1", "SPEC_ACCEPTANCE_SHAPE", "至少要有一条验收"))
    else:
        _check_acceptance_items(acceptance, violations)

    _check_product_html_prototype(change_dir, spec, violations)

    if state.get("gates", {}).get("G1") == "accepted":
        _check_hash(change_dir, state, violations)


def _looks_interactive_html(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="ignore").lower()
    markers = (
        "<button",
        "onclick=",
        "addeventlistener",
        'href="#',
        "role=\"tab\"",
        "data-go=",
        "data-open=",
        "data-screen=",
    )
    return any(marker in text for marker in markers)


def _check_product_html_prototype(
    change_dir: Path, spec: dict, violations: list[Violation]
) -> None:
    ui_required = spec.get("uiRequired")
    if ui_required is False:
        reason = spec.get("uiNoneReason")
        if not isinstance(reason, str) or not reason.strip():
            violations.append(
                Violation(
                    "G1",
                    "PROTO_SKIP_REASON",
                    "uiRequired 为 false 时须填写 uiNoneReason",
                )
            )
        return
    if ui_required is not True and ui_required is not False:
        # 缺省视为需要 UI 原型（与模板 uiRequired: true 一致）
        if "uiRequired" in spec:
            violations.append(
                Violation("G1", "PROTO_UI_FLAG", "uiRequired 必须是布尔")
            )
            return
    entry = change_dir / "prototype" / "index.html"
    if not entry.is_file():
        violations.append(
            Violation(
                "G1",
                "PROTO_MISSING",
                "有 UI 时须交付可交互产品原型 prototype/index.html",
            )
        )
        return
    if entry.stat().st_size < 200:
        violations.append(
            Violation("G1", "PROTO_EMPTY", "prototype/index.html 过短，须为可评审的 HTML 原型")
        )
        return
    if not _looks_interactive_html(entry):
        violations.append(
            Violation(
                "G1",
                "PROTO_NOT_INTERACTIVE",
                "产品原型须可交互（含 button / 事件 / 可切换页面等）",
            )
        )


def _check_id_items(
    items: list,
    prefix: str,
    required_keys: tuple[str, ...],
    gate: str,
    code: str,
    violations: list[Violation],
) -> None:
    seen: set[str] = set()
    for item in items:
        if not isinstance(item, dict):
            violations.append(Violation(gate, code, "条目必须是映射"))
            continue
        identifier = item.get("id")
        if (
            not isinstance(identifier, str)
            or not identifier.startswith(prefix)
            or identifier in seen
        ):
            violations.append(
                Violation(gate, code, f"编号重复或非法: {identifier}（须 {prefix}*）")
            )
        else:
            seen.add(identifier)
        for key in required_keys:
            value = item.get(key)
            if not isinstance(value, str) or not value.strip():
                violations.append(Violation(gate, code, f"{identifier} 缺少 {key}"))


def _check_acceptance_items(acceptance: list, violations: list[Violation]) -> None:
    seen: set[str] = set()
    for item in acceptance:
        if not isinstance(item, dict):
            violations.append(Violation("G1", "SPEC_ACCEPTANCE_SHAPE", "验收条目必须是映射"))
            continue
        identifier = item.get("id")
        if not isinstance(identifier, str) or identifier in seen:
            violations.append(Violation("G1", "SPEC_DUPLICATE_ID", f"验收编号重复或缺失: {identifier}"))
        else:
            seen.add(identifier)
        for key in ("given", "when", "then", "verify"):
            value = item.get(key)
            if not isinstance(value, str) or not value.strip():
                violations.append(
                    Violation("G1", "SPEC_ACCEPTANCE_SHAPE", f"{identifier} 缺少 {key}")
                )


def _check_hash(change_dir: Path, state: dict, violations: list[Violation]) -> None:
    recorded = state.get("specHash")
    actual = hashlib.sha256((change_dir / "spec.yaml").read_bytes()).hexdigest()
    if not isinstance(recorded, str) or not recorded:
        violations.append(Violation("G1", "SPEC_HASH_MISSING", "G1 已签字但没有 specHash"))
    elif recorded != actual:
        violations.append(Violation("G1", "SPEC_HASH_MISMATCH", "spec.yaml 在 G1 冻结后被修改"))


def _check_g2(change_dir: Path, state: dict, spec: dict, violations: list[Violation]) -> None:
    ux_path = change_dir / "ux.yaml"
    if state.get("path") == "light" and not ux_path.is_file():
        return
    ux = _read_yaml(ux_path, "G2", "UX_MISSING", "缺少 ux.yaml", violations)
    if ux is None:
        return
    if ux.get("skip") is True:
        reason = ux.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            violations.append(Violation("G2", "UX_SKIP_REASON", "ux.skip 为 true 时必须写 reason"))
        return
    expected = _acceptance_ids(spec)
    mapped = ux.get("acceptance")
    if not isinstance(mapped, list):
        violations.append(Violation("G2", "UX_UNMAPPED", "ux.yaml 缺少 acceptance 列表"))
        return
    seen: set[str] = set()
    for item in mapped:
        if not isinstance(item, dict):
            violations.append(Violation("G2", "UX_UNMAPPED", "视觉落点必须是映射"))
            continue
        identifier = item.get("id")
        if identifier not in expected:
            violations.append(
                Violation("G2", "UX_UNKNOWN_ACCEPTANCE", f"视觉引用了规格中不存在的 {identifier}")
            )
            continue
        if identifier in seen:
            violations.append(Violation("G2", "UX_DUPLICATE", f"{identifier} 被视觉映射了多次"))
        seen.add(identifier)
        for key in ("flow", "surface"):
            value = item.get(key)
            if not isinstance(value, str) or not value.strip():
                violations.append(Violation("G2", "UX_UNMAPPED", f"{identifier} 缺少 {key}"))
    missing = expected - seen
    if missing:
        violations.append(
            Violation("G2", "UX_UNMAPPED", "视觉未覆盖: " + ", ".join(sorted(missing)))
        )

    html_proto = ux.get("htmlPrototype")
    entry_rel = "prototype/ux/index.html"
    if isinstance(html_proto, dict):
        raw_entry = html_proto.get("entry")
        if isinstance(raw_entry, str) and raw_entry.strip():
            entry_rel = raw_entry.strip().replace("\\", "/")
    entry = (change_dir / entry_rel).resolve()
    try:
        entry.relative_to(change_dir.resolve())
    except ValueError:
        violations.append(
            Violation("G2", "UX_PROTO_PATH", "htmlPrototype.entry 必须落在 feature 目录内")
        )
        return
    if not entry.is_file():
        violations.append(
            Violation(
                "G2",
                "UX_PROTO_MISSING",
                f"有 UI 时须交付可交互 UX HTML 原型: {entry_rel}",
            )
        )
        return
    if entry.stat().st_size < 200 or not _looks_interactive_html(entry):
        violations.append(
            Violation(
                "G2",
                "UX_PROTO_NOT_INTERACTIVE",
                "UX 原型须为可交互 HTML（含 button / 事件 / 可切换页面等）",
            )
        )


def _check_g2t(change_dir: Path, state: dict, spec: dict, violations: list[Violation]) -> None:
    # light 仍要求 tech，保证验收有技术落点
    del state
    tech_md = change_dir / "tech.md"
    if not tech_md.is_file() or tech_md.stat().st_size == 0:
        violations.append(Violation("G2T", "TECH_DOC_MISSING", "缺少 tech.md 技术方案文档"))
    tech = _read_yaml(
        change_dir / "tech.yaml",
        "G2T",
        "TECH_MISSING",
        "缺少 tech.yaml",
        violations,
    )
    if tech is None:
        return
    _check_tech_doc_sections(tech, violations, change_dir)
    expected = _acceptance_ids(spec)
    mapped = tech.get("acceptance")
    if not isinstance(mapped, list):
        violations.append(Violation("G2T", "TECH_UNMAPPED", "tech.yaml 缺少 acceptance 列表"))
        return
    seen: set[str] = set()
    for item in mapped:
        if not isinstance(item, dict):
            violations.append(Violation("G2T", "TECH_UNMAPPED", "技术落点必须是映射"))
            continue
        identifier = item.get("id")
        if identifier not in expected:
            violations.append(
                Violation("G2T", "TECH_UNKNOWN_ACCEPTANCE", f"技术引用了规格中不存在的 {identifier}")
            )
            continue
        if identifier in seen:
            violations.append(Violation("G2T", "TECH_DUPLICATE", f"{identifier} 被技术映射了多次"))
        seen.add(identifier)
        for key in ("architecture", "interface", "data", "failureRecovery"):
            value = item.get(key)
            if not isinstance(value, str) or not value.strip():
                violations.append(Violation("G2T", "TECH_UNMAPPED", f"{identifier} 缺少 {key}"))
        constraints = item.get("constraints")
        if constraints is not None and not isinstance(constraints, list):
            violations.append(Violation("G2T", "TECH_UNMAPPED", f"{identifier} 的 constraints 必须是列表"))
    missing = expected - seen
    if missing:
        violations.append(
            Violation("G2T", "TECH_UNMAPPED", "技术未覆盖: " + ", ".join(sorted(missing)))
        )


def _check_diagram_artifact_path(
    change_dir: Path | None,
    rel: object,
    label: str,
    index: int,
    violations: list[Violation],
    *,
    suffix: str,
) -> None:
    if not isinstance(rel, str) or not rel.strip():
        violations.append(
            Violation("G2T", "TECH_DIAGRAM", f"diagrams[{index}].{label} 不能为空")
        )
        return
    path_text = rel.strip()
    if not path_text.lower().endswith(suffix):
        violations.append(
            Violation(
                "G2T",
                "TECH_DIAGRAM",
                f"diagrams[{index}].{label} 须以 {suffix} 结尾",
            )
        )
        return
    if change_dir is None:
        return
    target = (change_dir / path_text).resolve()
    try:
        target.relative_to(change_dir.resolve())
    except ValueError:
        violations.append(
            Violation(
                "G2T",
                "TECH_DIAGRAM",
                f"diagrams[{index}].{label} 必须落在 feature 目录内",
            )
        )
        return
    if not target.is_file():
        violations.append(
            Violation(
                "G2T",
                "TECH_DIAGRAM",
                f"diagrams[{index}].{label} 文件不存在: {path_text}",
            )
        )


def _check_tech_doc_sections(
    tech: dict, violations: list[Violation], change_dir: Path | None = None
) -> None:
    """技术方案：AI 约束 + 接口 + 图示 + 变更/选型/风险/快稳省/数据/埋点。"""
    summary = tech.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        violations.append(Violation("G2T", "TECH_SUMMARY", "summary 不能为空"))

    constraints = tech.get("aiConstraints")
    if not isinstance(constraints, dict):
        violations.append(Violation("G2T", "TECH_AI", "缺少 aiConstraints（开发 Agent 必遵约束）"))
    else:
        must_follow = constraints.get("mustFollow")
        if not isinstance(must_follow, list) or not must_follow:
            violations.append(
                Violation("G2T", "TECH_AI", "aiConstraints.mustFollow 至少一条")
            )
        else:
            for index, item in enumerate(must_follow):
                if not isinstance(item, str) or not item.strip():
                    violations.append(
                        Violation(
                            "G2T",
                            "TECH_AI",
                            f"aiConstraints.mustFollow[{index}] 不能为空",
                        )
                    )
        must_not = constraints.get("mustNot")
        if not isinstance(must_not, list):
            violations.append(Violation("G2T", "TECH_AI", "aiConstraints.mustNot 必须是列表"))
        elif not must_not:
            reason = constraints.get("mustNotNoneReason")
            if not isinstance(reason, str) or not reason.strip():
                violations.append(
                    Violation(
                        "G2T",
                        "TECH_AI",
                        "无禁止项时须填写 aiConstraints.mustNotNoneReason",
                    )
                )
        else:
            for index, item in enumerate(must_not):
                if not isinstance(item, str) or not item.strip():
                    violations.append(
                        Violation(
                            "G2T",
                            "TECH_AI",
                            f"aiConstraints.mustNot[{index}] 不能为空",
                        )
                    )
        invariants = constraints.get("invariants")
        if not isinstance(invariants, list):
            violations.append(
                Violation("G2T", "TECH_AI", "aiConstraints.invariants 必须是列表")
            )
        elif not invariants:
            reason = constraints.get("invariantsNoneReason")
            if not isinstance(reason, str) or not reason.strip():
                violations.append(
                    Violation(
                        "G2T",
                        "TECH_AI",
                        "无不变量时须填写 aiConstraints.invariantsNoneReason",
                    )
                )
        else:
            for index, item in enumerate(invariants):
                if not isinstance(item, str) or not item.strip():
                    violations.append(
                        Violation(
                            "G2T",
                            "TECH_AI",
                            f"aiConstraints.invariants[{index}] 不能为空",
                        )
                    )

    interfaces = tech.get("interfaces")
    if not isinstance(interfaces, list):
        violations.append(Violation("G2T", "TECH_IFACE", "interfaces 必须是列表"))
    elif not interfaces:
        reason = tech.get("interfacesNoneReason")
        if not isinstance(reason, str) or not reason.strip():
            violations.append(
                Violation("G2T", "TECH_IFACE", "无接口契约时须填写 interfacesNoneReason")
            )
    else:
        for index, item in enumerate(interfaces):
            if not isinstance(item, dict):
                violations.append(
                    Violation("G2T", "TECH_IFACE", f"interfaces[{index}] 必须是映射")
                )
                continue
            for key in ("name", "contract", "request", "response"):
                value = item.get(key)
                if not isinstance(value, str) or not value.strip():
                    violations.append(
                        Violation("G2T", "TECH_IFACE", f"interfaces[{index}] 缺少 {key}")
                    )
            kind = item.get("kind")
            if kind not in INTERFACE_KINDS:
                violations.append(
                    Violation(
                        "G2T",
                        "TECH_IFACE",
                        f"interfaces[{index}].kind 须为 {'|'.join(INTERFACE_KINDS)}",
                    )
                )
            direction = item.get("direction")
            if direction not in INTERFACE_DIRECTIONS:
                violations.append(
                    Violation(
                        "G2T",
                        "TECH_IFACE",
                        f"interfaces[{index}].direction 须为 provided|consumed",
                    )
                )
            errors = item.get("errors")
            if errors is not None and not isinstance(errors, list):
                violations.append(
                    Violation("G2T", "TECH_IFACE", f"interfaces[{index}].errors 必须是列表")
                )

    key_designs = tech.get("keyDesigns")
    if not isinstance(key_designs, list):
        violations.append(Violation("G2T", "TECH_KEY", "keyDesigns 必须是列表"))
    elif not key_designs:
        reason = tech.get("keyDesignsNoneReason")
        if not isinstance(reason, str) or not reason.strip():
            violations.append(
                Violation(
                    "G2T",
                    "TECH_KEY",
                    "无关键设计时须填写 keyDesignsNoneReason（并对照判定原则说明）",
                )
            )
    else:
        for index, item in enumerate(key_designs):
            if not isinstance(item, dict):
                violations.append(
                    Violation("G2T", "TECH_KEY", f"keyDesigns[{index}] 必须是映射")
                )
                continue
            for key in ("id", "title", "judgment", "problem", "decision", "coreScheme"):
                value = item.get(key)
                if not isinstance(value, str) or not value.strip():
                    violations.append(
                        Violation("G2T", "TECH_KEY", f"keyDesigns[{index}] 缺少 {key}")
                    )
            kinds = item.get("kinds")
            if not isinstance(kinds, list) or not kinds:
                violations.append(
                    Violation(
                        "G2T",
                        "TECH_KEY",
                        f"keyDesigns[{index}].kinds 至少一项（cornerstone|highlight|difficulty）",
                    )
                )
            else:
                for kind_index, kind in enumerate(kinds):
                    if kind not in KEY_DESIGN_KINDS:
                        violations.append(
                            Violation(
                                "G2T",
                                "TECH_KEY",
                                f"keyDesigns[{index}].kinds[{kind_index}] 非法",
                            )
                        )
            must_follow = item.get("mustFollow")
            if not isinstance(must_follow, list) or not must_follow:
                violations.append(
                    Violation(
                        "G2T",
                        "TECH_KEY",
                        f"keyDesigns[{index}].mustFollow 至少一条（供 AI 落实）",
                    )
                )
            elif any(not isinstance(x, str) or not x.strip() for x in must_follow):
                violations.append(
                    Violation(
                        "G2T",
                        "TECH_KEY",
                        f"keyDesigns[{index}].mustFollow 条目不能为空",
                    )
                )
            pitfalls = item.get("pitfalls")
            if not isinstance(pitfalls, list):
                violations.append(
                    Violation("G2T", "TECH_KEY", f"keyDesigns[{index}].pitfalls 必须是列表")
                )
            for list_key in ("relatedDiagrams", "relatedAcceptance"):
                related = item.get(list_key)
                if related is not None and not isinstance(related, list):
                    violations.append(
                        Violation(
                            "G2T",
                            "TECH_KEY",
                            f"keyDesigns[{index}].{list_key} 必须是列表",
                        )
                    )

    diagrams = tech.get("diagrams")
    if not isinstance(diagrams, list):
        violations.append(Violation("G2T", "TECH_DIAGRAM", "diagrams 必须是列表"))
    elif not diagrams:
        reason = tech.get("diagramsNoneReason")
        if not isinstance(reason, str) or not reason.strip():
            violations.append(
                Violation("G2T", "TECH_DIAGRAM", "无图时须填写 diagramsNoneReason")
            )
    else:
        architecture_layers: set[int] = set()
        for index, item in enumerate(diagrams):
            if not isinstance(item, dict):
                violations.append(
                    Violation("G2T", "TECH_DIAGRAM", f"diagrams[{index}] 必须是映射")
                )
                continue
            diagram_type = item.get("type")
            if diagram_type not in DIAGRAM_TYPES:
                violations.append(
                    Violation(
                        "G2T",
                        "TECH_DIAGRAM",
                        f"diagrams[{index}].type 须为 Archify 支持类型",
                    )
                )
            if item.get("tool") != "archify":
                violations.append(
                    Violation(
                        "G2T",
                        "TECH_DIAGRAM",
                        f"diagrams[{index}].tool 必须为 archify",
                    )
                )
            for key in ("id", "title", "scope"):
                value = item.get(key)
                if not isinstance(value, str) or not value.strip():
                    violations.append(
                        Violation(
                            "G2T",
                            "TECH_DIAGRAM",
                            f"diagrams[{index}] 缺少 {key}（多图时用 scope 区分范围）",
                        )
                    )
            if diagram_type == "architecture":
                layer = item.get("layer")
                if layer in (0, "0"):
                    architecture_layers.add(0)
                elif layer in (1, "1"):
                    architecture_layers.add(1)
                else:
                    violations.append(
                        Violation(
                            "G2T",
                            "TECH_DIAGRAM",
                            f"diagrams[{index}] 为 architecture 时 layer 须为 0 或 1",
                        )
                    )
            _check_diagram_artifact_path(
                change_dir, item.get("html"), "html", index, violations, suffix=".html"
            )
            _check_diagram_artifact_path(
                change_dir, item.get("svg"), "svg", index, violations, suffix=".svg"
            )
        if architecture_layers and architecture_layers != {0, 1}:
            gaps = tech.get("architectureLayerGaps")
            if not isinstance(gaps, str) or not gaps.strip():
                missing = sorted(set(ARCHITECTURE_LAYERS) - architecture_layers)
                violations.append(
                    Violation(
                        "G2T",
                        "TECH_DIAGRAM",
                        "架构图须同时覆盖 0 层与 1 层，或填写 architectureLayerGaps 说明缺层 "
                        f"（缺少 layer {missing}）",
                    )
                )

    changed = tech.get("changedFiles")
    if not isinstance(changed, list) or not changed:
        violations.append(Violation("G2T", "TECH_FILES", "changedFiles 至少一条（新增或修改路径）"))
    else:
        for index, item in enumerate(changed):
            if not isinstance(item, dict):
                violations.append(Violation("G2T", "TECH_FILES", f"changedFiles[{index}] 必须是映射"))
                continue
            path = item.get("path")
            action = item.get("action")
            if not isinstance(path, str) or not path.strip():
                violations.append(Violation("G2T", "TECH_FILES", f"changedFiles[{index}] 缺少 path"))
            if action not in ("add", "modify", "delete"):
                violations.append(
                    Violation("G2T", "TECH_FILES", f"changedFiles[{index}] action 须为 add|modify|delete")
                )

    choices = tech.get("techChoices")
    if not isinstance(choices, list) or not choices:
        violations.append(Violation("G2T", "TECH_CHOICE", "techChoices 至少一条技术方案选型"))
    else:
        for index, item in enumerate(choices):
            if not isinstance(item, dict):
                violations.append(Violation("G2T", "TECH_CHOICE", f"techChoices[{index}] 必须是映射"))
                continue
            for key in ("topic", "decision", "rationale"):
                value = item.get(key)
                if not isinstance(value, str) or not value.strip():
                    violations.append(
                        Violation("G2T", "TECH_CHOICE", f"techChoices[{index}] 缺少 {key}")
                    )

    risks = tech.get("risks")
    if not isinstance(risks, list):
        violations.append(Violation("G2T", "TECH_RISK", "risks 必须是列表"))
    elif not risks:
        reason = tech.get("risksNoneReason")
        if not isinstance(reason, str) or not reason.strip():
            violations.append(
                Violation("G2T", "TECH_RISK", "无风险时须填写 risksNoneReason")
            )
    else:
        for index, item in enumerate(risks):
            if not isinstance(item, dict):
                violations.append(Violation("G2T", "TECH_RISK", f"risks[{index}] 必须是映射"))
                continue
            for key in ("id", "description", "impact", "mitigation"):
                value = item.get(key)
                if not isinstance(value, str) or not value.strip():
                    violations.append(Violation("G2T", "TECH_RISK", f"risks[{index}] 缺少 {key}"))

    nfr = tech.get("nfr")
    if not isinstance(nfr, dict):
        legacy = tech.get("performancePower")
        if isinstance(legacy, dict):
            nfr = legacy
        else:
            violations.append(Violation("G2T", "TECH_PERF", "缺少 nfr（快稳省及扩展评估）"))
            nfr = None
    if isinstance(nfr, dict):
        for section in NFR_CORE:
            block = nfr.get(section)
            if not isinstance(block, dict):
                violations.append(Violation("G2T", "TECH_PERF", f"nfr.{section} 必须是映射"))
                continue
            for key in ("assessment", "mitigations"):
                value = block.get(key)
                if not isinstance(value, str) or not value.strip():
                    violations.append(
                        Violation("G2T", "TECH_PERF", f"nfr.{section}.{key} 不能为空")
                    )
        for section in NFR_OPTIONAL:
            block = nfr.get(section)
            if block is None:
                continue
            if not isinstance(block, dict):
                violations.append(Violation("G2T", "TECH_PERF", f"nfr.{section} 必须是映射"))
                continue
            involved = block.get("involved")
            if involved is not True and involved is not False:
                violations.append(
                    Violation("G2T", "TECH_PERF", f"nfr.{section}.involved 必须是布尔")
                )
            elif involved is False:
                reason = block.get("noneReason")
                if not isinstance(reason, str) or not reason.strip():
                    violations.append(
                        Violation(
                            "G2T",
                            "TECH_PERF",
                            f"nfr.{section} 不适用时须填写 noneReason",
                        )
                    )
            else:
                for key in ("assessment", "mitigations"):
                    value = block.get(key)
                    if not isinstance(value, str) or not value.strip():
                        violations.append(
                            Violation(
                                "G2T",
                                "TECH_PERF",
                                f"nfr.{section}.{key} 不能为空",
                            )
                        )

    data = tech.get("dataDesign")
    if not isinstance(data, dict):
        violations.append(Violation("G2T", "TECH_DATA", "缺少 dataDesign"))
    else:
        involved = data.get("involved")
        if involved is not True and involved is not False:
            violations.append(Violation("G2T", "TECH_DATA", "dataDesign.involved 必须是布尔"))
        elif involved is False:
            reason = data.get("noneReason")
            if not isinstance(reason, str) or not reason.strip():
                violations.append(
                    Violation("G2T", "TECH_DATA", "不涉及数据设计时须填写 noneReason")
                )
        else:
            tables = data.get("tables")
            models = data.get("models")
            has_tables = isinstance(tables, list) and bool(tables)
            has_models = isinstance(models, list) and bool(models)
            if not has_tables and not has_models:
                violations.append(
                    Violation("G2T", "TECH_DATA", "涉及数据设计时 tables 或 models 至少一项")
                )
            if has_tables:
                for index, table in enumerate(tables):
                    if not isinstance(table, dict):
                        violations.append(
                            Violation("G2T", "TECH_DATA", f"dataDesign.tables[{index}] 必须是映射")
                        )
                        continue
                    for key in ("name", "change", "purpose"):
                        value = table.get(key)
                        if not isinstance(value, str) or not value.strip():
                            violations.append(
                                Violation(
                                    "G2T",
                                    "TECH_DATA",
                                    f"dataDesign.tables[{index}] 缺少 {key}",
                                )
                            )
                    if table.get("change") not in ("add", "modify", "delete"):
                        violations.append(
                            Violation(
                                "G2T",
                                "TECH_DATA",
                                f"dataDesign.tables[{index}].change 须为 add|modify|delete",
                            )
                        )
                    fields = table.get("fields")
                    if fields is not None:
                        if not isinstance(fields, list):
                            violations.append(
                                Violation(
                                    "G2T",
                                    "TECH_DATA",
                                    f"dataDesign.tables[{index}].fields 必须是列表",
                                )
                            )
                        else:
                            for field_index, field in enumerate(fields):
                                if not isinstance(field, dict):
                                    violations.append(
                                        Violation(
                                            "G2T",
                                            "TECH_DATA",
                                            f"dataDesign.tables[{index}].fields[{field_index}] 必须是映射",
                                        )
                                    )
                                    continue
                                for key in ("name", "type", "description"):
                                    value = field.get(key)
                                    if not isinstance(value, str) or not value.strip():
                                        violations.append(
                                            Violation(
                                                "G2T",
                                                "TECH_DATA",
                                                f"dataDesign.tables[{index}].fields[{field_index}] 缺少 {key}",
                                            )
                                        )

    tracking = tech.get("tracking")
    if not isinstance(tracking, dict):
        violations.append(Violation("G2T", "TECH_TRACKING", "缺少 tracking（产品+技术埋点）"))
    else:
        product = tracking.get("product")
        technical = tracking.get("technical")
        if not isinstance(product, list) or not isinstance(technical, list):
            violations.append(
                Violation("G2T", "TECH_TRACKING", "tracking.product / tracking.technical 必须是列表")
            )
        elif not product and not technical:
            reason = tracking.get("noneReason")
            if not isinstance(reason, str) or not reason.strip():
                violations.append(
                    Violation("G2T", "TECH_TRACKING", "无埋点时须填写 tracking.noneReason")
                )
        else:
            for kind, events in (("product", product), ("technical", technical)):
                if not isinstance(events, list):
                    continue
                for index, item in enumerate(events):
                    if not isinstance(item, dict):
                        violations.append(
                            Violation("G2T", "TECH_TRACKING", f"tracking.{kind}[{index}] 必须是映射")
                        )
                        continue
                    for key in ("event", "trigger"):
                        value = item.get(key)
                        if not isinstance(value, str) or not value.strip():
                            violations.append(
                                Violation(
                                    "G2T",
                                    "TECH_TRACKING",
                                    f"tracking.{kind}[{index}] 缺少 {key}",
                                )
                            )
                    fields = item.get("fields")
                    if fields is None:
                        continue
                    if not isinstance(fields, list):
                        violations.append(
                            Violation(
                                "G2T",
                                "TECH_TRACKING",
                                f"tracking.{kind}[{index}].fields 必须是列表",
                            )
                        )
                        continue
                    for field_index, field in enumerate(fields):
                        if not isinstance(field, dict):
                            violations.append(
                                Violation(
                                    "G2T",
                                    "TECH_TRACKING",
                                    f"tracking.{kind}[{index}].fields[{field_index}] 必须是映射",
                                )
                            )
                            continue
                        for key in ("id", "description", "type"):
                            value = field.get(key)
                            if not isinstance(value, str) or not value.strip():
                                violations.append(
                                    Violation(
                                        "G2T",
                                        "TECH_TRACKING",
                                        f"tracking.{kind}[{index}].fields[{field_index}] 缺少 {key}",
                                    )
                                )


def _check_g3(change_dir: Path, state: dict, spec: dict, violations: list[Violation]) -> None:
    tasks_doc = _read_yaml(
        change_dir / "tasks.yaml",
        "G3",
        "TASK_MISSING",
        "缺少 tasks.yaml",
        violations,
    )
    if tasks_doc is None:
        return
    tasks = tasks_doc.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        violations.append(Violation("G3", "TASK_MISSING", "tasks.yaml 至少要有一个任务"))
        return
    if state.get("path") == "light" and len(tasks) != 1:
        violations.append(Violation("G3", "TASK_LIGHT_COUNT", "轻路径只能有一个任务"))
    known = {item.get("id") for item in tasks if isinstance(item, dict)}
    acceptance_ids = _acceptance_ids(spec)
    scopes: list[tuple[str, str]] = []
    for task in tasks:
        if not isinstance(task, dict):
            violations.append(Violation("G3", "TASK_MISSING", "任务必须是映射"))
            continue
        task_id = task.get("id")
        for dependency in task.get("blockedBy") or []:
            if dependency not in known:
                violations.append(
                    Violation("G3", "TASK_UNKNOWN_DEPENDENCY", f"{task_id} 依赖了不存在的 {dependency}")
                )
        write_scopes = task.get("writeScopes")
        if not isinstance(write_scopes, list) or not write_scopes:
            violations.append(Violation("G3", "TASK_MISSING_SCOPE", f"{task_id} 没有写集"))
        else:
            for scope in write_scopes:
                if isinstance(scope, str) and scope.strip():
                    scopes.append((str(task_id), _normalize_scope(scope)))
                else:
                    violations.append(Violation("G3", "TASK_MISSING_SCOPE", f"{task_id} 的写集为空"))
        for acceptance_id in task.get("acceptance") or []:
            if acceptance_id not in acceptance_ids:
                violations.append(
                    Violation(
                        "G3",
                        "TASK_UNKNOWN_ACCEPTANCE",
                        f"{task_id} 引用了不存在的验收 {acceptance_id}",
                    )
                )
    if _has_cycle(tasks):
        violations.append(Violation("G3", "TASK_CYCLE", "任务依赖存在环"))
    overlap = _scope_overlap(scopes)
    if overlap is not None:
        left, right = overlap
        violations.append(Violation("G3", "TASK_SCOPE_OVERLAP", f"{left} 与 {right} 的写集相交"))


def _check_gr(change_dir: Path, violations: list[Violation]) -> None:
    review = _read_yaml(
        change_dir / "review.yaml",
        "GR",
        "REVIEW_MISSING",
        "缺少 review.yaml",
        violations,
    )
    if review is None:
        return
    findings = review.get("findings")
    if findings is None:
        findings = []
    if not isinstance(findings, list):
        violations.append(Violation("GR", "REVIEW_SHAPE", "findings 必须是列表"))
        return
    for item in findings:
        if not isinstance(item, dict):
            violations.append(Violation("GR", "REVIEW_SHAPE", "finding 必须是映射"))
            continue
        identifier = item.get("id")
        severity = item.get("severity")
        status = item.get("status")
        if severity not in REVIEW_SEVERITIES:
            violations.append(
                Violation("GR", "REVIEW_SEVERITY", f"{identifier} 的 severity 非法: {severity}")
            )
            continue
        if severity == "blocking" and status != "fixed":
            violations.append(
                Violation("GR", "REVIEW_BLOCKING_OPEN", f"{identifier} 阻塞项未修复")
            )
        if severity == "dispute" and status != "resolved":
            violations.append(
                Violation("GR", "REVIEW_DISPUTE_OPEN", f"{identifier} 争议未裁决")
            )
        if severity == "dispute" and status == "resolved":
            resolution = item.get("resolution")
            if not isinstance(resolution, dict):
                violations.append(
                    Violation("GR", "REVIEW_DISPUTE_OPEN", f"{identifier} 缺少 resolution")
                )
                continue
            decision = resolution.get("decision")
            rationale = resolution.get("rationale")
            if decision not in ("change", "accept"):
                violations.append(
                    Violation("GR", "REVIEW_DISPUTE_OPEN", f"{identifier} 的 decision 非法")
                )
            if not isinstance(rationale, str) or not rationale.strip():
                violations.append(
                    Violation("GR", "REVIEW_DISPUTE_OPEN", f"{identifier} 缺少 rationale")
                )


def _check_g4(change_dir: Path, spec: dict, violations: list[Violation]) -> None:
    # G4 依赖 GR：若 review 仍有未关闭阻塞/争议，一并记在 G4
    review_violations: list[Violation] = []
    _check_gr(change_dir, review_violations)
    for item in review_violations:
        if item.code in ("REVIEW_BLOCKING_OPEN", "REVIEW_DISPUTE_OPEN", "REVIEW_MISSING"):
            violations.append(Violation("G4", item.code, item.message))
    evidence = _read_yaml(
        change_dir / "evidence.yaml",
        "G4",
        "EVIDENCE_MISSING",
        "缺少 evidence.yaml",
        violations,
    )
    if evidence is None:
        return
    results = evidence.get("results")
    if not isinstance(results, list):
        violations.append(Violation("G4", "EVIDENCE_GAP", "evidence.yaml 缺少 results"))
        return
    covered: set[str] = set()
    for item in results:
        if not isinstance(item, dict):
            violations.append(Violation("G4", "EVIDENCE_GAP", "证据条目必须是映射"))
            continue
        identifier = item.get("acceptanceId")
        command = item.get("command")
        if not isinstance(command, str) or not command.strip():
            violations.append(Violation("G4", "EVIDENCE_GAP", f"{identifier} 缺少 command"))
        if item.get("exitCode") != 0:
            violations.append(Violation("G4", "EVIDENCE_EXIT", f"{identifier} 的退出码不是 0"))
        if isinstance(identifier, str):
            covered.add(identifier)
    missing = _acceptance_ids(spec) - covered
    if missing:
        violations.append(
            Violation("G4", "EVIDENCE_GAP", "证据未覆盖: " + ", ".join(sorted(missing)))
        )


def _check_gd(change_dir: Path, violations: list[Violation]) -> None:
    deploy = _read_yaml(
        change_dir / "deploy.yaml",
        "GD",
        "DEPLOY_MISSING",
        "缺少 deploy.yaml",
        violations,
    )
    if deploy is None:
        return
    environment = deploy.get("environment")
    if not isinstance(environment, str) or not environment.strip():
        violations.append(Violation("GD", "DEPLOY_SHAPE", "environment 不能为空"))
    commands = deploy.get("commands")
    if not isinstance(commands, list) or not commands:
        violations.append(Violation("GD", "DEPLOY_SHAPE", "commands 至少一条"))
    else:
        for index, command in enumerate(commands):
            if not isinstance(command, str) or not command.strip():
                violations.append(Violation("GD", "DEPLOY_SHAPE", f"commands[{index}] 为空"))
    rollback = deploy.get("rollback")
    if not isinstance(rollback, str) or not rollback.strip():
        violations.append(Violation("GD", "DEPLOY_SHAPE", "rollback 不能为空"))


def _acceptance_ids(spec: dict) -> set[str]:
    acceptance = spec.get("acceptance")
    if not isinstance(acceptance, list):
        return set()
    return {item.get("id") for item in acceptance if isinstance(item, dict) and isinstance(item.get("id"), str)}


def _check_unique(
    items: list,
    prefix: str,
    gate: str,
    code: str,
    violations: list[Violation],
) -> None:
    seen: set[str] = set()
    for item in items:
        if not isinstance(item, dict):
            continue
        identifier = item.get("id")
        if not isinstance(identifier, str) or not identifier.startswith(prefix) or identifier in seen:
            violations.append(Violation(gate, code, f"编号重复或非法: {identifier}"))
        else:
            seen.add(identifier)


def _normalize_scope(scope: str) -> str:
    return scope.replace("\\", "/").strip("/")


def _scope_overlap(scopes: list[tuple[str, str]]) -> tuple[str, str] | None:
    for index, (left_id, left) in enumerate(scopes):
        for right_id, right in scopes[index + 1 :]:
            if left_id == right_id:
                continue
            if left == right or left.startswith(right + "/") or right.startswith(left + "/"):
                return left_id, right_id
    return None


def _has_cycle(tasks: list) -> bool:
    graph: dict[str, list[str]] = {}
    for task in tasks:
        if not isinstance(task, dict) or not isinstance(task.get("id"), str):
            continue
        blocked = task.get("blockedBy") or []
        graph[task["id"]] = [item for item in blocked if isinstance(item, str)]
    color = {task_id: 0 for task_id in graph}

    def visit(task_id: str) -> bool:
        color[task_id] = 1
        for dependency in graph.get(task_id, []):
            if dependency not in color:
                continue
            if color[dependency] == 1 or (color[dependency] == 0 and visit(dependency)):
                return True
        color[task_id] = 2
        return False

    return any(color[task_id] == 0 and visit(task_id) for task_id in graph)
