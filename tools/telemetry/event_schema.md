# Telemetry Event Schema

**Version:** 1  
**Status:** stable — 23 canonical events defined

---

## Event envelope

Every telemetry event emitted by EFT2 wraps its payload in a standard envelope:

```json
{
  "event": "TackleResolve",
  "event_id": "E-001",
  "schema_version": 1,
  "match_id": "<UUID or session ID>",
  "tick": 1240,
  "timestamp_sec": 24.8,
  "map": "Slam Dunk",
  "payload": { ... }
}
```

### Envelope fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `event` | string | yes | Canonical event name (e.g. `TackleResolve`) |
| `event_id` | string | yes | E-NNN identifier |
| `schema_version` | int | yes | Always 1 for this schema version |
| `match_id` | string | yes | Unique session/match identifier |
| `tick` | int | yes | Server tick at event emission |
| `timestamp_sec` | float | yes | Seconds elapsed since match start |
| `map` | string | yes | Canonical map name |
| `payload` | object | yes | Event-specific data (see per-event schemas below) |

---

## Common payload sub-types

### `PlayerRef`
```json
{ "player_id": "p1", "team": "red | blue", "position": [x, y, z], "speed": 312.5 }
```

### `BallRef`
```json
{ "position": [x, y, z], "velocity": [vx, vy, vz], "speed": 180.0 }
```

---

## Per-event payload schemas

### E-001 TackleResolve

Emitted when two players collide at charge/tackle relevance threshold.

```json
{
  "initiator": PlayerRef,
  "target": PlayerRef,
  "outcome": "win | lose | mutual | graze",
  "speed_delta": 45.0,
  "ball_state_after": "loose | transferred | retained | unchanged",
  "head_on": true
}
```

`outcome` values:
- `win` — initiator wins the collision; target knocked down or deflected
- `lose` — target wins; initiator knocked down
- `mutual` — both knocked down (close-speed head-on)
- `graze` — contact too glancing to resolve as a full tackle

---

### E-002 PossessionTransfer

Emitted when ball changes holder or becomes held from loose state.

```json
{
  "from_player": "player_id | null",
  "to_player": "player_id",
  "method": "pickup | catch | strip | reset_grant",
  "ball": BallRef,
  "position": [x, y, z]
}
```

---

### E-003 BallLoose

Emitted when ball leaves a holder without a new holder immediately.

```json
{
  "cause": "fumble | throw | tackle | hazard | reset",
  "from_player": "player_id | null",
  "ball": BallRef
}
```

---

### E-004 BallReset

Emitted when ball is repositioned by a game system (hazard, goal, stagnation, admin).

```json
{
  "reason": "hazard | goal | stagnation | admin | out_of_bounds",
  "reset_position": [x, y, z],
  "previous_position": [x, y, z],
  "previous_holder": "player_id | null"
}
```

---

### E-005 PlayerKnockdown

Emitted when a player enters knockdown state.

```json
{
  "player": PlayerRef,
  "cause": "tackle | head_on | hazard | self",
  "caused_by_player": "player_id | null",
  "ball_held_at_time": true,
  "recovery_position": [x, y, z]
}
```

---

### E-006 PlayerRecovered

Emitted when a knocked-down player returns to upright participation.

```json
{
  "player": PlayerRef,
  "knockdown_duration_sec": 1.4,
  "recovered_speed": 180.0
}
```

---

### E-007 GoalScored

Emitted when a scoring condition is satisfied.

```json
{
  "scoring_team": "red | blue",
  "scorer_player": "player_id | null",
  "scoring_method": "carry | throw | slam | own_goal | other",
  "score_red": 3,
  "score_blue": 2,
  "ball": BallRef,
  "goal_entity_id": "trigger_goal entity ID from VMF"
}
```

---

### E-008 ThrowAttempt

Emitted at throw commitment start and at throw release.

```json
{
  "phase": "windup | release",
  "thrower": PlayerRef,
  "ball": BallRef,
  "target_position": [x, y, z],
  "power": 0.85,
  "arc": "flat | medium | lob"
}
```

---

### E-009 DiveAttempt

Emitted when a player commits to a dive.

```json
{
  "player": PlayerRef,
  "direction": [dx, dy, dz],
  "ball_held": false,
  "outcome": "pending | success | miss | interrupted"
}
```

---

### E-010 HeadOn

Emitted for matched or near-matched frontal charge collisions.

```json
{
  "player_a": PlayerRef,
  "player_b": PlayerRef,
  "speed_a": 340.0,
  "speed_b": 335.0,
  "speed_delta": 5.0,
  "classification": "matched | one_sided | near_matched",
  "outcome": "a_wins | b_wins | mutual"
}
```

---

### E-011 HazardContact

Emitted when player or ball touches a hazard or reset-relevant volume.

```json
{
  "contact_type": "player | ball",
  "player": "player_id | null",
  "ball": BallRef,
  "hazard_entity_id": "trigger entity ID from VMF",
  "hazard_class": "trigger_ballreset | trigger_knockdown | void | other",
  "result": "knockdown | ball_reset | death | none"
}
```

---

### E-012 PowerupActivated

Emitted when a player or ball enters a powerup state.

```json
{
  "player": "player_id | null",
  "powerup_type": "speedball | waterball | iceball | scoreball | other",
  "powerup_entity_id": "trigger_powerup entity ID from VMF",
  "ball": BallRef,
  "effect_duration_sec": 10.0
}
```

---

### E-013 ScrumDetected

Analytic event — emitted when a local high-density contested ball event is detected.

```json
{
  "centre": [x, y, z],
  "radius": 150.0,
  "player_count": 5,
  "ball": BallRef,
  "duration_sec": 2.8,
  "outcome": "breakout | reset | stalemate | still_active"
}
```

---

### E-014 RouteBreakout

Analytic event — emitted when possession escapes high-density conflict into open route.

```json
{
  "carrier": PlayerRef,
  "exit_position": [x, y, z],
  "scrum_centre": [x, y, z],
  "carrier_speed": 325.0,
  "nearest_defender_distance": 280.0
}
```

---

### E-015 BallBounce

Emitted when ball contacts a surface and reflects.

```json
{
  "ball": BallRef,
  "surface_normal": [nx, ny, nz],
  "surface_entity": "brush entity ID or 'world'",
  "speed_before": 400.0,
  "speed_after": 320.0,
  "bounce_number": 1
}
```

---

### E-016 BallLanded

Emitted when ball comes to rest or terminal bounce after being loose.

```json
{
  "ball": BallRef,
  "position": [x, y, z],
  "loose_duration_sec": 1.2,
  "bounce_count": 3,
  "in_bounds": true
}
```

---

### E-017 PlayerAirborne

Emitted when a player becomes airborne.

```json
{
  "player": PlayerRef,
  "launch_velocity": [vx, vy, vz],
  "cause": "jump | jumppad | knockback | hazard",
  "ball_held": false
}
```

---

### E-018 PlayerDeath

Emitted when a player is eliminated (death zone, void, or admin kill).

```json
{
  "player": PlayerRef,
  "cause": "void | hazard | admin",
  "ball_held": false,
  "ball_released_position": "[x, y, z] | null"
}
```

---

### E-019 PlayerRespawn

Emitted when a player respawns after death.

```json
{
  "player": PlayerRef,
  "spawn_position": [x, y, z],
  "death_to_respawn_sec": 3.0,
  "nearest_contest_distance": 450.0
}
```

---

### E-020 PlayerRejoinsContest

Emitted when a respawned player enters contest proximity (within ~300 HU of active ball).

```json
{
  "player": PlayerRef,
  "respawn_to_contest_sec": 5.2,
  "ball_position": [x, y, z],
  "player_position": [x, y, z]
}
```

---

### E-021 BotDecision

Debug/simulation event — emitted when a bot AI makes a movement or targeting decision.

```json
{
  "bot": PlayerRef,
  "decision_type": "move_to_ball | move_to_intercept | charge_carrier | retreat | defend_goal",
  "target_position": [x, y, z],
  "confidence": 0.87,
  "reason": "ball_predicted_landing | carrier_visible | teammate_nearby"
}
```

---

### E-022 CarrierDirectionChange

Emitted when a ball carrier changes movement direction by more than a configured threshold.

```json
{
  "player": PlayerRef,
  "direction_before": [dx, dy, dz],
  "direction_after": [dx, dy, dz],
  "angle_delta_deg": 45.0,
  "speed_before": 315.0,
  "speed_after": 290.0,
  "nearest_defender_distance": 120.0
}
```

---

### E-023 ScoringMethodDetected

Emitted by map analyzer or game when it identifies the scoring method used at a goal.

```json
{
  "goal_event_tick": 1240,
  "goal_entity_id": "trigger_goal entity ID",
  "detected_method": "carry | throw | slam | own_goal | unknown",
  "confidence": "high | medium | low",
  "approach_vector": [dx, dy, dz],
  "notes": ""
}
```

---

## Extension rules

1. New events must be added to `events/` with a new E-NNN ID.
2. Existing event payloads may only add optional fields — never remove or rename fields once the schema is published.
3. Analytic events (E-013, E-014, E-021, E-023) may be omitted in production builds; they are required in simulation and dev builds.
4. All position/velocity values use EFT2 world units (HU equivalent). Conversion factors must be documented in the implementation if different.
