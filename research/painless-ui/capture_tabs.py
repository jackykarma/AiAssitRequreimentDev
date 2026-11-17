"""
Copyright (C), 2019-2029, OPLUS Mobile Comm Corp., Ltd
File: capture_tabs.py
Description: Stable tab/subpage ADB capture for painless UI kit research
Author: limao2@Apps.Gallery
Date: 2026/11/16
"""

import hashlib
import json
import subprocess
import time
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image

PKG = "tech.xiangzi.painless"
OUT = Path(__file__).resolve().parent
SCREENS = OUT / "screens"
UI = OUT / "ui"
PREVIEWS = OUT / "previews"
for d in (SCREENS, UI, PREVIEWS):
    d.mkdir(exist_ok=True)

# Physical 1440x3168 — bottom nav centers from first dump
TABS = {
    "words": (144, 2984),
    "read": (432, 2984),
    "search": (720, 2984),
    "stat": (1008, 2984),
    "setting": (1296, 2984),
}


def adb(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["adb", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def adb_bin(*args: str) -> bytes:
    return subprocess.check_output(["adb", *args])


def wait_device(timeout=60):
    t0 = time.time()
    while time.time() - t0 < timeout:
        r = adb("devices")
        for line in r.stdout.splitlines()[1:]:
            if "\tdevice" in line and "unauthorized" not in line:
                return True
        time.sleep(2)
    return False


def focus() -> str:
    r = adb("shell", "dumpsys", "window")
    for line in r.stdout.splitlines():
        if "mCurrentFocus=" in line:
            return line.strip()
    return ""


def assert_painless(where: str = ""):
    """Hard stop if foreground left tech.xiangzi.painless — never tap other apps."""
    f = focus()
    if PKG not in f:
        raise RuntimeError(f"focus left {PKG} at {where}: {f}")


def tap(x, y, wait=1.2):
    assert_painless(f"before tap ({x},{y})")
    adb("shell", "input", "tap", str(x), str(y))
    time.sleep(wait)
    # after tap: if somehow left package, abort immediately
    f = focus()
    if PKG not in f and "PopupWindow" not in f:
        raise RuntimeError(f"tap escaped {PKG}: {f}")


def back(n=1, wait=0.8):
    for _ in range(n):
        adb("shell", "input", "keyevent", "4")
        time.sleep(wait)


def swipe(x1, y1, x2, y2, ms=450, wait=1.0):
    adb("shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(ms))
    time.sleep(wait)


def ensure_app():
    f = focus()
    if PKG not in f:
        adb("shell", "monkey", "-p", PKG, "-c", "android.intent.category.LAUNCHER", "1")
        time.sleep(2.5)
    # dismiss popup overlays
    for _ in range(3):
        f = focus()
        if "PopupWindow" in f or "Dialog" in f:
            back(1, 0.6)
        else:
            break


def capture(name: str):
    data = adb_bin("exec-out", "screencap", "-p")
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        data = data.replace(b"\r\n", b"\n")
    png = SCREENS / f"{name}.png"
    png.write_bytes(data)
    img = Image.open(png)
    prev = PREVIEWS / f"{name}.jpg"
    img.resize((img.width // 3, img.height // 3), Image.Resampling.LANCZOS).convert("RGB").save(
        prev, quality=82
    )
    adb("shell", "uiautomator", "dump", "/sdcard/uidump.xml")
    xml = UI / f"{name}.xml"
    adb("pull", "/sdcard/uidump.xml", str(xml))
    meta = {
        "name": name,
        "focus": focus(),
        "size": list(img.size),
        "sha1": hashlib.sha1(data).hexdigest()[:12],
    }
    print(json.dumps(meta, ensure_ascii=False))
    return meta, xml


def texts(xml: Path, limit=12):
    try:
        root = ET.parse(xml).getroot()
    except Exception:
        return []
    out = []
    for n in root.iter("node"):
        t = (n.attrib.get("text") or "").strip()
        d = (n.attrib.get("content-desc") or "").strip()
        if t:
            out.append(t[:40])
        elif d:
            out.append(f"[{d[:30]}]")
        if len(out) >= limit:
            break
    return out


def find_clickable_labels(xml: Path):
    root = ET.parse(xml).getroot()
    items = []
    for n in root.iter("node"):
        if n.attrib.get("clickable") != "true":
            continue
        t = (n.attrib.get("text") or "").strip()
        d = (n.attrib.get("content-desc") or "").strip()
        rid = n.attrib.get("resource-id") or ""
        b = n.attrib.get("bounds") or ""
        label = t or d
        if not label:
            continue
        items.append((label, rid, b))
    return items


def bounds_center(b: str):
    import re

    m = re.fullmatch(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", b)
    if not m:
        return None
    x1, y1, x2, y2 = map(int, m.groups())
    return (x1 + x2) // 2, (y1 + y2) // 2


def go_tab(name: str):
    ensure_app()
    # ensure on main with bottom nav — back until MainActivity or max 4
    for _ in range(4):
        f = focus()
        if "MainActivity" in f and "PopupWindow" not in f:
            break
        back(1, 0.7)
    ensure_app()
    x, y = TABS[name]
    tap(x, y, wait=1.6)


def main():
    if not wait_device(90):
        raise SystemExit("device not authorized — please Allow USB debugging on phone")

    ensure_app()
    pages = []

    # dismiss leftover popup
    back(2, 0.5)
    ensure_app()

    plan = [
        ("50_tab_words", "words", None),
        ("51_tab_read", "read", None),
        ("52_tab_search", "search", None),
        ("53_tab_stat", "stat", None),
        ("54_tab_setting", "setting", None),
    ]

    for name, tab, _ in plan:
        go_tab(tab)
        m, xml = capture(name)
        m["texts"] = texts(xml)
        pages.append(m)

    # Home word chip -> popup/detail
    go_tab("words")
    m, xml = capture("60_words_clean")
    pages.append(m)
    # tap tag area approx from dump [200,1953][506,2073]
    tap(353, 2013, wait=1.5)
    m, xml = capture("61_words_tag_tap")
    m["texts"] = texts(xml)
    pages.append(m)
    # if popup, try open detail via content tap center
    tap(720, 1400, wait=1.5)
    m, xml = capture("62_word_detail_or_same")
    m["texts"] = texts(xml)
    pages.append(m)
    back(2, 0.8)

    # Read: open first article card area
    go_tab("read")
    m, xml = capture("70_read_list")
    m["texts"] = texts(xml)
    pages.append(m)
    # tap first list-ish area
    tap(720, 900, wait=1.8)
    m, xml = capture("71_read_article")
    m["texts"] = texts(xml)
    pages.append(m)
    # try floating tools if present — bottom tool card approx
    for label, x, y in [("朗读", 420, 2700), ("生词表", 720, 2700), ("翻译", 1020, 2700)]:
        tap(x, y, wait=1.2)
        m2, xml2 = capture(f"72_read_tool_{label}")
        m2["texts"] = texts(xml2)
        pages.append(m2)
        # if navigated away from article, reopen
        if "ArticleDetail" not in m2.get("focus", "") and "阅读" not in "".join(m2.get("texts", [])):
            back(1, 0.8)
    back(2, 0.8)

    # Search: open search input + walkman settings
    go_tab("search")
    m, xml = capture("80_search")
    m["texts"] = texts(xml)
    pages.append(m)
    # tap search input area top
    tap(720, 400, wait=1.2)
    m, xml = capture("81_search_input")
    m["texts"] = texts(xml)
    pages.append(m)
    back(1, 0.8)
    go_tab("search")
    # more button on player
    tap(1300, 700, wait=1.2)
    m, xml = capture("82_search_player_more")
    m["texts"] = texts(xml)
    pages.append(m)
    back(2, 0.8)

    # Stat deep
    go_tab("stat")
    m, xml = capture("90_stat")
    m["texts"] = texts(xml)
    pages.append(m)
    tap(720, 1100, wait=1.4)
    m, xml = capture("91_stat_tap")
    m["texts"] = texts(xml)
    pages.append(m)
    back(1, 0.8)

    # Setting: click first several rows by y scan
    go_tab("setting")
    m, xml = capture("100_setting")
    m["texts"] = texts(xml, 30)
    pages.append(m)
    labels = find_clickable_labels(xml)
    clicked = 0
    seen = set()
    skip = {"设置", "单词", "阅读", "搜索", "图表"}
    for label, rid, b in labels:
        if label in skip or label in seen:
            continue
        if len(label) > 18:
            continue
        c = bounds_center(b)
        if not c:
            continue
        # only mid-page rows
        if c[1] < 350 or c[1] > 2700:
            continue
        seen.add(label)
        tap(c[0], c[1], wait=1.4)
        safe = "".join(ch if ch.isalnum() or "\u4e00" <= ch <= "\u9fff" else "_" for ch in label)[:20]
        m2, xml2 = capture(f"101_setting_{clicked:02d}_{safe}")
        m2["texts"] = texts(xml2)
        pages.append(m2)
        back(1, 1.0)
        go_tab("setting")
        time.sleep(0.5)
        clicked += 1
        if clicked >= 10:
            break

    # scroll setting for more
    go_tab("setting")
    swipe(720, 2200, 720, 900, wait=1.0)
    m, xml = capture("102_setting_scrolled")
    m["texts"] = texts(xml, 30)
    pages.append(m)

    (OUT / "pages_index.json").write_text(json.dumps(pages, ensure_ascii=False, indent=2), encoding="utf-8")
    print("DONE", len(pages))


if __name__ == "__main__":
    main()
