# Tools/Scenario Harness

Encodes must-preserve EFT situations as structured test cases.

## Purpose

Scenario Harness captures the gameplay situations defined in `README.md` (S-001 through S-022) as machine-readable scenario definitions. Each scenario specifies the starting state, the triggering conditions, the expected outcomes, and the contract IDs it validates.

These scenarios form the behavioural test suite for EFT2. They are input to:

- `tools/telemetry/` — event schemas must be rich enough to detect each scenario
- `tools/simulation/` — simulation must be able to reproduce each scenario
- `Game/` — implementation must pass each scenario's expected-outcome check

## Schema

See `scenario_schema.md` for the full schema definition.

## CLI

```
python "tools/scenario harness/run_scenarios.py" --help
python "tools/scenario harness/run_scenarios.py" --list
python "tools/scenario harness/run_scenarios.py" --validate
```

`--list` prints all defined scenarios and their current status.  
`--validate` checks that scenario files are schema-valid and that all S-NNN IDs in README.md have a corresponding scenario definition.

## Scenario files

Scenarios live in `tools/scenario harness/scenarios/` as individual JSON files named `S-NNN_slug.json`.

## Output

- `tools/scenario harness/Output/SCENARIO_REPORT.json` — validation report
- `tools/scenario harness/Output/SCENARIO_REPORT.md` — human-readable summary

## Build order context

Scenario Harness is step 4 of the infrastructure rails. Telemetry follows.
