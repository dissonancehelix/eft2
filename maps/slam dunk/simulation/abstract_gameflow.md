# Slam Dunk Abstract Gameflow Simulation

This is coarse gameplay telemetry, not a physics replay.

- Trials: 400.
- Score outcome rate: 44.25%.
- Intercept/tackle outcome rate: 34.50%.
- Reset/hazard outcome rate: 11.00%.
- Mean carrier route time: 8.50s.
- Mean defender intercept time: 8.18s.
- Mean preventability margin: 0.32s.

Strongest reads:
- Defenders usually have a timing window before the carrier reaches a scoring route; expect tackles/scrums unless a jump/powerup route changes tempo.
- Scoring pressure outruns interception in the current coarse telemetry.
- Jump/push routes are not decorative; they materially reduce carrier route time in the model and should become s&box NavMeshLink/custom traversal candidates.
- Slam Dunk reads as a high-tempo scoring map with route interruption windows, not a simple open-field carry map.
