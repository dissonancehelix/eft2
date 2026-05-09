from __future__ import annotations

import argparse
import json
from pathlib import Path

from eft_entities import classify_entities, TRIGGER_CLASSES
from brushwork_perception import build_brushwork_perception, render_brushwork_markdown
from exporters import metadata, write_json, write_md
from geometry_backend import inspect_geometry_backends
from gameflow_sim import simulate_gameflow, simulation_summary
from recast_adapter import export_intermediate, inspect_recast
from semantic_groups import infer_semantics
from spatial_perception import summarize_spatial_backend
from virtual_perception import build_virtual_perception
from vmf_geometry import bounds_from_solids, build_world_mesh
from vmf_parser import extract_entities, parse_vmf


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze one organized EFT map domain.")
    parser.add_argument("map_dir", nargs="?", help="Path like Maps/Slam Dunk")
    parser.add_argument("--map", dest="map_name", help="Canonical map name under Maps, e.g. Slam Dunk")
    parser.add_argument("--maps-root", default="maps")
    args = parser.parse_args()
    if args.map_name:
        map_dir = Path(args.maps_root) / args.map_name
    elif args.map_dir:
        map_dir = Path(args.map_dir)
    else:
        parser.error("provide map_dir or --map")
    analyze_map(map_dir)
    return 0


def analyze_map(map_dir: Path) -> None:
    vmfs = sorted(map_dir.glob("*.vmf"))
    if not vmfs:
        raise FileNotFoundError(f"No VMF found in {map_dir}")
    source_vmf = vmfs[0]
    map_name = map_dir.name
    original_filename = _original_filename(map_dir, map_name)
    root = parse_vmf(source_vmf)
    entities, world_solids = extract_entities(root)
    for solid in world_solids:
        solid["bounds"] = bounds_from_solids([solid])
    for ent in entities:
        ent["bounds"] = bounds_from_solids(ent.get("solids", []), ent.get("origin"))
    world_mesh = build_world_mesh(world_solids)
    brush_entities = [e for e in entities if e.get("solids")]
    brushwork = build_brushwork_perception(world_solids, brush_entities)
    trigger_volumes = [e for e in entities if e.get("classname") in TRIGGER_CLASSES]
    eft = classify_entities(entities)
    semantics = infer_semantics(map_name, entities, world_solids)
    recast = inspect_recast(Path("."))
    geometry_backend = inspect_geometry_backends(Path("."))
    spatial_backend = summarize_spatial_backend(world_solids, entities)
    recast_export = export_intermediate(map_name, map_dir, world_solids, brush_entities)
    vp = build_virtual_perception(map_name, semantics, eft, world_solids)
    meta = metadata(map_name, source_vmf, original_filename)
    analysis = map_dir / "analysis"
    virtual = map_dir / "virtual perception"
    simulation_dir = map_dir / "simulation"
    write_json(analysis / "raw_entities.json", {**meta, "entities": entities})
    write_json(analysis / "brush_entities.json", {**meta, "brush_entities": brush_entities, "world_solids": world_solids})
    write_json(analysis / "brushwork.json", {**meta, **brushwork})
    write_json(analysis / "geometry_mesh.json", {**meta, **world_mesh})
    write_json(analysis / "trigger_volumes.json", {**meta, "trigger_volumes": trigger_volumes})
    write_json(analysis / "eft_entities.json", {**meta, **eft})
    write_json(analysis / "spawn_clusters.json", {**meta, "spawn_clusters": semantics["spawn_clusters"]})
    write_json(analysis / "goal_complexes.json", {**meta, "goal_complexes": semantics["goal_complexes"]})
    write_json(analysis / "hazard_regions.json", {**meta, "hazard_regions": semantics["hazard_regions"]})
    write_json(analysis / "reset_regions.json", {**meta, "reset_regions": semantics["reset_regions"]})
    write_json(analysis / "powerup_locations.json", {**meta, "powerup_locations": semantics["powerup_locations"]})
    write_json(analysis / "spatial_clusters.json", {**meta, "spatial_clusters": semantics["spatial_clusters"], "jump_push_regions": semantics["jump_push_regions"], "rotating_obstructions": semantics["rotating_obstructions"]})
    write_json(analysis / "geometry_backend_summary.json", {**meta, **geometry_backend})
    write_json(analysis / "navmesh_summary.json", {**meta, "status": recast["status"], "recast": recast, "geometry_backend": geometry_backend, "spatial_backend": spatial_backend, "export": recast_export, "sbox_runtime_target": {"uses_recast_navigation": True, "runtime_apis": ["Scene.NavMesh", "NavMeshAgent", "NavMeshLink", "NavMeshArea", "CalculatePathRequest"], "bot_goal": "Use analyzer route evidence to author and validate future in-game bot navigation, then validate with s&box Scene.NavMesh queries."}, "needed_next": "Use s&box Scene.NavMesh/Recast queries once maps are ported; until then, keep offline brush-mesh route reads evidence-bound."})
    write_json(analysis / "route_graph.json", {**meta, "status": "pending_recast_integration", "nodes": [], "edges": [], "note": "No route metrics faked before Recast integration."})
    profile = _gameplay_profile(meta, semantics, eft)
    sim = simulate_gameflow(map_name, semantics, eft)
    write_json(analysis / "gameplay_profile.json", profile)
    write_md(analysis / "confidence_report.md", _confidence_report(map_name, semantics))
    write_md(analysis / "summary.md", _summary(map_name, semantics, eft, recast))
    write_json(virtual / "viewpoints.json", {**meta, "viewpoints": vp["viewpoints"]})
    write_json(virtual / "route_reads.json", {**meta, "route_reads": vp["route_reads"]})
    write_json(virtual / "danger_fields.json", {**meta, "danger_fields": vp["danger_fields"]})
    write_json(virtual / "line_of_sight.json", {**meta, **vp["line_of_sight"]})
    write_md(virtual / "brushwork.md", render_brushwork_markdown(map_name, brushwork))
    write_md(virtual / "gameplay_flow.md", vp["gameplay_flow_md"])
    write_json(simulation_dir / "abstract_gameflow.json", {**meta, **sim})
    write_md(simulation_dir / "abstract_gameflow.md", simulation_summary(map_name, sim))
    print(f"Analyzed {map_name}: {len(entities)} entities, {len(world_solids)} world solids.")


def _original_filename(map_dir: Path, map_name: str) -> str | None:
    manifest_path = map_dir.parent / "source_manifest.json"
    if not manifest_path.exists():
        return None
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    entry = data.get(map_name)
    return entry.get("original_filename") if entry else None


def _gameplay_profile(meta: dict, semantics: dict, eft: dict) -> dict:
    counts = eft.get("eft_class_counts", {})
    return {
        **meta,
        "tags": semantics["gameplay_tags"],
        "raw_counts": counts,
        "estimated_constants": {
            "base_speed_hu_s": 350,
            "carrier_speed_hu_s": 262.5,
            "charge_threshold_hu_s": 300,
            "note": "Initial README constants only; route/intercept estimates are pending Recast integration.",
        },
        "confidence_notes": semantics["confidence_notes"],
        "needs_human_review": bool(semantics["confidence_notes"]),
    }


def _confidence_report(map_name: str, semantics: dict) -> str:
    lines = [f"# {map_name} Confidence Report", ""]
    for note in semantics["confidence_notes"]:
        lines.append(f"- {note}")
    if not semantics["confidence_notes"]:
        lines.append("- No major confidence warnings generated.")
    return "\n".join(lines)


def _summary(map_name: str, semantics: dict, eft: dict, recast: dict) -> str:
    counts = eft.get("eft_class_counts", {})
    tags = ", ".join(semantics["gameplay_tags"]) or "none inferred"
    lines = [
        f"# {map_name} Summary",
        "",
        "Generated analysis summary. This is not hand-authored canon.",
        "",
        f"- Inferred gameplay tags: {tags}.",
        f"- EFT-relevant raw classes: {json.dumps(counts, sort_keys=True)}.",
        f"- Spawn clusters: red={len(semantics['spawn_clusters']['red'])}, blue={len(semantics['spawn_clusters']['blue'])}.",
        f"- Goal complex candidates: {len(semantics['goal_complexes'])}.",
        f"- Hazard/reset candidates: {len(semantics['hazard_regions']) + len(semantics['reset_regions'])}.",
        f"- Powerup candidates: {len(semantics['powerup_locations'])}.",
        f"- Jump/push route candidates: {len(semantics['jump_push_regions'])}.",
        f"- Recast status: {recast['status']}.",
        "",
        "Gameplay interpretation should be reviewed against domain expertise when confidence notes or human-review flags are present.",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
