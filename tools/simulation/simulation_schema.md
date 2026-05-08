# Simulation Readiness Schema

## Envelope

```json
{
  "generated_by": "tools/simulation",
  "schema_version": 1,
  "generated_at": "ISO-8601 timestamp",
  "root": ".",
  "map_filter": null,
  "warnings": [],
  "summary": {},
  "gameplay_runtime": {},
  "telemetry_emitter": {},
  "blockers": [],
  "scenario_readiness": [],
  "map_readiness": [],
  "candidate_matrix": [],
  "recommended_first_targets": [],
  "inputs": {}
}
```

## Scenario Readiness Row

Each row records the scenario id, title, map scope, telemetry requirements, missing telemetry schemas, and readiness labels.

Scenario rows may be `scenario_defined` while still `blocked_by_gameplay_runtime`. That is expected until playable EFT2 mechanics and telemetry emitters exist.

## Map Readiness Row

Each row records the map name, map domain path, analysis folder, virtual perception folder, simulation folder, present artifacts, missing artifacts, and readiness labels.

`map_analysis_ready` means the minimum map analyzer and virtual perception artifacts are present. It does not mean the map can be simulated.

## Candidate Matrix

The matrix joins the first target scenarios with candidate maps. It reports whether the scenario exists, whether map analysis exists, whether a simulation placeholder is present, and whether the pair remains blocked by runtime.

## Evidence Rule

Readiness is not result. A row can identify a promising future scenario/map pair without claiming the gameflow has been simulated.
