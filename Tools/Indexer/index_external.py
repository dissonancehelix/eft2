"""External-tree indexes: GMod source, Source 1 FGDs, FFmpeg-Builds.

These trees are temporary. The indexer extracts useful reference metadata,
records cleanup recommendations, and never mutates the source trees.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from exporters import safe_read_text
from schemas import IndexEnvelope, rel

GMOD_DIR = "garrysmod-master"
FFMPEG_DIR = "FFmpeg-Builds-master"

WALK_BUDGET = 8000


def _shallow_walk(root: Path) -> tuple[int, int, bool]:
    """Returns (file_count, total_bytes, truncated)."""
    count = 0
    size = 0
    truncated = False
    for p in root.rglob("*"):
        if p.is_file():
            count += 1
            try:
                size += p.stat().st_size
            except OSError:
                pass
        if count > WALK_BUDGET:
            truncated = True
            break
    return count, size, truncated


def _gitignore_covers(repo_root: Path, dir_name: str) -> bool:
    gi = repo_root / ".gitignore"
    if not gi.exists():
        return False
    try:
        text = gi.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    needles = (f"/{dir_name}/", f"{dir_name}/", f"/{dir_name}", dir_name + "\n", dir_name + "\r")
    return any(n in text for n in needles)


# --- FGD parsing -----------------------------------------------------------

CLASS_RE = re.compile(
    r"@(SolidClass|PointClass|BaseClass|NPCClass|FilterClass|KeyFrameClass|MoveClass)([^=]*?)=\s*(\w+)",
    re.IGNORECASE,
)
BASE_RE = re.compile(r"base\s*\(\s*([^)]+)\s*\)", re.IGNORECASE)
KEYVALUE_RE = re.compile(r'^\s*([A-Za-z_][\w]*)\s*\(\s*(\w+)\s*\)\s*:\s*"([^"]+)"', re.MULTILINE)
INPUT_RE = re.compile(r'^\s*input\s+(\w+)\s*\(\s*(\w*)\s*\)', re.MULTILINE | re.IGNORECASE)
OUTPUT_RE = re.compile(r'^\s*output\s+(\w+)\s*\(\s*(\w*)\s*\)', re.MULTILINE | re.IGNORECASE)


def _parse_fgd(path: Path) -> dict[str, Any]:
    text, warn = safe_read_text(path, max_bytes=4_000_000)
    if text is None:
        return {"path": str(path), "skipped": warn}
    classes: list[dict[str, Any]] = []
    # Split on @...Class lines as block boundaries.
    blocks = re.split(r"(?=@(?:SolidClass|PointClass|BaseClass|NPCClass|FilterClass|KeyFrameClass|MoveClass)\b)", text, flags=re.IGNORECASE)
    for block in blocks:
        m = CLASS_RE.search(block)
        if not m:
            continue
        kind = m.group(1)
        header = m.group(2) or ""
        name = m.group(3)
        bases: list[str] = []
        bm = BASE_RE.search(header)
        if bm:
            bases = [b.strip() for b in bm.group(1).split(",") if b.strip()]
        keyvalues = [{"name": kv[0], "type": kv[1], "label": kv[2]} for kv in KEYVALUE_RE.findall(block)][:60]
        inputs = sorted({i[0] for i in INPUT_RE.findall(block)})[:40]
        outputs = sorted({o[0] for o in OUTPUT_RE.findall(block)})[:40]
        classes.append({
            "kind": kind,
            "name": name,
            "bases": bases,
            "keyvalue_count": len(keyvalues),
            "keyvalues": keyvalues,
            "inputs": inputs,
            "outputs": outputs,
        })
    return {
        "path": str(path).replace("\\", "/"),
        "size_bytes": path.stat().st_size,
        "class_count": len(classes),
        "classes": classes,
    }


# --- GMod -----------------------------------------------------------------

GMOD_HOOK_RE = re.compile(r"hook\.Add\s*\(\s*[\"']([^\"']+)[\"']", re.MULTILINE)


def index_gmod(repo_root: Path, env: IndexEnvelope) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    gmod = repo_root / GMOD_DIR
    if not gmod.is_dir():
        return None, None

    file_count, total_bytes, truncated = _shallow_walk(gmod)
    if truncated:
        env.warn(f"gmod_walk_truncated_at:{WALK_BUDGET}")

    gitignored = _gitignore_covers(repo_root, GMOD_DIR)
    if not gitignored:
        env.warn(f"gitignore_missing:{GMOD_DIR}")

    bin_dir = gmod / "bin"
    fgd_paths: list[Path] = []
    if bin_dir.is_dir():
        fgd_paths = sorted(bin_dir.glob("*.fgd"))

    fgd_index = None
    if fgd_paths:
        fgd_index = {
            "scanned_root": rel(bin_dir, repo_root),
            "fgd_count": len(fgd_paths),
            "fgds": [_parse_fgd(p) for p in fgd_paths],
        }
    else:
        env.warn("gmod_bin_fgds_missing")

    # Hook names from gamemode lua.
    hook_names: set[str] = set()
    gamemodes = gmod / "garrysmod" / "gamemodes"
    sample_lua_paths: list[str] = []
    if gamemodes.is_dir():
        seen = 0
        for p in gamemodes.rglob("*.lua"):
            seen += 1
            if seen > 1500:
                env.warn("gmod_lua_walk_truncated_at:1500")
                break
            sample_lua_paths.append(rel(p, repo_root))
            text, _ = safe_read_text(p, max_bytes=300_000)
            if text:
                for m in GMOD_HOOK_RE.findall(text):
                    hook_names.add(m)

    gmod_index = {
        "detected_path": rel(gmod, repo_root),
        "file_count_approx": file_count,
        "total_bytes_approx": total_bytes,
        "walk_truncated": truncated,
        "gitignore_covers": gitignored,
        "bin_fgd_paths": [rel(p, repo_root) for p in fgd_paths],
        "gamemode_lua_count": len(sample_lua_paths),
        "gamemode_lua_sample": sample_lua_paths[:80],
        "hook_names": sorted(hook_names),
        "derived_outputs": ["GMOD_REFERENCE_INDEX.json", "SOURCE1_FGD_INDEX.json"],
        "cleanup_recommendation": (
            "Temporary reference. After Map Analyzer consumes SOURCE1_FGD_INDEX.json, "
            "the entire garrysmod-master/ tree can be deleted from the workspace."
        ),
    }
    return gmod_index, fgd_index


# --- FFmpeg-Builds --------------------------------------------------------

FFMPEG_BIN_NAMES = {"ffmpeg", "ffmpeg.exe", "ffprobe", "ffprobe.exe", "ffplay", "ffplay.exe"}
FFMPEG_BIN_EXTS = {".exe", ".dll", ".so", ".dylib"}


def index_ffmpeg(repo_root: Path, env: IndexEnvelope) -> dict[str, Any] | None:
    ff = repo_root / FFMPEG_DIR
    if not ff.is_dir():
        return None

    file_count, total_bytes, truncated = _shallow_walk(ff)
    if truncated:
        env.warn(f"ffmpeg_walk_truncated_at:{WALK_BUDGET}")

    gitignored = _gitignore_covers(repo_root, FFMPEG_DIR)
    if not gitignored:
        env.warn(f"gitignore_missing:{FFMPEG_DIR}")

    top_level = sorted(p.name for p in ff.iterdir())
    has_variants = (ff / "variants").is_dir()
    has_scripts_d = (ff / "scripts.d").is_dir()
    has_patches = (ff / "patches").is_dir()

    binaries_found: list[str] = []
    usable_ffmpeg_exe: str | None = None
    seen = 0
    for p in ff.rglob("*"):
        seen += 1
        if seen > WALK_BUDGET:
            break
        if not p.is_file():
            continue
        if p.name.lower() in FFMPEG_BIN_NAMES:
            binaries_found.append(rel(p, repo_root))
            if p.name.lower() == "ffmpeg.exe":
                usable_ffmpeg_exe = rel(p, repo_root)
        elif p.suffix.lower() in FFMPEG_BIN_EXTS:
            binaries_found.append(rel(p, repo_root))

    is_only_build_infra = not binaries_found and (has_variants or has_scripts_d or has_patches)

    recommendation = (
        "Tree contains only upstream BtbN cross-build infrastructure (variants/, "
        "scripts.d/, patches/). No prebuilt ffmpeg binaries detected. EFT2 will not "
        "build ffmpeg from this matrix; future Tools/Observer/ should consume a "
        "prebuilt ffmpeg.exe placed elsewhere. Recommend deleting the entire "
        f"{FFMPEG_DIR}/ tree."
        if is_only_build_infra else
        "Tree contains binaries; review them before deletion. Extract any usable "
        f"ffmpeg.exe to a stable tools location, then delete {FFMPEG_DIR}/."
    )

    return {
        "detected_path": rel(ff, repo_root),
        "file_count_approx": file_count,
        "total_bytes_approx": total_bytes,
        "walk_truncated": truncated,
        "gitignore_covers": gitignored,
        "top_level": top_level,
        "has_variants": has_variants,
        "has_scripts_d": has_scripts_d,
        "has_patches": has_patches,
        "binaries_found": binaries_found,
        "usable_ffmpeg_exe": usable_ffmpeg_exe,
        "is_only_build_infrastructure": is_only_build_infra,
        "derived_outputs": ["FFMPEG_REFERENCE_INDEX.json"],
        "cleanup_recommendation": recommendation,
    }


def build(root: Path, env: IndexEnvelope) -> dict[str, dict[str, Any] | None]:
    gmod_index, fgd_index = index_gmod(root, env)
    ffmpeg_index = index_ffmpeg(root, env)

    return {
        "gmod": env.wrap(gmod_index) if gmod_index else None,
        "fgd": env.wrap(fgd_index) if fgd_index else None,
        "ffmpeg": env.wrap(ffmpeg_index) if ffmpeg_index else None,
    }
