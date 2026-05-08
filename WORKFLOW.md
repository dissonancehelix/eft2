# EFT2 Workflow

This document is the companion to the root `README.md`.

The README is the game contract: rules, feel, maps, validation targets, and evidence. This file is the engine/workflow contract: s&box structure, local reference paths, toolkit paths, implementation habits, and lessons from sample projects.

## Source Order

Before changing project files:

1. Read `AGENTS.md` if it exists.
2. Read `README.md` for the EFT2 game contract.
3. Read `DISSONANCE.md` if it exists.
4. Read this file when the task involves s&box, project structure, tooling, conversion, validation, or workflow.
5. Read the relevant Lua, VMF, docs, samples, or engine source before implementing.

If the README and this file disagree, the README wins on game identity/rules/feel. This file wins on engine workflow unless the user says otherwise.

## Canonical Engine And Toolkit Paths

| Purpose | Path |
|---|---|
| Active remaster workspace | `C:\Users\dissonance\Desktop\eft 2` |
| Game contract | `C:\Users\dissonance\Desktop\eft 2\README.md` |
| Engine/workflow contract | `C:\Users\dissonance\Desktop\eft 2\WORKFLOW.md` |
| Canonical installed s&box location | `C:\Program Files (x86)\Steam\steamapps\common\sbox` |
| Local s&box full source/reference tree | `C:\Users\dissonance\Desktop\eft 2\sbox-src` |
| Local saved s&box docs | `C:\Users\dissonance\Desktop\eft 2\sbox-src\docs` |
| Local s&box sample games | `C:\Users\dissonance\Desktop\eft 2\sbox-src\engine\Sandbox.Samples` |
| Local Facepunch SceneStaging testbed | `C:\Users\dissonance\Desktop\eft 2\sbox-src\engine\Sandbox.SceneStaging` |
| FFmpeg used for video analysis | `C:\Program Files\foobar2000\encoders\ffmpeg.exe` |
| Local video analysis output | `C:\Users\dissonance\Desktop\eft 2\video-analysis` |

## External Engine References

| Purpose | URL |
|---|---|
| s&box Steam page | `https://store.steampowered.com/app/590830/sbox/` |
| Facepunch public s&box source | `https://github.com/Facepunch/sbox-public` |
| Facepunch SceneStaging source | `https://github.com/Facepunch/sbox-scenestaging` |

## Repository Boundary

Keep local engine references out of Git unless the user deliberately promotes something:

- `sbox-src` is local reference only.
- `sbox-src\docs` is local reference only.
- `Sandbox.Samples` and `Sandbox.SceneStaging` are local reference only.
- `video-analysis` is local evidence/work product only.
- The actual EFT2 s&box project, once scaffolded, should be tracked.

The repo should not become a mirror of s&box docs/source. It should contain the EFT2 project, the game contract, durable helper docs, original Lua/map references needed for porting, and curated assets/source that actually belong to EFT2.

## Current Engine Ingestion State

As of 2026-05-08:

- `sbox-src` is the full local s&box source/reference tree.
- `sbox-src\docs` contains the saved local s&box docs.
- `sbox-src\engine\Sandbox.Samples` contains local sample game projects.
- `sbox-src\engine\Sandbox.SceneStaging` contains the Facepunch SceneStaging/testbed project.
- No EFT2 s&box game project has been scaffolded yet.

Already read or lightly inspected:

- `sbox-src\README.md`
- `sbox-src\docs\getting-started`
- `sbox-src\game\templates\game.minimal`
- `sbox-src\game\templates\game.playercontroller`
- `sbox-src\game\samples\sweeper`
- `sbox-src\engine\Sandbox.Samples\Bomb Royal`
- `sbox-src\engine\Sandbox.SceneStaging`
- s&box `Component`, `GameObject.Network`, `[Sync]`, `[Rpc.*]`, `Rigidbody`, `PlayerController`, `CharacterController`, `ISceneStartup`

## s&box Architecture Facts

s&box is not a Lua gamemode system. It is a C# scene/GameObject/Component engine.

Important implementation facts:

- Game projects are described by `.sbproj`.
- Scenes are files on disk and can be used as startup entry points.
- Game worlds are composed of GameObjects.
- GameObjects contain Components.
- Components implement behavior.
- `GameObjectSystem<T>` can provide scene-wide systems.
- `ISceneStartup` can hook map/scene startup.
- Networked objects use `GameObject.NetworkSpawn`, `[Sync]`, and `[Rpc.*]`.
- Built-in `PlayerController` exists, but EFT should not blindly use it.

## Sample Project Lessons

`Sandbox.Samples\Bomb Royal` is the strongest local multiplayer-game reference so far:

- `.sbproj` uses `Type: game`, `GameNetworkType: Multiplayer`, `TickRate: 50`, `StartupScene`, and `LaunchMode`.
- `BombRoyale` implements `Component.INetworkListener`, creates a lobby if networking is inactive, clones `PlayerPrefab`, assigns player slots, and calls `NetworkSpawn(connection)`.
- The state flow is host-owned: `StateSystem.Set<T>()`, `BaseState`, `LobbyState`, `GameState`, and `SummaryState`.
- Player state uses `[Sync]` and `[Sync(SyncFlags.FromHost)]` for replicated gameplay facts.
- RPCs separate owner-only, host-only, and broadcast effects.
- `MoveController` is a custom traced movement controller, not just a stock player controller.
- `RagdollController` shows host-authoritative ragdoll state and impulse application.
- Razor/SCSS HUD and nameplate panels are normal project UI, not a separate web app.

`Sandbox.SceneStaging` is the stronger engine/testbed reference:

- `.sbproj` shows `StartupScene`, `MapStartupScene`, `MapList`, multiplayer metadata, and normal launch mode.
- `GameNetworkManager` shows prefab spawning for new connections and avatar/clothing setup.
- `PlayerController` shows camera, input, `CharacterController`, synced eye angles, and animation helper usage.
- `NetworkTest` shows object carrying, ownership transfer with `Network.TakeOwnership()`, parenting, dropping, and physics restore.
- `TriggerDebug` shows `Component.ITriggerListener` for trigger enter/exit behavior.
- `MapLoadedHandler` shows `MapInstance.OnMapLoaded` and discovery of map-authored spawn points.
- Network stress examples are useful for later replication/load tests.

Do not copy these games mechanically. Use them to avoid guessing current s&box patterns.

## Likely EFT2 Architecture

| System | Responsibility |
|---|---|
| `GameSystem` | Match state, teams, score, round flow, map entity discovery, startup |
| `PlayerController` | Custom movement, charge state, dive, throw, knockdown, camera, animation |
| `Ball` | Carrier state, loose physics, pickup, fumble, reset, scoring eligibility |
| `GoalTrigger` | Touch/throw/hybrid scoring and team ownership |
| `SpawnPoint` | Red/blue/spectator spawn positions |
| `BallResetTrigger` | Hazard/stuck/void reset behavior |
| `JumpPad` | Map-authored movement boost |
| `Hazard` | Hurt/death/water/lava/void behavior |
| `Hud` | Score, timer, team, health, minimap, action text |
| `Telemetry` | Match events, replay data, tuning metrics |

Name project-owned gameplay components plainly. Use `Ball`, not `EftBall`; `GoalTrigger`, not `EftGoalTrigger`. Only add an `Eft` prefix when a plain name would collide with an engine/framework type or become ambiguous in real code.

The built-in s&box `PlayerController` is useful reference material, but EFT movement/collision is the sport. A custom controller or heavily constrained controller is expected; if a plain `PlayerController` name conflicts with project setup, choose the smallest clear name rather than branding every entity with `Eft`.

## Workflow Rules

- Patch existing documents surgically.
- Do not rewrite the README into engine notes.
- Keep engine/toolkit discoveries here unless they affect game rules.
- Keep local reference material ignored until deliberately promoted.
- Before scaffolding, compare the current samples/templates against the desired EFT2 shape.
- Before implementing gameplay, read the relevant Lua and VMF source.
- Prefer a small playable vertical slice over broad architecture.
- Avoid fake gameplay placeholders that make missing mechanics look done.
- Run available validation when practical.
- Record engine uncertainty instead of hiding it behind confident prose.

## First Scaffold Direction

When Phase 1 begins, start from the current s&box project shape:

- `.sbproj`
- `Assets`
- `Code`
- `ProjectSettings`
- startup scene
- tracked EFT2 project files only

Initial project metadata should likely be multiplayer, `TickRate: 50`, with a startup scene and no bundled local s&box docs/source.

The first playable implementation should prove the EFT loop: custom player movement, automatic ball pickup, carrier slowdown, tackle/knockdown, loose ball, one goal trigger, score/timer HUD, and telemetry hooks.
