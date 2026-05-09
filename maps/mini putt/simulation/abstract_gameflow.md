# mini putt Abstract Gameflow Simulation

This is coarse gameplay telemetry, not a physics replay.

- Trials: 400.
- Score outcome rate: 43.50%.
- Intercept/tackle outcome rate: 39.25%.
- Reset/hazard outcome rate: 4.75%.
- Mean carrier route time: 12.43s.
- Mean defender intercept time: 12.25s.
- Mean preventability margin: 0.18s.

Strongest reads:
- Defenders usually have a timing window before the carrier reaches a scoring route; expect tackles/scrums unless a jump/powerup route changes tempo.
- Scoring pressure outruns interception in the current coarse telemetry.
- Jump/push routes are not decorative; they materially reduce carrier route time in the model and should become s&box NavMeshLink/custom traversal candidates.
