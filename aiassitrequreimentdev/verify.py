"""
/*********************************************************************************
 ** Copyright (C), 2019-2029, OPLUS Mobile Comm Corp., Ltd
 ** All rights reserved.
 **
 ** File: - verify.py
 ** Description: 验收执行器。真实运行 spec.acceptance[].verify，采集退出码并回写证据；
 **              失败时按 C0/C1 自动提单回退，带重试上限防止无限改测循环。
 ** Version: 1.0
 ** Date: 2026/11/20
 ** Author: limao2@Apps.Gallery
 **
 ** ------------------------------- Revision History: ----------------------------
 ** <author> <date> <version> <desc>
 ** ------------------------------------------------------------------------------
 ** limao2@Apps.Gallery 2026/11/20 1.0 INIT：runner + 假绿检测 + 有界自动提单
 *********************************************************************************/
"""

from __future__ import annotations

import json
import shlex
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import yaml

from aiassitrequreimentdev.gates import _acceptance_ids
from aiassitrequreimentdev.progress import GATE_WORK_STAGE
from aiassitrequreimentdev.verify_match import (
    TODO_VERIFY,
    commands_match,
    is_fake_green,
    normalize_command,
    verify_hash,
)

DEFAULT_TIMEOUT = 120
DEFAULT_MAX_ATTEMPTS = 3
FIX_TASK_FILE = "fix-tasks.yaml"


@dataclass(frozen=True)
class VerifyOutcome:
    """单条 A* 的真实执行结果。"""

    acceptanceId: str
    command: str
    verify: str
    exitCode: int
    excerpt: str
    executedBy: str = "runner"
    executedAt: str = ""
    durationMs: int = 0
    verifyHash: str = ""
    timedOut: bool = False

    def to_evidence(self) -> dict:
        payload = asdict(self)
        # evidence.yaml 不重复写 verify 原文以外的冗余键，保留完整以便溯源
        return payload


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _read_state(feature_dir: Path) -> dict:
    state_path = feature_dir / "state.json"
    if not state_path.is_file():
        raise FileNotFoundError(f"缺少 state.json: {state_path}")
    state = json.loads(state_path.read_text(encoding="utf-8"))
    if not isinstance(state, dict):
        raise ValueError("state.json 必须是对象")
    return state


def _write_state(feature_dir: Path, state: dict) -> None:
    (feature_dir / "state.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _read_spec(feature_dir: Path) -> dict:
    spec_path = feature_dir / "spec.yaml"
    if not spec_path.is_file():
        raise FileNotFoundError(f"缺少 spec.yaml: {spec_path}")
    doc = yaml.safe_load(spec_path.read_text(encoding="utf-8")) or {}
    if not isinstance(doc, dict):
        raise ValueError("spec.yaml 必须是映射")
    return doc


def _acceptance_map(spec: dict) -> dict[str, dict]:
    result: dict[str, dict] = {}
    acceptance = spec.get("acceptance")
    if not isinstance(acceptance, list):
        return result
    for item in acceptance:
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            result[item["id"]] = item
    return result


def _run_one(command: str, *, cwd: Path, timeout: int, force_shell: bool) -> tuple[int, str, bool]:
    """执行一条命令，返回 (exitCode, excerpt, timedOut)。"""
    shell = force_shell
    argv: str | list[str]
    try:
        parts = shlex.split(command)
    except ValueError:
        parts = []
    if not parts and not shell:
        return 2, "命令无法解析为空，且未启用 shell 模式", False
    argv = command if shell else parts
    try:
        completed = subprocess.run(
            argv,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=shell,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        tail = (exc.stdout or "") + (exc.stderr or "")
        if isinstance(tail, bytes):
            tail = tail.decode("utf-8", errors="replace")
        return 124, (tail + f"\n[TIMEOUT] 超过 {timeout}s").strip()[-4000:], True
    except FileNotFoundError as exc:
        return 127, f"[COMMAND_NOT_FOUND] {exc}", False
    except OSError as exc:
        return 126, f"[EXEC_ERROR] {exc}", False
    output = (completed.stdout or "") + (completed.stderr or "")
    return completed.returncode, output.strip()[-4000:], False


def run_verification(
    feature_dir: Path,
    *,
    only: list[str] | None = None,
    timeout: int = DEFAULT_TIMEOUT,
    dry_run: bool = False,
    force_shell: bool = False,
    enable_runner_mode: bool = True,
) -> dict:
    """真实执行全部（或指定）A* 的 verify，回写 evidence.yaml，返回结果摘要。

    执行成功后将 state.verification.mode 切到 runner，G4 硬校验随之生效。
    """
    feature_dir = feature_dir.resolve()
    spec = _read_spec(feature_dir)
    acc_map = _acceptance_map(spec)
    selected = only if only else sorted(_acceptance_ids(spec))
    unknown = [item for item in selected if item not in acc_map]
    if unknown:
        raise ValueError(f"未知 A*: {', '.join(unknown)}；spec 中有: {', '.join(sorted(acc_map))}")

    outcomes: list[VerifyOutcome] = []
    for acceptance_id in selected:
        item = acc_map[acceptance_id]
        verify = item.get("verify")
        if not isinstance(verify, str) or not verify.strip() or verify.strip() == TODO_VERIFY:
            outcomes.append(
                VerifyOutcome(
                    acceptanceId=acceptance_id,
                    command="",
                    verify=verify if isinstance(verify, str) else "",
                    exitCode=2,
                    excerpt="[VERIFY_MISSING] spec.acceptance[].verify 未定义或仍是占位符",
                    verifyHash=verify_hash(verify if isinstance(verify, str) else ""),
                )
            )
            continue
        if dry_run:
            outcomes.append(
                VerifyOutcome(
                    acceptanceId=acceptance_id,
                    command=verify,
                    verify=verify,
                    exitCode=0,
                    excerpt="[DRY_RUN] 未实际执行",
                    verifyHash=verify_hash(verify),
                    executedBy="dry-run",
                )
            )
            continue
        started = datetime.now(timezone.utc)
        code, excerpt, timed_out = _run_one(
            verify, cwd=feature_dir, timeout=timeout, force_shell=force_shell
        )
        duration = int((datetime.now(timezone.utc) - started).total_seconds() * 1000)
        outcomes.append(
            VerifyOutcome(
                acceptanceId=acceptance_id,
                command=verify,
                verify=verify,
                exitCode=code,
                excerpt=excerpt,
                executedAt=_now_iso(),
                durationMs=duration,
                verifyHash=verify_hash(verify),
                timedOut=timed_out,
            )
        )

    if not dry_run:
        _write_evidence(feature_dir, outcomes)
        state = _read_state(feature_dir)
        verification = _ensure_verification(state)
        if enable_runner_mode:
            verification["mode"] = "runner"
        _write_state(feature_dir, state)

    failed = [item.acceptanceId for item in outcomes if item.exitCode != 0]
    return {
        "feature": feature_dir.name,
        "dryRun": dry_run,
        "mode": "runner" if enable_runner_mode and not dry_run else "self-report",
        "total": len(outcomes),
        "passed": len(outcomes) - len(failed),
        "failed": failed,
        "results": [asdict(item) for item in outcomes],
    }


def _write_evidence(feature_dir: Path, outcomes: list[VerifyOutcome]) -> Path:
    """合并写回 evidence.yaml：本次覆盖同名 A*，其余条目保留。"""
    path = feature_dir / "evidence.yaml"
    existing: dict[str, dict] = {}
    if path.is_file():
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            if isinstance(doc, dict) and isinstance(doc.get("results"), list):
                for item in doc["results"]:
                    if isinstance(item, dict) and isinstance(item.get("acceptanceId"), str):
                        existing[item["acceptanceId"]] = item
        except yaml.YAMLError:
            existing = {}
    for outcome in outcomes:
        existing[outcome.acceptanceId] = outcome.to_evidence()
    ordered = [existing[key] for key in sorted(existing)]
    path.write_text(
        "# 由 verify run 真实执行生成；command 与 spec.acceptance[].verify 同源。\n"
        + yaml.safe_dump({"results": ordered}, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return path


def _ensure_verification(state: dict) -> dict:
    verification = state.get("verification")
    if not isinstance(verification, dict):
        verification = {}
        state["verification"] = verification
    verification.setdefault("mode", "self-report")
    verification.setdefault("attempts", 0)
    verification.setdefault("maxAttempts", DEFAULT_MAX_ATTEMPTS)
    verification.setdefault("lastFailure", None)
    verification.setdefault("blocked", False)
    return verification


def verification_status(feature_dir: Path) -> dict:
    feature_dir = feature_dir.resolve()
    state = _read_state(feature_dir)
    verification = _ensure_verification(state)
    return {
        "feature": feature_dir.name,
        "stage": state.get("stage"),
        "mode": verification["mode"],
        "attempts": verification["attempts"],
        "maxAttempts": verification["maxAttempts"],
        "blocked": verification["blocked"],
        "lastFailure": verification["lastFailure"],
        "gates": state.get("gates", {}),
    }


def mark_verification_success(feature_dir: Path) -> dict:
    """全部 A* 通过时清零重试计数，解除 blocked。"""
    feature_dir = feature_dir.resolve()
    state = _read_state(feature_dir)
    verification = _ensure_verification(state)
    verification["attempts"] = 0
    verification["lastFailure"] = None
    verification["blocked"] = False
    _write_state(feature_dir, state)
    fix_task = _read_fix_task(feature_dir)
    if isinstance(fix_task, dict) and fix_task.get("status") == "open":
        fix_task["status"] = "fixed"
        fix_task["fixedAt"] = _now_iso()
        _write_fix_task(feature_dir, fix_task)
    return verification_status(feature_dir)


def _write_fix_task(feature_dir: Path, payload: dict) -> Path:
    """把失败证据打包成 dev agent 可直接认领的修复任务。"""
    path = feature_dir / FIX_TASK_FILE
    path.write_text(
        "# 由 verify run 失败自动生成；dev agent 认领本任务包在写集内修复。\n"
        + yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return path


def _read_fix_task(feature_dir: Path) -> dict | None:
    path = feature_dir / FIX_TASK_FILE
    if not path.is_file():
        return None
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return None
    return doc if isinstance(doc, dict) else None


def auto_fix_failures(
    feature_dir: Path,
    failed: list[str],
    *,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    reason_prefix: str = "AC 验收失败自动提单",
    results: list[dict] | None = None,
) -> dict:
    """失败 A* 自动提单（C0）并回退 G3+，生成修复任务包交 dev agent。

    闭环：verify run 失败 → 本函数提单+回退+派单 → dev agent 修复 → 主控重跑
    verify run → 通过则清计数。超过 maxAttempts 才标记 blocked 打断人。
    修复与判定分离：dev 碰不到 evidence.yaml 与门禁状态，判定仍由 runner 真跑。
    """
    feature_dir = feature_dir.resolve()
    if not failed:
        return {"action": "none", "reason": "no failures"}
    state = _read_state(feature_dir)
    verification = _ensure_verification(state)
    verification["maxAttempts"] = max_attempts
    attempts = int(verification["attempts"]) + 1
    verification["attempts"] = attempts
    verification["lastFailure"] = {"at": _now_iso(), "acceptanceIds": list(failed)}

    results_by_id = {item.get("acceptanceId"): item for item in (results or [])}
    details = []
    for aid in failed:
        outcome = results_by_id.get(aid, {})
        excerpt = outcome.get("excerpt", "")[:1500]
        if not excerpt.strip():
            excerpt = "[NO_OUTPUT] 失败命令未产生 stdout/stderr；dev 需本地复现该 verify 定位缺陷"
        details.append(
            {
                "acceptanceId": aid,
                "verify": outcome.get("verify", ""),
                "exitCode": outcome.get("exitCode"),
                "excerpt": excerpt,
                "hint": "按 excerpt 定位失败断言，在 tasks.yaml 写集内修复源码后重跑 verify",
            }
        )

    if verification.get("blocked") or attempts > max_attempts:
        verification["blocked"] = True
        _write_state(feature_dir, state)
        _write_fix_task(
            feature_dir,
            {
                "status": "blocked",
                "round": attempts,
                "maxAttempts": max_attempts,
                "reason": "已达重试上限，dev 未在写集内修复；交人工（I_TEST_STUCK）",
                "items": details,
            },
        )
        return {
            "action": "blocked",
            "attempts": attempts,
            "maxAttempts": max_attempts,
            "reason": "已达重试上限，停止自动修复，需人工介入（I_TEST_STUCK）",
            "acceptanceIds": list(failed),
            "interrupt": "I_TEST_STUCK",
            "nextRole": "human",
        }

    from aiassitrequreimentdev.change_log import record_change

    rollback_gates = ["G3", "GR", "G4", "GQA"]
    entry = record_change(
        feature_dir,
        initiated_by="tester",
        reason=f"{reason_prefix}: A* {', '.join(failed)} 真实执行未通过（第 {attempts}/{max_attempts} 次）",
        level="C0",
        category="tasks",
        summary=f"自动回退开发门禁，派 dev 修复 A* {', '.join(failed)} 后重跑 verify",
        artifacts=["source", "tasks.yaml", "evidence.yaml"],
        gates_rollback=rollback_gates,
        acceptance_ids=list(failed),
        status="applied",
        apply_rollback=True,
    )
    verification["blocked"] = False
    _write_state(feature_dir, state)
    _write_fix_task(
        feature_dir,
        {
            "status": "open",
            "round": attempts,
            "maxAttempts": max_attempts,
            "changeId": entry.get("id"),
            "assignTo": "dev",
            "items": details,
            "done": [
                "读 tasks.yaml 的 writeScopes 与 tech.yaml 的 aiConstraints/keyDesigns",
                "在写集内修复失败 A* 对应的源码；禁止改 spec/ux/tech/state/evidence/review",
                "修复完成后通知主控重跑 verify run；判定由 runner 真跑给出，dev 不自报",
            ],
        },
    )
    fresh = _read_state(feature_dir)
    return {
        "action": "auto-fix",
        "changeId": entry.get("id"),
        "attempts": attempts,
        "maxAttempts": max_attempts,
        "rolledBack": rollback_gates,
        "workStage": GATE_WORK_STAGE.get("G3"),
        "acceptanceIds": list(failed),
        "gates": fresh.get("gates", {}),
        "fixTask": FIX_TASK_FILE,
        "nextRole": "dev",
        "dispatch": "主控自动派 dev agent 认领 fix-tasks.yaml 在写集内修复；修复后重跑 verify run（勿打断人）",
    }


def verification_next(feature_dir: Path) -> dict:
    """主控编排入口：返回当前应由哪个角色行动，驱动无人值守循环。"""
    feature_dir = feature_dir.resolve()
    status = verification_status(feature_dir)
    state = _read_state(feature_dir)
    verification = _ensure_verification(state)
    fix_task = _read_fix_task(feature_dir)
    mode = status["mode"]
    if mode != "runner":
        return {
            **status,
            "nextRole": "lead",
            "reason": "尚未开启 runner 模式，先由主控跑 verify run 开启真实执行",
        }
    if verification.get("blocked"):
        return {**status, "nextRole": "human", "interrupt": "I_TEST_STUCK",
                "reason": "dev 重试已达上限，需人工介入"}
    if fix_task and fix_task.get("status") == "open":
        return {**status, "nextRole": "dev", "fixTask": FIX_TASK_FILE,
                "round": fix_task.get("round"),
                "reason": "verify 判失败，dev agent 认领修复任务包（自动派，勿打断人）"}
    if status["gates"].get("G4") == "accepted":
        if state.get("stage") == "done" or status["gates"].get("GQA") == "accepted":
            return {**status, "nextRole": "lead", "reason": "G4/GQA 已过，走 GD 上线确认（人）"}
        return {**status, "nextRole": "human", "reason": "AC 已通过，待人签收 qa.yaml 提测（GQA）"}
    return {**status, "nextRole": "tester",
            "reason": "runner 模式已开启但尚无有效证据，由主控代跑 verify run 取真实结果"}
