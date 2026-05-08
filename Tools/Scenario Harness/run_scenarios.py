"""EFT2 Scenario Harness.

Validates scenario definitions against the EFT2 game contract and emits
structured reports.

Run from repo root:

    python "Tools/Scenario Harness/run_scenarios.py" --help
    python "Tools/Scenario Harness/run_scenarios.py" --list
    python "Tools/Scenario Harness/run_scenarios.py" --validate
    python "Tools/Scenario Harness/run_scenarios.py" --validate --strict
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
SCENARIOS_DIR = HERE / "scenarios"
OUTPUT_DIR = HERE / "Output"
GENERATOR = "Tools/Scenario Harness"
SCHEMA_VERSION = 1

# Required top-level fields in every scenario file.
REQUIRED_FIELDS = {
    "schema_version", "id", "slug", "title", "contract_refs",
    "map_scope", "description", "preconditions", "trigger",
    "expected_outcomes", "must_not_outcomes", "mechanic_tags",
    "simulation_ready", "telemetry_events_required", "status",
}

ID_RE = re.compile(r"^S-\d{3}$")
VALID_STATUSES = {"defined", "needs_review", "validated"}

# Expected S-NNN IDs extracted from README.md (hard-coded from contract).
EXPECTED_IDS = {
    "S-001", "S-002", "S-003", "S-004", "S-005", "S-006", "S-007",
    "S-008", "S-009", "S-010", "S-011", "S-012", "S-013", "S-014",
    "S-015", "S-016", "S-017", "S-018", "S-019", "S-020", "S-021",
    "S-022",
}


# ---------------------------------------------------------------------------
# Load scenarios
# ---------------------------------------------------------------------------

def load_scenarios() -> tuple[list[dict[str, Any]], list[str]]:
    """Return (scenarios, errors). errors is empty on clean load."""
    scenarios: list[dict[str, Any]] = []
    errors: list[str] = []

    if not SCENARIOS_DIR.is_dir():
        errors.append(f"scenarios/ directory not found at {SCENARIOS_DIR}")
        return scenarios, errors

    for path in sorted(SCENARIOS_DIR.glob("S-*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            data["_source_path"] = str(path.relative_to(HERE.parent.parent))
            scenarios.append(data)
        except (OSError, json.JSONDecodeError) as e:
            errors.append(f"Failed to load {path.name}: {e}")

    return scenarios, errors


# ---------------------------------------------------------------------------
# Validate scenarios
# ---------------------------------------------------------------------------

def validate_scenario(s: dict[str, Any]) -> list[dict[str, Any]]:
    """Return list of finding dicts for a single scenario."""
    findings: list[dict[str, Any]] = []
    sid = s.get("id", "<unknown>")

    def err(msg: str):
        findings.append({"severity": "error", "id": sid, "message": msg})

    def warn(msg: str):
        findings.append({"severity": "warning", "id": sid, "message": msg})

    # Required fields
    missing = REQUIRED_FIELDS - set(s.keys())
    for field in sorted(missing):
        err(f"Missing required field: '{field}'")

    # ID format
    if not ID_RE.match(str(s.get("id", ""))):
        err(f"id '{s.get('id')}' does not match S-NNN pattern")

    # Status
    if s.get("status") not in VALID_STATUSES:
        err(f"status '{s.get('status')}' is not one of {sorted(VALID_STATUSES)}")

    # expected_outcomes: at least one required=True
    outcomes = s.get("expected_outcomes") or []
    if not outcomes:
        warn("No expected_outcomes defined")
    elif not any(o.get("required") for o in outcomes):
        warn("No expected_outcome has required=true")

    # must_not_outcomes: non-empty recommended
    if not (s.get("must_not_outcomes") or []):
        warn("No must_not_outcomes defined — consider adding at least one P-900-aligned constraint")

    # telemetry_events_required: non-empty recommended
    if not (s.get("telemetry_events_required") or []):
        warn("No telemetry_events_required listed — add at least the events needed to detect this scenario")

    # mechanic_tags: non-empty
    if not (s.get("mechanic_tags") or []):
        warn("No mechanic_tags — at least one EFT mechanic tag should be present")

    # contract_refs: warn if empty and not a map-specific scenario
    if not (s.get("contract_refs") or []) and s.get("map_scope") == "any":
        warn("No contract_refs — consider linking to at least one C-NNN, P-NNN, or M-NNN ID")

    return findings


def validate_coverage(scenarios: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Check that all expected S-NNN IDs have definitions."""
    findings: list[dict[str, Any]] = []
    defined_ids = {s["id"] for s in scenarios if "id" in s}

    for sid in sorted(EXPECTED_IDS - defined_ids):
        findings.append({
            "severity": "error",
            "id": sid,
            "message": f"Contract scenario {sid} is defined in README.md but has no scenario file in scenarios/",
        })

    for sid in sorted(defined_ids - EXPECTED_IDS):
        findings.append({
            "severity": "warning",
            "id": sid,
            "message": f"Scenario {sid} has a definition but is not in the expected README.md list — may be new",
        })

    return findings


# ---------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------

def render_report_md(
    scenarios: list[dict[str, Any]],
    findings: list[dict[str, Any]],
    load_errors: list[str],
) -> str:
    lines = ["# EFT2 Scenario Harness Report", ""]
    lines.append(f"Generated by `{GENERATOR}` — {datetime.now(timezone.utc).isoformat()}")
    lines.append("")

    errors = [f for f in findings if f["severity"] == "error"]
    warnings = [f for f in findings if f["severity"] == "warning"]
    lines.append(f"**Scenarios loaded:** {len(scenarios)}")
    lines.append(f"**Findings:** {len(errors)} error(s), {len(warnings)} warning(s)")
    lines.append("")

    if load_errors:
        lines.append("## Load errors")
        for e in load_errors:
            lines.append(f"- {e}")
        lines.append("")

    if errors:
        lines.append("## Errors (must fix)")
        for f in errors:
            lines.append(f"- **[{f['id']}]** {f['message']}")
        lines.append("")

    if warnings:
        lines.append("## Warnings")
        for f in warnings:
            lines.append(f"- [{f['id']}] {f['message']}")
        lines.append("")

    lines.append("## Scenario inventory")
    lines.append("")
    lines.append("| ID | Title | Map | Status | Sim Ready |")
    lines.append("|---|---|---|---|---|")
    for s in sorted(scenarios, key=lambda x: x.get("id", "")):
        sim = "yes" if s.get("simulation_ready") else "no"
        lines.append(
            f"| {s.get('id','')} | {s.get('title','')} | "
            f"{s.get('map_scope','')} | {s.get('status','')} | {sim} |"
        )
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def cmd_list(scenarios: list[dict[str, Any]]) -> int:
    print(f"{'ID':<8} {'Title':<42} {'Map':<12} {'Status':<14} SimReady")
    print("-" * 90)
    for s in sorted(scenarios, key=lambda x: x.get("id", "")):
        sim = "yes" if s.get("simulation_ready") else "no"
        print(
            f"{s.get('id',''):<8} {s.get('title',''):<42} "
            f"{s.get('map_scope',''):<12} {s.get('status',''):<14} {sim}"
        )
    print(f"\n{len(scenarios)} scenario(s) loaded from {SCENARIOS_DIR}")
    return 0


def cmd_validate(scenarios: list[dict[str, Any]], load_errors: list[str], strict: bool, verbose: bool) -> int:
    findings: list[dict[str, Any]] = []

    for s in scenarios:
        findings.extend(validate_scenario(s))

    findings.extend(validate_coverage(scenarios))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    report = {
        "generated_by": GENERATOR,
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scenario_count": len(scenarios),
        "load_error_count": len(load_errors),
        "load_errors": load_errors,
        "finding_count": len(findings),
        "error_count": sum(1 for f in findings if f["severity"] == "error"),
        "warning_count": sum(1 for f in findings if f["severity"] == "warning"),
        "findings": findings,
        "scenarios": [
            {k: v for k, v in s.items() if not k.startswith("_")}
            for s in sorted(scenarios, key=lambda x: x.get("id", ""))
        ],
    }

    json_path = OUTPUT_DIR / "SCENARIO_REPORT.json"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    md_path = OUTPUT_DIR / "SCENARIO_REPORT.md"
    md_path.write_text(render_report_md(scenarios, findings, load_errors), encoding="utf-8")

    errors = report["error_count"]
    warnings = report["warning_count"]
    print(f"{GENERATOR}: {len(scenarios)} scenario(s), {errors} error(s), {warnings} warning(s) — reports in {OUTPUT_DIR}")

    if verbose:
        for f in findings:
            if f["severity"] in ("error", "warning"):
                print(f"  [{f['severity'].upper()}] [{f['id']}] {f['message']}")

    if errors > 0 or load_errors:
        return 1
    if strict and warnings > 0:
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="EFT2 Scenario Harness — validate scenario definitions against the EFT2 contract."
    )
    p.add_argument("--list", action="store_true", help="Print all defined scenarios.")
    p.add_argument("--validate", action="store_true",
                   help="Validate scenario files and emit reports (default action).")
    p.add_argument("--strict", action="store_true",
                   help="Exit nonzero on warnings as well as errors.")
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args(argv)

    scenarios, load_errors = load_scenarios()

    if args.list:
        return cmd_list(scenarios)

    # Default to --validate if no action specified
    return cmd_validate(scenarios, load_errors, strict=args.strict, verbose=args.verbose)


if __name__ == "__main__":
    sys.exit(main())
