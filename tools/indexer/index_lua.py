"""LUA_INDEX.json — first-pass classification of Lua/."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from exporters import safe_read_text
from schemas import IndexEnvelope, rel

TAG_KEYWORDS: dict[str, list[str]] = {
    "movement": ["movement", "velocity", "walk", "run", "jump", "speed", "accel"],
    "ball": ["ball", "carry", "carrier", "pickup", "fumble"],
    "possession": ["possession", "owner", "carrier"],
    "tackle": ["tackle"],
    "head_on": ["head_on", "headon", "head-on", "collide"],
    "knockdown": ["knockdown", "knock_down", "ragdoll", "stun"],
    "throw": ["throw", "pass"],
    "dive": ["dive"],
    "goal": ["goal", "score"],
    "trigger": ["trigger"],
    "powerup": ["powerup", "power_up", "speedball"],
    "bot": ["bot", "ai", "navmesh"],
    "hud": ["hud", "vgui", "drawhud"],
    "round_flow": ["round", "match", "halftime", "kickoff"],
    "telemetry": ["telemetry", "log", "metrics", "stat"],
}

FUNC_RE = re.compile(r"^\s*(?:local\s+)?function\s+([\w\.\:]+)\s*\(", re.MULTILINE)
HOOK_RE = re.compile(r"hook\.Add\s*\(\s*[\"']([^\"']+)[\"']\s*,\s*[\"']([^\"']+)[\"']")
ENT_RE = re.compile(r"^\s*(ENT|GM|SWEP|SF)\.(\w+)\s*=", re.MULTILINE)


def _classify(name: str, text: str) -> list[str]:
    haystack = (name + "\n" + text).lower()
    tags: list[str] = []
    for tag, keywords in TAG_KEYWORDS.items():
        if any(kw in haystack for kw in keywords):
            tags.append(tag)
    return tags


def _index_file(path: Path, root: Path) -> dict[str, Any]:
    info: dict[str, Any] = {
        "path": rel(path, root),
        "size_bytes": path.stat().st_size,
    }
    text, warn = safe_read_text(path)
    if text is None:
        info["skipped"] = warn
        return info
    info["line_count"] = text.count("\n") + 1
    info["functions"] = sorted(set(FUNC_RE.findall(text)))[:200]
    info["hooks"] = sorted({h[0] for h in HOOK_RE.findall(text)})[:100]
    ent_assigns = sorted({f"{a}.{b}" for a, b in ENT_RE.findall(text)})[:100]
    info["entity_assignments"] = ent_assigns
    info["tags"] = _classify(path.name, text)
    return info


def build(root: Path, env: IndexEnvelope) -> dict[str, Any]:
    lua_root = root / "lua"
    if not lua_root.is_dir():
        env.warn("lua_dir_missing")
        return env.wrap({"present": False, "files": []})
    files: list[dict[str, Any]] = []
    tag_counts: dict[str, int] = {tag: 0 for tag in TAG_KEYWORDS}
    for path in sorted(lua_root.rglob("*.lua")):
        try:
            entry = _index_file(path, root)
        except OSError as e:
            env.warn(f"lua_read_failed:{rel(path, root)}:{e}")
            continue
        files.append(entry)
        for t in entry.get("tags", []):
            tag_counts[t] = tag_counts.get(t, 0) + 1
    return env.wrap({
        "present": True,
        "lua_root": rel(lua_root, root),
        "file_count": len(files),
        "tag_counts": tag_counts,
        "files": files,
    })
