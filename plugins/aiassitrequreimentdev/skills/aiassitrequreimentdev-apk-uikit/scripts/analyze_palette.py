"""
Copyright (C), 2019-2029, OPLUS Mobile Comm Corp., Ltd
File: analyze_palette.py
Description: Cluster dominant colors from captured screenshots → palette.json
Author: limao2@Apps.Gallery
Date: 2026/11/16
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from PIL import Image


def quant(c: tuple[int, int, int], step: int = 12) -> tuple[int, int, int]:
    return tuple((x // step) * step for x in c)  # type: ignore[return-value]


def is_near_white(c: tuple[int, int, int]) -> bool:
    return sum(c) >= 720


def is_near_black(c: tuple[int, int, int]) -> bool:
    return sum(c) <= 60


def sample_screen(path: Path) -> list[tuple[tuple[int, int, int], int]]:
    img = Image.open(path).convert("RGB")
    w, h = img.size
    crop = img.crop((int(w * 0.06), int(h * 0.08), int(w * 0.94), int(h * 0.9)))
    small = crop.resize((100, 180), Image.Resampling.LANCZOS)
    cnt: Counter[tuple[int, int, int]] = Counter()
    for p in small.getdata():
        q = quant(p)
        if is_near_black(q):
            continue
        cnt[q] += 1
    return cnt.most_common(12)


def hex_of(c: tuple[int, int, int]) -> str:
    return f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}"


def guess_roles(colors: list[tuple[tuple[int, int, int], int]]) -> dict:
    """Heuristic roles for kit tokens."""
    if not colors:
        return {}
    # bg: most common non-pure-white-ish pastel
    bg = colors[0][0]
    for c, _ in colors:
        if not is_near_white(c):
            bg = c
            break
    surface = (255, 255, 255)
    # accent: saturated-ish mid brightness
    accent = None
    for c, _ in colors:
        r, g, b = c
        mx, mn = max(c), min(c)
        if mx - mn >= 40 and 80 < (r + g + b) / 3 < 200:
            accent = c
            break
    if accent is None:
        accent = (80, 160, 60)
    secondary = []
    for c, _ in colors:
        if c == bg or c == accent:
            continue
        mx, mn = max(c), min(c)
        if mx - mn >= 30 and not is_near_white(c):
            secondary.append(c)
        if len(secondary) >= 3:
            break
    return {
        "bg": hex_of(bg),
        "surface": hex_of(surface),
        "accent": hex_of(accent),
        "secondary": [hex_of(c) for c in secondary],
        "rawTop": [{"hex": hex_of(c), "n": n} for c, n in colors[:8]],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--screens", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    files = sorted(args.screens.glob("*.png"))
    per_file = {}
    merged: Counter[tuple[int, int, int]] = Counter()
    for f in files:
        try:
            top = sample_screen(f)
        except Exception as e:  # noqa: BLE001
            per_file[f.name] = {"error": str(e)}
            continue
        per_file[f.name] = [{"hex": hex_of(c), "n": n} for c, n in top]
        for c, n in top:
            merged[c] += n

    roles = guess_roles(merged.most_common(16))
    payload = {"roles": roles, "perFile": per_file, "screenCount": len(files)}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(roles, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
