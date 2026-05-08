# Extreme Football Throwdown s&box Remaster Contract

This README is the living contract for the s&box port/remaster of **Extreme Football Throwdown**.

The old Garry's Mod `EFT.md` was created to clean up and preserve the GMod version. This file is its successor for the new game. It should become at least as detailed as the old contract, and eventually more detailed where s&box behavior, remaster decisions, map conversion, presentation, networking, telemetry, and validation require new constraints.

The goal is a full port/remaster: as close as possible to EFT's real sport identity, modernized through s&box / Source 2 for better visuals, performance, feel, and style.

This is not a loose remake.

## Absolute Rule

Leave the original GMod project and original `EFT.md` alone unless the user explicitly asks to edit them.

Original reference path:

`C:\Program Files (x86)\Steam\steamapps\common\GarrysMod\garrysmod\gamemodes\extremefootballthrowdown`

This remaster workspace is:

`C:\Users\dissonance\Desktop\eft 2`

## Source of Truth Hierarchy

1. Direct user instruction in the current session.
2. This root `README.md` for the s&box remaster contract.
3. The original GMod contract at `C:\Program Files (x86)\Steam\steamapps\common\GarrysMod\garrysmod\gamemodes\extremefootballthrowdown\EFT.md`, as inherited design/spec reference.
4. In-workspace Lua/source copy at `C:\Users\dissonance\Desktop\eft 2\lua-src`, as the preferred local reference for project work.
5. Installed GMod EFT folder, as shipped/reference backup behavior.
6. Original VMF/map sources in `C:\Users\dissonance\Desktop\EFT\Projects`.
7. Real gameplay evidence: Bloodbowl POV video, screenshots, future clips, demos, match logs, and replays.
8. s&box docs and source under `C:\Users\dissonance\Desktop\eft 2\sbox-src`.
9. External canonical references listed below.

When these sources disagree, do not hide the disagreement. Record the conflict and decide deliberately whether the remaster follows design intent, shipped Lua behavior, later map revisions, or live-match feel.

## Project Identity

EFT is a continuous collision sport where a swarm of players repeatedly interrupts and reassigns possession of a ball that automatically attaches to whoever physically contacts it after a tackle, throw, reset, or loose-ball event.

Possession is not a stable reward. Possession is a target marker.

The sport is not American football. It is closer to:

- Rocket League, but the player is the car.
- Rugby broken play, but compressed into an arena.
- Hockey pressure and turnover rhythm, without offsides or stoppage.
- Quake/Source movement discipline, but with collision/tackles instead of weapons.

The core loop:

`Engage -> Tackle -> Displacement -> Auto-possession transfer -> Immediate retarget -> Repeat`

Goals happen when pressure fails to reform for a short window.

## What Must Survive the Port

These are port blockers, not polish preferences.

- Possession is volatile and usually short.
- The carrier is slower than defenders.
- Ball pickup is automatic on contact.
- There is no pickup key, possession confirmation, or safe carry animation gate.
- Tackles and knockdowns are first-class outcomes.
- A tackle that stops a breakaway is as important as a goal.
- Head-on outcomes depend on instantaneous velocity, including tiny player-generated speed differences.
- Passing is a dangerous commitment, not a safe utility action.
- Dive tackles extend reach but create vulnerability.
- Knockdown removes upright participation for a meaningful window.
- Walls and obstacles kill charge by stopping forward progress.
- Wall contact does not automatically fumble the ball.
- Wall contact does not automatically knock the player down.
- Goals must remain preventable until the last moment.
- Scrums are the sport, not a failure state.
- Bots scaffold population and pressure; they must not become perfect tackle machines.

Do not modernize away tension, contested interactions, reversals, or chaos density.

## What Can Be Modernized

The remaster should improve:

- Visual identity and readability.
- Lighting, materials, models, animations, VFX, and sound.
- HUD, minimap, score presentation, action text, and spectator tools.
- Match flow UI and lobby/menu polish.
- Network reliability, prediction, and server authority.
- Map conversion pipeline and entity grammar.
- Telemetry, replay, diagnostics, and balance validation.
- Performance and player count stability.
- Bot navigation and population scaffolding.

Modernization is valid only when it preserves interaction properties.

If a cleaner implementation makes possession safer, tackles rarer, goals less preventable, scrums less dense, or head-ons less skill-readable, it is wrong even if the code is technically nicer.

## Canonical Filepaths

| Purpose | Path |
|---|---|
| Active remaster workspace | `C:\Users\dissonance\Desktop\eft 2` |
| This contract | `C:\Users\dissonance\Desktop\eft 2\README.md` |
| s&box full source | `C:\Users\dissonance\Desktop\eft 2\sbox-src` |
| s&box docs | `C:\Users\dissonance\Desktop\eft 2\sbox-src\docs` |
| In-workspace Lua/source reference | `C:\Users\dissonance\Desktop\eft 2\lua-src` |
| In-workspace canonical VMF subset | `C:\Users\dissonance\Desktop\eft 2\lua-src\content\VMFs` |
| In-workspace match logs | `C:\Users\dissonance\Desktop\eft 2\lua-src\logs` |
| Original EFT Lua gamemode | `C:\Program Files (x86)\Steam\steamapps\common\GarrysMod\garrysmod\gamemodes\extremefootballthrowdown` |
| Original GMod contract | `C:\Program Files (x86)\Steam\steamapps\common\GarrysMod\garrysmod\gamemodes\extremefootballthrowdown\EFT.md` |
| Original VMF projects | `C:\Users\dissonance\Desktop\EFT\Projects` |
| Bloodbowl POV recording | `C:\Users\dissonance\Desktop\eft 2\EFT Bloodbowl POV.mp4` |
| Bloodbowl screenshot 1 | `C:\Users\dissonance\Pictures\Steam\4000\screenshots\20161104051331_1.jpg` |
| Bloodbowl screenshot 2 | `C:\Users\dissonance\Pictures\Steam\4000\screenshots\20170424014628_1.jpg` |
| Current UI/style screenshot 1 | `C:\Users\dissonance\Pictures\Screenshots\Screenshot 2026-05-08 004339.png` |
| Current UI/style screenshot 2 | `C:\Users\dissonance\Pictures\Screenshots\Screenshot 2026-05-08 004356.png` |
| Current UI/style screenshot 3 | `C:\Users\dissonance\Pictures\Screenshots\Screenshot 2026-05-08 004419.png` |

## Repository Boundary

The GitHub repository should contain only durable EFT2 project material:

- This contract.
- Git hygiene/configuration files.
- The in-workspace Lua/source copy needed to port original behavior.
- Curated original map/source assets needed for map conversion and canonical behavior extraction.

Local reference/dev-only material stays out of Git unless deliberately promoted:

- `sbox-src`, including saved s&box docs, is local reference only.
- `EFT Bloodbowl POV.mp4` is local gameplay evidence only.
- `lua-src\logs` match recorder output is local evidence/dev capture unless a small fixture is intentionally selected.
- `lua-src\backgrounds` legacy menu/background images are local reference chrome unless needed for the remaster.
- `lua-src\screenshots` and copied screenshot references are local evidence unless deliberately promoted into curated docs/assets.

## External References

| Purpose | URL |
|---|---|
| s&box Steam page | `https://store.steampowered.com/app/590830/sbox/` |
| Facepunch public s&box source | `https://github.com/Facepunch/sbox-public` |
| GMod EFT repository/server lineage | `https://github.com/dissonancehelix/extremefootballthrowdown` |
| Extreme Football League historical group | `https://steamcommunity.com/groups/ExtremeFootballLeague` |

The local installed GMod gamemode was the first inspected Lua reference. The source is now copied into `lua-src`; future sessions should prefer `lua-src` for local project work and use the installed GMod path as historical/reference backup.

## Current Ingestion State

As of 2026-05-08:

- The active workspace root contains `sbox-src` and the Bloodbowl POV recording.
- The active workspace root now contains `lua-src`, an in-workspace copy of the GMod Lua/source package.
- No s&box EFT game project has been scaffolded yet.
- `sbox-src` is the full s&box source tree.
- `sbox-src\docs` contains the saved local s&box docs.
- The Lua implementation has been identified and key files have been read from the installed GMod path; future reads should use `lua-src` where possible.
- The original VMF folder has been inventoried: 204 `.vmf` files and 169 `.vmx` autosaves.
- `lua-src\content\VMFs` contains a curated in-workspace VMF subset, including Bloodbowl, Slam Dunk, Baseball Dash, Skystep, Space Jump, Tunnel, and other canonical/near-canonical maps.
- `lua-src\logs` contains match recorder JSON logs from 2026 sessions.
- The Bloodbowl POV recording has been checked: 20:58, 1280x720, 30 fps, about 359 MB.
- The Bloodbowl POV recording is from an older version of the game; use it primarily for match rhythm, camera feel, collision density, scoring tempo, and live-match chaos.
- The May 8, 2026 screenshots show the current, cleaner UI/presentation direction; use them as the primary style target for the port's HUD and visual language.
- The public Extreme Football League Steam group has been located and is accessible as a historical competitive reference. Its overview says the group was created for Extreme Football Throwdown and contains records, rosters, schedules, announcements, and livestreamed games. It lists Sunrust EFL and the old server `104.192.0.78:27023`.

Already read or lightly inspected:

- `sbox-src\README.md`
- `sbox-src\docs\getting-started`
- `sbox-src\game\templates\game.minimal`
- `sbox-src\game\templates\game.playercontroller`
- `sbox-src\game\samples\sweeper`
- s&box `Component`, `GameObject.Network`, `[Sync]`, `[Rpc.*]`, `Rigidbody`, `PlayerController`, `CharacterController`, `ISceneStartup`
- Original `EFT.md` structure, mechanics, map roster, diagnostics, replay notes
- `gamemode\obj_player.lua`
- `gamemode\obj_ball.lua`
- `gamemode\states\movement.lua`
- `gamemode\states\divetackle.lua`
- `gamemode\states\throw.lua`
- `entities\entities\trigger_goal.lua`
- `docs\engine_differences.md`
- `docs\porting_diagnostics.md`
- `docs\known_bad_states.md`
- `docs\mapping_guide.md`
- `docs\code_annotation_standard.md`

## s&box Architecture Implications

s&box is not a Lua gamemode system. It is a C# scene/GameObject/Component engine.

Important implementation facts:

- Game projects are described by `.sbproj`.
- Scenes are JSON files on disk.
- Game worlds are composed of GameObjects.
- GameObjects contain Components.
- Components implement behavior.
- `GameObjectSystem<T>` can provide scene-wide systems.
- `ISceneStartup` can hook map/scene startup.
- Networked objects use `GameObject.NetworkSpawn`, `[Sync]`, and `[Rpc.*]`.
- Built-in `PlayerController` exists, but EFT should not blindly use it.

Likely architecture:

| System | Responsibility |
|---|---|
| `EftGameSystem` | Match state, teams, score, round flow, map entity discovery, startup |
| `EftPlayerController` | Custom movement, charge state, dive, throw, knockdown, camera, animation |
| `EftBall` | Carrier state, loose physics, pickup, fumble, reset, scoring eligibility |
| `EftGoalTrigger` | Touch/throw/hybrid scoring and team ownership |
| `EftSpawnPoint` | Red/blue/spectator spawn positions |
| `EftBallResetTrigger` | Hazard/stuck/void reset behavior |
| `EftJumpPad` | Map-authored movement boost |
| `EftHazard` | Hurt/death/water/lava/void behavior |
| `EftHud` | Score, timer, team, health, minimap, action text |
| `EftTelemetry` | Match events, replay data, tuning metrics |

The built-in s&box `PlayerController` is useful reference material, but EFT movement/collision is the sport. A custom controller or heavily constrained controller is expected.

## Mechanical Constants To Preserve First

These values come from the inherited GMod contract and Lua. They are initial targets, not yet s&box-verified.

| Mechanic | Value |
|---|---:|
| Gravity | 600 HU/s^2 |
| Base max speed | 350 HU/s |
| Carrier speed | 262.5 HU/s |
| Pity carrier speed | 315 HU/s |
| Strafe-only speed | 160 HU/s |
| Charge threshold | 300 HU/s |
| Charge animation lead-in | about 270-280 HU/s |
| Approx time 0 -> charge | about 1.0 s |
| Approx time 0 -> max speed | about 1.5 s |
| Knockdown duration | 2.75 s |
| Post-hit charge immunity | 0.45 s |
| Per-attacker anti-stunlock immunity | 2.0 s |
| Tackle force multiplier | charger velocity x 1.65 |
| Attacker recoil | attacker velocity x -0.03 |
| Charge damage | 5 |
| Punch damage | 25 |
| Dive extra speed | +100 HU/s |
| Dive upward boost | 320 HU/s |
| Dive turn limit | 90 degrees/s |
| Punch duration | 0.5 s |
| Cross-counter window | last 0.2 s |
| Punch force | 360 |
| Jump vertical speed | 200 HU/s |
| Jump cooldown | 0.3 s |
| Ball mass | 25 |
| Ball linear damping | 0.01 |
| Ball angular damping | 0.25 |
| Fumble horizontal velocity | carrier velocity x 1.75 |
| Fumble vertical pop | 128 HU/s |
| Ball bounce reduction | 0.75x |
| Throw max windup | 1.0 s |
| Throw movement | 0 HU/s target, effectively frozen |
| Throw impulse | 1100 along aim vector |
| Ball untouched reset | 20 s |
| Goal cap | 10 |
| Match time | 15 min |
| Warmup | 30 s |
| Respawn delay | 5.0 s |
| Post-goal slow motion | 2.5 s at 0.1x |
| Pity trigger | trailing by 4+ goals |

Porting warning: Source 1 Hammer Units, Source movement, and s&box/Source 2/Jolt/Rubikon behavior may not map 1:1. Preserve player-perceived timing and interaction outcomes over numeric literalism when a direct conversion diverges.

## Core Mechanics Contract

### Movement And Charge

Players are dangerous only when grounded and above charge threshold. Charge state is a threat state, not just high velocity.

Requirements:

- Empty-handed players can build to 350 HU/s.
- Players must reach at least 300 HU/s to tackle.
- Carriers are below charge speed during normal play.
- Grounded charging must feel committed.
- Steering should be mouse-yaw driven while moving forward.
- Turning too sharply should bleed speed.
- Hitting walls or wrong-angle geometry should drop speed to zero or near-zero.
- Re-acceleration after a stop must take long enough to create vulnerability.

The "curve" must survive: skilled players can generate small velocity advantages by taking committed, clean, slightly curved lines into head-ons. Do not normalize these differences away.

### Tackles And Head-Ons

Tackles are the central interaction.

Requirements:

- A charger hitting a non-charging opponent knocks them down.
- A charging opponent meeting another charging opponent resolves by speed.
- Small speed differences matter.
- Grounded players beat airborne players in charge resolution.
- Airborne players cannot tackle.
- Carriers cannot initiate charge hits.
- Tackle collision should disqualify players from the next immediate contest by knockdown, recoil, or loss of charge.

Head-on collisions are a major veteran skill signal. If veterans cannot tell why they won or lost a head-on, the implementation has drifted.

### Knockdown And Recovery

Knockdown is population control. It removes upright participation long enough to change the next 1-5 seconds of play.

Requirements:

- Knockdown should last about 2.75 seconds.
- Effective removal should feel closer to 4-5 seconds after re-acceleration.
- Knocked-down players cannot pick up the ball.
- Knocked-down players are obstacles.
- Multiple attackers can chain pressure, but immunity timers should prevent single-attacker spam from becoming unreadable.

### Possession

Possession happens to players.

Requirements:

- Loose ball contact causes pickup automatically.
- Pickup should be instant and surprising.
- No deliberate interact key.
- No confirmation window.
- No "safe receive" smoothing that lowers volatility.
- Carrier speed penalty applies immediately.
- Carrier becomes the most important target on the field.

Possession stability is a failure condition. The ball should not be safely carried for long under pressure.

### Fumble And Ball Loose

Fumble is the sport's transition generator.

Requirements:

- Tackling a carrier creates a loose ball.
- Throwing creates a loose ball.
- Reset creates a loose ball at the reset point.
- Wall contact alone does not fumble.
- Random physics noise should not dominate the ball.
- Loose ball movement must be readable and contestable.
- The ball should not become an infinite-dribble exploit.

### Passing

Passing is the longest voluntary vulnerability state.

Requirements:

- Hold RMB to wind up.
- Release to throw.
- Full power takes about 1 second.
- Carrier is effectively frozen during windup.
- Early release is allowed but weaker.
- Most passes under pressure should be dangerous.
- Running into goal is often safer than throwing on touch/hybrid maps.
- Throw-only maps intentionally force teamwork and blocking.

Passing skill is prediction under interruption, not only aim.

### Dive

Dive is high-risk reach extension.

Requirements:

- Trigger while grounded, charging, and not carrying.
- Adds forward speed and upward boost.
- Rate-limits turning.
- Disables crouch abuse.
- Ends in vulnerability/knockdown.
- Success may slightly reduce recovery.
- Whiff should be punishable.

### Walls And Obstacles

"Wall" means any map geometry that stops progress: walls, pillars, platforms, ramps at bad angles, props, edges.

Requirements:

- Obstacle impact kills charge.
- Obstacle impact does not automatically fumble.
- Obstacle impact does not automatically knock down an upright player.
- Stopped players must need meaningful time to become dangerous again.

### Scoring

Scoring is the emotional payoff after pressure fails.

Goal types:

- Touch: carrier enters goal zone.
- Throw: thrown ball enters goal zone.
- Hybrid: both count.

Requirements:

- Goals must remain preventable until the last moment.
- Goal-line stands must be possible.
- Post-goal slow motion should celebrate without turning the game into stoppage-heavy football.
- Ball reset should force a new convergence.

## Required Player Perceptions

A correct implementation should make players feel:

- Hunted while carrying.
- Immediately relevant after spawning.
- Dangerous only when they have charge state.
- Responsible when losing a head-on.
- Exposed after missing a dive.
- Urgent during throw windup.
- Rewarded for predicting the next possession event.
- Pulled into dense local crises around the ball.

Players should not commonly feel:

- Safe while carrying.
- Like they are running a play.
- Like there are fixed offensive/defensive positions.
- Like the best strategy is formation defense.
- Like they are waiting for their turn.
- Like the ball is random noise.
- Like goals are unstoppable once the carrier is near.

## Bot Contract

Bots are not football players in formations. They are swarm/rotation agents.

Bots should:

- Chase loose balls.
- Threaten the carrier.
- Cut angles rather than follow trails.
- Body-block defenders when near a friendly carrier.
- Rotate toward likely next possession events.
- Avoid walls where possible.
- Keep moving.
- Show imperfect human-like head-on variance.

Bots should not:

- Line up in formations.
- Wait for downs, plays, or turns.
- Run scripted routes.
- Ignore loose balls.
- Stop moving to aim throws unless they truly have a window.
- Outperform good humans at head-on timing.

## Canonical Map Roster

This list comes from the inherited GMod `EFT.md`. Actual VMF availability has been checked lightly against `C:\Users\dissonance\Desktop\EFT\Projects`.

| Canonical filename | Display name | Source status |
|---|---|---|
| `eft_baseballdash_v3` | Baseball Dash | exact VMF found |
| `eft_big_metal03r1` | Big Metal | closest found: `eft_big_metal03r1_d.vmf` |
| `eft_bloodbowl_v5` | Bloodbowl | exact VMF found |
| `eft_castle_warfare` | Castle Warfare | multiple versioned VMFs found |
| `eft_chamber_v3` | Chamber | closest found: `eft_chamber_d.vmf`, `eft_chamber_v2.vmf` |
| `eft_cosmic_arena_v2` | Cosmic Arena | exact VMF found |
| `eft_countdown_v4` | Countdown | closest found: `eft_countdown_v2_d.vmf` |
| `eft_handegg_r2` | Handegg | exact VMF found |
| `eft_lake_parima_v2` | Lake Parima | not found in first pass |
| `eft_legoland_v2` | Legoland | exact VMF found |
| `eft_minecraft_v4` | Minecraft | exact VMF found |
| `eft_miniputt_v1r` | Mini Putt | closest found: `eft_miniputt_v1r_d.vmf` |
| `eft_sky_metal_v2` | Sky Metal | exact VMF found |
| `eft_skyline_v2` | Skyline | closest found: `eft_skyline_v3.vmf` |
| `eft_skystep_v4` | Skystep | exact VMF found |
| `eft_slamdunk_v6` | Slam Dunk | exact VMF found |
| `eft_soccer_b4` | Soccer | closest found: `eft_soccer_b1.vmf`, `eft_soccer_b2.vmf` |
| `eft_spacejump_v6` | Space Jump | exact VMF found |
| `eft_temple_sacrifice_v3` | Temple Sacrifice | exact VMF found |
| `eft_tunnel_v2` | Tunnel | exact VMF found |
| `eft_turbines_v2` | Turbines | closest found: `eft_turbines_v2_d.vmf` |

Map identity is partly scoring mode:

- Touch-only maps emphasize speed, rotation, and run-in goals.
- Throw-only maps force committed throws and teammate clearing.
- Hybrid maps allow the most strategic variety.

Map conversion must preserve gameplay grammar, not just geometry.

## Competitive / League Evidence

The old Extreme Football League group is historical evidence for how EFT was organized socially and competitively:

`https://steamcommunity.com/groups/ExtremeFootballLeague`

Do not treat league pages as mechanics source code. Treat them as evidence for:

- viable team sizes
- tournament map choices
- competitive map bans or preferences
- player/team culture
- old server and community lineage
- streamed-match/video leads
- records, rosters, and schedule context

Known public facts from first inspection:

- The group was founded July 9, 2015.
- The group describes itself as Sunrust EFL, created for Extreme Football Throwdown.
- The page points to records, rosters, schedules, date/time announcements, and livestreamed games.
- The old listed server was `104.192.0.78:27023`.
- 2022 tournament rules used 4-player teams and standard 4v4 games.
- 2022 tournament rules used 3 randomized maps per cycle.
- The 2022 schedule used Bloodbowl, Tunnel, Handegg, Sky Step, Baseball Dash, Space Jump, Slam Dunk, Skyline, and Temple Sacrifice.
- The 2022 rules mention that some maps were banned for poor gameplay, poor FPS, or not being suitable for competitive play.
- The Past Championships thread records a long Red Rhinos / Blue Bulls team history and repeated competitive seasons.

Port implication: EFT2 should support clean 4v4 play as a first-class competitive format, even if larger public-server chaos remains supported later.

## Golden Vertical Slice: Bloodbowl

Use Bloodbowl as the first vertical slice unless the user redirects.

Canonical reference:

`C:\Users\dissonance\Desktop\EFT\Projects\eft_bloodbowl_v5.vmf`

Feel reference:

`C:\Users\dissonance\Desktop\eft 2\EFT Bloodbowl POV.mp4`

Screenshot references:

- `C:\Users\dissonance\Pictures\Steam\4000\screenshots\20161104051331_1.jpg`
- `C:\Users\dissonance\Pictures\Steam\4000\screenshots\20170424014628_1.jpg`

Current UI/style references:

- `C:\Users\dissonance\Pictures\Screenshots\Screenshot 2026-05-08 004339.png`
- `C:\Users\dissonance\Pictures\Screenshots\Screenshot 2026-05-08 004356.png`
- `C:\Users\dissonance\Pictures\Screenshots\Screenshot 2026-05-08 004419.png`

Evidence split:

- Use the 2017 Bloodbowl POV for how the sport feels during real play.
- Use the current screenshots for the HUD style, team branding, player readability, and cleaned-up presentation direction.
- Do not regress to the older HUD clutter just because the old video is the strongest live-match footage.

Why Bloodbowl first:

- It is open, readable, and speed-dominant.
- It exposes core charge/intercept/head-on behavior.
- It has hybrid scoring.
- It has visible pits/hazards and ball reset triggers.
- It has real POV footage from live play.
- It provides a strong visual remaster target: stadium, field markings, team-colored stands, giant goals, scoreboard/HUD/minimap.

Light VMF parse for `eft_bloodbowl_v5`:

| Entity | Count |
|---|---:|
| `prop_ball` | 1 |
| `info_player_red` | 24 |
| `info_player_blue` | 24 |
| `trigger_goal` | 6 |
| `trigger_ballreset` | 4 |
| `trigger_hurt` | 6 |

Bloodbowl version note:

- `EFT.md` names `eft_bloodbowl_v5` as canonical.
- The 2017 POV likely reflects `v4` or `rmx` era feel.
- `v6` exists from 2020 and may contain later fixes.
- Do not assume latest is best. Compare deliberately.

## Phase Milestones

### Phase 0: Contract And Evidence Index

- Keep this README current.
- Build a map/source index from the canonical roster and VMFs.
- Deep-read Bloodbowl VMF.
- Extract key moments from the Bloodbowl POV video.
- Perform a second Bloodbowl POV pass around each score/reset/death/round-modifier sequence.
- Archive or locally summarize public EFL group pages, especially rules, rosters, schedule/maps, rankings, past championships, and announcements.
- Produce a golden slice spec.
- Record unresolved conflicts between old contract, Lua behavior, map source, and video feel.

### Phase 1: s&box Project Scaffold

- Create a minimal s&box game project in this workspace.
- Establish `.sbproj`, source folder structure, startup scene, and assembly globals.
- Boot in editor/game.
- Add no fake gameplay placeholders that obscure missing work.

### Phase 2: Core Loop Prototype

One arena, not full Bloodbowl yet.

Required:

- Red/blue teams.
- Spawn points.
- One ball.
- Basic movement at EFT speeds.
- Automatic pickup.
- Carrier speed penalty.
- Tackle.
- Knockdown.
- Fumble.
- Goal trigger.
- Ball reset.
- Minimal HUD.

Success condition: the prototype produces scrums, turnovers, and short possessions before it looks beautiful.

### Phase 3: Bloodbowl Vertical Slice

- Import or recreate Bloodbowl gameplay layout at correct scale.
- Preserve spawns, ball origin, pits, hurt/reset triggers, and scoring volumes.
- Recreate or improve stadium presentation.
- Tune camera readability.
- Tune movement/collision until live play resembles Bloodbowl rhythm.

### Phase 4: Full Core Mechanic Parity

- Dive tackle.
- Throw windup/release.
- Head-on resolution with velocity deltas.
- Punch and cross-counter.
- Knockdown recovery states.
- Wall stop and wall slam.
- Goal slow motion and reset flow.
- Jump pads, hazards, water/void resets.
- Score types: touch, throw, hybrid.

### Phase 5: Map Grammar And Conversion Pipeline

- Define VMF entity to s&box component mapping.
- Convert canonical maps in priority order.
- Preserve map-specific scoring identity.
- Validate by entity counts, playstyle, and interaction density.

### Phase 6: Bots And Match Population

- Port bots after the human core loop feels right.
- Bots should create pressure, not perfect play.
- Validate bot matches against possession/tackle/goal/throw metrics.

### Phase 7: Remaster Presentation

- Modern models, materials, lighting, stadium dressing, VFX, sound, UI, animation.
- Better team identity and spectator readability.
- Preserve old readability lessons: ball visibility, goal clarity, minimap utility, action text.

### Phase 8: Telemetry, Replay, And Tuning

- Match recorder.
- Replay or event viewer.
- Metrics:
  - possessions
  - possession duration
  - tackles
  - tackle/possession ratio
  - knockdowns
  - goals
  - head-ons
  - throw attempts
  - throw catches
  - ball resets
- Metrics diagnose drift; they do not replace feel.

## Validation Targets

Known healthy-ish inherited metrics:

- Human+bot data in old notes: about 257 possessions/match.
- About 785 tackles/match.
- Tackle/possession ratio about 3.05x.
- Goals/match about 6.4.
- Throw catch rate about 35%.
- Logged matched-speed head-ons about 10/match, with true frontal collisions higher.
- Average match duration about 16.6 minutes.

Do not treat these as final laws. Treat them as guardrails.

Early build checks:

- Carrier should feel hunted.
- Most contested possessions should be short.
- Players should become relevant quickly after respawn.
- Head-ons should feel skill-readable.
- Missing a dive should be scary.
- Throwing under pressure should feel like a gamble.
- Bloodbowl should feel open, fast, readable, and interception-heavy.
- Scrums should reform naturally after resets and fumbles.

## Known Bad States

If any of these appear, stop and diagnose before polishing:

| Bad state | Symptom | Likely issue |
|---|---|---|
| Walking simulator | Players spend too long reaching the ball | map too large, respawn too slow, movement too slow |
| Safe carrier | Carrier survives too easily | carrier speed too high, defenders too weak, tackles too hard to land |
| Velcro carrier | Ball sticks after tackle | possession/fumble order wrong, pickup radius too forgiving |
| Ghost tackle | Hit appears to land but carrier keeps running | prediction/server authority mismatch |
| Infinite dribble | Player avoids carrier penalty by nudging ball | ball physics impulse too high |
| Statue defense | Standing still blocks perfectly | collision width/friction too strong |
| Random head-ons | Players cannot read why they won/lost | velocity sampling or resolution wrong |
| Dead throw | Passing is never worth trying | windup/timing/defender pressure overtuned |

## Map Entity Grammar

Inherited GMod entities to preserve conceptually:

| GMod entity | Remaster role |
|---|---|
| `prop_ball` | ball spawn/object |
| `info_player_red` | red spawn |
| `info_player_blue` | blue spawn |
| `info_player_spectator` | spectator spawn |
| `trigger_goal` | scoring volume |
| `trigger_ballreset` | ball reset/hazard volume |
| `trigger_jumppad` | movement boost volume |
| `trigger_hurt` | damage/death hazard |
| `trigger_knockdown` | forced knockdown volume |
| `trigger_powerup` | powerup pickup/activation |
| `prop_goal` | visible goal prop |
| `logic_teamscore` | map-authored score logic |

Conversion should preserve:

- entity counts
- entity position/volume
- team ownership
- score type
- reset coverage
- hazard semantics
- jump pad vectors
- visibility/readability

## Visual And UX Contract

The remaster should look modern without becoming visually noisy.

Priorities:

- Ball must be readable at speed.
- Carrier must be readable.
- Team identity must be readable.
- Goal zones must be readable.
- Hazards must be readable.
- HUD must show score, timer, health, team, and key action text without obscuring the field.
- Minimap is useful and should be preserved or modernized.
- Camera should support veteran spatial awareness.

Current-version UI/style target:

- Keep the cleaned-up current HUD style as the primary UI target for EFT2.
- Bottom-center match strip: red team logo, red score, compact timer capsule, blue score, blue team logo.
- Team logos should remain large, readable, and characterful; the red rhino and blue bull marks are part of the sport's identity, not optional decoration.
- Normal play HUD should be cleaner than the 2017 POV: fewer floating panels, less top-center clutter, and a stronger single score/timer anchor.
- The minimap should stay top-left, square, high-contrast, and map-shaped rather than generic radar-only. It should show map geometry, team colors, ball/player indicators, and player clusters.
- Nameplates should remain bold, team-colored, and readable at action distance, with strong outline/shadow contrast.
- Bot/player labels are part of readability in crowded scrums. Modernize typography, but do not remove the ability to identify bodies quickly.
- In-world team branding on walls, ramps, scoreboards, and arena props should stay loud and readable.
- Preserve the arcade sports tone: saturated team color, exaggerated readability, physical comedy, and blunt score clarity.
- Modern materials, lighting, animation, and postprocess should improve the current look without making it sterile, generic, or cinematic at the expense of play readability.

Bloodbowl visual targets from screenshots:

- Large stadium bowl.
- Clear green field with white markings.
- Red/blue team stand coloration.
- Oversized yellow goal structures.
- Pits/hazards visible in the field.
- Simple third-person player readability.
- Scoreboards and action text visible in-world/HUD.

## Telemetry Contract

The remaster should emit canonical gameplay events:

| Event | Meaning |
|---|---|
| `TackleResolve` | two players collide at charge/tackle relevance |
| `PossessionTransfer` | pickup, catch, strip, reset possession |
| `BallLoose` | fumble, throw release, reset spawn |
| `BallReset` | hazard, goal, stagnation, admin/map reset |
| `PlayerKnockdown` | player enters knockdown |
| `PlayerRecovered` | player returns to upright participation |
| `GoalScored` | scoring condition satisfied |
| `ThrowAttempt` | carrier enters/release throw commitment |
| `DiveAttempt` | player commits to dive |
| `HeadOn` | matched or near-matched frontal charge collision |

Telemetry exists to preserve the sport during tuning.

## Working Rules For Agents

- Read this README before changing files.
- Read the original GMod `EFT.md` before changing gameplay behavior.
- Read the relevant Lua and VMF source before implementing a mechanic.
- Read relevant s&box docs/source before choosing an engine pattern.
- Patch documents surgically.
- Preserve weird but predictive details.
- Do not turn speculative ideas into canon.
- Do not edit the original GMod project unless explicitly asked.
- Prefer small playable increments over broad architecture.
- Show changed files and validation.
- When uncertain, inspect before acting.

## Open Questions To Resolve

- Should Bloodbowl geometry follow `v5`, `v6`, or a deliberate hybrid informed by 2017 POV?
- Which map should follow Bloodbowl in the port order: Slam Dunk, Baseball Dash, Tunnel, or Temple Sacrifice?
- Should the remaster preserve Source 1 HU scale exactly or define a calibrated s&box scale unit?
- How much of old animation timing should be literal vs reauthored?
- Should bots launch with the first public slice or after human multiplayer feel is stable?
- How should old VMF brush/entity data enter s&box: direct conversion, hand rebuild, or hybrid extraction?

Keep this section current. Resolved questions should become contract decisions above.
