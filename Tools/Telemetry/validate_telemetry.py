"""EFT2 Telemetry Validator.

Validates event schema definitions and checks cross-coverage with the Scenario
Harness and the EFT2 contract.

Run from repo root:

    python "Tools/Telemetry/validate_telemetry.py" --help
    python "Tools/Telemetry/validate_telemetry.py" --list
    python "Tools/Telemetry/validate_telemetry.py" --validate
    python "Tools/Telemetry/validate_telemetry.py" --validate --strict
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
EVENTS_DIR = HERE / "events"
OUTPUT_DIR = HERE / "Output"
SCENARIOS_DIR = Path(__file__).resolve().parent.parent / "Scenario Harness" / "scenarios"
GUARDRAILS_PATH = HERE / "metric_guardrails.json"
GENERATOR = "Tools/Telemetry"
SCHEMA_VERSION = 1

# Canonical event names from README.md Part V.
README_CANONICAL = {
    "TackleResolve", "PossessionTransfer", "BallLoose", "BallReset",
    "PlayerKnockdown", "PlayerRecovered", "GoalScored", "ThrowAttempt",
    "DiveAttempt", "HeadOn", "HazardContact", "PowerupActivated",
    "ScrumDetected", "RouteBreakout",
}

REQUIRED_FIELDS = {
    "schema_version", "event_id", "event", "category", "description",
    "contract_refs", "payload_fields", "emit_in_production",
    "emit_in_simulation", "emit_in_dev",
}

EVENT_ID_RE = re.compile(r"^E-\d{3}$")
VALID_CATEGORIES = {
    "canonical", "canonical_analytic", "extended", "extended_analytic",
}


# ---------------------------------------------------------------------------
# Alias resolution
# ---------------------------------------------------------------------------

def build_alias_map(events: list[dict[str, Any]]) -> dict[str, str]:
    """Map alias name -> canonical event name."""
    result: dict[str, str] = {}
    for e in events:
        for alias in e.get("aliases") or []:
            result[alias] = e["event"]
    return result


# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------

def load_events() -> tuple[list[dict[str, Any]], list[str]]:
    events: list[dict[str, Any]] = []
    errors: list[str] = []
    if not EVENTS_DIR.is_dir():
        errors.append(f"events/ directory not found: {EVENTS_DIR}")
        return events, errors
    for path in sorted(EVENTS_DIR.glob("E_*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            data["_source"] = path.name
            events.append(data)
        except (OSError, json.JSONDecodeError) as e:
            errors.append(f"Failed to load {path.name}: {e}")
    return events, errors


def load_scenarios() -> list[dict[str, Any]]:
    scenarios: list[dict[str, Any]] = []
    if not SCENARIOS_DIR.is_dir():
        return scenarios
    for path in sorted(SCENARIOS_DIR.glob("S-*.json")):
        try:
            scenarios.append(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            pass
    return scenarios


def load_guardrails() -> dict[str, Any] | None:
    if not GUARDRAILS_PATH.exists():
        return None
    try:
        return json.loads(GUARDRAILS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_event(e: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    eid = e.get("event_id", "<unknown>")

    def err(msg: str):
        findings.append({"severity": "error", "event_id": eid, "message": msg})

    def warn(msg: str):
        findings.append({"severity": "warning", "event_id": eid, "message": msg})

    missing = REQUIRED_FIELDS - set(e.keys())
    for f in sorted(missing):
        err(f"Missing required field: '{f}'")

    if not EVENT_ID_RE.match(str(eid)):
        err(f"event_id '{eid}' does not match E-NNN pattern")

    if e.get("category") not in VALID_CATEGORIES:
        err(f"category '{e.get('category')}' not in {sorted(VALID_CATEGORIES)}")

    if not e.get("description", "").strip():
        warn("description is empty")

    if not e.get("payload_fields"):
        warn("payload_fields is empty — events should define at least their payload shape")

    if e.get("category") in ("canonical", "canonical_analytic"):
        if e.get("event") not in README_CANONICAL:
            warn(f"Event '{e.get('event')}' has canonical category but is not in README.md Part V event list")

    return findings


def validate_readme_coverage(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    defined_names = {e["event"] for e in events if "event" in e}
    alias_map = build_alias_map(events)
    all_known = defined_names | set(alias_map.keys())
    findings: list[dict[str, Any]] = []
    for name in sorted(README_CANONICAL - defined_names):
        findings.append({
            "severity": "error",
            "event_id": "coverage",
            "message": f"README.md canonical event '{name}' has no event definition file",
        })
    return findings


def validate_scenario_coverage(
    events: list[dict[str, Any]],
    scenarios: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Check that every event name required by any scenario is defined or aliased."""
    defined_names = {e["event"] for e in events if "event" in e}
    alias_map = build_alias_map(events)
    all_known = defined_names | set(alias_map.keys())

    findings: list[dict[str, Any]] = []
    for s in scenarios:
        sid = s.get("id", "?")
        for ev_name in s.get("telemetry_events_required") or []:
            if ev_name not in all_known:
                findings.append({
                    "severity": "warning",
                    "event_id": "scenario_coverage",
                    "message": (
                        f"Scenario {sid} requires telemetry event '{ev_name}' "
                        f"which is not defined or aliased in events/"
                    ),
                })
            elif ev_name in alias_map:
                # It's an alias — note it but not an error
                findings.append({
                    "severity": "info",
                    "event_id": "alias",
                    "message": (
                        f"Scenario {sid} uses alias '{ev_name}' "
                        f"→ canonical '{alias_map[ev_name]}'"
                    ),
                })
    return findings


def validate_guardrails(guardrails: dict[str, Any] | None) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if guardrails is None:
        findings.append({
            "severity": "warning",
            "event_id": "guardrails",
            "message": "metric_guardrails.json not found",
        })
        return findings
    for g in guardrails.get("guardrails") or []:
        if not g.get("healthy_range"):
            findings.append({
                "severity": "warning",
                "event_id": g.get("metric_id", "?"),
                "message": f"Guardrail '{g.get('name')}' has no healthy_range defined",
            })
    return findings


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def render_md(
    events: list[dict[str, Any]],
    findings: list[dict[str, Any]],
    load_errors: list[str],
) -> str:
    lines = ["# EFT2 Telemetry Validation Report", ""]
    lines.append(f"Generated by `{GENERATOR}` — {datetime.now(timezone.utc).isoformat()}")
    lines.append("")

    errors = [f for f in findings if f["severity"] == "error"]
    warnings = [f for f in findings if f["severity"] == "warning"]
    infos = [f for f in findings if f["severity"] == "info"]

    lines.append(f"**Events loaded:** {len(events)}")
    lines.append(f"**Findings:** {len(errors)} error(s), {len(warnings)} warning(s), {len(infos)} info(s)")
    lines.append("")

    if load_errors:
        lines.append("## Load errors")
        for e in load_errors:
            lines.append(f"- {e}")
        lines.append("")

    if errors:
        lines.append("## Errors")
        for f in errors:
            lines.append(f"- **[{f['event_id']}]** {f['message']}")
        lines.append("")

    if warnings:
        lines.append("## Warnings")
        for f in warnings:
            lines.append(f"- [{f['event_id']}] {f['message']}")
        lines.append("")

    if infos:
        lines.append("## Alias notes")
        for f in infos:
            lines.append(f"- {f['message']}")
        lines.append("")

    lines.append("## Event inventory")
    lines.append("")
    lines.append("| E-ID | Event | Category | Production | Scenarios |")
    lines.append("|------|-------|----------|------------|----------|")
    for e in sorted(events, key=lambda x: x.get("event_id", "")):
        prod = "yes" if e.get("emit_in_production") else "no"
        srefs = ", ".join(e.get("scenario_refs") or []) or "—"
        lines.append(
            f"| {e.get('event_id','')} | `{e.get('event','')}` | "
            f"{e.get('category','')} | {prod} | {srefs} |"
        )
    lines.append("")

    lines.append("## Metric guardrails")
    lines.append("")
    gd = load_guardrails()
    if gd:
        lines.append("| G-ID | Metric | Healthy range | Unit |")
        lines.append("|------|--------|--------------|------|")
        for g in gd.get("guardrails") or []:
            r = g.get("healthy_range", {})
            rng = f"{r.get('min','?')} – {r.get('max','?')}"
            lines.append(f"| {g['metric_id']} | {g['name']} | {rng} | {g.get('unit','')} |")
    else:
        lines.append("metric_guardrails.json not found.")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def cmd_list(events: list[dict[str, Any]]) -> int:
    print(f"{'E-ID':<8} {'Event':<28} {'Category':<22} Prod  Scenarios")
    print("-" * 100)
    for e in sorted(events, key=lambda x: x.get("event_id", "")):
        prod = "yes" if e.get("emit_in_production") else "no "
        srefs = " ".join(e.get("scenario_refs") or []) or "—"
        print(
            f"{e.get('event_id',''):<8} {e.get('event',''):<28} "
            f"{e.get('category',''):<22} {prod}   {srefs}"
        )
    print(f"\n{len(events)} event(s) loaded from {EVENTS_DIR}")
    return 0


def cmd_validate(
    events: list[dict[str, Any]],
    scenarios: list[dict[str, Any]],
    load_errors: list[str],
    strict: bool,
    verbose: bool,
) -> int:
    findings: list[dict[str, Any]] = []

    for e in events:
        findings.extend(validate_event(e))

    findings.extend(validate_readme_coverage(events))
    findings.extend(validate_scenario_coverage(events, scenarios))
    findings.extend(validate_guardrails(load_guardrails()))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    errors = [f for f in findings if f["severity"] == "error"]
    warnings = [f for f in findings if f["severity"] == "warning"]

    report = {
        "generated_by": GENERATOR,
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "event_count": len(events),
        "load_error_count": len(load_errors),
        "load_errors": load_errors,
        "finding_count": len(findings),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "findings": findings,
    }

    (OUTPUT_DIR / "TELEMETRY_REPORT.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (OUTPUT_DIR / "TELEMETRY_REPORT.md").write_text(
        render_md(events, findings, load_errors), encoding="utf-8"
    )

    print(
        f"{GENERATOR}: {len(events)} event(s), "
        f"{len(errors)} error(s), {len(warnings)} warning(s) — reports in {OUTPUT_DIR}"
    )

    if verbose:
        for f in findings:
            if f["severity"] in ("error", "warning"):
                print(f"  [{f['severity'].upper()}] [{f['event_id']}] {f['message']}")
        # Always print alias info
        for f in findings:
            if f["severity"] == "info":
                print(f"  [INFO] {f['message']}")

    if errors or load_errors:
        return 1
    if strict and warnings:
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="EFT2 Telemetry Validator — validate event schemas and metric guardrails."
    )
    p.add_argument("--list", action="store_true", help="Print all defined events.")
    p.add_argument("--validate", action="store_true",
                   help="Validate event definitions and emit reports (default action).")
    p.add_argument("--strict", action="store_true",
                   help="Exit nonzero on warnings as well as errors.")
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args(argv)

    events, load_errors = load_events()
    scenarios = load_scenarios()

    if args.list:
        return cmd_list(events)

    return cmd_validate(events, scenarios, load_errors, strict=args.strict, verbose=args.verbose)


if __name__ == "__main__":
    sys.exit(main())
