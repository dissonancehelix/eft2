# Temporary Sim Reference Notes

The root `sim/` folder is temporary reference material from an older EFT simulation experiment. Do not treat it as current project structure or as authoritative runtime output.

## Useful Ideas Kept

- deterministic seeded/scripted runs are useful for catching symmetry and order bias
- event logs should be first-class outputs, not console noise
- rule state should be explicit: player position, velocity, carrier state, knockdown timer, ball owner, ball position, score
- first checks should target the core loop before bots, throws, hazards, or map-specific behavior
- map analysis and virtual perception can later provide geometry inputs for rule refinement
- multi-seed balance checks should come after the rule model is grounded in the playable `game/eft2/` implementation

## Ideas Deferred

- tactical bots and archetypes
- Bloodbowl/Slam Dunk map-specific simulation
- hazard weaponization and jump-pad behavior
- passing, throw fakes, dive, punch, power struggle, and item logic
- balance claims from large seed batches

## Current Replacement

`core_loop_model.py` is the project-owned replacement seed:

- mirrors the playable core-loop constants from `game/eft2/`
- emits the same core telemetry event names
- runs a deterministic scripted rule slice
- does not claim real-map simulation
- is suitable for later coupling to analyzed map geometry once a user-directed simulation pass starts
