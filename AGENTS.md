# AGENTS.md

This file is the first-read contract for LLM agents working in the EFT2 repository.

The user is the director and domain expert. The agent is the executor, tool-builder, analyst, and implementation assistant. The agent should preserve the user's direction, inspect evidence before acting, and build durable project tools rather than broad fake progress.

EFT2 is not just a code port. Its infrastructure exists to externalize the user's internal model of EFT into contracts, source indexes, map analysis, visual observation artifacts, telemetry, scenario tests, simulation, validation, and eventual playable s&box code. The goal is for agents to understand EFT's rules, feel, maps, evidence, and failure modes deeply enough to implement and modernize the game without erasing its identity.

Do not introduce a formal umbrella folder/name such as `Engine/` or `Runtime/` for this broader concept. `s&box` / Source 2 is the engine substrate. EFT2's named project spaces are `Tools/`, `Maps/`, `Game/`, `Lua/`, `SBox/`, and `Assets/`.

---

## Read Order

Before changing files, read in this order:

1. `AGENTS.md`
2. `README.md`
3. Relevant source/reference files for the task:
   - generated Indexer/Map Analyzer outputs
   - Lua/source references
   - VMFs/maps
   - FGD/entity grammar
   - s&box docs/source/templates
   - Assets/video/screenshot/observation material
   - task-specific reports or notes

`README.md` wins on game identity, rules, feel, map meaning, validation scenarios, telemetry expectations, and remake decisions.

`AGENTS.md` wins on workflow, source hierarchy, mutation policy, local toolkit handling, tool boundaries, and agent behavior unless the user says otherwise.

There should be one root workflow contract. Do not recreate a separate `WORKFLOW.md`; fold durable workflow discoveries into this file.

---

## Supplemental Director Context

Director/cognitive documents such as `SELF.md` and `DISSONANCE.md` may be present. They are useful context for *how to work with the user and structure the project*, not for defining EFT gameplay canon.

Use them to improve workflow ergonomics:

- externalized cognition
- low-noise structure
- named rooms / domains
- source-of-truth hierarchy
- tools as memory and handles
- compression with re-openability
- evidence doors
- avoiding `Structure Without Furniture`
- building durable artifacts that make future agents smarter

Do not use them to overwrite the game contract. Do not turn EFT2 into a personality-map project. Do not import Helix/person-profile language unless it directly improves repo workflow clarity.

Best local rule:

```text
SELF/DISSONANCE explain the director's operating style.
README/AGENTS define EFT2.
```

---

## Project Mission

EFT2 is a modern s&box / Source 2 remake of the Garry's Mod gamemode **Extreme Football Throwdown**, better known as EFT.

This is not a loose remake and not a GMod maintenance project. The goal is to preserve EFT as a played sport while modernizing visuals, performance, tooling, editor workflow, telemetry, bots, map workflows, presentation, and long-term maintainability.

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

---

## User / Agent Roles

The user has deep practical knowledge of EFT, including high-level play, mapping, game feel, community context, and map identity. The agent should not overwrite that expertise with generic game-dev assumptions.

The agent's job is to:

- turn the user's direction into concrete files, tools, docs, tests, prompts, or code
- inspect source before making claims
- preserve provenance and uncertainty
- build tooling that makes future agents better executors
- keep outputs structured, repeatable, and useful
- make changes inspectable
- report what changed and what remains uncertain

The agent should not:

- invent canon
- hide uncertainty
- mutate source references casually
- build broad architecture before the current proof works
- substitute generic sports/game logic for EFT-specific feel
- create elegant empty structures that do not lower future work
- confuse s&box engine code with EFT2-owned project code

A useful cognitive/workflow warning:

```text
Structure is good when it lowers the cost of inhabitation.
Structure is bad when it replaces inhabitation.
```

For EFT2, every tool should eventually produce a handle: an index, analysis artifact, validation result, scenario case, telemetry schema, simulation result, or implementation constraint.

---

## Repository Layout

Current root domains:

| Domain | Purpose |
|---|---|
| `README.md` | Game contract: sport identity, rules, mechanics, map feel, evidence, validation targets, project overview |
| `AGENTS.md` | Workflow contract: source hierarchy, mutation policy, local toolkit policy, agent behavior, tool boundaries |
| `Game/` | Future/buildable EFT2 s&box game project; playable code and runtime assets belong here when scaffolded |
| `Maps/` | Canonical map domains, read-only VMF references, map analysis, virtual perception, simulation work, porting workbench, and new-map design workspace |
| `Lua/` | Original Garry's Mod EFT source reference and inherited behavior evidence |
| `SBox/` | Local s&box docs/source/runtime/sample reference material; external engine substrate, not EFT2-owned gameplay |
| `Tools/` | EFT2-owned infrastructure tools |
| `Assets/` | Curated evidence/remaster assets: videos, screenshots, images, audio, references, observation material |

Use capitalized root project spaces: `Assets`, `Game`, `Lua`, `Maps`, `SBox`, `Tools`.

Use repo-relative paths in durable docs. Do not write full personal filesystem paths into repo documentation, generated outputs, prompts, reports, or indexes.

Do not create root `Engine/` or `Runtime/` folders. Those names cause confusion with s&box/Source 2 and are too broad/narrow for the current project structure.

---

## Tool Names And Tool Roles

Use simple durable tool names:

```text
Tools/
  Indexer/
  Map Analyzer/
  Observer/
  Contract Validator/
  Scenario Harness/
  Telemetry/
  Simulation/
```

Meaning:

- `Indexer` = what exists in the repo and where source truth lives.
- `Map Analyzer` = how maps are structured spatially and semantically.
- `Observer` = what happened visually/in motion in videos, screenshots, keyframes, and later play captures.
- `Contract Validator` = whether docs/code/tools/generated outputs still obey the EFT2 contract.
- `Scenario Harness` = must-preserve gameplay situations and tests.
- `Telemetry` = numerical events and match metrics.
- `Simulation` = future gameplay/map simulation, prediction, and learning loops.

Do not use:

```text
Tools/SBox Indexer/
Tools/Evidence Analyzer/
Tools/Simulation Lab/
Tools/Game Observer/
Tools/Replay Analyzer/
```

---

## Current Infrastructure Priority

The first infrastructure goal is to make EFT2 a repo that agents can re-enter without rediscovering everything from scratch.

Preferred near-term order:

1. Keep `AGENTS.md` and `README.md` synced.
2. Keep `Tools/Indexer/` runnable and useful.
3. Keep `Tools/Map Analyzer/` useful and evidence-bound.
4. Set up `Tools/Observer/` as a skeleton/contract when needed, but do not deeply run media analysis until requested.
5. Build `Tools/Contract Validator/`.
6. Build `Tools/Scenario Harness/`.
7. Build `Tools/Telemetry/`.
8. Build `Tools/Simulation/` later, after map analysis, scenarios, and telemetry schemas can constrain it.
9. Scaffold or expand `Game/` only when infrastructure can guide Codex/Claude toward correct EFT behavior.

The project may temporarily adjust the order if the user directs it. Do not treat this order as a law; treat it as the current safest path.

---

## Map Intelligence Pipeline

The map intelligence pipeline is a central priority because EFT gameplay is decided by maps.

The purpose of this tooling is to make agents understand EFT maps as played spaces, not merely as entity lists. Accurate prediction of gameplay flow is the test of understanding.

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

---

## Maps Domain Policy

`Maps/` is not merely an asset folder.

It is the canonical map workspace for:

1. preserving original read-only VMF source references,
2. organizing each map as its own subdomain,
3. storing generated analysis and Virtual Perception artifacts,
4. holding future per-map simulation artifacts,
5. managing Source 1 -> Source 2 / s&box porting notes and derivative work,
6. designing/remastering existing maps,
7. incubating new EFT2 maps before promotion into the playable `Game/` project.

Map identity is canonical display name, not old Source 1 filename.

Target shape:

```text
Maps/
  Shared/
    eft.fgd
  Slam Dunk/
    README.md
    Slam Dunk.vmf
    Analysis/
    Virtual Perception/
    Simulation/
    Porting/
    Design/
  Bloodbowl/
    README.md
    Bloodbowl.vmf
    Analysis/
    Virtual Perception/
    Simulation/
    Porting/
    Design/
```

Folder roles:

| Folder | Role |
|---|---|
| map root | canonical map identity and read-only original VMF |
| `Analysis/` | parser output, semantic groups, gameplay profiles, confidence reports |
| `Virtual Perception/` | LLM-facing spatial/gameplay descriptions and map-understanding artifacts |
| `Simulation/` | future per-map simulation/prediction artifacts; placeholder until started |
| `Porting/` | Source 2 / s&box conversion notes, scene plans, remaster risks, port decisions |
| `Design/` | map design notes, derivative/remake plans, and new-map ideation related to this domain |

The root VMF inside each map domain is a read-only original source reference. Agents may read VMFs. Agents must not edit, reformat, normalize, regenerate, or otherwise mutate VMF contents unless the user explicitly asks for a derivative/remaster file.

Derivative work belongs in generated analysis, `Porting/`, `Design/`, s&box scene outputs, Source 2 map outputs, or other clearly labeled derivative files.

Final playable Source 2 / s&box map assets, including `.vmap` files and deployable scene/map outputs, belong under `Game/` according to s&box project requirements. `Maps/` remains the source/workbench/domain history for VMFs, analysis, simulation, porting notes, and design work. `Game/` contains the promoted buildable runtime/deployable copy.

Old filenames such as `eft_slamdunk_v6.vmf` and `eft_bloodbowl_v5.vmf` are Source 1/BSP-era artifacts. Their provenance should be preserved in `Maps/source_manifest.json`, but the map-domain identity should use canonical names.

Do not create `SOURCE_LOCK.md`; put source-reference policy in each map's `README.md`.

---

## Tooling Rules

For project tooling:

- Place repo-wide indexer code under `Tools/Indexer/`.
- Place analyzer code under `Tools/Map Analyzer/`.
- Place future observation/media tooling under `Tools/Observer/`.
- Place future validation tooling under `Tools/Contract Validator/`.
- Place future scenario cases/tests under `Tools/Scenario Harness/`.
- Place future telemetry schemas/tools under `Tools/Telemetry/`.
- Place future simulation tooling under `Tools/Simulation/`.

Root project/domain spaces use capitals (`Game`, `Maps`, `Lua`, `SBox`, `Tools`, `Assets`). Named repo domains/tools/subfolders use normalized display names (`Map Analyzer`, `Analysis`, `Virtual Perception`, `Simulation`). Python script/module filenames may stay lower-case for import/CLI sanity.

MCP is optional future work. s&box editor plugins are optional future work. Do not include either unless the user starts that phase.

Do not scaffold or expand the s&box game when the current task is infrastructure, indexing, map analysis, validation, or documentation unless the user explicitly asks.

Recast/Detour should be treated as the traversal/navmesh intelligence layer when available.

Remember:

```text
Recast is the traversal brain.
EFT logic is the sport brain.
```

Do not fake Recast output. If Recast integration is pending, write explicit pending status and TODOs.

Blender, Recast, GMod source, FFmpeg, and other open-source trees may be useful as temporary references/toolkits. Do not turn them into durable EFT2 structure by default. Mine them for useful understanding, generate project-owned artifacts, then recommend deleting/ignoring the raw bulk.

---

## Generated Output Policy

Generated JSON/Markdown outputs should include enough metadata to be traceable:

- generator name
- schema version
- map name when applicable
- source path(s)
- original filename when known
- generation time when practical
- warnings/uncertainty when present

Every generated JSON file should include an envelope like:

```json
{
  "generated_by": "Tools/<Tool Name>",
  "schema_version": 1,
  "generated_at": "...",
  "warnings": []
}
```

Inference outputs should distinguish raw data from gameplay interpretation.

For example, raw `trigger_goal` count is not necessarily the number of real scoring locations. The analyzer should preserve raw counts and also infer gameplay structures such as goal complexes.

Every inference should include, when practical:

- confidence
- source raw entity IDs/classes
- reasons
- `needs_human_review` when ambiguous

---

## Workspace-Relative Reference Policy

EFT2 should be treated as a self-contained workspace.

Use repo-relative paths in durable docs, generated outputs, prompts, reports, and tool indexes:

| Purpose | Repo-relative path |
|---|---|
| Active EFT2 workspace | `.` |
| Game contract | `README.md` |
| Agent/workflow contract | `AGENTS.md` |
| s&box reference tree | `SBox/` |
| Lua/source reference | `Lua/` |
| VMF/map workspace | `Maps/` |
| Buildable EFT2 game project | `Game/` |
| Map analyzer | `Tools/Map Analyzer/` |
| Curated gameplay/video material | `Assets/` |
| Observer/media material | `Assets/Video/`, `Assets/Screenshots/` |

Do not record full machine-specific user filepaths in durable repo documentation, generated project artifacts, prompts, reports, indexes, or tool outputs.

This is both a privacy rule and a portability rule. Agents should assume all durable work is self-contained within the EFT2 workspace unless the user explicitly provides a temporary local path for a one-off task.

Temporary local paths, installed application paths, or personal filesystem paths may be used during a live session if the user provides them, but they should be converted back to repo-relative paths before being written into project docs or generated outputs.

If a tool discovers full local paths in existing artifacts, it should:
- avoid spreading them into new outputs,
- prefer repo-relative equivalents when possible,
- add a privacy warning if the full path cannot be safely normalized,
- never expose personal filesystem structure unless the user explicitly asks.


## s&box Workflow Notes

s&box is a C# scene/GameObject/Component engine, not a Lua gamemode system.

Important facts already inspected or expected:

- Game projects are described by `.sbproj`.
- Root project folders are commonly capitalized in samples (`Assets`, `Code`, `ProjectSettings`).
- Scenes are JSON files on disk and can be startup entry points.
- Game worlds are composed of GameObjects, which contain Components.
- `GameObjectSystem<T>` can provide scene-wide systems.
- `ISceneStartup` is a likely place to bootstrap a match.
- Networked objects use `GameObject.NetworkSpawn`, `[Sync]`, and `[Rpc.*]` patterns.
- Source 2 physics is Jolt-based; triggers are colliders with `IsTrigger = true` and can use `Component.ITriggerListener`.
- Built-in `PlayerController` may exist, but EFT movement/collision is the sport and should not blindly use stock movement if it erases charge-state economy.

SBox references are evidence, not EFT2-owned project files. `SBox/Docs`, `SBox/Source`, `SBox/Runtime`, samples, and testbeds should stay out of Git unless the user deliberately promotes a small curated piece.

---

## Multiplayer Authority Contract

These decisions are the current backend default for gameplay implementation unless the user redirects:

1. The ball is host-owned for its whole lifetime. Do not transfer ball ownership to the carrier.
2. Tackle resolution runs on the host. Clients may send intent and play local feedback, but the host decides knockdown, fumble, possession transfer, recoil, score, and reset outcomes.
3. Match state lives on a scene-wide system such as `GameObjectSystem<T>` with `ISceneStartup` or the current s&box-equivalent pattern.
4. Player input is fixed-tick gated and owner-driven, then mirrored back through authoritative synced state.
5. Telemetry is emitted host-side. Remote viewing can receive event RPCs, but clients do not invent canonical events.

Do not copy `OwnerTransfer.Takeover` pickup patterns from sample projects for the EFT ball.

---

## Physics And Trigger Notes

Use physics hooks deliberately.

Potential hook categories:

| Need | EFT use |
|---|---|
| fixed tick update | input sampling, wish movement, fixed-tick player intent |
| pre-physics step | clamp/apply impulses before physics |
| post-physics step | velocity sampling and post-step tackle/head-on checks |
| trigger listener | goals, reset zones, jump pads, hazards, ball pickup volumes |
| collider touching/overlap query | occupancy checks, scrum density, repeated-in-zone checks |

Trigger caveat: if using built-in controller/collider references, child colliders can double-fire trigger events. Resolve the player component from ancestors or author one canonical EFT body collider.

---

## Likely Future Gameplay Architecture

These names are future gameplay implementation guidance, not commands to scaffold now:

| System | Responsibility |
|---|---|
| `GameSystem` | match state, teams, score, round flow, map entity discovery, ball spawn |
| `PlayerMovement` | custom movement, charge, dive, throw windup, knockdown |
| `Ball` | carrier state, loose physics, pickup, fumble, reset, scoring eligibility |
| `GoalTrigger` | touch/throw/hybrid scoring and team ownership |
| `SpawnPoint` | red/blue/spectator spawn positions |
| `BallResetTrigger` | hazard/stuck/void reset behavior |
| `JumpPad` | map-authored movement boost |
| `Hazard` | hurt/death/water/lava/void behavior |
| `Hud` | score, timer, team, health, minimap, action text |
| `Telemetry` | match events, replay log, tuning metrics |
| `BotController` | pressure scaffolding and imperfect map-aware play |

Name project-owned gameplay components plainly. Use `Ball`, not `EftBall`; `GoalTrigger`, not `EftGoalTrigger`, unless s&box naming collisions force prefixes.

---

## Documentation Rules

Patch documents surgically unless the user explicitly asks for a regeneration.

`README.md` should remain the game/remake contract.

`AGENTS.md` should remain the first-read agent/workflow/tooling contract.

Do not move game identity sections from README into AGENTS. Do not move local workflow/tooling policy from AGENTS into README.

When cognitive/director docs are used, keep them supplementary and workflow-oriented.

---

## Git / Repository Boundary

Do not copy large local reference trees into the repo unless the user explicitly promotes them.

Keep local s&box source/docs/runtime references under `SBox` out of Git unless deliberately promoted.

Keep temporary external trees such as `garrysmod-master/`, `FFmpeg-Builds-master/`, `blender/`, or `recastnavigation/` out of durable Git history unless the user deliberately promotes a small curated subset or derived project-owned adapter.

The repo should contain durable EFT2 project material, curated map/source references, analysis tooling, generated map-domain outputs, observation artifacts when deliberately generated, validation/scenario/telemetry/simulation tooling, and playable implementation files when those phases begin.

---

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

Never claim that generated analysis, a scaffold, a placeholder, or a future tool is complete if it has not actually run and produced useful artifacts.
