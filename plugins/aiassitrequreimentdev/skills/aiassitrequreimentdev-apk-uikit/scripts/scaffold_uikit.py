"""
Copyright (C), 2019-2029, OPLUS Mobile Comm Corp., Ltd
File: scaffold_uikit.py
Description: Scaffold THEME/tokens/components/phone/showcase from palette.json
Author: limao2@Apps.Gallery
Date: 2026/11/16
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_json(path: Path | None, default):
    if not path or not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def scaffold(out: Path, prefix: str, package: str, app_name: str, palette: dict, pages: list) -> None:
    roles = palette.get("roles") or {}
    bg = roles.get("bg") or "#F0F5E7"
    surface = roles.get("surface") or "#FFFFFF"
    accent = roles.get("accent") or "#7BA23A"
    secondary = roles.get("secondary") or ["#F5A623", "#5B9BD5", "#E86A2A"]
    while len(secondary) < 3:
        secondary.append("#888888")

    p = prefix
    theme = f"""# {app_name} UI Kit

> 来源：真机 `{package}` ADB 抓取归纳（竞品/对标视觉参考，非官方 SDK 还原）。
> 生成：`aiassitrequreimentdev-apk-uikit` scaffold；须对照截图精修。

## 气质原则

| 原则 | 做法 |
| --- | --- |
| 画布 | 主背景 `{bg}` |
| 表面 | 卡片 `{surface}` |
| 主色 | Accent `{accent}` |
| 翻译防剧透 | `.{p}-blur-text` 高斯模糊，`.is-revealed` 揭晓 |
| 证据 | 上级目录 `screens/` / `previews/` / `PAGE_MAP.md` |

## 令牌摘要

- `--{p}-bg`: `{bg}`
- `--{p}-surface`: `{surface}`
- `--{p}-accent`: `{accent}`
- `--{p}-warn`: `{secondary[0]}`
- `--{p}-info`: `{secondary[1]}`
- `--{p}-warn-deep`: `{secondary[2]}`
- `--{p}-blur-spoiler`: `7px`

## 组件

`{p}-app` / `{p}-card` / `{p}-bottom-nav` / `{p}-blur-text` / `{p}-topbar` / `{p}-soft-btn`

## 抓取页（scaffold 时）

共 {len(pages)} 条 `pages_index` 记录；人工补全 PAGE_MAP 后精修 showcase。
"""
    write(out / "THEME.md", theme)

    tokens = f"""/*********************************************************************************
 ** Copyright (C), 2019-2029, OPLUS Mobile Comm Corp., Ltd
 ** All rights reserved.
 **
 ** File: - tokens.css
 ** Description: {app_name} UI kit tokens scaffolded from device capture
 ** Version: 1.0
 ** Date: 2026/11/16
 ** Author: limao2@Apps.Gallery
 *********************************************************************************/

:root,
html[data-{p}-theme="light"] {{
  --{p}-font: "PingFang SC", "SF Pro Text", "Segoe UI", "Noto Sans SC", system-ui, sans-serif;
  --{p}-fs-xs: 11px;
  --{p}-fs-sm: 13px;
  --{p}-fs-md: 15px;
  --{p}-fs-lg: 17px;
  --{p}-fs-title: 20px;
  --{p}-fs-display: 28px;
  --{p}-lh: 1.45;
  --{p}-fw-regular: 400;
  --{p}-fw-medium: 500;
  --{p}-fw-semibold: 600;
  --{p}-fw-bold: 700;
  --{p}-space-1: 4px;
  --{p}-space-2: 8px;
  --{p}-space-3: 12px;
  --{p}-space-4: 16px;
  --{p}-space-5: 20px;
  --{p}-space-6: 24px;
  --{p}-radius-sm: 8px;
  --{p}-radius-md: 12px;
  --{p}-radius-lg: 16px;
  --{p}-radius-card: 24px;
  --{p}-radius-pill: 999px;
  --{p}-phone-w: 360px;
  --{p}-phone-h: 740px;
  --{p}-phone-bezel: #2a2a2a;
  --{p}-ease: cubic-bezier(0.22, 1, 0.36, 1);
  --{p}-duration: 240ms;
  --{p}-blur-spoiler: 7px;
  --{p}-blur-spoiler-strong: 10px;
  --{p}-blur-spoiler-soft: 4px;
  --{p}-bg: {bg};
  --{p}-surface: {surface};
  --{p}-ink: #1c1c1e;
  --{p}-ink-secondary: #8e8e93;
  --{p}-ink-muted: #a8a8a0;
  --{p}-accent: {accent};
  --{p}-accent-soft: color-mix(in srgb, {accent} 22%, white);
  --{p}-accent-press: color-mix(in srgb, {accent} 80%, black);
  --{p}-warn: {secondary[0]};
  --{p}-warn-soft: color-mix(in srgb, {secondary[0]} 22%, white);
  --{p}-info: {secondary[1]};
  --{p}-info-soft: color-mix(in srgb, {secondary[1]} 22%, white);
  --{p}-warn-deep: {secondary[2]};
  --{p}-line: rgba(60, 60, 67, 0.12);
  --{p}-nav-idle: #9aa094;
  --{p}-shadow-card: 0 8px 24px rgba(60, 80, 40, 0.06);
  --{p}-scrim: rgba(0, 0, 0, 0.45);
  color-scheme: light;
}}
"""
    write(out / "tokens.css", tokens)

    components = f"""/*********************************************************************************
 ** Copyright (C), 2019-2029, OPLUS Mobile Comm Corp., Ltd
 ** File: - components.css
 ** Description: {app_name} scaffold components ({p}-*)
 *********************************************************************************/

* {{ box-sizing: border-box; }}

.{p}-app {{
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  background: var(--{p}-bg);
  color: var(--{p}-ink);
  font-family: var(--{p}-font);
  line-height: var(--{p}-lh);
  padding-top: 34px;
}}

.{p}-topbar {{
  min-height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  padding: 0 var(--{p}-space-4);
}}

.{p}-topbar__back {{
  position: absolute;
  left: var(--{p}-space-3);
  border: 0;
  background: transparent;
  color: var(--{p}-accent);
  font-size: 28px;
  cursor: pointer;
}}

.{p}-topbar__title {{
  font-size: var(--{p}-fs-lg);
  font-weight: var(--{p}-fw-medium);
}}

.{p}-scroll {{
  flex: 1;
  overflow: auto;
  padding: var(--{p}-space-3) var(--{p}-space-4) 88px;
}}

.{p}-card {{
  background: var(--{p}-surface);
  border-radius: var(--{p}-radius-card);
  box-shadow: var(--{p}-shadow-card);
  padding: var(--{p}-space-5);
}}

.{p}-card + .{p}-card {{ margin-top: var(--{p}-space-4); }}

.{p}-bottom-nav {{
  position: absolute;
  left: 0; right: 0; bottom: 0;
  height: 72px;
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  align-items: center;
  background: rgba(255,255,255,.92);
  backdrop-filter: blur(16px);
  border-top: 1px solid var(--{p}-line);
  padding-bottom: 8px;
}}

.{p}-bottom-nav button {{
  border: 0;
  background: transparent;
  color: var(--{p}-nav-idle);
  font-size: 11px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  cursor: pointer;
}}

.{p}-bottom-nav button.is-active {{ color: var(--{p}-accent); }}

.{p}-blur-text {{
  color: var(--{p}-ink-muted);
  filter: blur(var(--{p}-blur-spoiler));
  transition: filter var(--{p}-duration) var(--{p}-ease);
  user-select: none;
  cursor: pointer;
}}

.{p}-blur-text--soft {{ filter: blur(var(--{p}-blur-spoiler-soft)); }}
.{p}-blur-text--strong {{ filter: blur(var(--{p}-blur-spoiler-strong)); }}

.{p}-blur-text.is-revealed,
.{p}-blur-text[aria-pressed="true"] {{
  filter: none;
  cursor: text;
  color: var(--{p}-ink-secondary);
}}

.{p}-soft-btn {{
  border: 0;
  border-radius: var(--{p}-radius-md);
  padding: 12px 14px;
  font: inherit;
  font-weight: var(--{p}-fw-medium);
  cursor: pointer;
  background: var(--{p}-accent-soft);
  color: var(--{p}-ink);
}}

.{p}-label-pill {{
  display: inline-flex;
  padding: 3px 10px;
  border-radius: 8px;
  background: #1c1c1e;
  color: #fff;
  font-size: 11px;
  font-style: italic;
  font-weight: 700;
}}
"""
    write(out / "components.css", components)

    phone = f""".{p}-phone {{
  width: var(--{p}-phone-w);
  height: var(--{p}-phone-h);
  border-radius: 36px;
  background: var(--{p}-phone-bezel);
  padding: 10px;
  box-shadow: 0 20px 60px rgba(0,0,0,.25);
}}
.{p}-phone__screen {{
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: 28px;
  overflow: hidden;
  background: var(--{p}-bg);
}}
.{p}-phone__notch {{
  position: absolute;
  top: 8px;
  left: 50%;
  transform: translateX(-50%);
  width: 108px;
  height: 22px;
  border-radius: 14px;
  background: #111;
  z-index: 20;
  pointer-events: none;
}}
"""
    write(out / "phone.css", phone)

    page_names = [x.get("name", "") for x in pages[:12] if isinstance(x, dict)]
    pages_li = "".join(f"<li><code>{n}</code></li>" for n in page_names) or "<li>（尚无 pages_index）</li>"

    showcase = f"""<!doctype html>
<html lang="zh-CN" data-{p}-theme="light">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{app_name} UI Kit Showcase</title>
  <link rel="stylesheet" href="tokens.css" />
  <link rel="stylesheet" href="components.css" />
  <link rel="stylesheet" href="phone.css" />
  <style>
    body {{ margin:0; font-family: var(--{p}-font); background:#e7ecdf; }}
    .wrap {{ display:flex; gap:28px; padding:24px; flex-wrap:wrap; }}
    .side {{ background:#fff; border-radius:20px; padding:20px; max-width:320px; height:fit-content; }}
    .side h1 {{ margin:0 0 8px; font-size:20px; }}
    .side p {{ color:#666; font-size:13px; line-height:1.5; }}
  </style>
</head>
<body>
  <div class="wrap">
    <aside class="side">
      <h1>{app_name} UI Kit</h1>
      <p>包名 <code>{package}</code>。脚手架自动生成；请对照真机截图精修组件与 showcase。</p>
      <p>已抓页面样例：</p>
      <ul>{pages_li}</ul>
      <p>点击下方模糊文本可揭晓（防剧透模式）。</p>
    </aside>
    <div class="{p}-phone">
      <div class="{p}-phone__screen">
        <div class="{p}-phone__notch"></div>
        <div class="{p}-app">
          <div class="{p}-topbar"><div class="{p}-topbar__title">Home</div></div>
          <div class="{p}-scroll">
            <div class="{p}-card">
              <div style="font-size:22px;font-weight:700">Sample card</div>
              <div style="margin-top:8px;color:var(--{p}-ink-secondary)">Primary surface on eye-care canvas.</div>
              <div style="margin-top:14px">
                <span class="{p}-label-pill">translation</span>
                <div class="{p}-blur-text {p}-blur-text--strong" role="button" tabindex="0" aria-pressed="false" style="margin-top:8px">
                  这里是需要防剧透的翻译文本示例
                </div>
              </div>
              <button class="{p}-soft-btn" type="button" style="margin-top:16px">Primary action</button>
            </div>
          </div>
          <nav class="{p}-bottom-nav">
            <button class="is-active" type="button">Tab1</button>
            <button type="button">Tab2</button>
            <button type="button">Tab3</button>
            <button type="button">Tab4</button>
            <button type="button">Tab5</button>
          </nav>
        </div>
      </div>
    </div>
  </div>
  <script>
    document.querySelectorAll('.{p}-blur-text').forEach((el) => {{
      const toggle = () => {{
        const on = el.classList.toggle('is-revealed');
        el.setAttribute('aria-pressed', on ? 'true' : 'false');
      }};
      el.addEventListener('click', toggle);
      el.addEventListener('keydown', (e) => {{
        if (e.key === 'Enter' || e.key === ' ') {{ e.preventDefault(); toggle(); }}
      }});
    }});
  </script>
</body>
</html>
"""
    write(out / "showcase.html", showcase)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--prefix", default="pk")
    ap.add_argument("--palette", type=Path)
    ap.add_argument("--pages", type=Path)
    ap.add_argument("--package", required=True)
    ap.add_argument("--app-name", default="Captured App")
    args = ap.parse_args()

    palette = load_json(args.palette, {"roles": {}})
    pages = load_json(args.pages, [])
    scaffold(args.out, args.prefix, args.package, args.app_name, palette, pages)
    print(f"scaffolded {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
