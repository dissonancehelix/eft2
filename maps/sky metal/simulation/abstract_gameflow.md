# sky metal Abstract Gameflow Simulation

This is coarse gameplay telemetry, not a physics replay.

- Trials: 400.
- Score outcome rate: 46.00%.
- Intercept/tackle outcome rate: 31.00%.
- Reset/hazard outcome rate: 9.50%.
- Mean carrier route time: 14.94s.
- Mean defender intercept time: 14.92s.
- Mean preventability margin: 0.03s.

Strongest reads:
- Defenders usually have a timing window before the carrier reaches a scoring route; expect tackles/scrums unless a jump/powerup route changes tempo.
- Scoring pressure outruns interception in the current coarse telemetry.
- Jump/push routes are not decorative; they materially reduce carrier route time in the model and should become s&box NavMeshLink/custom traversal candidates.
