"""
/*********************************************************************************
 ** Copyright (C), 2019-2029, OPLUS Mobile Comm Corp., Ltd
 ** All rights reserved.
 **
 ** File: - aad.py
 ** Description: Plugin launcher: ensure package then run aiassitrequreimentdev CLI.
 ** Version: 1.1
 ** Date: 2026/11/14
 ** Author: limao2@Apps.Gallery
 **
 ** ------------------------------- Revision History: ----------------------------
 ** <author> <date> <version> <desc>
 ** ------------------------------------------------------------------------------
 ** limao2@Apps.Gallery 2026/11/14 1.0 INIT
 ** limao2@Apps.Gallery 2026/11/14 1.1 懒装 URL、失败提示、安装后重启解释器
 *********************************************************************************/
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def plugin_root_from(script_file: Path) -> Path:
    return script_file.resolve().parent.parent


def repo_root_from_plugin(plugin_root: Path) -> Path | None:
    candidate = plugin_root.resolve().parent.parent
    if (candidate / "aiassitrequreimentdev" / "__init__.py").is_file():
        return candidate
    return None


def package_importable() -> bool:
    try:
        import aiassitrequreimentdev  # noqa: F401
        return True
    except ImportError:
        return False


def git_requirement(remote: str, ref: str) -> str:
    remote = remote.strip()
    if remote.lower().startswith("git+"):
        return remote
    return f"git+{remote}@{ref}#egg=aiassitrequreimentdev"


def install_help(reason: str) -> str:
    py = sys.version.split()[0]
    return (
        f"{reason}\n"
        f"当前 Python {py}（需要 ≥3.11）。\n"
        "AAD_GIT_REMOTE 期望形式（未以 git+ 开头时只加一次前缀）：\n"
        "  https://host/org/repo.git\n"
        "    → git+https://host/org/repo.git@<AAD_GIT_REF>#egg=aiassitrequreimentdev\n"
        "  git@host:org/repo.git 或 ssh://git@host/org/repo.git\n"
        "    → 同样只加一次 git+，再追加 @<ref>#egg=aiassitrequreimentdev\n"
        "  git+https://host/org/repo.git[@ref][#egg=aiassitrequreimentdev]\n"
        "    → 已以 git+ 开头则原样作为 pip 依赖，不再加前缀，也不再追加 @ref\n"
        "可选 AAD_GIT_REF，默认 master（与本仓 origin/HEAD 一致）。\n"
        "公司 PyPI：python -m pip install -i <公司PyPI> aiassitrequreimentdev\n"
        "离线 wheel：python -m pip install --no-index --find-links <wheel目录> aiassitrequreimentdev\n"
    )


def _fail(reason: str) -> None:
    raise SystemExit(install_help(reason))


def _run_pip(runner, cmd: list[str]) -> None:
    try:
        runner(cmd)
    except subprocess.CalledProcessError as exc:
        shown = " ".join(cmd)
        _fail(f"pip 安装失败（exit {exc.returncode}）：{shown}")


def ensure_package(*, plugin_root: Path, runner=subprocess.check_call) -> bool:
    if package_importable():
        return False
    repo = repo_root_from_plugin(plugin_root)
    if repo is not None:
        _run_pip(runner, [sys.executable, "-m", "pip", "install", "-e", str(repo)])
        return True
    remote = os.environ.get("AAD_GIT_REMOTE", "").strip()
    ref = os.environ.get("AAD_GIT_REF", "master").strip() or "master"
    if not remote:
        _fail(
            "aiassitrequreimentdev 未安装，且无法定位源仓。"
            "请设置 AAD_GIT_REMOTE，或在完整 clone 中使用本脚本。"
        )
    _run_pip(
        runner,
        [sys.executable, "-m", "pip", "install", git_requirement(remote, ref)],
    )
    return True


def main(argv: list[str] | None = None, exec_fn=os.execv) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if os.environ.get("AAD_BOOTSTRAPPED") == "1":
        if not package_importable():
            _fail("安装后仍无法 import aiassitrequreimentdev。")
    else:
        plugin_root = plugin_root_from(Path(__file__))
        if ensure_package(plugin_root=plugin_root):
            os.environ["AAD_BOOTSTRAPPED"] = "1"
            script = str(Path(__file__).resolve())
            try:
                exec_fn(sys.executable, [sys.executable, script, *argv])
            except OSError as exc:
                _fail(f"无法重启解释器以加载新安装的包：{exc}")
            return 0
    from aiassitrequreimentdev.__main__ import main as cli_main

    return int(cli_main(argv))


if __name__ == "__main__":
    raise SystemExit(main())
