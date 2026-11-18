"""
/*********************************************************************************
 ** Copyright (C), 2019-2029, OPLUS Mobile Comm Corp., Ltd
 ** All rights reserved.
 **
 ** File: - smoke_diagrams.py
 ** Description: 烟测复制 Archify 真图夹具（禁止空壳桩）
 ** Version: 1.0
 ** Date: 2026/11/18
 ** Author: limao2@Apps.Gallery
 **
 ** ------------------------------- Revision History: ----------------------------
 ** <author> <date> <version> <desc>
 ** ------------------------------------------------------------------------------
 ** limao2@Apps.Gallery 2026/11/18 1.0 INIT
 *********************************************************************************/
"""

from __future__ import annotations

import shutil
from pathlib import Path

FIXTURE_OUT = Path(__file__).resolve().parent / "fixtures" / "smoke-diagrams" / "out"

# stem → (min_html_bytes, min_png_bytes)
REQUIRED = {
    "vocab.L0.architecture": (100_000, 50_000),
    "vocab.L1.architecture": (100_000, 50_000),
    "vocab.review.workflow": (100_000, 50_000),
    "vocab.checkin.sequence": (100_000, 50_000),
    "vocab.review.class": (100_000, 50_000),
}


def assert_fixtures_real() -> None:
    missing: list[str] = []
    for stem, (min_html, min_png) in REQUIRED.items():
        html = FIXTURE_OUT / f"{stem}.html"
        png = FIXTURE_OUT / f"{stem}.png"
        if not html.is_file() or html.stat().st_size < min_html:
            missing.append(f"{html} (need real Archify html >= {min_html}B)")
        else:
            text = html.read_text(encoding="utf-8", errors="ignore")
            if "Smoke Archify stub" in text:
                missing.append(f"{html} still stub")
            if "archify" not in text.lower():
                missing.append(f"{html} missing archify provenance")
            if "archify-reader-contract" not in text:
                missing.append(f"{html} missing archify-reader-contract")
        if not png.is_file() or png.stat().st_size < min_png:
            missing.append(f"{png} (need real png >= {min_png}B)")
    if missing:
        raise AssertionError(
            "烟测真图夹具缺失或仍为假图，请先 Archify finalize + export_diagram_png：\n"
            + "\n".join(missing)
        )


def copy_diagram(dest_dir: Path, stem: str, *, as_name: str | None = None) -> tuple[Path, Path]:
    """复制夹具 html+png 到 dest_dir，可改名（如 req.L0.architecture）。"""
    assert_fixtures_real()
    name = as_name or stem
    dest_dir.mkdir(parents=True, exist_ok=True)
    src_html = FIXTURE_OUT / f"{stem}.html"
    src_png = FIXTURE_OUT / f"{stem}.png"
    dst_html = dest_dir / f"{name}.html"
    dst_png = dest_dir / f"{name}.png"
    shutil.copy2(src_html, dst_html)
    shutil.copy2(src_png, dst_png)
    return dst_html, dst_png


def install_feature_vocab_diagrams(diagrams_dir: Path) -> None:
    for stem in REQUIRED:
        copy_diagram(diagrams_dir, stem)


def install_req_architecture_diagrams(diagrams_dir: Path) -> None:
    copy_diagram(diagrams_dir, "vocab.L0.architecture", as_name="req.L0.architecture")
    copy_diagram(diagrams_dir, "vocab.L1.architecture", as_name="req.L1.architecture")
    copy_diagram(
        diagrams_dir, "vocab.review.workflow", as_name="req.overview.workflow"
    )
