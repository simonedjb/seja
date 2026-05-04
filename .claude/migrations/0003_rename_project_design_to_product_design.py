"""
0003_rename_project_design_to_product_design.py

Rename the consumer-side project-design/ directory to product-design/ and
update any references to the old name in CLAUDE.md.

Version axis: gates on all consumer projects whose .seja-version < v0.3.0,
including pre-release / unversioned installations where .seja-version is 0.0.0.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from_version = "0.0.0"
to_version = "v0.3.0"


def _git_mv(root: Path, src: Path, dst: Path) -> bool:
    """Attempt git mv src dst inside *root*. Returns True on success."""
    git_dir = root / ".git"
    if not git_dir.exists():
        return False
    result = subprocess.run(
        [
            "git", "-C", str(root), "mv",
            str(src.relative_to(root)),
            str(dst.relative_to(root)),
        ],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def upgrade(root: Path) -> None:
    """Rename project-design/ → product-design/ in the consumer project."""
    src = root / "project-design"
    dst = root / "product-design"

    if not src.is_dir():
        print("INFO: project-design/ not found -- nothing to rename")
    elif dst.is_dir() and any(dst.iterdir()):
        print("INFO: product-design/ already exists and is non-empty -- skipping rename")
    else:
        used_git = _git_mv(root, src, dst)
        if used_git:
            print("OK: Renamed project-design/ → product-design/ (git mv)")
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            print("OK: Renamed project-design/ → product-design/ (shutil)")

    # Update CLAUDE.md -- replace path-form and backtick-quoted references.
    claude_md = root / "CLAUDE.md"
    if claude_md.is_file():
        original = claude_md.read_text(encoding="utf-8")
        updated = original.replace("project-design/", "product-design/")
        updated = updated.replace("`project-design`", "`product-design`")
        if updated != original:
            claude_md.write_text(updated, encoding="utf-8")
            print("OK: Updated project-design references in CLAUDE.md")
        else:
            print("INFO: No project-design references in CLAUDE.md -- already updated")


def downgrade(root: Path) -> None:
    """Best-effort reverse: rename product-design/ → project-design/."""
    src = root / "product-design"
    dst = root / "project-design"

    if not src.is_dir():
        print("INFO: product-design/ not found -- nothing to reverse")
    elif dst.is_dir() and any(dst.iterdir()):
        print("INFO: project-design/ already exists and is non-empty -- skipping reverse")
    else:
        used_git = _git_mv(root, src, dst)
        if not used_git:
            shutil.move(str(src), str(dst))
        print("OK: Renamed product-design/ → project-design/ (downgrade)")

    claude_md = root / "CLAUDE.md"
    if claude_md.is_file():
        original = claude_md.read_text(encoding="utf-8")
        updated = original.replace("product-design/", "project-design/")
        updated = updated.replace("`product-design`", "`project-design`")
        if updated != original:
            claude_md.write_text(updated, encoding="utf-8")
            print("OK: Reverted CLAUDE.md references")
