"""Sync plugins/.../skills -> .cursor/skills (single source of truth)."""
from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path

PLUGIN_SKILLS = Path("plugins/aiassitrequreimentdev/skills")
CURSOR_SKILLS = Path(".cursor/skills")


def sync(repo: Path, *, check: bool) -> int:
    src_root = repo / PLUGIN_SKILLS
    dst_root = repo / CURSOR_SKILLS
    if not src_root.is_dir():
        print(f"missing {src_root}", file=sys.stderr)
        return 2
    drift = False
    for skill_dir in sorted(p for p in src_root.iterdir() if p.is_dir()):
        src = skill_dir / "SKILL.md"
        if not src.is_file():
            continue
        dst = dst_root / skill_dir.name / "SKILL.md"
        if check:
            if not dst.is_file() or not filecmp.cmp(src, dst, shallow=False):
                print(f"drift: {dst}")
                drift = True
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return 1 if drift else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    return sync(args.repo.resolve(), check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
