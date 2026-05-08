# Tools/Telemetry

Defines canonical event schemas and metric guardrails for EFT2 matches and simulations.

## Purpose

Telemetry gives the project evidence-driven tuning. Every time the game runs — in simulation, playtest, or live match — it should emit structured events that let agents check whether the sport's behavioral identity is drifting.

From `README.md`:

> Telemetry exists to preserve the sport during tuning. Metrics diagnose drift; they do not replace feel.

## Contents

| Path | Purpose |
|------|---------|
| `events/` | One JSON schema file per canonical event (E-001..E-023) |
| `event_schema.md` | Full prose schema reference — envelope, field types, extension rules |
| `metric_guardrails.json` | Healthy-ish metric targets from the EFT2 contract |
| `validate_telemetry.py` | CLI — validates event definitions and checks scenario coverage |
| `Output/` | Generated validation reports |

## Canonical events (from README.md Part V)

| E-ID | Event name | Meaning |
|------|-----------|---------|
| E-001 | `TackleResolve` | Two players collide at charge/tackle relevance |
| E-002 | `PossessionTransfer` | Pickup, catch, strip, or reset possession change |
| E-003 | `BallLoose` | Fumble, throw release, reset spawn |
| E-004 | `BallReset` | Hazard, goal, stagnation, or admin/map reset |
| E-005 | `PlayerKnockdown` | Player enters knockdown state |
| E-006 | `PlayerRecovered` | Player returns to upright participation |
| E-007 | `GoalScored` | Scoring condition satisfied |
| E-008 | `ThrowAttempt` | Carrier enters or releases throw commitment |
| E-009 | `DiveAttempt` | Player commits to a dive |
| E-010 | `HeadOn` | Matched or near-matched frontal charge collision |
| E-011 | `HazardContact` | Player or ball touches hazard or reset-relevant volume |
| E-012 | `PowerupActivated` | Ball or player enters powerup state |
| E-013 | `ScrumDetected` | Local high-density contested ball event (analytic) |
| E-014 | `RouteBreakout` | Possession escapes high-density conflict into open route (analytic) |

## Extended events (required by Scenario Harness, not yet in contract)

| E-ID | Event name | Meaning |
|------|-----------|---------|
| E-015 | `BallBounce` | Ball contacts a surface and reflects |
| E-016 | `BallLanded` | Ball comes to rest or terminal bounce after being loose |
| E-017 | `PlayerAirborne` | Player becomes airborne |
| E-018 | `PlayerDeath` | Player is eliminated (death/void) |
| E-019 | `PlayerRespawn` | Player respawns after death |
| E-020 | `PlayerRejoinsContest` | Respawned player enters contest proximity |
| E-021 | `BotDecision` | Bot AI makes a movement or targeting decision (debug/sim) |
| E-022 | `CarrierDirectionChange` | Carrier changes movement direction significantly |
| E-023 | `ScoringMethodDetected` | Map analyzer or game identifies the scoring method used |

## Scenario event name aliases

The Scenario Harness was written before canonical event names were locked. The following aliases resolve to canonical events:

| Scenario name | Canonical name |
|---|---|
| `GoalScore` | `GoalScored` (E-007) |
| `KnockdownEvent` | `PlayerKnockdown` (E-005) |
| `HeadOnCollision` | `HeadOn` (E-010) |
| `HazardTrigger` | `HazardContact` (E-011) |
| `PowerupPickup` | `PowerupActivated` (E-012) |

## Metric guardrails

See `metric_guardrails.json`. These are drift alarms, not laws. A match outside these ranges warrants investigation — not automatic rejection.

## CLI

```
python "Tools/Telemetry/validate_telemetry.py" --help
python "Tools/Telemetry/validate_telemetry.py" --validate
python "Tools/Telemetry/validate_telemetry.py" --list
```

## Build order context

Telemetry is step 5 of the infrastructure rails. Simulation follows when map analysis, observation artifacts, scenarios, and these schemas are all stable.
