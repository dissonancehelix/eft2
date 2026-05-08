# Tools/Simulation

`tools/simulation/` is a dry-run readiness layer for future EFT2 simulation work.

It does not run gameplay simulation, reinforcement learning, physics, bots, or a gameplay runtime. It connects the evidence rails that must exist before those systems can be trusted:

- scenario definitions in `tools/scenario harness/scenarios/`
- telemetry schemas in `tools/telemetry/events/`
- metric guardrails in `tools/telemetry/metric_guardrails.json`
- map analyzer outputs in `maps/<map>/analysis/`
- virtual perception outputs in `maps/<map>/virtual perception/`
- per-map placeholders or artifacts in `maps/<map>/simulation/`
- real inherited evidence such as `lua/game logs/`

## Commands

```powershell
python "tools/simulation/assess_simulation_readiness.py" --help
python "tools/simulation/assess_simulation_readiness.py" --root .
python "tools/simulation/assess_simulation_readiness.py" --list
python "tools/simulation/assess_simulation_readiness.py" --map "Slam Dunk"
python "tools/simulation/assess_simulation_readiness.py" --map "Bloodbowl"
```

## Outputs

```text
tools/simulation/output/SIMULATION_READINESS.json
tools/simulation/output/SIMULATION_READINESS.md
```

The report answers:

- which scenarios are defined
- which telemetry events each scenario needs
- which map analysis and virtual perception artifacts exist
- which maps have per-map simulation folders or artifacts
- which scenario/map pairs are blocked by missing gameplay runtime
- which telemetry schemas exist but lack a runtime emitter
- which scenario/map pairs should be attempted first later

## Readiness Labels

- `blocked_by_gameplay_runtime`
- `map_ready_but_runtime_missing`
- `telemetry_schema_ready_emitter_missing`
- `scenario_defined`
- `scenario_missing`
- `map_analysis_ready`
- `map_analysis_missing`
- `simulation_placeholder_present`
- `simulation_ready_later`

## First Later Targets

The initial future targets are:

1. `S-021` Slam Dunk Hoop Decision on `Slam Dunk`
2. `S-022` Bloodbowl Flat Swarm on `Bloodbowl`
3. `S-005` Swarm Collapse on `Bloodbowl`
4. `S-009` Head-On Speed Duel on any open map
5. `S-001` Goal-Line Stand on any hybrid map

## Evidence Limits

Existing map analyzer outputs, real `lua/game logs`, and abstract gameflow artifacts are calibration evidence. They are not executable gameplay simulation. The tool must report blockers honestly until a real gameplay runtime and host-side telemetry emitter exist.
