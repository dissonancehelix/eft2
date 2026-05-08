"""MAPS_INDEX.json — canonical map domains, FGD discovery, provenance."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from schemas import IndexEnvelope, rel

# Directories to search for a custom EFT FGD, in priority order.
CUSTOM_FGD_SEARCH_DIRS = ("Maps/Shared", "Maps", ".", "Lua/content")

# Base Source 1 / s&box FGDs that are not the custom EFT FGD.
_BASE_FGDS = {
    "base.fgd", "garrysmod.fgd", "halflife2.fgd", "hl2mp.fgd",
    "s&box.fgd", "models_base.fgd", "models_gamedata.fgd",
    "vdata_base.fgd", "workshop_addoninfo.fgd", "workshop_addoninfo_base.fgd",
}


def _find_custom_fgds(root: Path) -> list[Path]:
    """Find non-base FGDs — matches by any name, not just eft.fgd."""
    found: list[Path] = []
    for sub in CUSTOM_FGD_SEARCH_DIRS:
        d = root / sub
        if not d.is_dir():
            continue
        for p in d.rglob("*.fgd"):
            if p.name.lower() not in _BASE_FGDS:
                found.append(p)
    return sorted(set(found))


_FGD_CLASS_RE = re.compile(
    r"@(SolidClass|PointClass|BaseClass)\b[^=]*=\s*(\w+)\s*:\s*\"([^\"]+)\"",
    re.IGNORECASE,
)


def _summarise_custom_fgd(path: Path, root: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return {"path": rel(path, root), "error": str(e)}
    classes = []
    for m in _FGD_CLASS_RE.finditer(text):
        classes.append({"kind": m.group(1), "name": m.group(2), "description": m.group(3)})
    includes = re.findall(r'@include\s+"([^"]+)"', text, re.IGNORECASE)
    return {
        "path": rel(path, root),
        "size_bytes": path.stat().st_size,
        "includes": includes,
        "class_count": len(classes),
        "classes": classes,
    }


def _provenance_for(name: str, manifest: dict[str, Any] | None) -> Any:
    if not manifest:
        return None
    entries = manifest.get("entries") or manifest.get("maps") or manifest
    if isinstance(entries, dict):
        return entries.get(name)
    if isinstance(entries, list):
        for e in entries:
            if isinstance(e, dict) and (e.get("canonical_name") == name or e.get("name") == name):
                return e
    return None


def _index_map(domain: Path, root: Path, manifest: dict[str, Any] | None) -> dict[str, Any]:
    name = domain.name
    vmfs = sorted(p for p in domain.glob("*.vmf"))
    analysis = domain / "Analysis"
    perception = domain / "Virtual Perception"
    simulation = domain / "Simulation"
    analysis_outputs = sorted(analysis.glob("*.json")) if analysis.is_dir() else []
    perception_outputs = sorted(perception.glob("*")) if perception.is_dir() else []
    confidence = analysis / "confidence_report.md" if analysis.is_dir() else None
    return {
        "canonical_name": name,
        "folder": rel(domain, root),
        "readme": (rel(domain / "README.md", root) if (domain / "README.md").exists() else None),
        "vmf_paths": [rel(v, root) for v in vmfs],
        "analysis_present": analysis.is_dir(),
        "analysis_output_count": len(analysis_outputs),
        "analysis_outputs": [rel(p, root) for p in analysis_outputs],
        "confidence_report": rel(confidence, root) if confidence and confidence.exists() else None,
        "virtual_perception_present": perception.is_dir(),
        "virtual_perception_output_count": len(perception_outputs),
        "simulation_present": simulation.is_dir(),
        "provenance": _provenance_for(name, manifest),
    }


def build(root: Path, env: IndexEnvelope) -> dict[str, Any]:
    maps_root = root / "Maps"
    if not maps_root.is_dir():
        env.warn("maps_dir_missing")
        return env.wrap({"present": False, "maps": []})

    manifest_path = maps_root / "source_manifest.json"
    manifest: dict[str, Any] | None = None
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            env.warn(f"source_manifest_parse_failed:{e}")

    domains: list[dict[str, Any]] = []
    loose_vmfs: list[str] = []
    for entry in sorted(maps_root.iterdir()):
        if entry.is_dir() and entry.name not in ("Shared",):
            domains.append(_index_map(entry, root, manifest))
        elif entry.is_file() and entry.suffix.lower() == ".vmf":
            loose_vmfs.append(rel(entry, root))

    custom_fgds = _find_custom_fgds(root)
    if not custom_fgds:
        env.warn("custom_eft_fgd_missing")

    custom_fgd_summaries = [_summarise_custom_fgd(p, root) for p in custom_fgds]

    shared_dir = maps_root / "Shared"

    return env.wrap({
        "present": True,
        "maps_root": rel(maps_root, root),
        "shared_dir_present": shared_dir.is_dir(),
        "source_manifest": rel(manifest_path, root) if manifest_path.exists() else None,
        "custom_eft_fgds": [rel(p, root) for p in custom_fgds],
        "custom_eft_fgd_contents": custom_fgd_summaries,
        "domain_count": len(domains),
        "domains": domains,
        "loose_vmfs": loose_vmfs,
    })
