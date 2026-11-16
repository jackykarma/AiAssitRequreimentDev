"""
/*********************************************************************************
 ** Copyright (C), 2019-2029, OPLUS Mobile Comm Corp., Ltd
 ** All rights reserved.
 **
 ** File: - __main__.py
 ** Description: aiassitrequreimentdev 命令行。feature 初始化、门禁、角色与全量/轻量路径。
 ** Version: 1.4
 ** Date: 2026/11/08
 ** Author: limao2@Apps.Gallery
 **
 ** ------------------------------- Revision History: ----------------------------
 ** <author> <date> <version> <desc>
 ** ------------------------------------------------------------------------------
 ** limao2@Apps.Gallery 2026/11/08 1.4 rename change→feature
 ** limao2@Apps.Gallery 2026/11/14 1.5 usage token stats CLI
 *********************************************************************************/
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.parse import quote

from aiassitrequreimentdev.board import adopt_role, refresh_board, set_path
from aiassitrequreimentdev.change_log import (
    CHANGE_CATEGORIES,
    CHANGE_LEVELS,
    CHANGE_ROLES,
    CHANGE_STATUSES,
    format_change_report,
    record_change,
)
from aiassitrequreimentdev.gates import (
    GATES,
    evaluate,
    init_feature,
    init_requirement,
    resolve_feature_id,
    resolve_requirement_id,
    seal_spec,
)
from aiassitrequreimentdev.split import (
    evaluate_requirement,
    feature_listed_in_split,
    load_split,
)
from aiassitrequreimentdev.paths import menu_text as path_menu_text
from aiassitrequreimentdev.paths import recommend_path, resolve_path
from aiassitrequreimentdev.roles import menu_text, resolve_menu_choice
from aiassitrequreimentdev.usage import (
    USAGE_STAGES,
    format_usage_report,
    record_usage,
    summarize_usage,
    load_usage,
)


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8")


def _normalize_argv(argv: list[str]) -> list[str]:
    """兼容 `usage|change|tasks <dir> <sub>` 与 `<cmd> <sub> <dir>` 两种顺序。"""
    if len(argv) < 3:
        return argv
    head = argv[0]
    sub_by_cmd = {
        "usage": ("record", "show"),
        "change": ("record", "show"),
        "tasks": ("scaffold",),
    }
    if head not in sub_by_cmd:
        return argv
    subcommands = sub_by_cmd[head]
    if argv[1] in subcommands:
        return argv
    if argv[2] in subcommands:
        return [head, argv[2], argv[1], *argv[3:]]
    return argv


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
    argv = _normalize_argv(list(sys.argv[1:] if argv is None else argv))
    parser = argparse.ArgumentParser(prog="aiassitrequreimentdev", description="规格门禁与 feature 入口")
    sub = parser.add_subparsers(dest="command", required=True)

    init_parser = sub.add_parser(
        "init", help="按模板创建一个 feature 目录；id=FEAT-序号-kebab名称"
    )
    init_parser.add_argument(
        "feature_id",
        help="完整 id（FEAT-001-move-album）或仅序号段 FEAT-001（须配合 --name）",
    )
    init_parser.add_argument(
        "--name", help="kebab 名称，如 move-album；与序号段拼装完整 id"
    )
    init_parser.add_argument("--root", default=".", help="仓库根目录")
    init_parser.add_argument(
        "--requirement",
        help="关联的 requirementId（REQ-序号-名称-YYYYMMDD）",
    )

    req_parser = sub.add_parser(
        "init-req",
        help="创建需求目录（需求级 PRD + split.yaml）；id=REQ-序号-名称-YYYYMMDD",
    )
    req_parser.add_argument(
        "requirement_id",
        help="完整 id（REQ-001-move-album-20220305）或仅序号段 REQ-001（须配合 --name）",
    )
    req_parser.add_argument("--name", help="kebab 名称，如 move-album；与序号段拼装完整 id")
    req_parser.add_argument("--date", help="YYYYMMDD，默认今天；仅与 --name 拼装时使用")
    req_parser.add_argument("--root", default=".", help="仓库根目录")

    check_parser = sub.add_parser("check", help="检查一个 feature 目录的门禁")
    check_parser.add_argument("feature_dir")
    check_parser.add_argument("--gate", choices=GATES, help="只判断这一道门禁")
    check_parser.add_argument(
        "--accept",
        action="store_true",
        help="门禁通过时写入 gates.*.accepted 并推进 stage（须同时指定 --gate；G1 会 seal）",
    )

    check_req_parser = sub.add_parser(
        "check-req", help="检查需求目录 split.yaml（及目录名与 requirementId）"
    )
    check_req_parser.add_argument("requirement_dir")

    seal_parser = sub.add_parser("seal", help="把 spec.yaml 的哈希写入 state.json")
    seal_parser.add_argument("feature_dir")

    sub.add_parser("roles", help="打印可选择的角色菜单")

    adopt_parser = sub.add_parser("adopt", help="为 feature 写入当前角色并刷新共仓看板")
    adopt_parser.add_argument("feature_dir")
    adopt_parser.add_argument("--role", required=True, help="角色 id、中文名或菜单编号")

    board_parser = sub.add_parser("board", help="刷新 features/<id>/BOARD.md 共仓看板")
    board_parser.add_argument("feature_dir")

    recommend_parser = sub.add_parser(
        "recommend", help="根据需求描述推荐 full/light/light-auto"
    )
    recommend_parser.add_argument(
        "--text",
        "--need",
        dest="text",
        required=True,
        help="用户需求原文（--need 与 --text 等价）",
    )
    recommend_parser.add_argument("--json", action="store_true", help="输出 JSON")

    path_parser = sub.add_parser(
        "path", help="确认并写入研发路径 full/light/light-auto"
    )
    path_parser.add_argument("feature_dir")
    path_parser.add_argument(
        "--path",
        required=True,
        help="full / light / light-auto / 全量 / 轻量 / 轻量自动 / 1 / 2 / 3",
    )
    path_parser.add_argument("--recommended", help="系统推荐值，写入 state.pathRecommended")

    paths_parser = sub.add_parser("paths", help="打印路径菜单，可附带推荐")
    paths_parser.add_argument(
        "--text",
        "--need",
        dest="text",
        help="需求原文，用于生成推荐（--need 与 --text 等价）",
    )

    start_parser = sub.add_parser(
        "start", help="初始化或复用 feature，并打印角色/路径选择提示"
    )
    start_parser.add_argument(
        "feature_id",
        help="完整 id（FEAT-001-move-album）或仅序号段 FEAT-001（须配合 --name）",
    )
    start_parser.add_argument(
        "--name", help="kebab 名称；与序号段拼装完整 id（仅新建时）"
    )
    start_parser.add_argument("--root", default=".", help="仓库根目录")
    start_parser.add_argument("--role", help="若已知角色，直接 adopt")
    start_parser.add_argument(
        "--need", help="需求原文，用于推荐 full/light/light-auto"
    )
    start_parser.add_argument("--path", help="若已知路径，直接确认")

    usage_parser = sub.add_parser("usage", help="记录或查看各角色阶段 token 用量")
    usage_sub = usage_parser.add_subparsers(dest="usage_command", required=True)
    usage_record = usage_sub.add_parser("record", help="追加一条用量记录")
    usage_record.add_argument("feature_dir")
    usage_record.add_argument("--role", required=True, help="product/architect/developer/tester/deployer/lead/ux/reviewer")
    usage_record.add_argument(
        "--stage",
        help="阶段，默认取角色建议阶段；可选 " + "|".join(USAGE_STAGES),
    )
    usage_record.add_argument("--input", type=int, default=0, dest="input_tokens", help="input tokens")
    usage_record.add_argument("--output", type=int, default=0, dest="output_tokens", help="output tokens")
    usage_record.add_argument("--total", type=int, default=None, dest="total_tokens", help="若省略则=input+output")
    usage_record.add_argument("--model", default="", help="模型名（可选）")
    usage_record.add_argument("--gate", default="", help="关联门禁，如 G1")
    usage_record.add_argument("--note", default="", help="备注")
    usage_show = usage_sub.add_parser("show", help="打印用量汇总")
    usage_show.add_argument("feature_dir")
    usage_show.add_argument("--json", action="store_true", help="输出 JSON")

    tasks_parser = sub.add_parser("tasks", help="任务图：按验收生成 tasks.yaml 骨架")
    tasks_sub = tasks_parser.add_subparsers(dest="tasks_command", required=True)
    tasks_scaffold = tasks_sub.add_parser(
        "scaffold", help="按 spec.acceptance 生成 tasks.yaml（轻量族单任务）"
    )
    tasks_scaffold.add_argument("feature_dir")
    tasks_scaffold.add_argument(
        "--mode",
        choices=("auto", "single", "per-acceptance"),
        default="auto",
        help="auto=轻量/单 A* 合并；per-acceptance=每条 A* 一任务",
    )
    tasks_scaffold.add_argument(
        "--force", action="store_true", help="覆盖已有非空 tasks.yaml"
    )

    change_parser = sub.add_parser(
        "change",
        help="记录或查看变更台账（feature 或 requirement 目录）",
    )
    change_sub = change_parser.add_subparsers(dest="change_command", required=True)
    change_record = change_sub.add_parser(
        "record",
        help="追加一条变更；目录可以是 features/<id> 或 requirements/<REQ>",
    )
    change_record.add_argument(
        "feature_dir",
        help="feature 目录或需求目录（requirements/REQ-…）",
    )
    change_record.add_argument(
        "--initiated-by",
        required=True,
        help="发起角色: " + "|".join(CHANGE_ROLES),
    )
    change_record.add_argument("--name", default="", help="发起人姓名/账号")
    change_record.add_argument("--reason", required=True, help="变更原因")
    change_record.add_argument("--level", required=True, choices=CHANGE_LEVELS, help="C0..C4")
    change_record.add_argument(
        "--category",
        required=True,
        choices=CHANGE_CATEGORIES,
        help="product|ux|tech|tasks|split|other",
    )
    change_record.add_argument("--summary", required=True, help="一句话摘要")
    change_record.add_argument(
        "--artifacts",
        default="",
        help="影响文件，逗号分隔，如 spec.yaml,prd.md",
    )
    change_record.add_argument(
        "--gates",
        default="",
        help="须回退门禁，逗号分隔，如 G1,G2,G2T",
    )
    change_record.add_argument("--acceptance", default="", help="相关 A*，逗号分隔")
    change_record.add_argument("--features", default="", help="相关 feature id，逗号分隔")
    change_record.add_argument(
        "--status",
        default="proposed",
        choices=CHANGE_STATUSES,
        help="proposed|approved|applied",
    )
    change_record.add_argument("--confirmed-by", default="", help="确认人角色（C3/C4 建议）")
    change_record.add_argument("--confirmed-name", default="", help="确认人姓名")
    change_record.add_argument(
        "--rollback",
        action="store_true",
        help="强制按 gatesRollback 回退门禁（含 proposed）",
    )
    change_record.add_argument(
        "--no-rollback",
        action="store_true",
        help="禁止自动回退（approved/applied 默认会回退）",
    )
    change_show = change_sub.add_parser("show", help="打印变更台账")
    change_show.add_argument("feature_dir")
    change_show.add_argument("--json", action="store_true", help="输出 JSON")

    args = parser.parse_args(argv)

    if args.command == "init-req":
        try:
            requirement_id = resolve_requirement_id(
                args.requirement_id,
                name=args.name,
                date_text=args.date,
            )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        destination = init_requirement(Path(args.root), requirement_id)
        print(destination)
        print("下一步：产品写需求级 PRD，再填 split.yaml 决定 1 或 N 个 feature。")
        return 0

    if args.command == "init":
        try:
            feature_id = resolve_feature_id(args.feature_id, name=args.name)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        destination = init_feature(
            Path(args.root),
            feature_id,
            requirement_id=args.requirement,
        )
        refresh_board(destination)
        print(destination)
        if args.requirement:
            req_dir = Path(args.root) / "requirements" / args.requirement
            split_doc = load_split(req_dir / "split.yaml")
            if split_doc is None:
                print(
                    f"警告：未找到 {req_dir / 'split.yaml'}，请先写 split 再批量建 feature。",
                    file=sys.stderr,
                )
            elif not feature_listed_in_split(split_doc, feature_id):
                print(
                    f"警告：{feature_id} 未出现在 split.yaml features[] 中，请核对拆分表。",
                    file=sys.stderr,
                )
        return 0

    if args.command == "check-req":
        violations = evaluate_requirement(Path(args.requirement_dir))
        if not violations:
            print("REQ ready")
            return 0
        for item in violations:
            print(f"{item.gate} {item.code} {item.message}")
        return 1

    if args.command == "seal":
        print(seal_spec(Path(args.feature_dir)))
        return 0

    if args.command == "roles":
        print(menu_text())
        return 0

    if args.command == "adopt":
        state = adopt_role(Path(args.feature_dir), args.role)
        role = resolve_menu_choice(args.role)
        assert role is not None
        print(json.dumps({"actorRole": state["actorRole"], "skill": role.skill}, ensure_ascii=False))
        print(f"请启用技能：{role.skill}")
        print(f"可写：{', '.join(role.writes)}")
        print(f"共仓必读：{', '.join(role.reads)}")
        return 0

    if args.command == "board":
        path = refresh_board(Path(args.feature_dir))
        print(path)
        return 0

    if args.command == "recommend":
        recommendation = recommend_path(args.text)
        payload = {
            "path": recommendation.path,
            "confidence": recommendation.confidence,
            "reasons": list(recommendation.reasons),
            "picker": (
                "docs/path-picker.html?recommend="
                + recommendation.path
                + "&reason="
                + quote(recommendation.reasons[0], safe="")
            ),
        }
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(path_menu_text(recommendation))
            print("")
            print("请在对话内确认路径；备用选择页：" + payload["picker"])
        return 0

    if args.command == "paths":
        recommendation = recommend_path(args.text) if args.text else None
        print(path_menu_text(recommendation))
        if recommendation is not None:
            print("")
            print(
                "请在对话内确认路径；备用选择页：docs/path-picker.html?recommend="
                + recommendation.path
                + "&reason="
                + quote(recommendation.reasons[0], safe="")
            )
        else:
            print("")
            print("请在对话内确认路径；备用选择页：docs/path-picker.html")
        return 0

    if args.command == "path":
        option = resolve_path(args.path)
        if option is None:
            print(f"未知路径: {args.path}", file=sys.stderr)
            return 2
        state = set_path(Path(args.feature_dir), args.path, recommended=args.recommended)
        print(
            json.dumps(
                {
                    "path": state["path"],
                    "pathConfirmed": state.get("pathConfirmed"),
                    "pathRecommended": state.get("pathRecommended"),
                },
                ensure_ascii=False,
            )
        )
        return 0

    if args.command == "start":
        root = Path(args.root)
        try:
            feature_id = resolve_feature_id(args.feature_id, name=args.name)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        destination = root / "features" / feature_id
        if not destination.exists():
            destination = init_feature(root, feature_id)
        refresh_board(destination)
        print(destination)
        print("")
        print(menu_text())
        print("")
        print("请在对话内选择角色（AskQuestion 或回复编号）；主控再 adopt。HTML picker 仅备用。")
        if args.role:
            adopt_role(destination, args.role)
            role = resolve_menu_choice(args.role)
            assert role is not None
            print("")
            print(f"已选择角色：{role.label} → 启用 {role.skill}")
        recommendation = recommend_path(args.need) if args.need else None
        print("")
        print(path_menu_text(recommendation))
        print("")
        print("请在对话内确认路径（AskQuestion 或回复编号）；主控再 path。HTML picker 仅备用。")
        if recommendation is not None:
            picker = (
                "docs/path-picker.html?recommend="
                + recommendation.path
                + "&reason="
                + quote(recommendation.reasons[0], safe="")
            )
            print("备用选择页：" + picker)
        else:
            print("备用选择页：docs/path-picker.html（可先提供需求后再 recommend）")
        if args.path:
            set_path(
                destination,
                args.path,
                recommended=recommendation.path if recommendation else None,
            )
            option = resolve_path(args.path)
            assert option is not None
            print("")
            print(f"已确认路径：{option.label}（{option.id}）")
        return 0

    if args.command == "usage":
        feature_dir = Path(args.feature_dir)
        if args.usage_command == "record":
            try:
                entry = record_usage(
                    feature_dir,
                    role=args.role,
                    stage=args.stage,
                    input_tokens=args.input_tokens,
                    output_tokens=args.output_tokens,
                    total_tokens=args.total_tokens,
                    model=args.model,
                    gate=args.gate,
                    note=args.note,
                )
            except ValueError as exc:
                print(str(exc), file=sys.stderr)
                return 2
            refresh_board(feature_dir)
            print(json.dumps(entry, ensure_ascii=False))
            return 0
        if args.usage_command == "show":
            if args.json:
                doc = load_usage(feature_dir)
                print(
                    json.dumps(
                        {"entries": doc.get("entries", []), "summary": summarize_usage(doc)},
                        ensure_ascii=False,
                        indent=2,
                    )
                )
            else:
                print(format_usage_report(feature_dir))
            return 0
        return 2

    if args.command == "tasks":
        feature_dir = Path(args.feature_dir)
        if args.tasks_command == "scaffold":
            from aiassitrequreimentdev.tasks_scaffold import scaffold_tasks

            try:
                path = scaffold_tasks(
                    feature_dir, mode=args.mode, force=args.force
                )
            except (FileExistsError, FileNotFoundError, ValueError) as exc:
                print(str(exc), file=sys.stderr)
                return 2
            refresh_board(feature_dir)
            print(path)
            print(
                "已生成 tasks.yaml 骨架：请改 writeScopes 为真实写集，"
                "确认 verify 与 A* 同源后 check --gate G3。"
            )
            return 0
        return 2

    if args.command == "change":
        feature_dir = Path(args.feature_dir)
        if args.change_command == "record":
            def _split(raw: str) -> list[str]:
                return [part.strip() for part in raw.split(",") if part.strip()]

            apply_rollback: bool | None
            if args.no_rollback:
                apply_rollback = False
            elif args.rollback:
                apply_rollback = True
            else:
                apply_rollback = None

            try:
                entry = record_change(
                    feature_dir,
                    initiated_by=args.initiated_by,
                    name=args.name,
                    reason=args.reason,
                    level=args.level,
                    category=args.category,
                    summary=args.summary,
                    artifacts=_split(args.artifacts),
                    gates_rollback=_split(args.gates),
                    acceptance_ids=_split(args.acceptance),
                    features=_split(args.features),
                    status=args.status,
                    confirmed_by_role=args.confirmed_by,
                    confirmed_by_name=args.confirmed_name,
                    apply_rollback=apply_rollback,
                )
            except ValueError as exc:
                print(str(exc), file=sys.stderr)
                return 2
            # feature 目录才刷新 BOARD；需求目录无 BOARD
            if (feature_dir / "state.json").is_file():
                refresh_board(feature_dir)
            print(json.dumps(entry, ensure_ascii=False, indent=2))
            if entry.get("_rollbackApplied"):
                print(
                    "已按 gatesRollback 回退受影响 feature 门禁（含下游）；"
                    "含 G1 已清 specHash。改 split/PRD 与切片后 check --accept，"
                    "最后将 status 改为 applied。"
                )
            else:
                print(
                    "下一步：C4 改 split.yaml / 需求级 PRD；C3/C4 人确认后用 approved；"
                    "受影响 feature 用 --features 列出以便回退门禁。"
                )
            return 0
        if args.change_command == "show":
            if args.json:
                from aiassitrequreimentdev.change_log import load_change_doc

                print(json.dumps(load_change_doc(feature_dir), ensure_ascii=False, indent=2))
            else:
                print(format_change_report(feature_dir))
            return 0
        return 2

    if args.command == "check":
        feature_dir = Path(args.feature_dir)
        report = evaluate(feature_dir)
        selected = report.violations
        if args.gate:
            selected = [item for item in selected if item.gate == args.gate]
        if selected:
            for item in selected:
                print(f"{item.gate} {item.code} {item.message}")
            return 1

        print(f"{args.gate or 'ALL'} ready")
        if args.accept:
            if not args.gate:
                print("--accept 须同时指定 --gate", file=sys.stderr)
                return 2
            from aiassitrequreimentdev.progress import accept_gate

            try:
                state = accept_gate(feature_dir, args.gate)
            except ValueError as exc:
                print(str(exc), file=sys.stderr)
                return 2
            refresh_board(feature_dir)
            print(
                json.dumps(
                    {
                        "accepted": args.gate,
                        "stage": state.get("stage"),
                        "gates": state.get("gates"),
                        "specHash": state.get("specHash"),
                    },
                    ensure_ascii=False,
                )
            )
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
