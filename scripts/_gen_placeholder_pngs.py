# Copyright (C), 2019-2029, OPLUS Mobile Comm Corp., Ltd
# File: - _gen_placeholder_pngs.py
# Description: Generate gray PNG placeholders for Archify diagram templates.
# Version: 1.0
# Date: 2026/11/16
# Author: limao2@Apps.Gallery
from __future__ import annotations

import struct
import zlib
from pathlib import Path


def write_gray_png(
    path: Path,
    w: int = 480,
    h: int = 270,
    rgb: tuple[int, int, int] = (0xE5, 0xE7, 0xEB),
) -> None:
    r, g, b = rgb
    raw = b"".join(b"\x00" + bytes([r, g, b]) * w for _ in range(h))

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)
    print(path, len(png))


def main() -> None:
    base = Path("aiassitrequreimentdev/templates/feature/diagrams")
    names = [
        "PLACEHOLDER.1.class.png",
        "PLACEHOLDER.1.architecture.png",
        "PLACEHOLDER.1.erd.png",
        "PLACEHOLDER.2.architecture.png",
        "PLACEHOLDER.2.class.png",
        "PLACEHOLDER.3.architecture.png",
        "PLACEHOLDER.3.sequence.png",
        "PLACEHOLDER.4.workflow.png",
        "PLACEHOLDER.5.workflow.png",
        "PLACEHOLDER.6.workflow.png",
        "PLACEHOLDER.7.workflow.png",
    ]
    for name in names:
        write_gray_png(base / name)
    for path in base.glob("PLACEHOLDER.*.svg"):
        path.unlink()
        print("removed", path)


if __name__ == "__main__":
    main()
