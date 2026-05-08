# Baseball Dash Abstract Gameflow Simulation

This is coarse gameplay telemetry, not a physics replay.

- Trials: 400.
- Score outcome rate: 57.75%.
- Intercept/tackle outcome rate: 2.25%.
- Reset/hazard outcome rate: 13.00%.
- Mean carrier route time: 4.44s.
- Mean defender intercept time: 9.70s.
- Mean preventability margin: -5.26s.

Strongest reads:
- Carrier routes often beat first defender timing in this abstract model; expect fast scoring pressure.
- Scoring pressure outruns interception in the current coarse telemetry.
- Jump/push routes are not decorative; they materially reduce carrier route time in the model and should become s&box NavMeshLink/custom traversal candidates.
