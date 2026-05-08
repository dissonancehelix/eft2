# Scenario Schema

**Version:** 1  
**Status:** stable — matches S-001 through S-022 definitions

---

## Scenario envelope

Each scenario file in `scenarios/` has this structure:

```json
{
  "schema_version": 1,
  "id": "S-001",
  "slug": "goal_line_stand",
  "title": "Goal-Line Stand",
  "contract_refs": ["C-001", "C-002", "P-950"],
  "map_scope": "any | Slam Dunk | Bloodbowl | <canonical name>",
  "description": "Carrier is stopped at the goal line by one or more defenders.",
  "preconditions": {
    "ball_state": "carried",
    "carrier_position": "near_goal",
    "defenders_nearby": true,
    "score_proximity": "within_10_units"
  },
  "trigger": "carrier_enters_goal_proximity",
  "expected_outcomes": [
    {
      "outcome_id": "tackle_stops_carrier",
      "description": "Carrier is tackled; ball becomes loose or transferred.",
      "required": true,
      "validates": ["volatile_possession", "carrier_danger"]
    },
    {
      "outcome_id": "goal_scored_despite_defense",
      "description": "Carrier reaches goal zone despite defenders — score registered.",
      "required": false,
      "validates": ["goal_score"]
    }
  ],
  "must_not_outcomes": [
    {
      "outcome_id": "ball_frozen_in_place",
      "description": "Ball must not freeze or become unrecoverable at the goal line.",
      "violates": ["P-900", "C-001"]
    }
  ],
  "mechanic_tags": ["possession", "carrier_danger", "tackle", "volatile_possession"],
  "simulation_ready": false,
  "telemetry_events_required": ["TackleResolve", "PossessionTransfer", "GoalScore"],
  "notes": "",
  "status": "defined"
}
```

---

## Field reference

### Top-level

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | int | Always 1 for this schema version |
| `id` | string | `S-NNN` identifier matching README.md |
| `slug` | string | Snake_case short name |
| `title` | string | Human title matching README.md |
| `contract_refs` | string[] | Contract IDs this scenario validates |
| `map_scope` | string | `"any"` or a canonical map name |
| `description` | string | What this scenario tests |
| `preconditions` | object | Starting state requirements (free-form) |
| `trigger` | string | Event that starts the scenario |
| `expected_outcomes` | array | See below |
| `must_not_outcomes` | array | Outcomes that would be contract violations |
| `mechanic_tags` | string[] | EFT mechanic vocabulary tags |
| `simulation_ready` | bool | Can Simulation/ reproduce this scenario |
| `telemetry_events_required` | string[] | Telemetry event names needed to detect this |
| `notes` | string | Free-form notes |
| `status` | string | `defined \| needs_review \| validated` |

### `expected_outcomes` entries

| Field | Type | Description |
|-------|------|-------------|
| `outcome_id` | string | Short slug for the outcome |
| `description` | string | What should happen |
| `required` | bool | Must occur for the scenario to be considered valid |
| `validates` | string[] | Mechanic anchors this outcome exercises |

### `must_not_outcomes` entries

| Field | Type | Description |
|-------|------|-------------|
| `outcome_id` | string | Short slug |
| `description` | string | What must not happen |
| `violates` | string[] | Contract IDs this would violate |

---

## Status values

| Value | Meaning |
|-------|---------|
| `defined` | Scenario written; not yet simulation-tested |
| `needs_review` | Preconditions or outcomes need domain-expert review |
| `validated` | Scenario has been exercised and outcomes confirmed |
