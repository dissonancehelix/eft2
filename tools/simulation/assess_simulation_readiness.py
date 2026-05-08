"""EFT2 dry-run simulation readiness assessor.

This is not a simulator. It connects scenario definitions, telemetry schemas,
map analysis outputs, virtual perception artifacts, per-map simulation folders,
and gameplay-runtime blockers so future simulation work starts from evidence
instead of invented results.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from exporters import write_json, write_markdown
from schemas import (
    GENERATOR,
    INITIAL_TARGETS,
    REQUIRED_ANALYSIS_ARTIFACTS,
    REQUIRED_VIRTUAL_PERCEPTION_ARTIFACTS,
    RUNTIME_MARKERS,
    SCHEMA_VERSION,
)


OUTPUT_DIR = Path("tools") / "simulation" / "output"


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def normalize(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value.replace("_", " ").replace("-", " ")).strip().lower()


def load_json_files(folder: Path, pattern: str) -> tuple[list[dict[str, Any]], list[str]]:
    rows: list[dict[str, Any]] = []
    errors: list[str] = []
    if not folder.is_dir():
        return rows, [f"missing folder: {folder.as_posix()}"]
    for path in sorted(folder.glob(pattern)):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            data["_source_path"] = path
            rows.append(data)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"failed to load {path.name}: {exc}")
    return rows, errors


def load_manifest(root: Path) -> dict[str, Any]:
    path = root / "maps" / "source_manifest.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def actual_map_dirs(root: Path) -> list[Path]:
    maps_root = root / "maps"
    if not maps_root.is_dir():
        return []
    ignored = {"shared", "_unsorted", "__pycache__"}
    return [p for p in sorted(maps_root.iterdir(), key=lambda x: x.name.lower()) if p.is_dir() and p.name.lower() not in ignored]


def map_display_name(path: Path, manifest: dict[str, Any]) -> str:
    norm = normalize(path.name)
    for key, row in manifest.items():
        candidates = {
            normalize(key),
            normalize(row.get("canonical_display_name")),
            normalize(row.get("folder_name")),
        }
        if norm in candidates:
            return row.get("canonical_display_name") or key
    return " ".join(part.capitalize() for part in path.name.split())


def find_child_dir(map_dir: Path, wanted: str) -> Path:
    wanted_norm = normalize(wanted)
    for child in map_dir.iterdir():
        if child.is_dir() and normalize(child.name) == wanted_norm:
            return child
    return map_dir / wanted


def analyze_map(root: Path, map_dir: Path, manifest: dict[str, Any], runtime_present: bool) -> dict[str, Any]:
    name = map_display_name(map_dir, manifest)
    analysis_dir = find_child_dir(map_dir, "analysis")
    vp_dir = find_child_dir(map_dir, "virtual perception")
    sim_dir = find_child_dir(map_dir, "simulation")

    analysis_files = {p.name.lower(): rel(p, root) for p in analysis_dir.glob("*") if p.is_file()} if analysis_dir.is_dir() else {}
    vp_files = {p.name.lower(): rel(p, root) for p in vp_dir.glob("*") if p.is_file()} if vp_dir.is_dir() else {}
    sim_files = {p.name.lower(): rel(p, root) for p in sim_dir.glob("*") if p.is_file()} if sim_dir.is_dir() else {}

    missing_analysis = [name for name in REQUIRED_ANALYSIS_ARTIFACTS if name.lower() not in analysis_files]
    missing_vp = [name for name in REQUIRED_VIRTUAL_PERCEPTION_ARTIFACTS if name.lower() not in vp_files]

    analysis_ready = not missing_analysis and not missing_vp
    labels = []
    labels.append("map_analysis_ready" if analysis_ready else "map_analysis_missing")
    if sim_dir.is_dir():
        labels.append("simulation_placeholder_present")
    if analysis_ready and not runtime_present:
        labels.append("map_ready_but_runtime_missing")
    if analysis_ready and runtime_present:
        labels.append("simulation_ready_later")

    return {
        "map": name,
        "map_dir": rel(map_dir, root),
        "labels": labels,
        "analysis_dir": rel(analysis_dir, root),
        "virtual_perception_dir": rel(vp_dir, root),
        "simulation_dir": rel(sim_dir, root),
        "analysis_artifacts_present": sorted(analysis_files.values()),
        "virtual_perception_artifacts_present": sorted(vp_files.values()),
        "simulation_artifacts_present": sorted(sim_files.values()),
        "missing_analysis_requirements": missing_analysis,
        "missing_virtual_perception_requirements": missing_vp,
    }


def event_lookup(events: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    lookup: dict[str, dict[str, Any]] = {}
    for event in events:
        if event.get("event"):
            lookup[normalize(event["event"])] = event
        for alias in event.get("aliases") or []:
            lookup[normalize(alias)] = event
    return lookup


def scenario_rows(scenarios: list[dict[str, Any]], events: list[dict[str, Any]], runtime_present: bool, emitter_present: bool) -> list[dict[str, Any]]:
    lookup = event_lookup(events)
    rows = []
    for scenario in sorted(scenarios, key=lambda s: s.get("id", "")):
        required = scenario.get("telemetry_events_required") or []
        missing = [name for name in required if normalize(name) not in lookup]
        ready_events = [name for name in required if normalize(name) in lookup]
        labels = ["scenario_defined"]
        if missing:
            labels.append("telemetry_schema_missing")
        elif required and not emitter_present:
            labels.append("telemetry_schema_ready_emitter_missing")
        if not runtime_present:
            labels.append("blocked_by_gameplay_runtime")
        if scenario.get("simulation_ready") is True and runtime_present and emitter_present and not missing:
            labels.append("simulation_ready_later")
        rows.append({
            "id": scenario.get("id"),
            "slug": scenario.get("slug"),
            "title": scenario.get("title"),
            "map_scope": scenario.get("map_scope"),
            "source_path": rel(Path(scenario["_source_path"]), Path.cwd()) if scenario.get("_source_path") else None,
            "labels": labels,
            "telemetry_events_required": required,
            "telemetry_schema_ready": ready_events,
            "missing_telemetry_events": missing,
            "simulation_ready_flag": scenario.get("simulation_ready"),
            "status": scenario.get("status"),
        })
    return rows


def gameplay_runtime_status(root: Path) -> dict[str, Any]:
    game_code = root / "game" / "eft2" / "Code"
    marker_hits = []
    if game_code.is_dir():
        files = {p.name for p in game_code.rglob("*.cs")}
        marker_hits = sorted(marker for marker in RUNTIME_MARKERS if marker in files)
    present = len(marker_hits) >= 3
    return {
        "present": present,
        "code_dir": rel(game_code, root),
        "marker_hits": marker_hits,
        "missing_markers": [marker for marker in RUNTIME_MARKERS if marker not in marker_hits],
        "rule": "requires at least three core EFT gameplay runtime markers before scenarios can be executable",
    }


def telemetry_emitter_status(root: Path) -> dict[str, Any]:
    candidates = []
    for base in [root / "game", root / "tools"]:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".cs", ".py"}:
                if path.name.lower() in {"validate_telemetry.py", "assess_simulation_readiness.py"}:
                    continue
                try:
                    text = path.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                if "EmitTelemetry" in text or "TelemetryEmitter" in text or "emit_event" in text:
                    candidates.append(rel(path, root))
    return {
        "present": bool(candidates),
        "candidate_files": sorted(candidates),
        "rule": "requires an actual gameplay/runtime emitter, not just telemetry schema validators",
    }


def candidate_matrix(targets: list[dict[str, str]], scenarios: dict[str, dict[str, Any]], maps: dict[str, dict[str, Any]], runtime_present: bool) -> list[dict[str, Any]]:
    rows = []
    for target in targets:
        sid = target["scenario_id"]
        map_name = target["map"]
        scenario = scenarios.get(sid)
        map_row = maps.get(normalize(map_name))
        labels = []
        labels.append("scenario_defined" if scenario else "scenario_missing")
        if map_row:
            labels.extend(label for label in map_row["labels"] if label in {"map_analysis_ready", "map_analysis_missing", "simulation_placeholder_present", "map_ready_but_runtime_missing"})
        elif map_name.startswith("any/"):
            labels.append("map_selection_needed")
        else:
            labels.append("map_analysis_missing")
        if not runtime_present:
            labels.append("blocked_by_gameplay_runtime")
        status = "ready_later_after_runtime" if scenario and map_row and "map_analysis_ready" in map_row["labels"] and runtime_present else "blocked"
        rows.append({
            "scenario_id": sid,
            "map": map_name,
            "labels": sorted(set(labels)),
            "status": status,
            "reason": target["reason"],
        })
    return rows


def build_report(root: Path, map_filter: str | None = None) -> dict[str, Any]:
    scenarios, scenario_errors = load_json_files(root / "tools" / "scenario harness" / "scenarios", "S-*.json")
    events, event_errors = load_json_files(root / "tools" / "telemetry" / "events", "E_*.json")
    manifest = load_manifest(root)
    runtime = gameplay_runtime_status(root)
    emitter = telemetry_emitter_status(root)

    map_rows_all = [analyze_map(root, d, manifest, runtime["present"]) for d in actual_map_dirs(root)]
    if map_filter:
        wanted = normalize(map_filter)
        map_rows = [m for m in map_rows_all if normalize(m["map"]) == wanted or normalize(Path(m["map_dir"]).name) == wanted]
    else:
        map_rows = map_rows_all

    scenario_readiness = scenario_rows(scenarios, events, runtime["present"], emitter["present"])
    scenario_by_id = {row["id"]: row for row in scenario_readiness if row.get("id")}
    map_by_name = {normalize(row["map"]): row for row in map_rows_all}
    matrix = candidate_matrix(INITIAL_TARGETS, scenario_by_id, map_by_name, runtime["present"])

    blockers = []
    if scenario_errors:
        blockers.append({"id": "scenario_load_errors", "message": "; ".join(scenario_errors)})
    if event_errors:
        blockers.append({"id": "telemetry_load_errors", "message": "; ".join(event_errors)})
    if not runtime["present"]:
        blockers.append({"id": "gameplay_runtime_missing", "message": "No executable EFT gameplay runtime was detected under game/eft2/Code."})
    if not emitter["present"]:
        blockers.append({"id": "telemetry_emitter_missing", "message": "Telemetry schemas exist, but no gameplay/runtime emitter was detected."})

    report = {
        "generated_by": GENERATOR,
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": ".",
        "map_filter": map_filter,
        "warnings": [
            "This report is simulation readiness only.",
            "Do not treat existing abstract gameflow artifacts as live simulation results.",
        ],
        "summary": {
            "scenarios_defined": len(scenarios),
            "telemetry_events_defined": len(events),
            "candidate_maps": len(map_rows_all),
            "reported_maps": len(map_rows),
            "map_analysis_ready": sum(1 for row in map_rows_all if "map_analysis_ready" in row["labels"]),
            "reported_map_analysis_ready": sum(1 for row in map_rows if "map_analysis_ready" in row["labels"]),
            "gameplay_runtime_present": runtime["present"],
            "telemetry_emitter_present": emitter["present"],
        },
        "gameplay_runtime": runtime,
        "telemetry_emitter": emitter,
        "metric_guardrails_present": (root / "tools" / "telemetry" / "metric_guardrails.json").exists(),
        "blockers": blockers,
        "scenario_readiness": scenario_readiness,
        "map_readiness": map_rows,
        "candidate_matrix": matrix,
        "recommended_first_targets": matrix,
        "inputs": {
            "scenarios": "tools/scenario harness/scenarios/",
            "telemetry_events": "tools/telemetry/events/",
            "metric_guardrails": "tools/telemetry/metric_guardrails.json",
            "maps": "maps/",
            "map_manifest": "maps/source_manifest.json",
            "lua_game_logs": "lua/game logs/",
        },
    }
    return report


def print_list(report: dict[str, Any]) -> None:
    print("Scenarios:")
    for row in report["scenario_readiness"]:
        print(f"  {row['id']} {row['title']} [{', '.join(row['labels'])}]")
    print("\nMaps:")
    for row in report["map_readiness"]:
        print(f"  {row['map']} [{', '.join(row['labels'])}]")
    print("\nRecommended first targets:")
    for row in report["recommended_first_targets"]:
        print(f"  {row['scenario_id']} on {row['map']} [{row['status']}]")


def main() -> int:
    parser = argparse.ArgumentParser(description="Assess EFT2 simulation readiness without running gameplay simulation.")
    parser.add_argument("--root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--map", dest="map_filter", help="Optional canonical map name filter, e.g. 'Slam Dunk'.")
    parser.add_argument("--list", action="store_true", help="Print scenario/map readiness list after writing outputs.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    report = build_report(root, args.map_filter)
    output_dir = root / OUTPUT_DIR
    write_json(output_dir / "SIMULATION_READINESS.json", report)
    write_markdown(output_dir / "SIMULATION_READINESS.md", report)
    if args.list:
        print_list(report)
    else:
        print(f"Scenarios defined: {report['summary']['scenarios_defined']}")
        print(f"Maps ready: {report['summary']['reported_map_analysis_ready']} / {report['summary']['reported_maps']} reported ({report['summary']['map_analysis_ready']} / {report['summary']['candidate_maps']} total)")
        print(f"Gameplay runtime present: {report['summary']['gameplay_runtime_present']}")
        print(f"Telemetry emitter present: {report['summary']['telemetry_emitter_present']}")
        print(f"Wrote {OUTPUT_DIR.as_posix()}/SIMULATION_READINESS.json")
        print(f"Wrote {OUTPUT_DIR.as_posix()}/SIMULATION_READINESS.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
