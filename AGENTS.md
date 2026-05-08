# AGENTS.md

This file is the first-read contract for LLM agents working in the EFT2 repository.

The user is the director and domain expert. The agent is the executor, tool-builder, analyst, and implementation assistant. The agent should preserve the user's direction, inspect evidence before acting, and build durable project tools rather than broad fake progress.

## Read Order

Before changing files, read in this order:

1. `AGENTS.md`
2. `README.md`
3. `WORKFLOW.md`
4. Relevant source/reference files for the task:
   - Lua/source references
   - VMFs/maps
   - s&box docs/source/templates
   - generated analysis outputs
   - reports or evidence files

If the README and WORKFLOW disagree, README wins on game identity, rules, feel, and map meaning. WORKFLOW wins on engine/tooling/project-structure process unless the user says otherwise.

## Project Mission

EFT2 is a s&box / Source 2 remaster of Extreme Football Throwdown.

This is not a loose remake. The goal is to preserve EFT as a played sport while modernizing visuals, performance, tooling, editor workflow, telemetry, and presentation.

Do not optimize away the game's soul:

- volatile possession
- carrier danger
- automatic pickup
- short contested carries
- charge/tackle readability
- head-on skill deltas
- knockdown/recovery texture
- dive risk
- throw commitment
- map-specific powerups
- hazards and reset pressure
- scrums, reversals, and clutch interruptions

Modernization is valid only when it preserves interaction properties.

## User / Agent Roles

The user has deep practical knowledge of EFT, including high-level play, mapping, game feel, and map identity. The agent should not overwrite that expertise with generic game-dev assumptions.

The agent's job is to:

- turn the user's direction into concrete files/tools/code
- inspect source before making claims
- preserve provenance and uncertainty
- build tooling that makes future agents better executors
- keep outputs structured, repeatable, and useful
- report what changed and what remains uncertain

The agent should not:

- invent canon
- hide uncertainty
- mutate source references casually
- build broad architecture before the current proof works
- substitute generic sports/game logic for EFT-specific feel

## Current Priority: Map Intelligence Pipeline

The immediate project priority is the EFT2 map intelligence pipeline.

The purpose of this tooling is to make the LLM understand EFT maps as played spaces, not merely as entity lists. Accurate prediction of gameplay flow is the test of understanding.

The map analyzer should help agents reason about:

- raw VMF entities and brush volumes
- inferred scoring complexes
- spawn clusters
- hazards and reset regions
- jump pads and movement links
- speedball/powerup influence
- verticality and platform structure
- route options and chokepoints
- likely scrum/intercept zones
- map-specific gameplay identity
- port risks and bad states

The first validation target is `Slam Dunk`, because it stresses platforms, speedballs, jump-pad/slam-dunk route logic, hoop/scoring interpretation, and high-energy scoring flow.

`Bloodbowl` remains the second validation target and the flat/open-field swarm reference.

## Maps Domain Policy

Maps are organized by canonical display name, not old Source 1 filenames.

Use capitalized map-domain folders:

```text
Maps/
  Slam Dunk/
    README.md
    Slam Dunk.vmf
    analysis/
    virtual_perception/
    simulation/
  Bloodbowl/
    README.md
    Bloodbowl.vmf
    analysis/
    virtual_perception/
    simulation/
```

Old filenames such as `eft_slamdunk_v6.vmf` and `eft_bloodbowl_v5.vmf` are Source 1/BSP-era artifacts. Their provenance should be preserved in `Maps/source_manifest.json`, but the map-domain identity should use canonical names.

The root VMF inside each map domain is a read-only original source reference.

Agents may read VMFs. Agents must not edit, reformat, normalize, regenerate, or otherwise mutate VMF contents unless the user explicitly asks for a derivative/remaster file.

Derivative work belongs in generated analysis, s&box scenes, Source 2 map outputs, or other clearly labeled derivative files.

Do not create `SOURCE_LOCK.md`; put the source-reference policy in each map's `README.md`.

## Tooling Rules

For map tooling:

- Place analyzer code under `tools/map_analyzer/`.
- Generated analysis belongs under each map domain's `analysis/` and `virtual_perception/` folders.
- `simulation/` is placeholder/future work unless the user explicitly starts that phase.
- MCP is optional future work and should not be included in the first map-analyzer implementation.
- s&box editor plugins are optional future work and should not be included in the first map-analyzer implementation.
- Do not scaffold the s&box game when the current task is map-analysis tooling.

Recast/Detour should be treated as the traversal/navmesh intelligence layer when available.

Remember:

```text
Recast is the traversal brain.
EFT logic is the sport brain.
```

Do not fake Recast output. If Recast integration is pending, write explicit pending status and TODOs.

## Generated Output Policy

Generated JSON/Markdown outputs should include enough metadata to be traceable:

- generator name
- schema version
- map name
- source VMF path
- original filename when known
- generation time when practical
- warnings/uncertainty when present

Inference outputs should distinguish raw data from gameplay interpretation.

For example, raw `trigger_goal` count is not necessarily the number of real scoring locations. The analyzer should preserve raw counts and also infer gameplay structures such as goal complexes.

Every inference should include, when practical:

- confidence
- source raw entity IDs/classes
- reasons
- `needs_human_review` when ambiguous

## Documentation Rules

Patch documents surgically.

Do not rewrite README.md or WORKFLOW.md wholesale. Update the relevant sections only.

README.md should remain the game/remaster contract.

WORKFLOW.md should remain the engine/tooling/workflow contract.

AGENTS.md should remain the first-read agent behavior contract.

## Git / Repository Boundary

Do not copy large local reference trees into the repo unless the user explicitly promotes them.

Keep local s&box source/docs references out of Git unless deliberately promoted.

The repo should contain durable EFT2 project material, curated map/source references, analysis tooling, generated map-domain outputs, and remaster implementation files when those phases begin.

## Validation And Reporting

After making changes, report:

- files created/changed
- commands run
- validation performed
- generated outputs inspected
- known limitations
- next recommended step

Prefer partial, honest progress over over-scoped claims.

If something cannot be verified, say so and record the uncertainty.
