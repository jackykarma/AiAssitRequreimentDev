"""
Copyright (C), 2019-2029, OPLUS Mobile Comm Corp., Ltd
File: capture_app_ui.py
Description: Package-locked ADB UI crawl → screens/ui/previews/pages_index.json
Author: limao2@Apps.Gallery
Date: 2026/11/16
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import time
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image

BOUNDS_RE = re.compile(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]")
SKIP_LABELS = {
    "允许",
    "拒绝",
    "取消",
    "确定",
    "关闭",
    "同意并继续",
}


def adb(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["adb", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def adb_bin(*args: str) -> bytes:
    return subprocess.check_output(["adb", *args])


def wait_device(timeout: int = 90) -> bool:
    t0 = time.time()
    while time.time() - t0 < timeout:
        for line in adb("devices").stdout.splitlines()[1:]:
            if "\tdevice" in line and "unauthorized" not in line:
                return True
        time.sleep(2)
    return False


def focus() -> str:
    for line in adb("shell", "dumpsys", "window").stdout.splitlines():
        if "mCurrentFocus=" in line:
            return line.strip()
    return ""


def focused_app() -> str:
    for line in adb("shell", "dumpsys", "window").stdout.splitlines():
        if "mFocusedApp=" in line:
            return line.strip()
    return ""


def package_in_foreground(package: str) -> bool:
    blob = focus() + "\n" + focused_app()
    return package in blob


def assert_package(package: str, where: str = "") -> None:
    if not package_in_foreground(package):
        raise RuntimeError(
            f"focus left {package} at {where}: focus={focus()!r} app={focused_app()!r}"
        )


def parse_bounds(s: str):
    m = BOUNDS_RE.fullmatch(s or "")
    if not m:
        return None
    x1, y1, x2, y2 = map(int, m.groups())
    return x1, y1, x2, y2, (x1 + x2) // 2, (y1 + y2) // 2


def tap(package: str, x: int, y: int, wait: float = 1.2) -> None:
    assert_package(package, f"before tap ({x},{y})")
    adb("shell", "input", "tap", str(x), str(y))
    time.sleep(wait)
    f = focus()
    if package not in f and "PopupWindow" not in f and "Dialog" not in f:
        raise RuntimeError(f"tap escaped {package}: {f}")


def back(n: int = 1, wait: float = 0.7) -> None:
    for _ in range(n):
        adb("shell", "input", "keyevent", "4")
        time.sleep(wait)


def ensure_app(package: str) -> None:
    if package_in_foreground(package):
        # dismiss foreign overlays only if still our package underneath
        return
    adb("shell", "monkey", "-p", package, "-c", "android.intent.category.LAUNCHER", "1")
    time.sleep(2.5)
    assert_package(package, "after launch")


def capture(package: str, out: Path, name: str) -> dict:
    assert_package(package, f"capture {name}")
    data = adb_bin("exec-out", "screencap", "-p")
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        data = data.replace(b"\r\n", b"\n")
    screens = out / "screens"
    previews = out / "previews"
    ui = out / "ui"
    for d in (screens, previews, ui):
        d.mkdir(parents=True, exist_ok=True)
    png = screens / f"{name}.png"
    png.write_bytes(data)
    img = Image.open(png)
    prev = previews / f"{name}.jpg"
    img.resize((max(1, img.width // 3), max(1, img.height // 3)), Image.Resampling.LANCZOS).convert(
        "RGB"
    ).save(prev, quality=82)
    adb("shell", "uiautomator", "dump", "/sdcard/uidump_apk_uikit.xml")
    xml = ui / f"{name}.xml"
    adb("pull", "/sdcard/uidump_apk_uikit.xml", str(xml))
    meta = {
        "name": name,
        "focus": focus(),
        "focusedApp": focused_app(),
        "packageOk": package_in_foreground(package),
        "size": list(img.size),
        "sha1": hashlib.sha1(data).hexdigest()[:12],
        "png": png.name,
        "preview": prev.name,
        "xml": xml.name,
    }
    print(json.dumps(meta, ensure_ascii=False))
    return meta


def iter_nodes(xml_path: Path):
    root = ET.parse(xml_path).getroot()
    for n in root.iter("node"):
        yield n.attrib


def node_label(a: dict) -> str:
    return ((a.get("text") or "").strip() or (a.get("content-desc") or "").strip())[:40]


def discover_tabs(xml_path: Path, package: str) -> list[dict]:
    """Find bottom-nav like items: content-desc or *tab* resource-ids near bottom."""
    tabs = []
    screen_h = 0
    for a in iter_nodes(xml_path):
        b = parse_bounds(a.get("bounds", ""))
        if b:
            screen_h = max(screen_h, b[3])
    if screen_h <= 0:
        screen_h = 3000
    bottom = screen_h * 0.88
    for a in iter_nodes(xml_path):
        rid = a.get("resource-id") or ""
        desc = (a.get("content-desc") or "").strip()
        click = a.get("clickable") == "true"
        b = parse_bounds(a.get("bounds", ""))
        if not b or b[5] < bottom:
            continue
        if package and rid and not rid.startswith(package) and ":id/tab" not in rid:
            # still allow Material nav containers without package prefix rarely
            pass
        if "tab" in rid.lower() or desc:
            if not click and "tab" not in rid.lower():
                continue
            if not click:
                # parent may be clickable; still record center for tap attempt via clickable ancestor later
                pass
            tabs.append(
                {
                    "label": desc or rid.split("/")[-1],
                    "resourceId": rid,
                    "cx": b[4],
                    "cy": b[5],
                    "clickable": click,
                }
            )
    # dedupe by x bucket
    tabs.sort(key=lambda t: t["cx"])
    dedup = []
    for t in tabs:
        if dedup and abs(dedup[-1]["cx"] - t["cx"]) < 40:
            continue
        dedup.append(t)
    return dedup[:8]


def discover_clickables(xml_path: Path, package: str, screen_h: int) -> list[dict]:
    items = []
    for a in iter_nodes(xml_path):
        if a.get("clickable") != "true":
            continue
        label = node_label(a)
        rid = a.get("resource-id") or ""
        if rid and not rid.startswith(package) and not rid.startswith("android:id/"):
            # skip foreign ids
            if package not in rid:
                continue
        b = parse_bounds(a.get("bounds", ""))
        if not b:
            continue
        # avoid system nav / status
        if b[5] < screen_h * 0.08 or b[5] > screen_h * 0.96:
            continue
        if label in SKIP_LABELS:
            continue
        area = (b[2] - b[0]) * (b[3] - b[1])
        if area < 80 * 80:
            continue
        items.append({"label": label or rid.split("/")[-1] or "anon", "rid": rid, "cx": b[4], "cy": b[5], "area": area})
    # prefer mid-size controls
    items.sort(key=lambda x: abs(x["area"] - 200 * 200))
    return items


def safe_name(s: str) -> str:
    s = re.sub(r"[^\w\u4e00-\u9fff]+", "_", s).strip("_")
    return (s or "page")[:32]


def crawl(package: str, out: Path, max_pages: int) -> list[dict]:
    ensure_app(package)
    # clear popups belonging to app
    for _ in range(2):
        if "PopupWindow" in focus():
            back(1)
        else:
            break
    ensure_app(package)

    pages: list[dict] = []
    seen_sha: set[str] = set()

    meta = capture(package, out, "00_home")
    pages.append(meta)
    seen_sha.add(meta["sha1"])
    xml = out / "ui" / "00_home.xml"

    # estimate screen height
    screen_h = meta["size"][1]

    tabs = discover_tabs(xml, package)
    (out / "discovered_tabs.json").write_text(json.dumps(tabs, ensure_ascii=False, indent=2), encoding="utf-8")

    for i, tab in enumerate(tabs):
        if len(pages) >= max_pages:
            break
        ensure_app(package)
        # return to main if possible
        for _ in range(3):
            if package_in_foreground(package) and "MainActivity" in focused_app():
                break
            if package_in_foreground(package):
                back(1)
            else:
                ensure_app(package)
                break
        tap(package, tab["cx"], tab["cy"], wait=1.5)
        name = f"1{i:02d}_tab_{safe_name(tab['label'])}"
        m = capture(package, out, name)
        if m["sha1"] in seen_sha:
            m["note"] = "duplicate_hash"
        else:
            seen_sha.add(m["sha1"])
        pages.append(m)

        # one-level drill: up to 3 in-tab clickables
        tab_xml = out / "ui" / f"{name}.xml"
        clicks = discover_clickables(tab_xml, package, screen_h)
        drilled = 0
        for c in clicks:
            if len(pages) >= max_pages or drilled >= 3:
                break
            if c["label"] in {t["label"] for t in tabs}:
                continue
            tap(package, c["cx"], c["cy"], wait=1.4)
            if not package_in_foreground(package) and "PopupWindow" not in focus():
                raise RuntimeError(f"left package after clicking {c}")
            child = f"2{i:02d}_{drilled:02d}_{safe_name(c['label'])}"
            m2 = capture(package, out, child)
            pages.append(m2)
            seen_sha.add(m2["sha1"])
            drilled += 1
            back(1, 0.9)
            # reselect tab
            if package_in_foreground(package):
                tap(package, tab["cx"], tab["cy"], wait=1.0)

    (out / "pages_index.json").write_text(json.dumps(pages, ensure_ascii=False, indent=2), encoding="utf-8")
    return pages


def capture_once(package: str, out: Path, name: str) -> dict:
    ensure_app(package)
    pages_path = out / "pages_index.json"
    pages = []
    if pages_path.exists():
        pages = json.loads(pages_path.read_text(encoding="utf-8"))
    m = capture(package, out, name)
    pages.append(m)
    pages_path.write_text(json.dumps(pages, ensure_ascii=False, indent=2), encoding="utf-8")
    return m


def main() -> int:
    ap = argparse.ArgumentParser(description="ADB crawl UI for one Android package → ui research folder")
    ap.add_argument("--package", required=True)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--max-pages", type=int, default=40)
    ap.add_argument("--once", default="", help="capture only current foreground page with this name")
    args = ap.parse_args()

    if not wait_device():
        raise SystemExit("adb device not ready / unauthorized — allow USB debugging on phone")

    args.out.mkdir(parents=True, exist_ok=True)
    # write package meta
    ver = ""
    for line in adb("shell", "dumpsys", "package", args.package).stdout.splitlines():
        if "versionName=" in line:
            ver = line.strip()
            break
    (args.out / "app_meta.json").write_text(
        json.dumps({"package": args.package, "versionLine": ver}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    if args.once:
        capture_once(args.package, args.out, args.once)
    else:
        pages = crawl(args.package, args.out, args.max_pages)
        print(f"DONE pages={len(pages)} out={args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
