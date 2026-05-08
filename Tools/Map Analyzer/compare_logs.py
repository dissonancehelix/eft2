from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

MAP_NAMES = {
    "eft_slamdunk_v6": "Slam Dunk",
    "eft_bloodbowl_v5": "Bloodbowl",
    "eft_baseballdash_v3": "Baseball Dash",
    "eft_legoland_v2": "Legoland",
    "eft_tunnel_v2": "Tunnel",
    "eft_soccer_b4": "Soccer",
    "eft_handegg_r2": "Handegg",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare real Lua game logs to abstract map gameflow telemetry.")
    parser.add_argument("--logs-root", default="Lua/game logs")
    parser.add_argument("--maps-root", default="Maps")
    parser.add_argument("--out", default="Tools/Map Analyzer/log_comparison.json")
    args = parser.parse_args()
    result = compare(Path(args.logs_root), Path(args.maps_root))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Wrote {out}")
    for name, item in result["maps"].items():
        fit = item["fit"]
        if fit["overall"] == "no_simulation":
            print(f"{name}: fit=no_simulation")
        else:
            print(f"{name}: fit={fit['overall']} score_delta={fit['score_rate_delta']:.3f} intercept_delta={fit['intercept_rate_delta']:.3f} reset_delta={fit['reset_rate_delta']:.3f}")
    return 0


def compare(logs_root: Path, maps_root: Path) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for path in sorted(logs_root.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        raw_map = data.get("map", "")
        canonical = MAP_NAMES.get(raw_map, raw_map)
        events = data.get("events", [])
        counts = Counter(event.get("type") for event in events)
        duration_min = max(float(data.get("duration") or 0) / 60.0, 0.001)
        grouped[canonical].append({
            "file": str(path).replace("\\", "/"),
            "raw_map": raw_map,
            "duration_s": data.get("duration"),
            "event_counts": dict(counts),
            "rates_per_min": {k: round(v / duration_min, 4) for k, v in counts.items()},
            "resolution_rates": _resolution_rates(counts),
        })
    maps = {}
    for canonical, logs in grouped.items():
        sim = _load_sim(maps_root, canonical)
        observed = _aggregate_logs(logs)
        maps[canonical] = {
            "log_count": len(logs),
            "logs": logs,
            "observed": observed,
            "simulation": sim,
            "fit": _fit(observed, sim),
        }
    return {
        "status": "log_vs_abstract_gameflow_comparison",
        "comparison_note": "Observed resolution rates normalize goals, tackles/head-ons, and ball resets. This is closer to abstract possession trials than raw per-minute counts, but still not a perfect semantic match.",
        "maps": maps,
    }


def _resolution_rates(counts: Counter) -> dict[str, float]:
    intercept = counts.get("tackle_success", 0) + counts.get("head_on", 0)
    score = counts.get("goal", 0)
    reset = counts.get("ball_reset", 0)
    total = max(score + intercept + reset, 1)
    return {
        "score_rate": score / total,
        "intercept_rate": intercept / total,
        "reset_or_hazard_rate": reset / total,
        "resolution_count": total,
    }


def _aggregate_logs(logs: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter()
    duration = 0.0
    for log in logs:
        counts.update(log["event_counts"])
        duration += float(log.get("duration_s") or 0)
    rates = _resolution_rates(counts)
    duration_min = max(duration / 60.0, 0.001)
    return {
        "duration_s": duration,
        "event_counts": dict(counts),
        "rates_per_min": {k: round(v / duration_min, 4) for k, v in counts.items()},
        "resolution_rates": rates,
    }


def _load_sim(maps_root: Path, canonical: str) -> dict[str, Any] | None:
    path = maps_root / canonical / "Simulation" / "abstract_gameflow.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    agg = data.get("aggregates", {})
    return {
        "path": str(path).replace("\\", "/"),
        "score_rate": agg.get("score_rate"),
        "intercept_rate": agg.get("intercept_rate"),
        "reset_or_hazard_rate": agg.get("reset_or_hazard_rate"),
        "scrum_continues_rate": agg.get("scrum_continues_rate"),
        "mean_preventability_margin_s": agg.get("mean_preventability_margin_s"),
    }


def _fit(observed: dict[str, Any], sim: dict[str, Any] | None) -> dict[str, Any]:
    if not sim:
        return {"overall": "no_simulation"}
    obs = observed["resolution_rates"]
    score_delta = abs(obs["score_rate"] - (sim.get("score_rate") or 0))
    intercept_delta = abs(obs["intercept_rate"] - (sim.get("intercept_rate") or 0))
    reset_delta = abs(obs["reset_or_hazard_rate"] - (sim.get("reset_or_hazard_rate") or 0))
    mean_delta = (score_delta + intercept_delta + reset_delta) / 3.0
    if mean_delta < 0.12:
        overall = "close"
    elif mean_delta < 0.25:
        overall = "directional"
    else:
        overall = "poor"
    return {
        "overall": overall,
        "mean_absolute_delta": mean_delta,
        "score_rate_delta": score_delta,
        "intercept_rate_delta": intercept_delta,
        "reset_rate_delta": reset_delta,
        "observed_resolution_rates": obs,
        "simulation_rates": sim,
    }


if __name__ == "__main__":
    raise SystemExit(main())
