"""
Copyright (C), 2019-2029, OPLUS Mobile Comm Corp., Ltd
File: capture_pages.py
Description: ADB crawl screenshots + UI dumps for painless app competitive UI kit
Author: limao2@Apps.Gallery
Date: 2026/11/16
"""

import hashlib
import json
import re
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
SCREENS.mkdir(exist_ok=True)
UI.mkdir(exist_ok=True)
PREVIEWS.mkdir(exist_ok=True)

BOUNDS_RE = re.compile(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]")


def adb(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["adb", *args], capture_output=True, text=True, encoding="utf-8", errors="replace")


def adb_bin(*args: str) -> bytes:
    return subprocess.check_output(["adb", *args])


def parse_bounds(s: str):
    m = BOUNDS_RE.fullmatch(s or "")
    if not m:
        return None
    x1, y1, x2, y2 = map(int, m.groups())
    return x1, y1, x2, y2, (x1 + x2) // 2, (y1 + y2) // 2


def tap(x: int, y: int, wait: float = 1.2):
    adb("shell", "input", "tap", str(x), str(y))
    time.sleep(wait)


def back(wait: float = 1.0):
    adb("shell", "input", "keyevent", "4")
    time.sleep(wait)


def swipe(x1, y1, x2, y2, ms=400, wait=1.0):
    adb("shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(ms))
    time.sleep(wait)


def current_focus() -> str:
    r = adb("shell", "dumpsys", "window")
    for line in r.stdout.splitlines():
        if "mCurrentFocus" in line or "mFocusedApp" in line:
            return line.strip()
    return ""


def dump_ui(name: str):
    adb("shell", "uiautomator", "dump", "/sdcard/uidump.xml")
    dest = UI / f"{name}.xml"
    adb("pull", "/sdcard/uidump.xml", str(dest))
    return dest


def capture(name: str):
    png = SCREENS / f"{name}.png"
    data = adb_bin("exec-out", "screencap", "-p")
    png.write_bytes(data)
    img = Image.open(png)
    preview = PREVIEWS / f"{name}.jpg"
    p = img.resize((max(1, img.width // 3), max(1, img.height // 3)), Image.Resampling.LANCZOS)
    p.convert("RGB").save(preview, quality=82)
    xml = dump_ui(name)
    focus = current_focus()
    meta = {
        "name": name,
        "focus": focus,
        "size": list(img.size),
        "png": str(png.name),
        "preview": str(preview.name),
        "xml": str(xml.name),
        "sha1": hashlib.sha1(data).hexdigest()[:12],
    }
    print(json.dumps(meta, ensure_ascii=False))
    return meta, xml


def iter_nodes(xml_path: Path):
    root = ET.parse(xml_path).getroot()
    for n in root.iter("node"):
        yield n.attrib


def find_by_id(xml_path: Path, rid: str):
    for a in iter_nodes(xml_path):
        if a.get("resource-id") == rid:
            return a
    return None


def find_by_text(xml_path: Path, text: str, exact=True):
    for a in iter_nodes(xml_path):
        t = a.get("text") or ""
        if exact and t == text:
            return a
        if not exact and text in t:
            return a
    return None


def tap_node(attrib, wait=1.2):
    b = parse_bounds(attrib.get("bounds", ""))
    if not b:
        return False
    tap(b[4], b[5], wait=wait)
    return True


def ensure_app():
    focus = current_focus()
    if PKG not in focus:
        adb("shell", "monkey", "-p", PKG, "-c", "android.intent.category.LAUNCHER", "1")
        time.sleep(2.5)


def go_tab(xml_path: Path, tab_id: str):
    n = find_by_id(xml_path, tab_id)
    if n:
        tap_node(n, wait=1.5)
        return True
    return False


def main():
    ensure_app()
    pages = []

    # Home / 单词
    m, xml = capture("01_tab_words")
    pages.append(m)

    # Open tag (word chip)
    tag = find_by_id(xml, f"{PKG}:id/tag_tv")
    if tag:
        tap_node(tag, wait=1.8)
        m, xml2 = capture("02_word_tag_or_detail")
        pages.append(m)
        back(1.2)

    # More menu
    m0, xml = capture("01b_words_refresh") if False else (None, dump_ui("tmp_home"))
    # Re-dump current
    ensure_app()
    m, xml = capture("03_words_before_more")
    pages.append(m)
    more = find_by_id(xml, f"{PKG}:id/top_more_iv")
    if more:
        tap_node(more, wait=1.2)
        m, xml = capture("04_words_more_menu")
        pages.append(m)
        back(1.0)

    # Side buttons: share / speak / chart
    m, xml = capture("05_words_base")
    pages.append(m)
    for btn_id, name in [
        (f"{PKG}:id/share_btn", "06_share"),
        (f"{PKG}:id/speak_btn", "07_speak"),
        (f"{PKG}:id/chart_btn", "08_chart_from_home"),
    ]:
        n = find_by_id(xml, btn_id)
        if n:
            tap_node(n, wait=1.5)
            m2, _ = capture(name)
            pages.append(m2)
            back(1.2)
            # refresh base xml
            _, xml = capture(f"{name}_back")
            pages.append({"name": f"{name}_back", "note": "return"})

    # Tabs
    tab_map = [
        (f"{PKG}:id/tab_read", "10_tab_read"),
        (f"{PKG}:id/tab_search", "11_tab_search"),
        (f"{PKG}:id/tab_stat", "12_tab_stat"),
        (f"{PKG}:id/tab_setting", "13_tab_setting"),
        (f"{PKG}:id/tab_home", "14_tab_home_again"),
    ]
    _, xml = capture("09_before_tabs")
    for rid, name in tab_map:
        if go_tab(xml, rid):
            m, xml = capture(name)
            pages.append(m)
        else:
            print(f"missing tab {rid}")

    # Explore setting list items
    if "13_tab_setting" in [p.get("name") for p in pages]:
        setting_xml = UI / "13_tab_setting.xml"
        # click first few clickable TextViews with Chinese labels
        clicked = 0
        for a in iter_nodes(setting_xml):
            if a.get("clickable") != "true":
                continue
            text = (a.get("text") or "").strip()
            desc = (a.get("content-desc") or "").strip()
            label = text or desc
            if not label or len(label) > 20:
                continue
            if label in {"设置", "单词", "阅读", "搜索", "图表"}:
                continue
            safe = re.sub(r"[^\w\u4e00-\u9fff]+", "_", label)[:24]
            tap_node(a, wait=1.5)
            m, _ = capture(f"15_setting_{clicked:02d}_{safe}")
            pages.append(m)
            back(1.2)
            clicked += 1
            if clicked >= 8:
                break
            # refresh setting page
            go_tab(dump_ui("tmp_set"), f"{PKG}:id/tab_setting")
            time.sleep(0.8)
            setting_xml = dump_ui("tmp_set2")

    # Explore read tab items
    go_tab(dump_ui("tmp_nav"), f"{PKG}:id/tab_read")
    time.sleep(1.0)
    m, read_xml = capture("20_read_explore")
    pages.append(m)
    clicked = 0
    for a in iter_nodes(read_xml):
        if a.get("clickable") != "true":
            continue
        text = (a.get("text") or "").strip()
        if not text or len(text) < 2:
            continue
        if text in {"阅读", "单词", "搜索", "图表", "设置"}:
            continue
        # avoid huge article bodies
        if len(text) > 30:
            continue
        safe = re.sub(r"[^\w\u4e00-\u9fff]+", "_", text)[:24]
        tap_node(a, wait=1.6)
        m2, _ = capture(f"21_read_{clicked:02d}_{safe}")
        pages.append(m2)
        back(1.2)
        clicked += 1
        if clicked >= 6:
            break
        go_tab(dump_ui("tmp_read"), f"{PKG}:id/tab_read")
        time.sleep(0.8)
        _, read_xml = capture(f"20_read_refresh_{clicked}")

    # Search explore
    go_tab(dump_ui("tmp_nav2"), f"{PKG}:id/tab_search")
    time.sleep(1.0)
    m, search_xml = capture("30_search_explore")
    pages.append(m)
    # tap first suggestion / history if any
    clicked = 0
    for a in iter_nodes(search_xml):
        if a.get("clickable") != "true":
            continue
        text = (a.get("text") or "").strip()
        if not text or text in {"搜索", "单词", "阅读", "图表", "设置"}:
            continue
        if len(text) > 24:
            continue
        safe = re.sub(r"[^\w\u4e00-\u9fffA-Za-z]+", "_", text)[:24]
        tap_node(a, wait=1.5)
        m2, _ = capture(f"31_search_{clicked:02d}_{safe}")
        pages.append(m2)
        back(1.2)
        clicked += 1
        if clicked >= 5:
            break
        go_tab(dump_ui("tmp_search"), f"{PKG}:id/tab_search")
        time.sleep(0.8)
        _, search_xml = capture(f"30_search_refresh_{clicked}")

    # Stat explore
    go_tab(dump_ui("tmp_nav3"), f"{PKG}:id/tab_stat")
    time.sleep(1.0)
    m, stat_xml = capture("40_stat_explore")
    pages.append(m)
    clicked = 0
    for a in iter_nodes(stat_xml):
        if a.get("clickable") != "true":
            continue
        text = (a.get("text") or a.get("content-desc") or "").strip()
        if not text or text in {"图表", "单词", "阅读", "搜索", "设置"}:
            continue
        if len(text) > 24:
            continue
        safe = re.sub(r"[^\w\u4e00-\u9fffA-Za-z]+", "_", text)[:24]
        tap_node(a, wait=1.5)
        m2, _ = capture(f"41_stat_{clicked:02d}_{safe}")
        pages.append(m2)
        back(1.2)
        clicked += 1
        if clicked >= 5:
            break
        go_tab(dump_ui("tmp_stat"), f"{PKG}:id/tab_stat")
        time.sleep(0.8)
        _, stat_xml = capture(f"40_stat_refresh_{clicked}")

    (OUT / "pages_index.json").write_text(
        json.dumps(pages, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"DONE pages={len(pages)}")


if __name__ == "__main__":
    main()
