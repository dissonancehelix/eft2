from __future__ import annotations

import math
import random
from typing import Any

EFT_CONSTANTS = {
    "base_speed_hu_s": 350.0,
    "carrier_speed_hu_s": 262.5,
    "pity_carrier_speed_hu_s": 315.0,
    "strafe_only_speed_hu_s": 160.0,
    "charge_threshold_hu_s": 300.0,
    "time_to_charge_s": 1.0,
    "time_to_max_speed_s": 1.5,
    "post_hit_charge_immunity_s": 0.45,
    "dive_extra_speed_hu_s": 100.0,
    "dive_landing_penalty_multiplier": 0.5,
}


def simulate_gameflow(map_name: str, semantics: dict[str, Any], eft_entities: dict[str, Any], trials: int = 400, seed: int = 2) -> dict[str, Any]:
    rng = random.Random(seed)
    landmarks = _landmarks(semantics, eft_entities)
    route_candidates = _route_candidates(landmarks)
    trial_results = [_simulate_trial(rng, route_candidates, landmarks) for _ in range(trials)]
    aggregates = _aggregate(trial_results)
    return {
        "status": "abstract_core_gameplay_telemetry",
        "model_scope": [
            "Uses README movement constants and extracted map landmarks.",
            "Models possession pressure, carrier exposure, defender intercept opportunity, powerup/jump-route influence, and scoring likelihood.",
            "Does not model real player input, exact ball physics, ragdolls, prop collision, or s&box Scene.NavMesh yet.",
        ],
        "constants": EFT_CONSTANTS,
        "landmarks": landmarks,
        "route_candidates": route_candidates,
        "trials": trials,
        "seed": seed,
        "aggregates": aggregates,
        "sample_trials": trial_results[:25],
        "interpretation": _interpret(map_name, aggregates, route_candidates),
    }


def simulation_summary(map_name: str, sim: dict[str, Any]) -> str:
    agg = sim["aggregates"]
    lines = [
        f"# {map_name} Abstract Gameflow Simulation",
        "",
        "This is coarse gameplay telemetry, not a physics replay.",
        "",
        f"- Trials: {sim['trials']}.",
        f"- Score outcome rate: {agg['score_rate']:.2%}.",
        f"- Intercept/tackle outcome rate: {agg['intercept_rate']:.2%}.",
        f"- Reset/hazard outcome rate: {agg['reset_or_hazard_rate']:.2%}.",
        f"- Mean carrier route time: {agg['mean_carrier_time_s']:.2f}s.",
        f"- Mean defender intercept time: {agg['mean_defender_time_s']:.2f}s.",
        f"- Mean preventability margin: {agg['mean_preventability_margin_s']:.2f}s.",
        "",
        "Strongest reads:",
    ]
    for read in sim["interpretation"]:
        lines.append(f"- {read}")
    return "\n".join(lines)


def _landmarks(semantics: dict[str, Any], eft_entities: dict[str, Any]) -> dict[str, Any]:
    balls = [e for e in eft_entities.get("entities", []) if e.get("classname") == "prop_ball" and e.get("origin")]
    ball = balls[0]["origin"] if balls else None
    return {
        "ball_spawn": ball,
        "red_spawns": semantics.get("spawn_clusters", {}).get("red", []),
        "blue_spawns": semantics.get("spawn_clusters", {}).get("blue", []),
        "goals": semantics.get("goal_complexes", []),
        "powerups": semantics.get("powerup_locations", []),
        "jump_push_regions": semantics.get("jump_push_regions", []),
        "hazards": semantics.get("hazard_regions", []) + semantics.get("reset_regions", []),
    }


def _route_candidates(landmarks: dict[str, Any]) -> list[dict[str, Any]]:
    ball = landmarks.get("ball_spawn")
    if not ball:
        return []
    routes = []
    spawns = [(f"red_spawn_{i + 1}", c) for i, c in enumerate(landmarks["red_spawns"])]
    spawns += [(f"blue_spawn_{i + 1}", c) for i, c in enumerate(landmarks["blue_spawns"])]
    goals = landmarks["goals"] or []
    powerups = landmarks["powerups"]
    jumps = landmarks["jump_push_regions"]
    for spawn_label, spawn in spawns:
        spawn_center = spawn.get("center")
        if not spawn_center:
            continue
        for goal in goals:
            goal_center = goal.get("center")
            if not goal_center:
                continue
            direct_distance = _dist(ball, goal_center)
            support_distance = _dist(spawn_center, ball)
            nearest_powerup = _nearest(ball, goal_center, powerups)
            nearest_jump = _nearest(ball, goal_center, jumps)
            route_type = "direct_carry"
            modifier = 1.0
            influences = []
            if nearest_powerup and nearest_powerup["distance_to_segment"] < 1400:
                route_type = "powerup_influenced_carry"
                modifier *= 0.88
                influences.append(nearest_powerup["region"]["id"])
            if nearest_jump and nearest_jump["distance_to_segment"] < 900:
                route_type = "jump_push_route"
                modifier *= 0.78
                influences.append(nearest_jump["region"]["id"])
            routes.append({
                "id": f"route_{len(routes) + 1}",
                "from_spawn": spawn_label,
                "ball_to_goal": goal.get("id"),
                "route_type": route_type,
                "support_distance_hu": round(support_distance, 2),
                "carrier_distance_hu": round(direct_distance * modifier, 2),
                "raw_ball_to_goal_distance_hu": round(direct_distance, 2),
                "influence_regions": influences,
                "confidence": 0.55 if influences else 0.45,
            })
    return routes


def _simulate_trial(rng: random.Random, routes: list[dict[str, Any]], landmarks: dict[str, Any]) -> dict[str, Any]:
    route = rng.choice(routes) if routes else {}
    carrier_distance = route.get("carrier_distance_hu", 0.0)
    support_distance = route.get("support_distance_hu", 0.0)
    carrier_time = carrier_distance / EFT_CONSTANTS["carrier_speed_hu_s"] if carrier_distance else 999.0
    defender_time = support_distance / EFT_CONSTANTS["base_speed_hu_s"] + EFT_CONSTANTS["time_to_charge_s"]
    pressure = _clamp((carrier_time - defender_time + 1.5) / 4.0, 0.05, 0.95)
    if route.get("route_type") == "jump_push_route":
        pressure *= 0.75
    if route.get("route_type") == "powerup_influenced_carry":
        pressure *= 0.82
    hazard_pressure = _hazard_pressure(route, landmarks)
    score_chance = _clamp(0.58 - pressure * 0.35 - hazard_pressure * 0.25, 0.08, 0.88)
    roll = rng.random()
    if roll < score_chance:
        outcome = "score"
    elif roll < score_chance + pressure:
        outcome = "intercept_or_tackle"
    elif roll < score_chance + pressure + hazard_pressure:
        outcome = "reset_or_hazard"
    else:
        outcome = "scrum_continues"
    return {
        "route_id": route.get("id"),
        "route_type": route.get("route_type"),
        "outcome": outcome,
        "carrier_time_s": round(carrier_time, 3),
        "defender_intercept_time_s": round(defender_time, 3),
        "preventability_margin_s": round(carrier_time - defender_time, 3),
        "pressure": round(pressure, 3),
        "hazard_pressure": round(hazard_pressure, 3),
        "score_chance": round(score_chance, 3),
    }


def _aggregate(results: list[dict[str, Any]]) -> dict[str, Any]:
    if not results:
        return {}
    n = len(results)
    return {
        "score_rate": _rate(results, "score"),
        "intercept_rate": _rate(results, "intercept_or_tackle"),
        "reset_or_hazard_rate": _rate(results, "reset_or_hazard"),
        "scrum_continues_rate": _rate(results, "scrum_continues"),
        "mean_carrier_time_s": _mean(r["carrier_time_s"] for r in results),
        "mean_defender_time_s": _mean(r["defender_intercept_time_s"] for r in results),
        "mean_preventability_margin_s": _mean(r["preventability_margin_s"] for r in results),
        "route_type_counts": {kind: sum(1 for r in results if r.get("route_type") == kind) for kind in sorted({r.get("route_type") for r in results})},
        "trial_count": n,
    }


def _interpret(map_name: str, agg: dict[str, Any], routes: list[dict[str, Any]]) -> list[str]:
    reads = []
    if agg.get("mean_preventability_margin_s", 0) > 0:
        reads.append("Defenders usually have a timing window before the carrier reaches a scoring route; expect tackles/scrums unless a jump/powerup route changes tempo.")
    else:
        reads.append("Carrier routes often beat first defender timing in this abstract model; expect fast scoring pressure.")
    if agg.get("score_rate", 0) > agg.get("intercept_rate", 0):
        reads.append("Scoring pressure outruns interception in the current coarse telemetry.")
    else:
        reads.append("Interception/tackle pressure is at least as important as clean scoring in the current coarse telemetry.")
    if any(r.get("route_type") == "jump_push_route" for r in routes):
        reads.append("Jump/push routes are not decorative; they materially reduce carrier route time in the model and should become s&box NavMeshLink/custom traversal candidates.")
    if any(r.get("route_type") == "powerup_influenced_carry" for r in routes):
        reads.append("Powerup-adjacent routes create tempo changes and should be tracked as route-value telemetry.")
    if map_name == "Slam Dunk":
        reads.append("Slam Dunk reads as a high-tempo scoring map with route interruption windows, not a simple open-field carry map.")
    return reads


def _nearest(start: list[float], end: list[float], regions: list[dict[str, Any]]) -> dict[str, Any] | None:
    best = None
    for region in regions:
        center = region.get("center")
        if not center:
            continue
        distance = _point_segment_distance(center, start, end)
        if best is None or distance < best["distance_to_segment"]:
            best = {"region": region, "distance_to_segment": distance}
    return best


def _hazard_pressure(route: dict[str, Any], landmarks: dict[str, Any]) -> float:
    if not route or not landmarks.get("hazards"):
        return 0.02
    return 0.12 if route.get("route_type") == "jump_push_route" else 0.07


def _rate(results: list[dict[str, Any]], outcome: str) -> float:
    return sum(1 for r in results if r["outcome"] == outcome) / len(results)


def _mean(values) -> float:
    vals = list(values)
    return round(sum(vals) / len(vals), 4) if vals else 0.0


def _dist(a: list[float], b: list[float]) -> float:
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


def _point_segment_distance(point: list[float], start: list[float], end: list[float]) -> float:
    seg = [end[i] - start[i] for i in range(3)]
    length2 = sum(v * v for v in seg)
    if length2 == 0:
        return _dist(point, start)
    t = _clamp(sum((point[i] - start[i]) * seg[i] for i in range(3)) / length2, 0.0, 1.0)
    projected = [start[i] + seg[i] * t for i in range(3)]
    return _dist(point, projected)


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))
