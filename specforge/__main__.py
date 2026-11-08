"""
/*********************************************************************************
 ** Copyright (C), 2019-2029, OPLUS Mobile Comm Corp., Ltd
 ** All rights reserved.
 **
 ** File: - __main__.py
 ** Description: specforge 命令行。feature 初始化、门禁、角色与全量/轻量路径。
 ** Version: 1.4
 ** Date: 2026/11/08
 ** Author: limao2@Apps.Gallery
 **
 ** ------------------------------- Revision History: ----------------------------
 ** <author> <date> <version> <desc>
 ** ------------------------------------------------------------------------------
 ** limao2@Apps.Gallery 2026/11/08 1.4 rename change→feature
 *********************************************************************************/
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.parse import quote

from specforge.board import adopt_role, refresh_board, set_path
from specforge.gates import GATES, evaluate, init_feature, init_requirement, seal_spec
from specforge.paths import menu_text as path_menu_text
from specforge.paths import recommend_path, resolve_path
from specforge.roles import menu_text, resolve_menu_choice


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
    parser = argparse.ArgumentParser(prog="specforge", description="规格门禁与 feature 入口")
    sub = parser.add_subparsers(dest="command", required=True)

    init_parser = sub.add_parser("init", help="按模板创建一个 feature 目录")
    init_parser.add_argument("feature_id")
    init_parser.add_argument("--root", default=".", help="仓库根目录")
    init_parser.add_argument("--requirement", help="关联的 requirementId")

    req_parser = sub.add_parser("init-req", help="创建需求目录（需求级 PRD + split.yaml）")
    req_parser.add_argument("requirement_id")
    req_parser.add_argument("--root", default=".", help="仓库根目录")

    check_parser = sub.add_parser("check", help="检查一个 feature 目录的门禁")
    check_parser.add_argument("feature_dir")
    check_parser.add_argument("--gate", choices=GATES, help="只判断这一道门禁")

    seal_parser = sub.add_parser("seal", help="把 spec.yaml 的哈希写入 state.json")
    seal_parser.add_argument("feature_dir")

    sub.add_parser("roles", help="打印可选择的角色菜单")

    adopt_parser = sub.add_parser("adopt", help="为 feature 写入当前角色并刷新共仓看板")
    adopt_parser.add_argument("feature_dir")
    adopt_parser.add_argument("--role", required=True, help="角色 id、中文名或菜单编号")

    board_parser = sub.add_parser("board", help="刷新 features/<id>/BOARD.md 共仓看板")
    board_parser.add_argument("feature_dir")

    recommend_parser = sub.add_parser("recommend", help="根据需求描述推荐 full/light")
    recommend_parser.add_argument("--text", required=True, help="用户需求原文")
    recommend_parser.add_argument("--json", action="store_true", help="输出 JSON")

    path_parser = sub.add_parser("path", help="确认并写入研发路径 full/light")
    path_parser.add_argument("feature_dir")
    path_parser.add_argument("--path", required=True, help="full / light / 全量 / 轻量 / 1 / 2")
    path_parser.add_argument("--recommended", help="系统推荐值，写入 state.pathRecommended")

    paths_parser = sub.add_parser("paths", help="打印全量/轻量菜单，可附带推荐")
    paths_parser.add_argument("--text", help="需求原文，用于生成推荐")

    start_parser = sub.add_parser("start", help="初始化或复用 feature，并打印角色/路径选择提示")
    start_parser.add_argument("feature_id")
    start_parser.add_argument("--root", default=".", help="仓库根目录")
    start_parser.add_argument("--role", help="若已知角色，直接 adopt")
    start_parser.add_argument("--need", help="需求原文，用于推荐 full/light")
    start_parser.add_argument("--path", help="若已知路径，直接确认")

    args = parser.parse_args(argv)

    if args.command == "init-req":
        destination = init_requirement(Path(args.root), args.requirement_id)
        print(destination)
        print("下一步：产品写需求级 PRD，再填 split.yaml 决定 1 或 N 个 feature。")
        return 0

    if args.command == "init":
        destination = init_feature(
            Path(args.root),
            args.feature_id,
            requirement_id=args.requirement,
        )
        refresh_board(destination)
        print(destination)
        return 0

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
            print("选择页：" + payload["picker"])
        return 0

    if args.command == "paths":
        recommendation = recommend_path(args.text) if args.text else None
        print(path_menu_text(recommendation))
        if recommendation is not None:
            print("")
            print(
                "选择页：docs/path-picker.html?recommend="
                + recommendation.path
                + "&reason="
                + quote(recommendation.reasons[0], safe="")
            )
        else:
            print("")
            print("选择页：docs/path-picker.html")
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
        destination = root / "features" / args.feature_id
        if not destination.exists():
            destination = init_feature(root, args.feature_id)
        refresh_board(destination)
        print(destination)
        print("")
        print(menu_text())
        print("")
        print("角色选择页：docs/role-picker.html")
        if args.role:
            adopt_role(destination, args.role)
            role = resolve_menu_choice(args.role)
            assert role is not None
            print("")
            print(f"已选择角色：{role.label} → 启用 {role.skill}")
        recommendation = recommend_path(args.need) if args.need else None
        print("")
        print(path_menu_text(recommendation))
        if recommendation is not None:
            picker = (
                "docs/path-picker.html?recommend="
                + recommendation.path
                + "&reason="
                + quote(recommendation.reasons[0], safe="")
            )
            print("")
            print("路径选择页：" + picker)
        else:
            print("")
            print("路径选择页：docs/path-picker.html（可先提供需求后再 recommend）")
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

    report = evaluate(Path(args.feature_dir))
    selected = report.violations
    if args.gate:
        selected = [item for item in selected if item.gate == args.gate]
    if not selected:
        print(f"{args.gate or 'ALL'} ready")
        return 0
    for item in selected:
        print(f"{item.gate} {item.code} {item.message}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
