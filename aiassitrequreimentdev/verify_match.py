"""
/*********************************************************************************
 ** Copyright (C), 2019-2029, OPLUS Mobile Comm Corp., Ltd
 ** All rights reserved.
 **
 ** File: - verify_match.py
 ** Description: 验收命令同源比对与假绿模式识别（门禁与执行器共用，避免循环依赖）。
 ** Version: 1.0
 ** Date: 2026/11/20
 ** Author: limao2@Apps.Gallery
 *********************************************************************************/
"""

from __future__ import annotations

import hashlib
import re

_FAKE_GREEN_EXACT = {
    "true",
    ":",
    "exit 0",
    "exit 0;",
    "echo ok",
    "echo pass",
    "echo success",
    "echo done",
    "pwd",
}
_FAKE_GREEN_RE = re.compile(r"^(?:true|:\s*|exit\s+0|echo\b[^&|;]*)$", re.IGNORECASE)
_SHELL_CHAIN_RE = re.compile(
    r"(?:&&|\|\||;|\||>|>>)\s*(?:true|:\s*|exit\s+0)\s*$", re.IGNORECASE
)
TODO_VERIFY = "TODO_SET_VERIFY"


def is_fake_green(command: object) -> bool:
    """识别明显空转命令；保守策略，只拦确定无断言价值的模式。"""
    if not isinstance(command, str):
        return True
    normalized = command.strip().lower()
    if not normalized or normalized in _FAKE_GREEN_EXACT:
        return True
    if _FAKE_GREEN_RE.match(normalized):
        return True
    return bool(_SHELL_CHAIN_RE.search(normalized))


def normalize_command(text: object) -> str:
    if not isinstance(text, str):
        return ""
    return re.sub(r"\s+", " ", text).strip()


def commands_match(command: object, verify: object) -> bool:
    """同源判定：command 须与 A* 的 verify 一致或仅为其参数扩展。"""
    cmd = normalize_command(command)
    ver = normalize_command(verify)
    if not cmd or not ver or ver == TODO_VERIFY:
        return False
    if cmd == ver:
        return True
    return cmd.startswith(ver + " ")


def verify_hash(verify: object) -> str:
    return hashlib.sha256(normalize_command(verify).encode("utf-8")).hexdigest()
