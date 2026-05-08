from __future__ import annotations

from itertools import combinations
from typing import Any

from vmf_geometry import mesh_segment_hits, segment_aabb_hits


def build_virtual_perception(map_name: str, semantics: dict[str, Any], eft_entities: dict[str, Any], world_solids: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    world_solids = world_solids or []
    viewpoints = []
    ball_entities = [e for e in eft_entities.get("entities", []) if e.get("classname") == "prop_ball"]
    for ent in ball_entities:
        viewpoints.append(_view("ball_spawn", "Ball spawn", ent.get("origin"), [ent.get("id")], ["Primary convergence point at round/reset start."]))
    for team, clusters in semantics["spawn_clusters"].items():
        for cluster in clusters:
            viewpoints.append(_view(f"{team}_spawn_cluster", f"{team.title()} spawn cluster", cluster.get("center"), cluster.get("source_entity_ids"), cluster.get("reasons", [])))
    for key in ["goal_complexes", "hazard_regions", "reset_regions", "powerup_locations", "jump_push_regions", "rotating_obstructions"]:
        for region in semantics.get(key, []):
            viewpoints.append(_view(region["type"], region["id"], region.get("center"), region.get("source_entity_ids"), region.get("reasons", []), region.get("confidence"), region.get("needs_human_review")))
    route_reads = []
    for jump in semantics.get("jump_push_regions", []):
        route_reads.append({
            "type": "movement_boost_route_candidate",
            "from": "nearby traversal area",
            "to": "boost destination unknown until route/navmesh analysis",
            "source_region": jump["id"],
            "confidence": 0.45,
            "needs_human_review": True,
            "reasons": jump.get("reasons", []) + ["Route endpoint requires Recast or trigger output interpretation."],
        })
    danger_fields = []
    for region in semantics.get("hazard_regions", []) + semantics.get("reset_regions", []):
        danger_fields.append({
            "region": region["id"],
            "type": region["type"],
            "center": region.get("center"),
            "gameplay_meaning": "Danger/reset pressure near this region can redirect possession and route choices.",
            "confidence": region.get("confidence"),
            "needs_human_review": region.get("needs_human_review"),
        })
    line_of_sight = _line_of_sight_probes(viewpoints, world_solids)
    flow = _flow_summary(map_name, semantics, viewpoints)
    return {
        "viewpoints": viewpoints,
        "route_reads": route_reads,
        "danger_fields": danger_fields,
        "line_of_sight": line_of_sight,
        "gameplay_flow_md": flow,
    }


def _line_of_sight_probes(viewpoints: list[dict[str, Any]], world_solids: list[dict[str, Any]]) -> dict[str, Any]:
    landmarks = [v for v in viewpoints if v.get("origin")]
    mesh_active = any((solid.get("mesh") or {}).get("triangles") for solid in world_solids)
    probes = []
    for a, b in combinations(landmarks[:16], 2):
        hits = mesh_segment_hits(a["origin"], b["origin"], world_solids, limit=10) if mesh_active else segment_aabb_hits(a["origin"], b["origin"], world_solids, limit=10)
        probes.append({
            "from": a["label"],
            "to": b["label"],
            "from_origin": a["origin"],
            "to_origin": b["origin"],
            "blocker_count": len(hits),
            "sample_blockers": hits[:5],
            "read": "likely_exposed" if not hits else "geometry_intersected",
            "confidence": 0.45 if mesh_active and not hits else 0.38 if mesh_active else 0.25,
            "needs_human_review": True,
        })
    return {
        "status": "brush_mesh_visibility_probe" if mesh_active else "aabb_visibility_probe_pending_mesh_backend",
        "probes": probes,
        "note": "Uses reconstructed VMF brush triangles for sight probes when available. Treat as map-vision evidence, not final Source/s&box collision truth.",
    }


def _view(kind, label, origin, source_ids, reasons, confidence=0.6, needs_human_review=False):
    return {
        "type": kind,
        "label": label,
        "origin": origin,
        "source_entity_ids": source_ids,
        "nearby_landmarks": [],
        "route_connections": [],
        "gameplay_meaning": "Candidate gameplay landmark for LLM spatial reasoning.",
        "uncertain": bool(needs_human_review),
        "confidence": confidence,
        "reasons": reasons,
    }


def _flow_summary(map_name: str, semantics: dict[str, Any], viewpoints: list[dict[str, Any]]) -> str:
    tags = ", ".join(semantics.get("gameplay_tags", [])) or "none inferred"
    lines = [
        f"# {map_name} Gameplay Flow",
        "",
        "This is a generated Virtual Perception artifact for LLM map reasoning. It is not hand-authored canon.",
        "",
        f"- Inferred tags: {tags}.",
        f"- Viewpoint count: {len(viewpoints)}.",
        f"- Goal complex candidates: {len(semantics.get('goal_complexes', []))}.",
        f"- Hazard/reset candidates: {len(semantics.get('hazard_regions', [])) + len(semantics.get('reset_regions', []))}.",
        f"- Powerup candidates: {len(semantics.get('powerup_locations', []))}.",
        f"- Jump/push route candidates: {len(semantics.get('jump_push_regions', []))}.",
        "",
        "Uncertain interpretations require user/domain-expert review, especially where raw trigger counts may not equal gameplay structures.",
    ]
    return "\n".join(lines)
