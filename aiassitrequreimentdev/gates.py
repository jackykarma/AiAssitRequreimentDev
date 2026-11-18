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
 ** limao2@Apps.Gallery 2026/11/16 1.3 archify html+png diagram contract
 ** limao2@Apps.Gallery 2026/11/14 1.3 dual-audience tech + diagrams[]
 ** limao2@Apps.Gallery 2026/11/14 1.4 L0/L1 arch + keyDesigns + multi diagrams
 ** limao2@Apps.Gallery 2026/11/14 1.5 nfr/iface/data/tracking + design templates
 ** limao2@Apps.Gallery 2026/11/14 1.6 interactive HTML prototype G1/G2
 ** limao2@Apps.Gallery 2026/11/14 1.7 requirement id = REQ-seq-name-YYYYMMDD
 ** limao2@Apps.Gallery 2026/11/15 1.8 tech.md 内嵌 SVG 预览 + sequence 图质量
 ** limao2@Apps.Gallery 2026/11/15 1.9 full 路径强制 workflow/sequence/class 图
 ** limao2@Apps.Gallery 2026/11/15 1.10 Archify HTML 溯源（generator + reader-contract）
 ** limao2@Apps.Gallery 2026/11/16 1.11 预览改为 html+png，取消 svg 合同
 ** limao2@Apps.Gallery 2026/11/15 1.11 specify 模板章节标题强制对齐
 ** limao2@Apps.Gallery 2026/11/15 1.12 product SSOT；G1 的 S* 改为可选
 ** limao2@Apps.Gallery 2026/11/15 1.13 G2 interactionRules + ui-kit visual baseline
 ** limao2@Apps.Gallery 2026/11/15 1.14 G2 visual.baseline 人选；custom 免强制 ui-kit
 ** limao2@Apps.Gallery 2026/11/15 1.15 light-auto 路径（无 UI 小需求）
 ** limao2@Apps.Gallery 2026/11/15 1.16 G2 无 UI 跳过模板 ux；seal 写 G1 accepted；G0 pathConfirmed
 ** limao2@Apps.Gallery 2026/11/15 1.17 feature 级 tech 标题；light 免强制 H3 架构小节
 ** limao2@Apps.Gallery 2026/11/18 1.18 visual.baseline 扩展 research kit catalog（painless/midoo）
 *********************************************************************************/
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

import yaml

from aiassitrequreimentdev.change_log import repo_root_for
from aiassitrequreimentdev.paths import is_light_path
from aiassitrequreimentdev.template_headings import (
    SPEC_PRD_H2,
    TECH_MD_H2,
    TECH_MD_H3_REQUIRED,
    TECH_SPEC_H2,
    extract_markdown_headings,
    missing_headings,
)

# REQ-001-move-album-20220305
REQUIREMENT_ID_RE = re.compile(
    r"^REQ-(?P<seq>\d+)-(?P<name>[a-z0-9]+(?:-[a-z0-9]+)*)-(?P<date>\d{8})$"
)
REQUIREMENT_SEQ_RE = re.compile(r"^REQ-\d+$")
REQUIREMENT_ID_HINT = (
    "需求 id 格式：REQ-<序号>-<kebab名称>-<YYYYMMDD>，"
    "例如 REQ-001-move-album-20220305"
)

# FEAT-001-move-album
FEATURE_ID_RE = re.compile(
    r"^FEAT-(?P<seq>\d+)-(?P<name>[a-z0-9]+(?:-[a-z0-9]+)*)$"
)
FEATURE_SEQ_RE = re.compile(r"^FEAT-\d+$")
FEATURE_ID_HINT = (
    "feature id 格式：FEAT-<序号>-<kebab名称>，"
    "例如 FEAT-001-move-album"
)
FEATURE_ID_PLACEHOLDER = "FEAT-000-example-name"

GATES = ("G0", "G1", "G2", "G2T", "G3", "GR", "G4", "GD")
PATHS = ("full", "light", "light-auto")
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


def _validate_requirement_date(value: str) -> str:
    try:
        datetime.strptime(value, "%Y%m%d")
    except ValueError as exc:
        raise ValueError(f"需求日期须为合法 YYYYMMDD，收到: {value}") from exc
    return value


def validate_requirement_id(requirement_id: str) -> str:
    """校验并返回完整需求 id：REQ-<序号>-<kebab名称>-<YYYYMMDD>。"""
    text = requirement_id.strip()
    matched = REQUIREMENT_ID_RE.fullmatch(text)
    if not matched:
        raise ValueError(f"{REQUIREMENT_ID_HINT}；收到: {requirement_id}")
    _validate_requirement_date(matched.group("date"))
    return text


def compose_requirement_id(
    seq: str,
    name: str,
    *,
    date_text: str | None = None,
) -> str:
    """由序号段与名称拼出完整需求 id；日期默认今天。"""
    seq_text = seq.strip()
    if not REQUIREMENT_SEQ_RE.fullmatch(seq_text):
        raise ValueError(f"需求序号段须为 REQ-<数字>，例如 REQ-001；收到: {seq}")
    slug = name.strip().lower().replace("_", "-").strip("-")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise ValueError(
            f"需求名称须为 kebab-case（小写字母/数字/短横线），例如 move-album；收到: {name}"
        )
    day = _validate_requirement_date(date_text) if date_text else date.today().strftime("%Y%m%d")
    return f"{seq_text}-{slug}-{day}"


def resolve_requirement_id(
    requirement_id: str,
    *,
    name: str | None = None,
    date_text: str | None = None,
) -> str:
    """接受完整 id，或 REQ-序号 + --name [--date] 拼装。"""
    text = requirement_id.strip()
    if REQUIREMENT_ID_RE.fullmatch(text):
        if name or date_text:
            raise ValueError("已提供完整需求 id 时不要再传 --name / --date")
        return validate_requirement_id(text)
    if REQUIREMENT_SEQ_RE.fullmatch(text):
        if not name:
            raise ValueError(f"{REQUIREMENT_ID_HINT}；也可：init-req REQ-001 --name move-album")
        return compose_requirement_id(text, name, date_text=date_text)
    raise ValueError(f"{REQUIREMENT_ID_HINT}；收到: {requirement_id}")


def validate_feature_id(feature_id: str) -> str:
    """校验并返回完整 feature id：FEAT-<序号>-<kebab名称>。"""
    text = feature_id.strip()
    if not FEATURE_ID_RE.fullmatch(text):
        raise ValueError(f"{FEATURE_ID_HINT}；收到: {feature_id}")
    return text


def compose_feature_id(seq: str, name: str) -> str:
    """由序号段与名称拼出完整 feature id。"""
    seq_text = seq.strip()
    if not FEATURE_SEQ_RE.fullmatch(seq_text):
        raise ValueError(f"feature 序号段须为 FEAT-<数字>，例如 FEAT-001；收到: {seq}")
    slug = name.strip().lower().replace("_", "-").strip("-")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise ValueError(
            f"feature 名称须为 kebab-case（小写字母/数字/短横线），例如 move-album；收到: {name}"
        )
    return f"{seq_text}-{slug}"


def resolve_feature_id(feature_id: str, *, name: str | None = None) -> str:
    """接受完整 id，或 FEAT-序号 + --name 拼装。"""
    text = feature_id.strip()
    if FEATURE_ID_RE.fullmatch(text):
        if name:
            raise ValueError("已提供完整 feature id 时不要再传 --name")
        return validate_feature_id(text)
    if FEATURE_SEQ_RE.fullmatch(text):
        if not name:
            raise ValueError(
                f"{FEATURE_ID_HINT}；也可：init FEAT-001 --name move-album"
            )
        return compose_feature_id(text, name)
    raise ValueError(f"{FEATURE_ID_HINT}；收到: {feature_id}")


def init_requirement(root: Path, requirement_id: str) -> Path:
    requirement_id = validate_requirement_id(requirement_id)
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
            first["id"] = FEATURE_ID_PLACEHOLDER
    split_path.write_text(
        yaml.safe_dump(split_doc, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return destination


def init_feature(root: Path, feature_id: str, *, requirement_id: str | None = None) -> Path:
    feature_id = validate_feature_id(feature_id)
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
    change_path = destination / "change.yaml"
    if change_path.is_file():
        change_doc = yaml.safe_load(change_path.read_text(encoding="utf-8")) or {}
        if isinstance(change_doc, dict):
            change_doc["featureId"] = feature_id
            if not isinstance(change_doc.get("changes"), list):
                change_doc["changes"] = []
            change_path.write_text(
                yaml.safe_dump(change_doc, allow_unicode=True, sort_keys=False),
                encoding="utf-8",
            )
    if requirement_id:
        requirement_id = validate_requirement_id(requirement_id)
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
    """写入 specHash，并将 gates.G1 标为 accepted（冻结规格）。

    主控应先 `check --gate G1` 通过再 seal；本函数不再要求手改 state.gates。
    """
    digest = hashlib.sha256((feature_dir / "spec.yaml").read_bytes()).hexdigest()
    state_path = feature_dir / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["specHash"] = digest
    gates = state.setdefault("gates", {})
    if not isinstance(gates, dict):
        gates = {}
        state["gates"] = gates
    gates["G1"] = "accepted"
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return digest


def evaluate(feature_dir: Path) -> Report:
    violations: list[Violation] = []
    state = _read_state(feature_dir, violations)
    if state is None:
        return Report(violations)
    _check_change_log(feature_dir, violations)
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


def _check_change_log(feature_dir: Path, violations: list[Violation]) -> None:
    """有 change.yaml 时校验台账条目形状；缺失不挡（旧 feature），init 会带模板。"""
    path = feature_dir / "change.yaml"
    if not path.is_file():
        return
    try:
        from aiassitrequreimentdev.change_log import validate_change_entry

        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as exc:  # noqa: BLE001
        violations.append(
            Violation("G0", "CHANGE_LOG", f"change.yaml 无法解析: {exc}")
        )
        return
    if not isinstance(doc, dict):
        violations.append(Violation("G0", "CHANGE_LOG", "change.yaml 必须是映射"))
        return
    changes = doc.get("changes")
    if changes is None:
        return
    if not isinstance(changes, list):
        violations.append(Violation("G0", "CHANGE_LOG", "changes 必须是列表"))
        return
    for item in changes:
        if not isinstance(item, dict):
            violations.append(Violation("G0", "CHANGE_LOG", "变更条目必须是映射"))
            continue
        for message in validate_change_entry(item):
            violations.append(Violation("G0", "CHANGE_LOG", message))


def _check_g0(state: dict, spec: dict | None, violations: list[Violation]) -> None:
    path = state.get("path")
    if path not in PATHS:
        violations.append(
            Violation("G0", "STATE_PATH", "path 只能是 full、light 或 light-auto")
        )
        return
    if state.get("pathConfirmed") is not True:
        violations.append(
            Violation(
                "G0",
                "G0_PATH_UNCONFIRMED",
                "须先确认研发路径（path 命令写入 pathConfirmed=true）",
            )
        )
    if is_light_path(path) and spec is not None:
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

    # S* 可选：主路径由 UJ 覆盖；有条目时仍校验形状，避免半填干扰下游
    scenarios = spec.get("scenarios")
    if scenarios is None:
        violations.append(Violation("G1", "SPEC_MISSING_FIELD", "spec.yaml 缺少 scenarios"))
    elif not isinstance(scenarios, list):
        violations.append(Violation("G1", "SPEC_SCENARIO", "scenarios 必须是列表（可为空）"))
    elif scenarios:
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
    if state.get("path") == "light-auto" and spec.get("uiRequired") is not False:
        violations.append(
            Violation(
                "G1",
                "LIGHT_AUTO_UI",
                "light-auto 路径要求 uiRequired=false（无 UX/UI 才可 seal 后连跑）",
            )
        )
    _check_template_headings(
        change_dir / "prd.md",
        SPEC_PRD_H2,
        level=2,
        gate="G1",
        code="PRD_TEMPLATE",
        label="prd.md（须对齐 templates/feature/prd.md 章节）",
        violations=violations,
        must_exist=True,
    )

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


def _check_template_headings(
    path: Path,
    required_titles: tuple[str, ...],
    *,
    level: int,
    gate: str,
    code: str,
    label: str,
    violations: list[Violation],
    must_exist: bool,
) -> None:
    """人读 Markdown 必须保留 specify 模板的完整章节标题，禁止删减/改名/合并。"""
    if not path.is_file():
        if must_exist:
            violations.append(
                Violation(
                    gate,
                    code,
                    f"缺少 {label}；须从对应 specify 模板拷贝后按章节填写，不得自创精简版",
                )
            )
        return
    text = path.read_text(encoding="utf-8", errors="ignore")
    headings = extract_markdown_headings(text).get(level, [])
    miss = missing_headings(headings, required_titles)
    if miss:
        preview = "；".join(miss[:6])
        more = f" 等共 {len(miss)} 处" if len(miss) > 6 else ""
        violations.append(
            Violation(
                gate,
                code,
                f"{label} 章节与模板不对齐，缺少：{preview}{more}。"
                "须保留模板全部对应级标题原文，禁止删减、改名或合并章节",
            )
        )


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
    # 无 UI：不强制 UX；init 模板 ux.yaml（skip:false）不得挡 light-auto / 无界面切片
    if spec.get("uiRequired") is False:
        if ux_path.is_file():
            ux = _read_yaml(ux_path, "G2", "UX_MISSING", "缺少 ux.yaml", violations)
            if ux is not None and ux.get("skip") is True:
                reason = ux.get("reason")
                if not isinstance(reason, str) or not reason.strip():
                    violations.append(
                        Violation("G2", "UX_SKIP_REASON", "ux.skip 为 true 时必须写 reason")
                    )
        return
    if is_light_path(state.get("path")) and not ux_path.is_file():
        return
    ux = _read_yaml(ux_path, "G2", "UX_MISSING", "缺少 ux.yaml", violations)
    if ux is None:
        return
    if ux.get("skip") is True:
        reason = ux.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            violations.append(Violation("G2", "UX_SKIP_REASON", "ux.skip 为 true 时必须写 reason"))
        return
    _check_ux_interaction_rules(ux, violations)
    _check_ux_visual(ux, violations, change_dir)
    expected = _acceptance_ids(spec)
    mapped = ux.get("acceptance")
    if not isinstance(mapped, list):
        violations.append(Violation("G2", "UX_UNMAPPED", "ux.yaml 缺少 acceptance 列表"))
        return
    seen: set[str] = set()
    for item in mapped:
        if not isinstance(item, dict):
            violations.append(Violation("G2", "UX_UNMAPPED", "验收落点必须是映射"))
            continue
        identifier = item.get("id")
        if identifier not in expected:
            violations.append(
                Violation("G2", "UX_UNKNOWN_ACCEPTANCE", f"UX 引用了规格中不存在的 {identifier}")
            )
            continue
        if identifier in seen:
            violations.append(Violation("G2", "UX_DUPLICATE", f"{identifier} 被 UX 映射了多次"))
        seen.add(identifier)
        for key in ("flow", "surface"):
            value = item.get(key)
            if not isinstance(value, str) or not value.strip():
                violations.append(Violation("G2", "UX_UNMAPPED", f"{identifier} 缺少 {key}"))
    missing = expected - seen
    if missing:
        violations.append(
            Violation("G2", "UX_UNMAPPED", "UX 未覆盖验收: " + ", ".join(sorted(missing)))
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
        return
    visual = ux.get("visual") if isinstance(ux.get("visual"), dict) else {}
    baseline = visual.get("baseline")
    # custom：自由发挥不强制 kit；其它 baseline 须引用对应 path/prefix
    if baseline != "custom":
        kit = _visual_kit_by_id(change_dir, baseline if isinstance(baseline, str) else "ui-kit")
        # 项目锁定风格可能只在 projectStyle 里，不在 kits 列表
        if kit is None and isinstance(baseline, str):
            ps = _project_style(change_dir)
            if baseline == ps.get("id"):
                kit = {
                    "id": ps.get("id"),
                    "prefix": ps.get("prefix"),
                    "path": ps.get("path"),
                    "source": "project",
                }
        proto_text = entry.read_text(encoding="utf-8", errors="ignore").lower()
        path_hint = ""
        prefix = "uk"
        if isinstance(kit, dict):
            raw_path = kit.get("path") or kit.get("featurePath") or ""
            if isinstance(raw_path, str) and raw_path.strip():
                path_hint = raw_path.strip().replace("\\", "/").lower()
            raw_prefix = kit.get("prefix")
            if isinstance(raw_prefix, str) and raw_prefix.strip():
                prefix = raw_prefix.strip().lower()
        markers: list[str] = []
        if isinstance(kit, dict) and isinstance(kit.get("prefix"), str) and kit.get("prefix").strip():
            markers.append(f"{str(kit.get('prefix')).strip().lower()}-")
        elif baseline == "ui-kit":
            markers.append("uk-")
        if baseline == "ui-kit" or (isinstance(kit, dict) and kit.get("source") == "template"):
            markers.append("ui-kit")
        if path_hint:
            markers.append(path_hint)
            markers.append(Path(path_hint).name.lower())
        # 项目风格若尚未配置 path/prefix，跳过引用检查（配置后即强制）
        if isinstance(kit, dict) and kit.get("source") == "project":
            require_markers = bool(path_hint) or (
                isinstance(kit.get("prefix"), str) and bool(str(kit.get("prefix")).strip())
            )
        else:
            require_markers = bool(markers)
        if require_markers and not any(m and m in proto_text for m in markers):
            label = baseline if isinstance(baseline, str) and baseline.strip() else "ui-kit"
            violations.append(
                Violation(
                    "G2",
                    "UX_PROTO_UIKIT",
                    f"visual.baseline={label} 时 UX 原型须引用对应 kit"
                    f"（path 或 {prefix}-* 类名；见 research/ui-kits/catalog.yaml）；"
                    "自由发挥请设 baseline=custom 并写 notes",
                )
            )


# 无 catalog 文件时的内置三种风格 + custom（与 research/ui-kits/catalog.yaml 对齐）
_BUILTIN_UI_KITS: list[dict] = [
    {
        "id": "ui-kit",
        "label": "Music 默认 kit",
        "prefix": "uk",
        "path": "prototype/shared/ui-kit",
        "source": "template",
    },
    {
        "id": "painless",
        "label": "无痛单词（painless）",
        "prefix": "pk",
        "path": "research/painless-ui/ui-kit",
        "source": "apk-uikit",
    },
    {
        "id": "midoo",
        "label": "Midoo AI",
        "prefix": "md",
        "path": "research/midoo-ui/ui-kit",
        "source": "apk-uikit",
    },
    {
        "id": "custom",
        "label": "自由发挥",
        "prefix": None,
        "path": None,
        "source": "freeform",
    },
]


def _load_ui_kit_catalog(change_dir: Path) -> dict:
    root = repo_root_for(change_dir)
    path = root / "research" / "ui-kits" / "catalog.yaml"
    if not path.is_file():
        return {
            "default": "ui-kit",
            "styleKitIds": ["ui-kit", "painless", "midoo"],
            "projectStyle": {"locked": False, "id": "project"},
            "kits": list(_BUILTIN_UI_KITS),
        }
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return doc if isinstance(doc, dict) else {}


def _project_style(change_dir: Path) -> dict:
    catalog = _load_ui_kit_catalog(change_dir)
    raw = catalog.get("projectStyle")
    if not isinstance(raw, dict):
        return {"locked": False, "id": "project"}
    kit_id = raw.get("id")
    if not isinstance(kit_id, str) or not kit_id.strip():
        kit_id = "project"
    return {
        "locked": bool(raw.get("locked")),
        "id": kit_id.strip(),
        "label": raw.get("label") or "项目自有风格",
        "path": raw.get("path") if isinstance(raw.get("path"), str) else None,
        "prefix": raw.get("prefix") if isinstance(raw.get("prefix"), str) else None,
        "themeDoc": raw.get("themeDoc") if isinstance(raw.get("themeDoc"), str) else None,
        "notes": raw.get("notes") if isinstance(raw.get("notes"), str) else "",
    }


def _catalog_kits_by_id(catalog: dict) -> dict[str, dict]:
    kits = catalog.get("kits")
    if not isinstance(kits, list):
        return {item["id"]: item for item in _BUILTIN_UI_KITS}
    out: dict[str, dict] = {}
    for item in kits:
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            out[item["id"]] = item
    # 保证三种内置风格始终可选（即使旧 catalog 未登记）
    for item in _BUILTIN_UI_KITS:
        out.setdefault(item["id"], item)
    return out


def _allowed_visual_baselines(change_dir: Path) -> set[str]:
    catalog = _load_ui_kit_catalog(change_dir)
    ids = set(_catalog_kits_by_id(catalog))
    ids.update({"ui-kit", "painless", "midoo", "custom", "project"})
    ps = _project_style(change_dir)
    ids.add(str(ps.get("id") or "project"))
    return ids


def _visual_kit_by_id(change_dir: Path, kit_id: str) -> dict | None:
    kits = _catalog_kits_by_id(_load_ui_kit_catalog(change_dir))
    if kit_id in kits:
        return kits[kit_id]
    ps = _project_style(change_dir)
    if kit_id == ps.get("id"):
        return {
            "id": ps.get("id"),
            "label": ps.get("label"),
            "prefix": ps.get("prefix"),
            "path": ps.get("path"),
            "source": "project",
        }
    for item in _BUILTIN_UI_KITS:
        if item["id"] == kit_id:
            return item
    return None


def _check_ux_interaction_rules(ux: dict, violations: list[Violation]) -> None:
    rules = ux.get("interactionRules")
    if not isinstance(rules, list) or not rules:
        violations.append(
            Violation(
                "G2",
                "UX_RULES",
                "有 UI 时须填写 interactionRules（≥1：when/behavior；交互规则是 G2 主交付）",
            )
        )
        return
    seen: set[str] = set()
    for item in rules:
        if not isinstance(item, dict):
            violations.append(Violation("G2", "UX_RULES", "interactionRules 条目必须是映射"))
            continue
        identifier = item.get("id")
        if (
            not isinstance(identifier, str)
            or not identifier.startswith("IR")
            or identifier in seen
        ):
            violations.append(
                Violation("G2", "UX_RULES", f"交互规则编号非法或重复: {identifier}（须 IR*）")
            )
        else:
            seen.add(identifier)
        for key in ("when", "behavior"):
            value = item.get(key)
            if not isinstance(value, str) or not value.strip():
                violations.append(Violation("G2", "UX_RULES", f"{identifier} 缺少 {key}"))


def _check_ux_visual(
    ux: dict, violations: list[Violation], change_dir: Path | None = None
) -> None:
    visual = ux.get("visual")
    if visual is None:
        violations.append(
            Violation(
                "G2",
                "UX_VISUAL",
                "有 UI 时须填写 visual.baseline（项目锁定用 project；否则 ui-kit|painless|midoo|custom…）",
            )
        )
        return
    if not isinstance(visual, dict):
        violations.append(Violation("G2", "UX_VISUAL", "visual 必须是映射"))
        return
    baseline = visual.get("baseline")
    allowed = (
        _allowed_visual_baselines(change_dir)
        if change_dir is not None
        else {"ui-kit", "custom", "painless", "midoo", "project"}
    )
    if baseline not in allowed:
        allowed_txt = "|".join(sorted(allowed))
        violations.append(
            Violation(
                "G2",
                "UX_VISUAL",
                f"visual.baseline 须为已注册项（{allowed_txt}；见 research/ui-kits/catalog.yaml）",
            )
        )
    notes = visual.get("notes")
    notes_ok = isinstance(notes, str) and bool(notes.strip())
    if baseline == "custom" and not notes_ok:
        violations.append(
            Violation(
                "G2",
                "UX_VISUAL",
                "visual.baseline=custom 时须在 notes 说明为何不用已注册 kit",
            )
        )
    # 项目已锁定自有风格：偏离 project 须 notes
    if change_dir is not None:
        ps = _project_style(change_dir)
        project_id = ps.get("id") or "project"
        if ps.get("locked") and baseline not in {project_id, None} and not notes_ok:
            violations.append(
                Violation(
                    "G2",
                    "UX_VISUAL",
                    f"projectStyle.locked=true 时默认遵循 {project_id}；"
                    f"若 baseline={baseline} 偏离项目风格，须在 visual.notes 说明原因",
                )
            )
    motion = visual.get("motion")
    if motion is None:
        return
    if not isinstance(motion, list):
        violations.append(Violation("G2", "UX_MOTION", "visual.motion 必须是列表"))
        return
    seen: set[str] = set()
    for item in motion:
        if not isinstance(item, dict):
            violations.append(Violation("G2", "UX_MOTION", "motion 条目必须是映射"))
            continue
        identifier = item.get("id")
        if (
            not isinstance(identifier, str)
            or not identifier.startswith("M")
            or identifier in seen
        ):
            violations.append(
                Violation("G2", "UX_MOTION", f"动效编号非法或重复: {identifier}（须 M*）")
            )
        else:
            seen.add(identifier)
        for key in ("trigger", "effect"):
            value = item.get(key)
            if not isinstance(value, str) or not value.strip():
                violations.append(Violation("G2", "UX_MOTION", f"{identifier} 缺少 {key}"))


def _check_g2t(change_dir: Path, state: dict, spec: dict, violations: list[Violation]) -> None:
    # light 仍要求 tech，保证验收有技术落点；full 另强制 L0/L1 三级标题
    path_mode = state.get("path")
    tech_md = change_dir / "tech.md"
    if not tech_md.is_file() or tech_md.stat().st_size == 0:
        violations.append(Violation("G2T", "TECH_DOC_MISSING", "缺少 tech.md 技术方案文档"))
    else:
        _check_template_headings(
            tech_md,
            TECH_MD_H2,
            level=2,
            gate="G2T",
            code="TECH_MD_TEMPLATE",
            label="tech.md（须对齐 templates/feature/tech.md 章节）",
            violations=violations,
            must_exist=True,
        )
        if path_mode == "full":
            _check_template_headings(
                tech_md,
                TECH_MD_H3_REQUIRED,
                level=3,
                gate="G2T",
                code="TECH_MD_TEMPLATE",
                label="tech.md 强制三级标题（full 路径）",
                violations=violations,
                must_exist=True,
            )
    _check_template_headings(
        change_dir / "tech-spec.md",
        TECH_SPEC_H2,
        level=2,
        gate="G2T",
        code="TECH_SPEC_TEMPLATE",
        label="tech-spec.md（须对齐 templates/feature/tech-spec.md 章节）",
        violations=violations,
        must_exist=True,
    )
    tech = _read_yaml(
        change_dir / "tech.yaml",
        "G2T",
        "TECH_MISSING",
        "缺少 tech.yaml",
        violations,
    )
    if tech is None:
        return
    _check_tech_doc_sections(tech, violations, change_dir, path_mode=path_mode)
    _check_tech_md_diagram_embeds(change_dir, tech, violations)
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


def _check_tech_md_diagram_embeds(
    change_dir: Path, tech: dict, violations: list[Violation]
) -> None:
    """tech.md 须用 Markdown 图片语法内嵌每张 png，禁止仅表格/文字链接。"""
    diagrams = tech.get("diagrams")
    if not isinstance(diagrams, list) or not diagrams:
        return
    tech_md = change_dir / "tech.md"
    if not tech_md.is_file():
        return
    text = tech_md.read_text(encoding="utf-8")
    for index, item in enumerate(diagrams):
        if not isinstance(item, dict):
            continue
        if item.get("svg"):
            violations.append(
                Violation(
                    "G2T",
                    "TECH_DIAGRAM",
                    f"diagrams[{index}] 已废弃 svg 字段；预览合同改为 png（Markdown 可预览），"
                    "请删除 svg 并登记 png",
                )
            )
        png = item.get("png")
        if not isinstance(png, str) or not png.strip():
            continue
        png_norm = png.strip().replace("\\", "/")
        # ![任意说明](diagrams/xxx.png) 或带 ./ 前缀
        pattern = rf"!\[[^\]]*\]\((?:\./)?{re.escape(png_norm)}\)"
        if re.search(pattern, text) is None:
            violations.append(
                Violation(
                    "G2T",
                    "TECH_MD_EMBED",
                    f"tech.md 须直接内嵌预览 diagrams[{index}]："
                    f"![]({png_norm})（禁止仅表格或文字链接；勿再用 svg）",
                )
            )


def _check_diagram_archify_html(
    change_dir: Path | None,
    item: dict,
    index: int,
    violations: list[Violation],
) -> None:
    """要求 HTML 为 Archify finalize 产物（禁止手写/Mermaid 冒充）。"""
    if change_dir is None:
        return
    html_rel = item.get("html")
    if not isinstance(html_rel, str) or not html_rel.strip():
        return
    path = (change_dir / html_rel.strip()).resolve()
    try:
        path.relative_to(change_dir.resolve())
    except ValueError:
        return
    if not path.is_file():
        return
    raw = path.read_text(encoding="utf-8", errors="ignore")
    lower = raw.lower()
    has_generator = bool(
        re.search(r'<meta\s+name=["\']generator["\']\s+content=["\']archify\b', lower)
    )
    has_contract = "archify-reader-contract" in lower
    has_fonts = 'id="archify-fonts"' in lower or "id='archify-fonts'" in lower
    if not (has_generator and has_contract and has_fonts):
        violations.append(
            Violation(
                "G2T",
                "TECH_DIAGRAM_ARCHIFY",
                f"diagrams[{index}].html 须为 Archify 正式产物（含 meta generator=archify、"
                "archify-reader-contract、style#archify-fonts）。禁止手写 HTML/Mermaid/随便画图 "
                "冒充；须按 archify 技能 finalize 后另导出同 stem 的 png 供 tech.md 预览。"
                "工具：https://github.com/tt-a1i/archify",
            )
        )


def _check_diagram_png_quality(
    change_dir: Path | None,
    item: dict,
    index: int,
    violations: list[Violation],
) -> None:
    """拒绝空壳/非 PNG；登记进 tech.yaml 的预览图须为真实 PNG 字节。"""
    if change_dir is None:
        return
    png_rel = item.get("png")
    if not isinstance(png_rel, str) or not png_rel.strip():
        return
    path = (change_dir / png_rel.strip()).resolve()
    try:
        path.relative_to(change_dir.resolve())
    except ValueError:
        return
    if not path.is_file():
        return
    raw = path.read_bytes()
    if not raw.startswith(b"\x89PNG\r\n\x1a\n"):
        violations.append(
            Violation(
                "G2T",
                "TECH_DIAGRAM_QUALITY",
                f"diagrams[{index}].png 不是有效 PNG 文件（缺少 PNG 签名）",
            )
        )
        return
    # 模板占位可很小；正式登记图须可审阅（截自 Archify HTML）
    if len(raw) < 2048:
        violations.append(
            Violation(
                "G2T",
                "TECH_DIAGRAM_QUALITY",
                f"diagrams[{index}].png 过小（<{len(raw)}B），须为 Archify HTML 截出的可审阅预览，"
                "禁止 1×1/空壳占位登记进 tech.yaml",
            )
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
    tech: dict,
    violations: list[Violation],
    change_dir: Path | None = None,
    *,
    path_mode: object = None,
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
                change_dir, item.get("png"), "png", index, violations, suffix=".png"
            )
            _check_diagram_archify_html(change_dir, item, index, violations)
            _check_diagram_png_quality(change_dir, item, index, violations)
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
        # full 路径有图时：流程 / 时序 / 类图三类都要有（与架构 L0/L1 并列）
        if path_mode == "full" and diagrams:
            present_types = {
                item.get("type")
                for item in diagrams
                if isinstance(item, dict) and isinstance(item.get("type"), str)
            }
            for required in ("workflow", "sequence", "class"):
                if required not in present_types:
                    violations.append(
                        Violation(
                            "G2T",
                            "TECH_DIAGRAM_TYPE",
                            f"full 路径须提供 {required} 图（diagrams[].type={required}），"
                            "并在 tech.md 内嵌对应 SVG；勿只交架构图",
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
    if is_light_path(state.get("path")) and len(tasks) != 1:
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
