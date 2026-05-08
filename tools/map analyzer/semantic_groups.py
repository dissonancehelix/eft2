from __future__ import annotations

from typing import Any

from eft_entities import TRIGGER_CLASSES
from vmf_geometry import cluster_points


def infer_semantics(map_name: str, entities: list[dict[str, Any]], world_solids: list[dict[str, Any]]) -> dict[str, Any]:
    by_class: dict[str, list[dict[str, Any]]] = {}
    for ent in entities:
        by_class.setdefault(ent.get("classname", ""), []).append(ent)
    goals = _goal_complexes(by_class.get("trigger_goal", []))
    hazards = _regions(by_class.get("trigger_hurt", []) + by_class.get("trigger_knockdown", []), "hazard_region", "Hazard or forced knockdown trigger.")
    resets = _regions(by_class.get("trigger_ballreset", []), "reset_region", "Ball reset trigger volume.")
    powerups = _regions(by_class.get("trigger_powerup", []), "powerup_location", "Ball/player powerup influence site.")
    jump_routes = _regions(by_class.get("trigger_jumppad", []) + by_class.get("trigger_abspush", []), "jump_push_region", "Map-authored movement boost route.")
    rotating = _regions(by_class.get("func_rotating", []), "rotating_obstruction", "Rotating brush/object that can shape shots or traversal.")
    spawns = {
        "red": _spawn_clusters(by_class.get("info_player_red", []), "red"),
        "blue": _spawn_clusters(by_class.get("info_player_blue", []), "blue"),
        "spectator": _spawn_clusters(by_class.get("info_player_spectator", []), "spectator"),
    }
    spatial_clusters = _spatial_clusters(entities, world_solids)
    tags = _profile_tags(by_class, goals, hazards, powerups, jump_routes, rotating, spatial_clusters)
    return {
        "spawn_clusters": spawns,
        "goal_complexes": goals,
        "hazard_regions": hazards,
        "reset_regions": resets,
        "powerup_locations": powerups,
        "jump_push_regions": jump_routes,
        "rotating_obstructions": rotating,
        "spatial_clusters": spatial_clusters,
        "gameplay_tags": tags,
        "confidence_notes": _confidence_notes(map_name, by_class, goals, powerups, jump_routes, spatial_clusters),
    }


def _spawn_clusters(entities: list[dict[str, Any]], team: str) -> list[dict[str, Any]]:
    clusters = cluster_points(entities, radius=896.0)
    for cluster in clusters:
        cluster.update({
            "type": f"{team}_spawn_cluster",
            "confidence": 0.9 if cluster["count"] > 1 else 0.7,
            "reasons": [f"Clustered {cluster['count']} {team} spawn entities by origin proximity."],
            "needs_human_review": cluster["count"] <= 1,
        })
    return clusters


def _regions(entities: list[dict[str, Any]], kind: str, reason: str) -> list[dict[str, Any]]:
    out = []
    for index, ent in enumerate(entities, start=1):
        bounds = ent.get("bounds")
        source_id = ent.get("id")
        confidence = 0.75 if bounds else 0.45
        needs_review = bounds is None or kind == "goal_complex"
        reasons = [reason, f"Source entity class `{ent.get('classname')}` id `{source_id}`."]
        if bounds:
            reasons.append("Brush bounds extracted from VMF side plane points.")
        else:
            reasons.append("No brush bounds available; interpretation relies on raw entity keys only.")
        out.append({
            "id": f"{kind}_{index}",
            "type": kind,
            "center": bounds.get("center") if bounds else ent.get("origin"),
            "bounds": bounds,
            "confidence": confidence,
            "reasons": reasons,
            "source_entity_ids": [source_id],
            "source_classes": [ent.get("classname")],
            "needs_human_review": needs_review,
        })
    return out


def _goal_complexes(entities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    raw = _regions(entities, "goal_trigger", "Scoring trigger volume.")
    groups: list[dict[str, Any]] = []
    for region in raw:
        center = region.get("center")
        keyvalues = _source_keyvalues(entities, region["source_entity_ids"][0])
        teamid = keyvalues.get("teamid")
        scoretype = keyvalues.get("scoretype")
        matched = None
        for group in groups:
            if center and group.get("center") and _dist2(center, group["center"]) <= 192.0 * 192.0:
                matched = group
                break
        if matched is None:
            matched = {
                "id": f"goal_complex_{len(groups) + 1}",
                "type": "goal_complex",
                "center": center,
                "bounds": region.get("bounds"),
                "confidence": 0.72 if region.get("bounds") else 0.45,
                "reasons": [
                    "Grouped nearby raw trigger_goal entities into a gameplay scoring-complex candidate.",
                    "Raw trigger count is preserved separately and is not treated as final scoring-location count.",
                ],
                "source_entity_ids": [],
                "source_classes": ["trigger_goal"],
                "raw_trigger_count": 0,
                "teamids": [],
                "scoretypes": [],
                "semantics_used": ["VMF trigger_goal teamid key", "VMF trigger_goal scoretype key"],
                "needs_human_review": True,
            }
            groups.append(matched)
        matched["source_entity_ids"].extend(region["source_entity_ids"])
        matched["raw_trigger_count"] += 1
        if teamid is not None and teamid not in matched["teamids"]:
            matched["teamids"].append(teamid)
        if scoretype is not None and scoretype not in matched["scoretypes"]:
            matched["scoretypes"].append(scoretype)
        if center and matched.get("center"):
            n = matched["raw_trigger_count"]
            matched["center"] = [(matched["center"][i] * (n - 1) + center[i]) / n for i in range(3)]
    return groups


def _source_keyvalues(entities: list[dict[str, Any]], entity_id: int | None) -> dict[str, Any]:
    for ent in entities:
        if ent.get("id") == entity_id:
            return ent.get("keyvalues", {})
    return {}


def _dist2(a: list[float], b: list[float]) -> float:
    return sum((a[i] - b[i]) ** 2 for i in range(3))


def _spatial_clusters(entities: list[dict[str, Any]], world_solids: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items = []
    for ent in entities:
        if ent.get("origin"):
            items.append(ent)
    clusters = cluster_points(items, radius=1280.0)
    for cluster in clusters:
        cluster.update({
            "type": "entity_spatial_cluster",
            "confidence": 0.45,
            "reasons": ["Loose entity-origin cluster; useful as a first-pass landmark grouping, not final gameplay meaning."],
            "needs_human_review": True,
        })
    z_levels = []
    for solid in world_solids:
        b = solid.get("bounds")
        if b and b.get("size", [0, 0, 0])[0] > 128 and b.get("size", [0, 0, 0])[1] > 128:
            z_levels.append(round(b["center"][2], 1))
    if z_levels:
        clusters.append({
            "type": "world_z_level_summary",
            "sampled_level_count": len(set(z_levels)),
            "sampled_z_levels": sorted(set(z_levels))[:80],
            "confidence": 0.35,
            "reasons": ["World brush AABB z-centers suggest vertical/platform structure candidates."],
            "needs_human_review": True,
        })
    return clusters


def _profile_tags(by_class: dict[str, list[dict[str, Any]]], goals, hazards, powerups, jump_routes, rotating, spatial_clusters) -> list[str]:
    tags = []
    goal_count = len(goals)
    if goal_count >= 4:
        tags.append("hybrid_scoring")
    elif goal_count == 2:
        tags.append("touch_or_throw_scoring")
    if hazards:
        tags.append("hazard_regulated")
    if powerups:
        tags.append("powerup_route")
        tags.append("speedball_tempo")
    if jump_routes:
        tags.append("jump_pad_route")
        tags.append("vertical_platform")
    if rotating:
        tags.append("rotating_obstruction_shot")
    red = len(by_class.get("info_player_red", []))
    blue = len(by_class.get("info_player_blue", []))
    if red >= 20 and blue >= 20 and goal_count >= 4:
        tags.append("open_field_intercept")
        tags.append("flat_swarm")
    if any(c.get("type") == "world_z_level_summary" and c.get("sampled_level_count", 0) > 8 for c in spatial_clusters):
        tags.append("vertical_platform")
    return sorted(set(tags))


def _confidence_notes(map_name: str, by_class: dict[str, list[dict[str, Any]]], goals, powerups, jump_routes, spatial_clusters) -> list[str]:
    notes = []
    if map_name == "Slam Dunk":
        notes.append("Slam Dunk validation expects basketball/hoop scoring, vertical routes, powerup tempo, and movement-assisted scoring only when supported by extracted data.")
    if len(goals) > 1:
        notes.append("Multiple raw trigger_goal entities require semantic grouping before claiming real scoring structure.")
    if not powerups:
        notes.append("No trigger_powerup entities found; do not infer speedball/powerup routing without other evidence.")
    if not jump_routes:
        notes.append("No trigger_jumppad/trigger_abspush entities found; do not infer jump-pad routes without other evidence.")
    if any(c.get("type") == "world_z_level_summary" for c in spatial_clusters):
        notes.append("Vertical/platform claims are approximate until Recast or stronger geometry analysis is active.")
    return notes
