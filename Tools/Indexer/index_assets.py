"""OBSERVATION_INDEX.json + MULTIMODAL_CONTEXT.md — Assets/ inventory."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from schemas import IndexEnvelope, rel

VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".avi", ".webm"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tga", ".webp"}

OBSERVED_ARTIFACTS = (
    "video_manifest.json",
    "screenshot_manifest.json",
    "events.json",
    "timeline.json",
    "observations.md",
    "gameplay_flow.md",
    "hud_readability.md",
)
OBSERVED_DIRS = ("keyframes", "contact_sheets")


def _scan_subdir(d: Path, root: Path) -> dict[str, Any]:
    if not d.is_dir():
        return {"present": False, "path": rel(d, root)}
    videos: list[dict[str, Any]] = []
    images: list[dict[str, Any]] = []
    other: list[str] = []
    artifacts: dict[str, str] = {}
    for p in d.rglob("*"):
        if p.is_dir():
            if p.name.lower() in OBSERVED_DIRS:
                artifacts[p.name] = rel(p, root)
            continue
        try:
            size = p.stat().st_size
        except OSError:
            continue
        ext = p.suffix.lower()
        rec = {"path": rel(p, root), "size_bytes": size}
        if ext in VIDEO_EXTS:
            videos.append(rec)
        elif ext in IMAGE_EXTS:
            images.append(rec)
        elif p.name.lower() in OBSERVED_ARTIFACTS:
            artifacts[p.name] = rel(p, root)
        elif p.suffix.lower() in (".md", ".json", ".txt"):
            other.append(rel(p, root))
    return {
        "present": True,
        "path": rel(d, root),
        "video_count": len(videos),
        "videos": videos,
        "image_count": len(images),
        "images": images[:200],
        "image_truncated": len(images) > 200,
        "observation_artifacts": artifacts,
        "other_files": other,
    }


def build(root: Path, env: IndexEnvelope) -> dict[str, Any]:
    assets = root / "Assets"
    if not assets.is_dir():
        env.warn("assets_dir_missing")
        return env.wrap({"present": False})
    sections = {
        "Video": _scan_subdir(assets / "Video", root),
        "Screenshots": _scan_subdir(assets / "Screenshots", root),
        "Backgrounds": _scan_subdir(assets / "Backgrounds", root),
    }

    pending = []
    for name, sec in sections.items():
        if not sec.get("present"):
            continue
        media_count = sec.get("video_count", 0) + sec.get("image_count", 0)
        artifacts = sec.get("observation_artifacts", {})
        if media_count > 0 and not artifacts:
            pending.append(name)

    return env.wrap({
        "present": True,
        "assets_root": rel(assets, root),
        "sections": sections,
        "pending_observer_processing": pending,
    })


def render_multimodal_md(payload: dict[str, Any]) -> str:
    if not payload.get("present"):
        return "# Multimodal Context\n\nNo `Assets/` directory found.\n"
    lines = ["# Multimodal Context", ""]
    lines.append("This report summarizes observation material under `Assets/` and what")
    lines.append("an LLM agent can learn from it without re-inspecting the raw media.")
    lines.append("")
    sections = payload.get("sections", {})
    for name in ("Video", "Screenshots", "Backgrounds"):
        sec = sections.get(name, {})
        lines.append(f"## {name}")
        if not sec.get("present"):
            lines.append("- not present")
            lines.append("")
            continue
        lines.append(f"- path: `{sec.get('path')}`")
        lines.append(f"- videos: {sec.get('video_count', 0)}")
        lines.append(f"- images: {sec.get('image_count', 0)}")
        artifacts = sec.get("observation_artifacts") or {}
        if artifacts:
            lines.append("- observation artifacts:")
            for k, v in sorted(artifacts.items()):
                lines.append(f"  - `{v}` ({k})")
        else:
            lines.append("- observation artifacts: none — raw media only")
        lines.append("")
    pending = payload.get("pending_observer_processing") or []
    lines.append("## Status")
    if pending:
        lines.append("Sections with raw media but no extracted timeline/keyframes/observations:")
        for p in pending:
            lines.append(f"- {p}")
        lines.append("")
        lines.append("These are pending future `Tools/Observer/` processing.")
    else:
        lines.append("No sections flagged as needing Observer processing.")
    lines.append("")
    lines.append("## Why this exists")
    lines.append("")
    lines.append("EFT2 wants LLM agents to understand the sport as if they had watched it.")
    lines.append("Raw videos and screenshots are not directly LLM-readable. `Tools/Observer/`")
    lines.append("will eventually convert media into structured timelines, keyframes,")
    lines.append("contact sheets, and prose observations. The Indexer only reports what")
    lines.append("exists today.")
    return "\n".join(lines)
