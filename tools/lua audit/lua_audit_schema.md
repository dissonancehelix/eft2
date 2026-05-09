# Lua Audit Schema

Schema version: `1`. Generator: `tools/lua audit`.

## Block record

```jsonc
{
  "id": "LUA-BALL_POSSESSION-PROP-BALL-ENT-INITIALIZE-001",
  "audit_quality": "inferred",            // mechanical | inferred | human_confirmed
  "identity_key": "lua/entities/entities/prop_ball/init.lua::function::ENT:Initialize::",
  "file": "lua/entities/entities/prop_ball/init.lua",
  "symbol": "ENT:Initialize",
  "block_kind": "function",               // function | hook | net
  "line_range": [14, 14],                 // metadata only; not part of identity
  "cluster": "ball_possession",
  "cluster_reason": "path:prop_ball",

  "plain_english": "Ball entity / carrier lifecycle behavior.",
  "gameplay_meaning": "Possession transfer, pickup, drop, or fumble bookkeeping.",
  "tacit_meaning": "",                    // conservative; empty if not strongly inferable

  "state_read":  ["Pos", "Angles"],
  "state_written":["Owner", "Mass"],

  "related_lua":   ["shared.lua"],
  "related_readme_ids": ["M-140", "M-150", "P-080"],
  "related_fgd_entities": ["prop_ball"],
  "related_map_concepts": [],
  "related_sbox_concepts": [],

  "inherited_manifest_links": [
    "Mechanics: M-140 (Possession Base), M-150 (Fumble Physics)",
    "Principles: P-080 (Ball Readability)"
  ],

  "csharp_owner": {
    "file": "game/eft2/Code/Ball.cs",
    "status": "candidate_present",        // candidate_present | partial | planned | missing | needs_inspection
    "parity_verified": false,
    "note": "basename heuristic (prop_ball -> ball.cs)"
  },

  "telemetry_events": [],
  "scenario_ids": [],
  "simulation_relevance": "rule grounding for possession volatility",

  "port_risk": "high",                    // low | medium | high
  "confidence": "medium",                 // low | medium | high
  "needs_human_review": false,
  "missing_evidence": null,
  "notes": ""
}
```

## Identity key (stable IDs)

```
relpath :: block_kind :: symbol :: normalized_signature
```

- `relpath` is repo-relative, forward slashes.
- `block_kind` is `function`, `hook`, or `net`.
- `symbol` for hooks is `hook.Add:<event>/<id>`; for net handlers
  `net.Receive:<msg>`; for functions the literal function name (`ENT:X`,
  `GM:Y`, `mod.func`).
- `normalized_signature` is the parameter list with whitespace collapsed.
- If `symbol` is missing/anonymous, substitute a 10-char SHA1 prefix of the
  first ~200 bytes of the body (comments stripped, whitespace collapsed).

`id_registry.json` persists `identity_key -> id` so reruns reuse IDs and
new blocks append rather than reflowing existing IDs.

`line_range` is captured but never part of identity.

## Audit quality

- `mechanical` — derived directly from source (paths, symbols, manifest
  comments, related files via `include`/`AddCSLuaFile`).
- `inferred` — first-pass heuristic interpretation. Default for
  `plain_english`, `gameplay_meaning`, `tacit_meaning`, `port_risk`,
  `simulation_relevance`. Always paired with `confidence: low` unless a
  cluster heuristic fired strongly.
- `human_confirmed` — set by a later human-review pass. The auditor never
  emits this on first run.

## C# owner status

| Status              | Meaning                                                       |
|---------------------|---------------------------------------------------------------|
| `candidate_present` | A plausible owner file exists. Parity is **not** verified.    |
| `partial`           | Human-confirmed: implements some but not all behavior.        |
| `planned`           | A cluster suggests an owner; the file does not yet exist.     |
| `missing`           | No cluster suggestion and no plausible owner.                 |
| `needs_inspection`  | A candidate exists but the heuristic is not confident.        |

`parity_verified` is always `false` until a human review pass sets it.

## Cluster IDs

`player_movement_charge`, `tackle_knockdown_immunity`, `ball_possession`,
`throwing_passing`, `scoring_goals`, `round_flow`, `map_entities_fgd`,
`hud_minimap_scoreboard`, `bots_ai`, `status_powerups`, `audio_presentation`,
`admin_debug_dev`, plus `unclassified` for blocks no heuristic placed.

## Bridge entry shape

```jsonc
{
  "cluster": "ball_possession",
  "title": "ball possession / pickup / drop / fumble",
  "lua_evidence": { "block_count": 42, "files": [...], "sample_ids": [...] },
  "semantic_meaning": "...",
  "tacit_played_meaning": "...",
  "sbox_surface": { "engine_concept": "Component + ITriggerListener" },
  "csharp_owner": { "file": "game/eft2/Code/Ball.cs",
                    "status": "candidate_present",
                    "parity_verified": false },
  "telemetry_scenario_validation": {
      "telemetry_events": [], "scenario_ids": [], "note": "..."
  },
  "simulation_relevance": "...",
  "port_risk": "high"
}
```
