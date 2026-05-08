"""Shared constants for the EFT2 simulation readiness tool."""
from __future__ import annotations


GENERATOR = "tools/simulation"
SCHEMA_VERSION = 1

READINESS_LABELS = {
    "blocked_by_gameplay_runtime",
    "map_ready_but_runtime_missing",
    "telemetry_schema_ready_emitter_missing",
    "scenario_defined",
    "scenario_missing",
    "map_analysis_ready",
    "map_analysis_missing",
    "simulation_placeholder_present",
    "simulation_ready_later",
}

INITIAL_TARGETS = [
    {"scenario_id": "S-021", "map": "Slam Dunk", "reason": "Hoop/throw/slam route pressure needs map intelligence before runtime tests."},
    {"scenario_id": "S-022", "map": "Bloodbowl", "reason": "Flat open-field swarm is the cleanest full-gameplay feel benchmark."},
    {"scenario_id": "S-005", "map": "Bloodbowl", "reason": "Swarm collapse maps directly to Bloodbowl's open-field convergence."},
    {"scenario_id": "S-009", "map": "any/open map", "reason": "Head-on speed duel can later validate charge/tackle readability on open layouts."},
    {"scenario_id": "S-001", "map": "any/hybrid map", "reason": "Goal-line stand validates preventability once goals and runtime telemetry exist."},
]

REQUIRED_ANALYSIS_ARTIFACTS = [
    "raw_entities.json",
    "eft_entities.json",
    "spawn_clusters.json",
    "goal_complexes.json",
    "gameplay_profile.json",
    "summary.md",
]

REQUIRED_VIRTUAL_PERCEPTION_ARTIFACTS = [
    "viewpoints.json",
    "route_reads.json",
    "danger_fields.json",
    "gameplay_flow.md",
]

RUNTIME_MARKERS = [
    "Ball.cs",
    "GoalTrigger.cs",
    "PlayerMovement.cs",
    "GameSystem.cs",
    "BallResetTrigger.cs",
]
