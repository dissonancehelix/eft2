"""SBOX_INDEX.json — shallow s&box reference index, prioritized."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from schemas import IndexEnvelope, rel

PRIORITY_KEYWORDS: list[tuple[str, list[str]]] = [
    ("sbproj", []),  # filename glob
    ("component", ["component"]),
    ("networking", ["network", "rpc", "sync"]),
    ("trigger", ["trigger"]),
    ("navigation", ["navmesh", "navigation", "pathing"]),
    ("scene", ["scene", "scenestaging"]),
    ("player_controller", ["playercontroller", "player_controller"]),
    ("ui_hud", ["hud", "razor", "scss", "ui/"]),
]

FILE_BUDGET = 4000


def build(root: Path, env: IndexEnvelope) -> dict[str, Any]:
    sbox_root = root / "sbox"
    if not sbox_root.is_dir():
        env.warn("sbox_dir_missing")
        return env.wrap({"present": False})

    subdirs = {
        "Docs": (sbox_root / "Docs").is_dir(),
        "Source": (sbox_root / "Source").is_dir(),
        "Runtime": (sbox_root / "Runtime").is_dir(),
    }

    found: dict[str, list[str]] = {key: [] for key, _ in PRIORITY_KEYWORDS}
    sbproj: list[str] = []
    sample_projects: list[str] = []
    seen = 0
    truncated = False

    for path in sbox_root.rglob("*"):
        seen += 1
        if seen > FILE_BUDGET:
            truncated = True
            break
        if not path.is_file():
            continue
        rp = rel(path, root)
        rp_low = rp.lower()
        if path.suffix.lower() == ".sbproj":
            sbproj.append(rp)
            sample_projects.append(rel(path.parent, root))
            continue
        for key, kws in PRIORITY_KEYWORDS:
            if not kws:
                continue
            if any(kw in rp_low for kw in kws):
                bucket = found[key]
                if len(bucket) < 60:
                    bucket.append(rp)
                break

    if truncated:
        env.warn(f"sbox_scan_truncated_at:{FILE_BUDGET}")

    return env.wrap({
        "present": True,
        "sbox_root": rel(sbox_root, root),
        "subdirs": subdirs,
        "sbproj_files": sorted(sbproj),
        "sample_projects": sorted(set(sample_projects)),
        "by_priority": found,
        "scan_truncated": truncated,
        "files_seen": seen,
    })
