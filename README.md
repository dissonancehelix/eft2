# EFT2 Game Contract

This README is the living game contract for **EFT2**, the modern s&box / Source 2 remake of **Extreme Football Throwdown**.

The original Garry's Mod game is the source inheritance. EFT2 is not simply the old Lua gamemode moved into a new engine. It is a modern remake that must preserve the sport's behavioral identity while rebuilding the game with better tools, visuals, performance, presentation, validation, map intelligence, telemetry, and long-term maintainability.

**This is not a loose remake.**

EFT2 succeeds only if a veteran can enter the new game and instinctively recognize the sport within seconds: the same pressure, the same short possession windows, the same violent retargeting after a tackle, the same readable head-on stakes, the same scrum-to-breakout rhythm, the same map-specific personality.

Visual polish, animation, UI, materials, physics implementation, networking architecture, and code structure may change. The behavioral outcomes that made EFT a real digital sport must survive.

> If a change makes the game cleaner but reduces tension, contested interactions, possession volatility, reversals, or veteran-readable timing, the change is wrong even if technically sound.

---

## 0. Document Role

This file owns:

- game identity
- rules and invariants
- mechanics
- player feel
- map behavior
- map roster and entity grammar
- validation targets
- telemetry expectations
- drift diagnostics
- modern remake decisions
- phase milestones
- unresolved design forks

`AGENTS.md` owns:

- workflow rules
- source hierarchy
- mutation policy
- local toolkit policy
- analyzer/scaffold task boundaries
- s&box source/reference handling
- backend implementation notes

The README should describe **what EFT2 must become**. `AGENTS.md` should describe **how agents work on the repository**.

---

## 1. Absolute Rule

Leave the original GMod project and original GMod `EFT.md` alone unless the user explicitly asks to edit them.

Original reference material that belongs to EFT2 should live under explicit repo domains:

```text
EFT2/
  README.md
  AGENTS.md
  Game/
  Maps/
  Lua/
  SBox/
  Tools/
  Assets/
```

Do not rely on machine-specific paths in this README. Local paths, toolkit paths, and temporary repo-root source drops belong in `AGENTS.md` or local notes, not in the game contract.

---

## 2. Source Of Truth Hierarchy

When implementing, validating, or resolving conflicts, use this order:

1. Direct user instruction in the current session.
2. This root `README.md` for EFT2 game identity, rules, feel, maps, validation, and project overview.
3. `AGENTS.md` for workflow, source hierarchy, tooling, mutation policy, and local development boundaries.
4. The original GMod `EFT.md`/manifest if preserved under this repo, as inherited design/spec reference.
5. Lua/source copy under `Lua`, as the preferred implementation reference for original behavior.
6. Original VMF/map sources preserved under `Maps`.
7. `Maps/Shared/eft.fgd`, if present, as Hammer entity grammar reference.
8. Real gameplay evidence: Bloodbowl POV video, screenshots, future clips, demos, match logs, and replays.
9. Generated analyzer outputs under `Maps/<Map Name>/Analysis/` and `Maps/<Map Name>/Virtual Perception/`.
10. s&box source/docs/examples under `SBox`, as engine reference.
11. External references listed below.

When sources disagree, do not hide the disagreement. Record it and decide deliberately whether EFT2 follows:

- original design intent
- shipped Lua behavior
- later community fork behavior
- specific map revision behavior
- competitive/veteran preference
- live-match feel
- Source 2 remake constraints

Preserve weird but predictive behavior unless the user deliberately chooses otherwise.

---

## 3. Repository Domains

| Domain | Role |
|---|---|
| `README.md` | EFT2 game/remake contract |
| `AGENTS.md` | agent workflow, source hierarchy, mutation and tooling policy |
| `Game/` | future buildable EFT2 s&box game project |
| `Maps/` | canonical map domains, VMF source references, generated map analysis |
| `Lua/` | original GMod Lua/source reference for behavior extraction |
| `SBox/` | s&box docs/source/runtime/sample reference material |
| `Tools/` | EFT2-owned tools: `Tools/Indexer/` (repo working memory), `Tools/Map Analyzer/` (map intelligence), and future Observer, Contract Validator, Scenario Harness, Telemetry, Simulation |
| `Assets/` | curated evidence and remaster assets: video notes, screenshots, images, audio, references |

`WORKFLOW.md` is not part of the current durable structure unless the user explicitly restores it. Workflow and tooling policy belong in `AGENTS.md`.

---

## 4. External References

| Purpose | URL |
|---|---|
| Original JetBoom EFT repository/reference lineage | `https://github.com/JetBoom/extremefootballthrowdown` |
| Current/community EFT source lineage if used by this project | `https://github.com/dissonancehelix/extremefootballthrowdown` |
| Extreme Football League historical group | `https://steamcommunity.com/groups/ExtremeFootballLeague` |
| Extreme Football League historical VOD channel | `https://www.youtube.com/@ExtremeFootballLeague` |
| s&box documentation | `https://sbox.game/dev/doc/` |
| Facepunch s&box docs/source references | `https://github.com/Facepunch/sbox-docs`, `https://github.com/Facepunch/sbox-public` |
| Recast/Detour reference | `https://github.com/recastnavigation/recastnavigation` |
| Blender reference, if used as spatial/backend inspiration | `https://github.com/blender/blender` |

External analogies and references are orientation aids. They do not override EFT-specific evidence.

---

# Part I — What EFT2 Is

## 5. Project Identity

**Extreme Football Throwdown** is a continuous collision sport where a swarm of players repeatedly interrupts and reassigns possession of a ball that automatically attaches to whoever physically contacts it after a tackle, throw, reset, or loose-ball event.

Players do not choose possession. Possession happens to them.

Possession is not a stable reward. Possession is a target marker.

The carrier is temporarily empowered because they can score, but immediately endangered because every opponent now has a clear target. The ball is both opportunity and curse.

The core loop:

```text
Engage -> Tackle -> Displacement -> Auto-possession transfer -> Immediate retarget -> Repeat
```

Goals occur when pressure fails to reform for a brief window. A score is not usually the result of a clean planned play. It is the visible payoff after a local crisis collapses in one team's favor.

## 6. What EFT2 Is Not

This section exists because agents and designers often misread the word "football."

### EFT2 Is Not American Football

| American football concept | EFT reality | Why it matters |
|---|---|---|
| Downs / plays | Do not exist | No first-and-ten, no huddles, no play calls |
| Stoppage after tackle | Does not happen | Tackle -> fumble -> ball remains live |
| Offensive/defensive lines | No formations | Everyone is a possible tackler, carrier, escort, or victim |
| Quarterback | No fixed role | Whoever gets the ball is the carrier |
| Scripted routes | No playbook | Decisions are emergent and local |
| Possession after tackle | Ball becomes loose | Anyone can grab it |
| Clock stoppage | Almost never | Only brief goal/reset sequences |
| Field goals / punts | Do not exist as football concepts | Scoring means ball satisfies map-authored goal condition |
| Turn-based possession | Impossible | Possession can change many times in seconds |

### EFT2 Is Not These Either

| Game / genre | Why not |
|---|---|
| Basketball | No shot clock, no stable possession, no formal out-of-bounds |
| Soccer | Forward passing allowed, tackling is body collision, ball can auto-attach |
| Capture the Flag | Ball resets to contest points, not team bases |
| Madden / FIFA / NBA2K | No playcalling, no formations, no simulation sport structure |
| Blood Bowl tabletop | Not turn-based |
| Arena shooter | Movement discipline matters, but collisions replace guns |
| Party ragdoll game | Ragdoll comedy exists, but the core sport is mechanically serious |

### Useful Orientation Analogies

The community's native vocabulary includes Blood Bowl, NFL Blitz, American Gladiators, Tron, basketball/Slam Dunk, Mini Putt, and map-specific folk tech. For implementation orientation, EFT2 can also be thought of as:

- Rocket League, but the player is the car.
- Rugby broken play compressed into an arena.
- Hockey turnover rhythm without offsides or stoppage.
- Source/Quake movement discipline with tackles and throws instead of weapons.
- A fighting game neutral layer stretched across a spatial arena.

These analogies are useful only if they clarify EFT's own behavior. Do not let them overwrite the sport.

---

# Part II — Core Concepts

## C-001 Continuous Contest

Players are repeatedly drawn into contested interactions around the ball.

Possession is the trigger. Every carrier is a target. Every loose ball is an invitation to swarm. The game loop must never allow a player to feel safe or finished until the ball resets or a score resolves.

Scrums are not a failure state. Scrums are the sport.

Typical cycle:

```text
scrum -> fumble -> scramble -> breakout attempt -> re-collapse -> goal or reset
```

## C-002 Short Possession

Possession is temporary and unstable.

Because carriers are slower than defenders, a carrier who cannot reach the goal or create a passing window within seconds will be caught and stripped. Long possession is usually a sign that map pressure, defender speed, collision, or bot/player behavior is broken.

Most decisive windows are under five seconds. Many are under one or two seconds.

## C-003 Simultaneous Relevance

Most players should be able to affect events within seconds.

Map scale, movement speed, respawn timing, reset locations, and spawn placement must combine so players rejoin the same tactical sentence rather than arriving after the play is over.

## C-004 Last-Second Intervention

Scores must remain preventable until the final moment.

Goal-line stands, last-frame tackles, dive intercepts, jump catches, body-blocks, and forced resets are central emotional payoffs.

A goal that becomes unstoppable too early is not EFT.

## C-005 Predictive Positioning

Players succeed by moving early, not reacting late.

Experienced players constantly ask:

> Where will the next possession event occur within the next 1-2 seconds?

They are not merely tracking the ball. They are tracking the next collision, fumble, catch, bounce, or reset that will decide the ball.

Good players often move slightly away from the current carrier if they predict an imminent tackle. This is not zoning in a slow tactical sense. It is pre-reaction.

## C-006 Controlled Chaos

Outcomes are uncertain but readable.

Fumbles, bounces, ragdolls, and scrums create variance. That variance must still be consistent enough for players to make informed risk assessments.

Uncertainty should come from players, collision, map pressure, and timing — not from unreadable random ball physics.

## C-007 Migrating Conflict Zone

The important location of play constantly relocates.

A corner scramble can become a center breakout instantly. A midfield tackle can turn into a goal-line emergency. A reset can convert a defensive escape into a neutral scrum.

EFT is a cascade game: small local interactions accumulate until pressure fails to reform and the state resolves suddenly into a run-in goal, committed throw, defensive save, or counter-collapse.

## C-008 Downfield Contest Creation

Passing and throwing create new contests, not guaranteed possession.

A pass is often a controlled fumble into a better fight. The value is not always "teammate catches cleanly." The value may be moving the next contested collision to a better location.

## C-009 Commitment Under Uncertainty

Players must act before full information exists.

Tackles, dives, jumps, throws, and turns are commitments. If a player waits until they are certain, they are usually too late.

EFT rewards decisive early action more than perfect late reaction.

## C-010 Continuous Participation

Respawns and resets return players into the same ongoing play.

Elimination, death, pitfall, water, knockdown, and wall-slam are tactical participation removals. They must hurt, but they must not turn the game into long spectator downtime.

## C-011 Transition Dominance

The most important events in EFT are transitions, not stable states.

```text
tackle -> fumble -> pickup -> new target
throw -> loose ball -> contested catch/pickup -> new target
hazard -> reset -> convergence -> scrum
```

Stable carry is not the core. Possession change is the core.

A good player is not necessarily the one who holds the ball longest. A good player is the one correctly positioned for the highest number of state transitions.

### Tackle Taxonomy

Tackles serve two different functions:

| Type | Target | Result | Meaning |
|---|---|---|---|
| Possession tackle | carrier | ball drops/fumbles, possession transition begins | direct turnover pressure |
| Clearance tackle | non-carrier | upright contester removed | creates running/throwing room |

Clearance tackles are not failed possession attempts. They are how teammates create scoring windows.

---

# Part III — Non-Negotiable Invariants

## P-010 Sport Identity

EFT2 is a continuous-contact team sport with a ball and goals.

It is not an abstract spatial toy. It is a digital sport with score, pressure, rivalry, roles, and public skill signals.

## P-020 Interaction Frequency

The game must generate frequent contested interactions around the ball.

If possession becomes safe, EFT dies.

Protects: C-001, C-002, C-009.

## P-030 Role Fluidity

Players do not have fixed roles.

A player constantly shifts between carrier, defender, escort, interceptor, clearer, loose-ball scavenger, and victim based on what matters next.

No code should enforce class-based restrictions that prevent a player from acting on the ball or opponents.

Protects: C-003, C-010, C-011.

## P-040 Prediction Dominance

Skill is rewarded for anticipating future interactions/positions, not merely reacting to the current ball location.

Mechanics must favor early positioning and angle cutting over raw reaction time.

Protects: C-005, C-009.

## P-050 Movement Constraints

All players share the same base movement capabilities.

The carrier is always slower than defenders in normal play. Players win by moving earlier and taking better paths, not by having superior stats.

Protects: C-005, C-003.

## P-060 Head-On Collision Skill

Head-ons are decided by instantaneous velocity and commitment.

Small player-generated velocity differences must matter. If head-ons become symmetric, normalized, or random-feeling, a major veteran skill layer disappears.

Bot players must not become perfect head-on machines.

Protects: C-006, C-009, C-011.

## P-070 Passing Purpose

Passing is for playmaking and survival, not safe ball movement.

A pass is a dangerous commitment. On many maps, running is safer. On throw-only maps, passing becomes mandatory and teammates must create the breathing room.

Protects: C-008, C-007, C-001.

## P-080 Ball Readability

The ball is a focal point for interaction, not a pure chaos generator.

Throws should remain consistent. Fumbles may be dynamic but must remain readable and contestable. Random physics noise must not dominate player decisions.

Protects: C-006, C-005.

## P-090 Hazards, Death, And Reset Migration

Hazards are population control and conflict migration tools.

Voids, pits, lava, water, death triggers, and reset triggers regulate engagement density by removing participants and/or forcing ball relocation.

A reset is not downtime. A reset is a forced re-scrum.

Protects: C-010, C-003, C-007.

## P-100 Reversals And Hype

The system must maximize opportunities for sudden reversals:

- clutch goal saves
- swarm escapes
- tackle chains
- jump-flung catches
- predicted interceptions
- desperate hazard resets
- last-second throw blocks
- perimeter pickups from scrums

Scoring must remain meaningful and hype.

Protects: C-004, C-001.

## P-900 What Breaks EFT2

Do not do these unless the user deliberately chooses a new sport:

- making possession safe/stable
- making throws risk-free or instant
- allowing full mobility during throw without a deliberate design fork
- removing fumbles
- removing forced resets
- making the ball highly random
- softening knockdowns until consequences vanish
- allowing meaningful action while knocked down
- slowing respawns so players cannot rejoin active play
- removing head-on momentum influence
- making head-ons symmetric/random
- over-smoothing friction or wall punishment
- making ball resets create downtime
- preventing scrums from forming
- delaying automatic possession transfer on contact
- giving bots perfect tracking, perfect head-ons, or perfect throws
- replacing chaotic collision sport identity with formal sports-sim structure
- using "modern physics realism" to erase arcade-readable outcomes

## P-910 Excluded Or Deferred Mechanics

| Mechanic | Status / reason |
|---|---|
| Fixed formations | Excluded; EFT uses emergent roles |
| Downs / play calls | Excluded; play is continuous |
| Aim assist on tackles | Excluded; skill expression matters |
| Throwing guide/path trace | Excluded by default; lowers skill expression |
| Turn-based possession | Excluded; possession volatility is core |
| Safe pickup/receive animation | Excluded; auto-pickup surprise is core |
| Power struggles | Design fork; old mash, Publish 429 seeded-key, or Source 2-native alternative must be deliberate |
| Items | Deferred; some are part of legacy texture but unbalanced for first slice |
| High jump | Removed/deferred unless intentionally revived |
| Featherball / scoreball / unusual ball states | Deferred unless map-specific identity requires them |

## P-950 Behavioral Guarantees

### Possession Volatility

Possession should naturally change hands frequently during active play. The carrier should feel temporarily empowered but inevitably threatened.

### Collision Density

Players should regularly be within a few seconds of a meaningful interaction: tackle attempt, interception attempt, contested ball, body-block, hazard reset, or goal-line stand.

### Carrier Emotional Tension

The carrier must feel dangerous but not safe. A scoring attempt should always feel possible and interruptible.

### Shared Attention Convergence

The game should naturally pull most players toward the evolving conflict location without explicit coordination.

### Global Readability

Major events must be immediately understandable: turnovers, breakaways, saves, last-second stops, goals, resets, and knockdowns.

### Universal Influence

Low-skill players should still matter through body presence, pressure, accidental interference, and recovery attempts. The game should reward mastery without making casual presence irrelevant.

### Map Authority

Maps are gameplay regulators, not scenery. Geometry changes re-entry timing, collision angles, participant density, hazard removal frequency, throw survival probability, route viability, cascade likelihood, and scoring tempo.

During engine porting, adapt the engine to preserve map behavior rather than simplifying maps to fit generic physics assumptions.

---

# Part IV — Simulation Model For EFT2

All numeric values below are inherited targets. EFT2 may need s&box/Source 2 calibration. Preserve player-perceived timing and outcomes over literal numeric imitation when direct conversion diverges.

## M-110 Movement And Charge

| Property | Target |
|---|---:|
| Gravity | 600 HU/s² equivalent |
| Base max speed | 350 HU/s equivalent |
| Carrier speed | 262.5 HU/s equivalent |
| Pity carrier speed | 315 HU/s equivalent |
| Strafe-only speed | 160 HU/s equivalent |
| Charge threshold | 300 HU/s equivalent |
| Charge animation lead-in | about 270-280 HU/s |
| Approx 0 -> charge | about 1.0s |
| Approx 0 -> max | about 1.5s |
| Turning grace | about 4 degrees before heavy penalty |
| Wiggle/curve boost | small, player-generated, about +5 to +10 HU/s equivalent |

Charge state means:

```text
grounded + velocity above threshold + eligible state
```

Charge state is not just speed. It is the player's threat state.

### Forward-Locked Charging

Charging should behave like a committed missile:

- forward input matters
- yaw steering matters
- sharp turns cost speed
- zig-zag abuse should not be optimal
- once a player picks a line, changing course should carry risk

### The Curve

Veterans could gain tiny speed advantages by turning cleanly into a collision within the grace zone. The result was not random: players who understood movement could win 357 vs 356 style head-ons.

EFT2 must preserve this **skill-readable micro-advantage** somehow, even if the exact Source 1 movement formula is replaced.

### Wall Punishment

Any obstacle that stops forward progress should destroy charge and create vulnerability.

"Wall" means:

- wall
- pillar
- platform edge
- prop
- ramp at a bad angle
- goal structure
- ring
- map edge
- geometry that kills momentum

Wall contact does not automatically fumble. Wall contact does not automatically knock down an upright player. The punishment is loss of state.

## M-120 Knockdown And Recovery

| Property | Target |
|---|---:|
| Knockdown duration | about 2.75s |
| Effective removal | about 4-5s including recovery/re-acceleration |
| Post-hit charge immunity | about 0.45s |
| Per-attacker anti-stunlock immunity | about 2.0s |
| Cumulative/global immunity fork | preserve/review inherited clock behavior |

Knockdown is population control. It temporarily removes upright participation.

Requirements:

- knocked-down players cannot pick up ball
- knocked-down players can remain obstacles
- downed bodies may affect play if source behavior supports it
- recovery should be visible and readable
- chain stunning by multiple attackers may exist, but must be bounded
- single-attacker spam should not become unreadable bodycamping

## M-130 Tackle Mechanics

| Property | Target |
|---|---:|
| Charge threshold | 300 HU/s equivalent |
| Tackle range | dynamic body/radius equivalent |
| Impact force | target receives charger velocity x ~1.65 equivalent |
| Attacker recoil | attacker velocity x ~-0.03 equivalent |
| Charge damage | low / mostly symbolic unless health system matters |

Rules:

- charging grounded player vs neutral target: charge wins
- charging vs charging: higher speed wins unless close-speed special case applies
- ground beats air in charge resolution
- airborne players cannot tackle
- carrier cannot normally initiate charge hits
- tackle on carrier causes fumble/loose ball
- tackle on non-carrier is a clearance/disqualification action

## M-135 Combat Matrix

| Matchup | Expected result |
|---|---|
| Charge vs neutral | charge wins |
| Charge vs charge | higher speed wins; close case may trigger head-on/power struggle behavior |
| Dive vs neutral | dive wins if contact succeeds |
| Dive vs charge | charge generally wins |
| Punch vs charge, correct cross-counter timing | punch wins |
| Punch vs charge, bad timing | charge wins |
| Dive vs punch | punch can win depending on timing/source behavior |
| Neutral vs neutral | solid stop/body obstruction |

## M-140 Dive Mechanics

| Property | Target |
|---|---:|
| Trigger | secondary attack while charging, grounded, not carrying |
| Extra speed | +100 HU/s equivalent |
| Upward boost | 320 HU/s equivalent |
| Turn rate | about 90 degrees/s |
| Ends in vulnerability | yes |
| Whiff penalty | yes |
| Hit reward | slightly faster recovery if inherited behavior supports it |
| Ball pickup during dive | yes, as risky interception route |
| Dive ball-intercept landing penalty | about 50% speed reduction |

Dive is a high-risk reach extension, not a free movement upgrade.

Dive-tackle ball pickup is a first-class EFT mechanic and should not be lost in the remake.

## M-145 Punch And Cross-Counter

| Property | Target |
|---|---:|
| Punch duration | about 0.5s |
| Cross-counter window | last 0.2s |
| Force | about 360 impulse equivalent |
| Use case | rare, defensive, cornered, goal-line, timing punish |

Punching is not the primary combat loop. Charging/tackling is.

Cross-counter is a tight timing punish: a charger hitting a player during the correct punch window gets stopped/spun/knocked down depending on inherited behavior and chosen port design.

## M-150 Possession

Possession rules:

- pickup on ball contact
- no pickup key
- no confirmation animation gate
- no deliberate possession acceptance
- knocked-down players cannot pick up
- carrier speed penalty applies immediately
- carrier becomes target of the field
- carrying disables rush/charge in relevant inherited builds
- throwing or being tackled breaks possession
- reset creates a new loose/available ball state

Auto-pickup surprise is intentional. "Oh no, I have it" moments create instant retargeting.

## M-160 Fumble / Ball Loose

| Property | Target |
|---|---:|
| Fumble horizontal velocity | carrier velocity x ~1.75 |
| Fumble vertical pop | about 128 HU/s |
| Ball mass | 25 equivalent |
| Linear damping | low, about 0.01 equivalent |
| Angular damping | about 0.25 equivalent |
| Bounce reduction | about 0.75x |
| General pickup immunity after drop | about 1.0s |
| Team pass immunity | about 0.2s ball / 0.25s carry items |

Loose ball should be contestable and readable. It should not roll forever, stop dead every time, or become random noise.

## M-170 Passing And Throw Windup

| Property | Target |
|---|---:|
| Input | hold secondary while carrying, release to throw |
| Full windup | about 1.0s |
| Throw impulse | about 1100 along aim vector |
| Arc | gravity-affected |
| Speedball windup | faster, about 0.5x |
| Speedball throw | stronger if inherited state supports it |

Passing is the longest voluntary vulnerability state.

The old contract and later source/community behavior may disagree on whether throw windup fully freezes the carrier or allows beginning a throw without stopping. EFT2 must treat this as a deliberate design fork:

- **Frozen throw model:** maximizes commitment and vulnerability.
- **Moving-start throw model:** preserves later flow if source confirms it and veteran feel supports it.

Do not decide casually. This affects the run/pass balance.

## M-175 Jump

| Property | Target |
|---|---:|
| Vertical speed | about 200 HU/s |
| Cooldown | about 0.3s |
| Breaks charge | yes |

Airborne state is paradoxical:

- airborne players are harder to tackle in some contexts
- airborne players cannot tackle
- landing is a vulnerable transition

Jumping is useful for carriers, platforms, throws, and gaps. Jumping is bad in a scrum if it removes your ability to contest.

## M-178 Walls, Obstacles, And Wall Slam

Obstacle impact:

- kills charge
- usually sets speed to zero/near-zero
- does not fumble by itself
- does not knock down upright players by itself

Wall slam for already-knocked players may be preserved if source behavior and Source 2 physics support it:

| Property | Target |
|---|---:|
| Speed threshold | about 200 HU/s |
| Freeze duration | about 0.9s |
| Wall normal | steep surface |
| Damage | low/symbolic; time lost matters more |

## M-179 Collision Model

EFT collision is gameplay, not generic physics.

| Interaction | Expected behavior |
|---|---|
| Opponents | solid / tackle logic applies |
| Teammates | pass-through or reduced blocking to prevent griefing |
| Knocked-down bodies | potentially solid to all, obstacle texture |
| Getting up | may use avoid/pass-through state for flow |
| Diving/charging/knockdown | may require temporary collision mode changes |

The inherited game used normal/pass-through/avoid style logic to preserve flow and hit detection. EFT2 should preserve the outcome even if implemented differently.

## M-180 Hazards And Resets

| Hazard | Player effect | Ball effect |
|---|---|---|
| water | helpless/swim/slow, not necessarily death | instant reset |
| lava | death or hurt + water/reset behavior | instant reset |
| bottomless pit / void | death | reset via trigger or anti-stuck |
| spike pit | death/participation removal | reset or loose-ball denial |
| roof/stuck/skybox | anti-exploit | timer or instant reset |

Ball reset triggers:

- untouched 20s
- water contact
- carrier in deep water
- skybox/stuck
- hazard volumes
- goal scored
- map-authored reset volumes

Resets should force new convergence.

## M-190 Scoring

| Property | Target |
|---|---:|
| Goal value | usually 1 |
| Touch score | carrier enters touch-enabled goal |
| Throw score | thrown ball enters throw-enabled goal |
| Hybrid score | both count |
| Post-goal slow motion | about 2.5s at 0.1x |
| Reset flow | celebration -> ball reset -> pre-round/brief freeze -> resume |

Scoring is map-authored. The scoring volume is not always equal to the visible goal. Multiple raw triggers may represent one gameplay scoring complex.

## M-195 Match Structure

| Setting | Target |
|---|---:|
| Goal cap | 10 for EFT2 target unless changed |
| Match time | 15 minutes |
| Warmup | about 30s |
| Respawn delay | about 5s |
| Bonus/live-time handling | preserve live-play pacing |

## M-198 Pity Mechanic

Pity mechanic target:

- trigger when one team trails by 4+ goals
- losing team's carrier speed rises from 0.75x to about 0.90x
- pity carrier becomes about 315 HU/s
- still below empty-handed 350 HU/s defenders, but much more dangerous

This is not "rage mode." It is a carrier-speed compensation lever.

## M-199 Team Sizes

| Context | Target |
|---|---:|
| Low population | 3v3 playable |
| Competitive baseline | 4v4 or 5v5 depending era/league target |
| Public baseline | 5v5 to 10v10 |
| Large chaos | 10v10+ supported later |
| Bot fill | scaffold empty servers, do not replace humans |

EFT2 should support clean 4v4 as a first-class competitive format and larger public chaos later.

---

# Part V — Canonical Events And Telemetry

EFT2 should emit canonical gameplay events so tuning can be evidence-driven.

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
| `HazardContact` | player/ball touches hazard or reset-relevant volume |
| `PowerupActivated` | ball/player enters powerup state |
| `ScrumDetected` | local high-density contested ball event, generated analytically |
| `RouteBreakout` | possession escapes high-density conflict into open route, generated analytically |

Telemetry exists to preserve the sport during tuning. Metrics diagnose drift; they do not replace feel.

Healthy inherited-ish guardrails:

| Metric | Healthy-ish target / inherited note |
|---|---|
| average possession duration | about 1-3s |
| tackle/possession ratio | about 2-4x |
| goals/match | about 6-ish, map dependent |
| throw catch rate | around 35% in inherited mixed data |
| matched-speed head-ons | logged subset only; true frontal contests higher |
| human relevance after respawn | should rejoin active tactical sentence |
| scrum duration | often 2-5s before breakout/reset |

Do not treat these as laws. Treat them as drift alarms.

---

# Part VI — The Feel

## The Soul Of EFT2

Football is the theme. The actual genre is a high-frequency role-switching arena sport where collision physics create localized crises and players continuously predict, cause, and escape those crises.

EFT2 is not about stable possession. It is about transitions.

The fun comes from how often your importance changes:

```text
defender -> tackler -> knocked down -> recovering -> loose-ball scavenger -> carrier -> victim -> defender
```

Physics assigns roles repeatedly.

## Charge State Economy

Charge state is the single most important resource.

At 300+ HU/s equivalent and grounded, a player controls space. Below charge state, the player is prey. Walls, sharp turns, jumps, and collisions matter because they force players to lose state.

| Situation | Charge? | Threat |
|---|---|---|
| sprinting at full speed, grounded | yes | maximum |
| just landed around 280 HU/s equivalent | no | vulnerable |
| hit a wall and stopped | no | dead if enemies nearby |
| sharp turn dropped below threshold | no | exposed |
| carrier at 262.5 equivalent | no | target |
| pity carrier around 315 equivalent | yes or near yes depending rules | dangerous |

The "1.5-second eternity" matters. Going from 0 to dangerous again takes long enough for the swarm to punish you.

## Air Vulnerability Paradox

Airborne movement is useful but dangerous.

| State | Can tackle? | Can be tackled? | Meaning |
|---|---|---|---|
| grounded + charging | yes | yes/head-on | combat state |
| airborne | no | context-dependent | evasion/repositioning |
| landing | maybe after speed recovers | yes | vulnerable transition |

Jumping is smart for platform routes, gap crossing, carrier evasion, and height throws. Jumping is stupid if it removes the last defender's ability to contest.

## Human Cognitive Model

Players did not think in formations, routes, zones, or plays.

Experienced players operated on immediate prediction:

> Where will the next possession event occur?

They reacted to confirmed predictions rather than completed events. Good defenders did not chase the carrier directly; they moved toward the likely interruption point.

The game was learned procedurally:

```text
observe -> anticipate interruption -> reposition -> collide -> retarget
```

EFT2 must preserve this procedural feel. If players start deliberating like a formal sports sim, the remake has drifted.

## Reflex Continuity

The goal of the remake is not visual fidelity alone. It is **reflex continuity**.

A veteran player should:

- recognize charge state immediately
- feel carrier danger immediately
- know when a head-on was lost by speed/timing
- instinctively cut angles
- expect fumbles after tackles
- expect scrums after resets
- fear wall stops
- feel throw windup as danger
- know when a goal is still preventable

If veterans must relearn the interaction timing from scratch, EFT2 is wrong even if the mechanics appear similar on paper.

## Emotional Rhythm

The match has a rhythm:

```text
scrum/crescendo -> breakout/release -> chase/tension -> goal/climax -> reset/silence -> re-scrum
```

Knockdown, recovery, re-acceleration, and re-engagement create repeating intervals. Any change that flattens this rhythm makes EFT2 feel monotonous.

## Required Player Perceptions

Players should feel:

- hunted while carrying
- immediately relevant after spawning
- dangerous only when charged
- responsible when losing a head-on
- exposed after missing a dive
- urgent during throw windup
- rewarded for predicting the next possession event
- pulled into dense local crises
- able to make a last-second save
- aware that the map itself changes the sport

Players should not commonly feel:

- safe carrying the ball
- like they are running a planned play
- like fixed positions exist
- like they are waiting for their turn
- like goals are unstoppable near the line
- like the ball is random physics noise
- like bots are perfect
- like map geometry is decorative

---

# Part VII — Player Decision Model

## What Players React To

| Information | Meaning | Response time |
|---|---|---|
| nearest enemy vector | "Am I about to be tackled?" | instant |
| own speed | "Am I charged?" | constant |
| ball carrier identity | "Who is target?" | <0.5s |
| distance to goal | "Can I score before caught?" | read on pickup |
| teammate positions | "Can they clear or receive?" | peripheral |
| map geometry ahead | "Will I lose speed?" | constant |
| enemy velocity vectors | "Where is intercept?" | 1-2s lookahead |
| downed bodies | "Obstacle or soon-active enemy?" | peripheral |
| score/time | "Risk or safe reset?" | occasional |

Players react to spatial pressure: the feeling that space is closing.

## Safe vs Threatened

**Safe-ish:**

- moving 340+ with no enemy in forward cone
- teammate has ball and you are near enough to clear
- elevated platform with route options
- open path to goal
- just respawned near active play

**Threatened:**

- carrying ball
- below charge threshold
- enemy directly ahead
- in corridor
- winding up throw
- just landed
- knocked down
- near wall/edge/hazard
- isolated with no clearing teammate

## Run vs Throw

```text
I HAVE THE BALL.

Path to goal clear?
  -> RUN.

Close to goal?
  -> RUN.

Enemy pressure ahead and teammate open?
  -> CONSIDER THROW, but only if the window exists.

On elevated platform?
  -> THROW may be viable.

Throw-only map?
  -> THROW is mandatory, so teammates must clear/block.

Default?
  -> RUN.
```

Anything that makes throwing too safe turns EFT from a running/collision sport into a passing game. Anything that makes throwing useless removes playmaking and throw-only map identity.

## Why Positioning Beats Reaction

Positioning decisions that win:

- cut the carrier's future angle
- stay on scrum perimeter
- arrive goal-side before the carrier
- use ramps instead of jumps to preserve charge
- take powerup route before the obvious chase route
- move toward the fumble, not the current carrier
- clear the defender who matters next

Reaction time matters less because meaningful decisions happen before contact.

---

# Part VIII — Modern Remake Principles

## Behavioral Fidelity Over Literal Fidelity

EFT2 does not need to reproduce every Source 1 implementation detail literally. It must reproduce the behavioral outcomes players perceive.

May vary:

- rendering
- animation system
- networking architecture
- physics solver implementation
- code structure
- asset fidelity
- HUD implementation
- scene/entity architecture
- editor tooling

Must remain functionally equivalent:

- automatic possession transfer on contact
- carrier vulnerability
- throw commitment window
- head-on velocity priority
- dense tackle/fumble/retarget loops
- immediate attention migration after possession change
- participation removal through knockdown/hazards
- map-authored scoring and hazard grammar
- map-specific powerup identity
- goals preventable until final moment

## Modernization Targets

EFT2 should improve:

- visual identity
- readability
- lighting/materials/models
- animation clarity
- VFX and sound
- HUD/minimap/action text
- match flow UI
- spectator tools
- networking/prediction/server authority
- map conversion tooling
- telemetry/replays
- diagnostics
- bot pathing
- editor workflow
- performance/player count stability

Modernization is valid only when it preserves interaction properties.

## s&box / Source 2 Adaptation

s&box is a C# scene/GameObject/Component engine, not a Lua gamemode system.

Expected future architecture:

| System | Responsibility |
|---|---|
| `GameSystem` | match state, teams, score, round flow, entity discovery |
| `PlayerController` or equivalent | EFT movement, charge, dive, throw, knockdown, camera, animation |
| `Ball` | carrier state, loose physics, pickup, fumble, reset, scoring eligibility |
| `GoalTrigger` | touch/throw/hybrid scoring and team ownership |
| `SpawnPoint` | red/blue/spectator spawn points |
| `BallResetTrigger` | hazard/stuck/void reset behavior |
| `JumpPad` | map-authored movement boost |
| `Hazard` | hurt/death/water/lava/void behavior |
| `PowerupTrigger` | speedball/waterball/iceball/etc. |
| `Hud` | score, timer, health, team, minimap, action text |
| `Telemetry` | match events, replay data, tuning metrics |
| `BotController` | local-rule pressure scaffolding, not perfect play |

Use plain names unless engine collisions require prefixes. `Ball` is better than `EftBall` if there is no ambiguity.

Do not blindly use stock movement if it erases EFT charge-state economy.

---

# Part IX — Maps

## Map Authority

Maps are not scenery. Maps are behavioral parameters.

Geometry changes:

- re-entry timing
- collision angles
- number of simultaneous participants
- hazard removal frequency
- throw survival probability
- scoring precision
- reset migration
- line of sight
- powerup route value
- swarm density
- breakout likelihood
- cascade speed

A player who dominates Bloodbowl may struggle on Slam Dunk because the sport changes by map.

## Canonical Map Roster

| Source filename | Display name | Notes |
|---|---|---|
| `eft_baseballdash_v3` | Baseball Dash | baseball diamond, throw-only, large-server favorite |
| `eft_big_metal03r1` | Big Metal | industrial arena |
| `eft_bloodbowl_v5` | Bloodbowl | flat NFL-style stadium, open swarm reference |
| `eft_castle_warfare` | Castle Warfare | medieval/castle setting |
| `eft_chamber_v3` | Chamber | enclosed arena |
| `eft_cosmic_arena_v2` | Cosmic Arena | space theme, powerup-heavy |
| `eft_countdown_v4` | Countdown | rotation/canonical candidate |
| `eft_handegg_r2` | Handegg | American football field identity |
| `eft_lake_parima_v2` | Lake Parima | outdoor/lake, waterball relevance |
| `eft_legoland_v2` | Legoland | colorful block arena |
| `eft_minecraft_v4` | Minecraft | block arena |
| `eft_miniputt_v1r` | Mini Putt | golf theme, multiple goal types |
| `eft_sky_metal_v2` | Sky Metal | elevated platforms, throw-only |
| `eft_skyline_v2` | Skyline | rooftop setting |
| `eft_skystep_v4` | Skystep | floating platforms, tight corridors, throw-only |
| `eft_slamdunk_v6` | Slam Dunk | basketball theme, separate throw/touch goals |
| `eft_soccer_b4` | Soccer | soccer field |
| `eft_spacejump_v6` | Space Jump | low gravity / sky-route identity |
| `eft_temple_sacrifice_v3` | Temple Sacrifice | Aztec theme, lava gaps, precision throws |
| `eft_tunnel_v2` | Tunnel | underground corridors, touch-only |
| `eft_turbines_v2` | Turbines | turbine arena, spawn-bounce tech history |

Map version suffixes are Source 1/BSP-era provenance, not EFT2 identity. EFT2 map domains should use display names.

## EFT2 Map Domain Structure

`Maps/` contains canonical map domains.

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
  Bloodbowl/
    README.md
    Bloodbowl.vmf
    Analysis/
    Virtual Perception/
    Simulation/
```

The root VMF in each map domain is a read-only original Source 1 reference. Do not edit, reformat, normalize, or regenerate it. Original filenames and suffixes live in `Maps/source_manifest.json`.

Generated folders:

| Folder | Role |
|---|---|
| `Analysis/` | structured parser output, semantic groups, confidence reports, gameplay profiles |
| `Virtual Perception/` | LLM-facing spatial/gameplay artifacts |
| `Simulation/` | future optional gameplay prediction; placeholder until started |

## Map Identity By Scoring Mode

| Mode | Meaning | Examples |
|---|---|---|
| touch-only | carrier must run ball into goal | Tunnel, Skyline, Chamber, Legoland |
| throw-only | ball must be thrown into goal | Baseball Dash, Skystep, Space Jump, Temple Sacrifice, Sky Metal |
| hybrid | touch and throw both matter | Slam Dunk, Bloodbowl, Soccer, Mini Putt, Cosmic Arena |

Scoring mode changes the sport. Throw-only maps are not gimmicks; they force teammate clearing and committed shot windows.

## Map Geometry As Tactical Space

| Feature | Tactical purpose | Example |
|---|---|---|
| raised platforms | alternate lanes, height throws, route split | Slam Dunk |
| ramps | speed-preserving elevation changes | many maps |
| jump pads | launch routes, surprise angles, slam routes | Slam Dunk, Skystep |
| corridors | chokepoints, body-block defense | Tunnel |
| wide fields | swarm chaos, carrier dodge space | Bloodbowl, Soccer |
| pits/voids | participation removal, intentional reset | Space Jump |
| lava/water | hazard + reset semantics | Temple Sacrifice |
| rings/hoops | precision scoring, shot obstruction | Slam Dunk, Mini Putt |
| rotating blockers | shot denial, timing layer | map-specific |
| pillars/props | line-of-sight breaks, jukes, wall-stop risk | various |

## Map Design Signals

Good EFT maps:

- create frequent contested interactions
- preserve quick re-entry
- make scoring possible and preventable
- create identifiable route decisions
- support map-specific identity
- make powerups meaningful
- use hazards to regulate density, not random punishment
- reward both prediction and commitment
- allow scrums to form and resolve

Bad EFT maps:

- are too large
- produce long non-interactive travel
- allow ball-spawn camping
- create instant uncounterable goals
- trap matches in 0-0 overtime
- make scoring random
- over-clutter until collision becomes noise
- remove the ball from contest too often
- punish low-skill participation so hard that new players cannot matter

## Map Intelligence

Map analysis must teach agents how maps play, not merely what entities exist.

Raw entity count is evidence, not meaning.

A map analyzer must infer:

- spawn clusters
- ball spawn
- goal complexes
- score types
- hazards
- reset regions
- powerup locations and route value
- jump/push route logic
- platform and vertical layer structure
- chokepoints
- likely scrum zones
- likely breakout routes
- likely defender intercept zones
- likely goal-line stand points
- map identity tags

Every inference should include confidence and evidence.

### First Map Intelligence Target: Slam Dunk

Slam Dunk is first for offline map intelligence because it stresses:

- platform layout
- verticality
- speedball/powerup placement
- jump/push route logic
- hoop/scoring complex interpretation
- throw scoring vs movement-assisted slam-dunk scoring
- high-energy scoring flow
- clutch shot/dunk windows

Do not hard-code memory into analyzer output. Use known Slam Dunk behavior as validation expectations. The analyzer should infer as much as possible from VMF, FGD, geometry, and entity semantics.

### Second Map Intelligence Target: Bloodbowl

Bloodbowl is second for map intelligence and remains the later full gameplay vertical slice.

It tests:

- open flat layout
- spawn-to-ball convergence
- flat swarm behavior
- hybrid scoring
- pits/hazards/resets
- raw trigger counts vs actual scoring complexes
- readable speed/intercept/head-on behavior

## Map Entity Grammar

Inherited GMod/Hammer entities to preserve conceptually:

| Entity | Role |
|---|---|
| `prop_ball` | ball spawn/object |
| `info_player_red` | red spawn |
| `info_player_blue` | blue spawn |
| `info_player_spectator` | spectator spawn |
| `info_observer_point` | spectator/camera reference |
| `trigger_goal` | scoring volume |
| `trigger_ballreset` | ball reset/hazard volume |
| `trigger_jumppad` | movement boost volume |
| `trigger_abspush` | legacy push/jumppad alias |
| `trigger_hurt` | damage/death hazard |
| `trigger_knockdown` | forced knockdown volume |
| `trigger_powerup` | powerup pickup/activation |
| `prop_goal` | visible goal prop |
| `logic_teamscore` | map-authored score logic |
| `env_teamsound` | team-specific audio |
| `logic_norandomweapons` | spawn/item behavior hint |

Conversion must preserve:

- entity count
- position
- volume
- team ownership
- score type
- trigger intent
- reset coverage
- hazard semantics
- jump vectors
- powerup type/duration
- visibility/readability
- relationship to surrounding geometry

## FGD Semantics

`Maps/Shared/eft.fgd`, if present, is the shared read-only Hammer entity semantics reference.

Important expected semantics:

| Entity | Important fields |
|---|---|
| `trigger_goal` | `teamid`, `points`, `scoretype` |
| `trigger_powerup` | `powerup`, `poweruptime` |
| `trigger_jumppad` | `pushvelocity`, `knockdown`, direction/force keys |
| `trigger_abspush` | legacy jump/push semantics |
| `trigger_ballreset` | reset area semantics |
| `trigger_knockdown` | knockdown duration/effect |
| `prop_ball` | ball spawn and outputs |
| `logic_teamscore` | score event I/O |

Score type:

| Value | Meaning |
|---:|---|
| 0 | no scoring |
| 1 | touch only |
| 2 | throw only |
| 3 | touch and throw |

## Ball Powerups

Powerups are often map identity, not cosmetic spice.

| Powerup | Expected meaning |
|---|---|
| `speedball` | speed boost, faster throw windup, stronger throw |
| `waterball` | carrier can use water routes |
| `iceball` | low friction / sliding ball behavior |
| `scoreball` | scoring modifier / special map state if enabled |
| `blitzball` | explosive/fire legacy behavior if enabled |
| `magnetball` | disabled/deferred unless deliberately revived |
| `strongarm` / strong throw states | stronger throws if inherited map uses it |
| `featherball` / gravity states | deferred unless map identity requires |

Map analyzer and conversion must treat powerups as gameplay grammar.

---

# Part X — Bots

## Bot Role

Bots exist to prevent empty-server inertia and maintain engagement density.

They are population scaffolding, not replacement humans.

Bots should feel like mid-level humans:

- active
- sometimes wrong
- sometimes brilliant
- often chaotic
- readable
- imperfect

They should be tuned by prediction horizon and decision quality, not mechanical cheating.

## Bot Anti-Patterns

Never make bots:

- line up in formations
- stop after tackles
- wait for turns
- run scripted routes
- ignore loose balls
- walk when they should charge
- path along walls until they lose speed
- aim throws perfectly
- win head-ons perfectly
- replace human mastery
- use global strategy trees that erase local chaos

## Core Bot Behaviors

Priority order:

1. Stay upright if possible.
2. Move toward the current or next transfer interface.
3. Snap instantly to new ball/carrier attractors.
4. Stagger commitment; do not dogpile perfectly.
5. Attack angles, not current positions.
6. Maintain angular diversity around carrier/ball.
7. Detect throw windup and commitment windows.
8. Use local rules; emergent strategy comes from correct transitions.
9. Avoid walls, pits, and bad geometry.
10. Keep moving.

## Local Decision Sketch

```text
IF knocked down:
  recover, keep tracking likely next conflict

IF carrying ball:
  run to goal if path is clear
  avoid head-on defenders
  throw only if pressure and map/scoring mode justify it
  consider reset if pinned near own goal and map supports it

IF ball is loose:
  contest immediately
  predict bounce/pickup point
  avoid redundant path with teammates

IF teammate has ball:
  clear nearest relevant defender
  maintain angular support, not formation
  prepare for fumble/pickup

IF enemy has ball:
  cut off future movement
  compress options
  commit if within tackle window
  do not chase previous carrier after possession changes
```

## Bot Map Awareness

Bots must understand map identity:

- throw-only maps require shot setup
- touch maps reward run-in support
- hybrid maps require mode choice
- jump pads create route commitments
- hazards create reset and participation removal
- narrow corridors enable body-blocks
- platforms change line of sight and throw viability
- speedballs alter tempo and route value

Bots should eventually consume Map Analyzer outputs.

---

# Part XI — Visual And UX Contract

EFT2 should look modern without becoming sterile or visually noisy.

Priorities:

- ball readability at speed
- carrier readability
- team readability
- goal readability
- hazard readability
- charge/knockdown state readability
- clear score/timer
- readable action text
- useful minimap
- veteran spatial awareness

## Team Identity

Red Rhinos and Blue Bulls are part of the sport's identity.

Preserve loud team color, large readable logos, and arcade sports clarity.

## HUD Target

The modern HUD should be cleaner than old GMod clutter while preserving information density:

- bottom/central score strip or equivalent strong score anchor
- red logo + red score
- compact timer
- blue score + blue logo
- health/charge/possession state readable
- minimap top-left or similarly stable
- action text readable but not obstructive
- nameplates readable in scrums
- carrier indicator obvious
- goal/score celebration clear

## Visual Tone

Preserve:

- arcade sports tone
- saturated team color
- physical comedy
- chunky readable bodies
- exaggerated collision readability
- map-specific themes
- in-world team branding
- clear hazards
- clear goals

Avoid:

- cinematic darkness that hides play
- realistic physics that erase outcome signatures
- tiny player silhouettes
- muted team identity
- generic arena blandness
- over-polished animation that masks mechanical timing

---

# Part XII — Scenario Library

These scenarios are validation stories. They should eventually become tests, replay fixtures, telemetry checks, or manual QA scripts.

## S-001 Goal-Line Stand

Setup: carrier is within about 50 HU equivalent of goal; defender is charging.

Expected: defender can deny score if hit occurs before goal condition resolves.

Anti-outcome: carrier scores despite clearly being hit first.

Validates: C-004, C-001, M-130, M-190.

## S-002 Panic Short Pass

Setup: carrier is swarmed by two defenders.

Expected: early/low-power throw creates nearby contested loose ball.

Anti-outcome: perfect safe pass or ball sticks to carrier.

Validates: C-002, C-006, M-170.

## S-003 Long Throw Recovery

Setup: carrier throws high arc downfield into space.

Expected: ball is recoverable and creates a new contest.

Anti-outcome: ball rolls forever, clips through world, or becomes uncatchable noise.

Validates: C-008, C-007.

## S-004 Jump-Flung Fumble

Setup: carrier jumps and is hit or loses control during vertical motion.

Expected: verticality produces readable chaos and contestable ball movement.

Anti-outcome: carrier drops straight down with no spatial consequence.

Validates: C-006, C-009.

## S-005 Swarm Collapse

Setup: loose ball, four or more players converge.

Expected: collisions, knockdowns, possible ball pop-out, new local crisis.

Anti-outcome: players ghost through each other without consequence.

Validates: C-001, C-003.

## S-006 Midfield Collection

Setup: ball lobbed across middle, defender cuts lane.

Expected: defender collects by running through the ball path; no special catch key.

Anti-outcome: interception requires formal animation/confirmation.

Validates: C-005, C-003.

## S-007 Escort Clearing

Setup: carrier follows teammate; defender approaches.

Expected: teammate tackles/blocks defender, carrier continues.

Anti-outcome: teammate body presence irrelevant.

Validates: C-003, C-001.

## S-008 Intentional Hazard Reset

Setup: carrier pinned near own goal.

Expected: carrier/team can intentionally dump ball into void/hazard/reset to force neutral contest where map supports it.

Anti-outcome: reset creates long downtime or grants unfair possession.

Validates: C-002, C-007, P-090.

## S-009 Head-On Speed Duel

Setup: player A hits at slightly higher speed than player B.

Expected: higher-speed player wins or close-speed special case resolves readably.

Anti-outcome: random winner.

Validates: C-006, C-009, P-060.

## S-010 Last-Second Touchdown Stop

Setup: carrier airborne or running into goal; defender hits just before scoring.

Expected: denial if hit precedes goal condition.

Anti-outcome: goal becomes unstoppable once carrier is near.

Validates: C-004, C-001.

## S-011 Loose Ball Bounce

Setup: ball bounces after fumble/throw.

Expected: readable reflection and contestable landing.

Anti-outcome: ball stops dead or flies erratically.

Validates: C-006, C-005.

## S-012 Respawn Rejoin

Setup: player dies while ball is contested.

Expected: respawn path allows return to active or immediately subsequent contest.

Anti-outcome: player spends >10s irrelevant.

Validates: C-010, C-003.

## S-013 Choke Corridor Fight

Setup: ball in narrow hallway.

Expected: body-blocking/clearing matters.

Anti-outcome: corridor defense is impossible or purely random.

Validates: C-001, C-002.

## S-014 Score Counter-Attack

Setup: team A scores; ball resets.

Expected: team B can rush reset point, create immediate new contest.

Anti-outcome: goal creates long dead play.

Validates: C-007, C-010.

## S-015 Tackle Chain

Setup: A tackles B, ball pops to C, D tackles C.

Expected: rapid chain of possession/knockdown events.

Anti-outcome: cooldowns prevent the second valid tackle.

Validates: C-002, C-006.

## S-016 Goal-Line Intercept

Setup: loose ball rolling/flying into goal.

Expected: player can cut it off and save.

Anti-outcome: ball becomes non-interactable near scoring.

Validates: C-004, C-003.

## S-017 Mid-Air Catch / Pickup

Setup: ball thrown high; player jumps into path.

Expected: player can collect through contact and carry momentum/state according to rules.

Anti-outcome: only grounded scripted catches work.

Validates: C-005, C-009.

## S-018 Powerup Route

Setup: carrier chooses longer route through speedball/powerup.

Expected: powerup changes tempo enough to matter, but route remains contestable.

Anti-outcome: powerup is cosmetic or guaranteed victory.

Validates: map identity, P-080, P-090.

## S-019 Carrier Juke

Setup: defender charges straight; carrier cuts/uses geometry.

Expected: defender overcommits and loses relevance; carrier gains short window.

Anti-outcome: defender magnetically tracks perfectly.

Validates: C-009, C-005.

## S-020 Bot Positioning

Setup: ball loose to one side.

Expected: bot moves toward future contest/pickup, not stale current location.

Anti-outcome: bot chases behind play.

Validates: C-005, C-003.

## S-021 Slam Dunk Hoop Decision

Setup: Slam Dunk scoring complex with throw and movement-assisted dunk routes.

Expected: analyzer/implementation distinguishes scoring methods and preserves route pressure.

Anti-outcome: all triggers reduced to one generic goal box.

Validates: map intelligence, M-190.

## S-022 Bloodbowl Flat Swarm

Setup: Bloodbowl reset/loose ball near center.

Expected: open-field convergence, tackles, and breakouts occur quickly.

Anti-outcome: players spread out or carry safely across field.

Validates: Bloodbowl vertical slice.

---

# Part XIII — Diagnostics

## Correct Behavior

Commonly observed in healthy EFT-like play:

- possession changes frequently
- carriers rarely feel safe
- scrums form around next possession events
- goals happen after brief participation imbalance
- players switch roles repeatedly
- throw attempts are often interrupted
- one removed participant can alter the next seconds
- players converge on loose balls without incentives
- head-ons reward smoother approach and timing
- players re-enter conflict after recovery
- maps visibly change the sport

## Drift Conditions

If these happen consistently, EFT2 is diverging:

- possession chains last too long
- goals result from planned advance instead of sudden break
- players spread out and stop collapsing toward interaction
- carriers feel safe
- throws succeed without protection
- head-ons feel random or symmetrical
- scrums are rare or optional
- players hesitate after turnovers
- removing one player has little effect
- bots outperform humans mechanically
- hazards feel like random punishment instead of map pressure
- powerups do not change route decisions
- wall contact feels harmless
- veteran players must relearn basic timing

## Known Bad States

| Bad state | Symptom | Likely issue |
|---|---|---|
| Walking simulator | too much travel, low interaction | map too large, movement too slow, respawn too far |
| Safe carrier | carrier survives easily | carrier speed too high, tackles too weak, defenders too slow |
| Velcro carrier | ball sticks after tackle | possession/fumble order wrong |
| Ghost tackle | hit looks valid but fails | prediction/server authority/collision mismatch |
| Infinite dribble | player avoids carry penalty | ball physics/pickup rules wrong |
| Statue defense | standing still blocks perfectly | collision/friction too strong |
| Random head-ons | no readable winner | velocity sampling/resolution wrong |
| Dead throw | passing never worth trying | windup/pressure overtuned |
| Throwball | passing always better than running | throw too safe or carrier too weak |
| No scrum | players never converge | spawn/reset/map scale/bot logic wrong |
| Dead reset | reset creates downtime | reset location/timing wrong |
| Perfect bots | bots dominate humans | mechanical skill too high |
| Cosmetic powerups | powerups ignored | map identity lost |
| Generic maps | all maps play alike | geometry/entity grammar lost |

## Evaluation Checklist For Changes

Before accepting a gameplay change, ask:

1. Does it alter vulnerability duration after losing speed?
2. Does it make carrying safer or more dangerous?
3. Does it make throwing more or less attractive relative to running?
4. Does it change scrum formation or resolution?
5. Does it reward positioning or reaction time?
6. Does it flatten match emotional rhythm?
7. Would a veteran make the same decision in the same situation?
8. Does it preserve reflex continuity?
9. Does it preserve map identity?
10. Does it preserve low-skill relevance without deleting high-skill mastery?

---

# Part XIV — Traceability

## ID Families

| Prefix | Meaning |
|---|---|
| `C-###` | Core concept / why |
| `P-###` | Invariant / non-negotiable rule |
| `M-###` | Mechanic / simulation model |
| `E-###` | Telemetry event |
| `S-###` | Scenario |
| `A-###` | Archetype |
| `D-###` | Diagnostic |
| `MAP-###` | Map dossier / map rule |
| `Q-###` | Open question / decision fork |

## Commenting Standard

Future gameplay code should use traceability comments when practical:

```csharp
// EFT2 LINKS:
// Mechanics: M-130, M-150
// Principles: P-020, P-060
// Concepts: C-001, C-011
// Scenarios: S-001, S-009, S-015
```

## Initial Trace Index

| ID | Name | Source reference / future EFT2 area |
|---|---|---|
| `P-050` | Movement constraints | Lua movement, future PlayerController |
| `M-110` | Charge logic | Lua player movement, future PlayerController |
| `M-120` | Knockdown | Lua states/status, future PlayerState |
| `M-130` | Tackle/head-on | Lua player collision, future TackleResolver |
| `M-150` | Possession | Lua ball, future Ball |
| `M-170` | Throw | Lua throw state, future ThrowComponent |
| `M-180` | Hazards/resets | Lua triggers, future Hazard/BallResetTrigger |
| `M-190` | Scoring | `trigger_goal`, future GoalTrigger |
| `B-000` | Bots | Lua bot AI, future BotController |
| `MAP-001` | Map entity grammar | VMF + FGD + Map Analyzer |

---

# Part XV — Controls And Runtime Settings

These are inherited controls/settings and may be redesigned for EFT2 input/UI while preserving behavior.

## Player Controls

| Input | Neutral | Airborne | Carrier |
|---|---|---|---|
| WASD | move | air influence | move slower |
| Jump | jump | no extra unless allowed | jump |
| Crouch | crouch if supported | often disabled/limited | crouch if supported |
| Primary | punch/attack | punch if allowed | defensive punch if allowed |
| Secondary | dive when charging | dive/none depending state | hold/release throw |
| Look behind | 180/look-back | look-back | look-back |

## Server/Game Settings To Preserve Conceptually

| Setting | Target |
|---|---|
| match length | 15 minutes |
| score limit | 10 |
| warmup | 30 seconds |
| overtime | design fork |
| pity trigger | 4 goal deficit |
| bots enabled | yes for population scaffolding |
| bot skill | tunable |
| competitive rules | eventually supported |
| map vote | eventually supported |
| telemetry | should be on for dev/testing |

---

# Part XVI — Competitive / Community Context

EFT historically functioned as a persistent server place, not a matchmaking product. Players joined mid-game, left mid-game, memed, trolled, played seriously, formed rivalries, and learned by doing.

The sport survived because:

- the core loop is robust to bad play
- low-skill players still matter
- skill is visible enough to create reputation
- head-ons and scoring create public signals
- the server/community context gave matches continuity
- maps created distinct nights and arguments

EFT2 should not sterilize the goofy/wacky culture, but should not design for griefing either. The system should survive social chaos naturally.

## Competitive Team Sizes

Historical evidence supports both 5v5 and later 4v4 tournament play. EFT2 should support:

- 3v3 low population
- 4v4 competitive
- 5v5 classic competitive sweet spot
- 10v10 public chaos
- larger chaos only after performance and readability support it

## Player Archetypes

| Archetype | Behavior | Strength | Weakness |
|---|---|---|---|
| Ballhog Runner | rarely passes, runs personally | scoring pressure | predictable vs swarm |
| Safe Passer | throws under pressure | retention/chaos | low solo threat |
| Defensive Interceptor | reads lanes/fumbles | turnover generation | may miss direct pressure |
| Space Clearer | tackles non-carriers for teammate | enables goals | low personal score |
| Reset Strategist | dumps ball to hazard/reset | prevents concession | can waste attack |
| Opportunistic Scavenger | hovers near scrum edge | fumble goals | low direct control |
| Predictive Defender | moves to future carrier path | high-skill stops | can look passive |
| Panic Thrower | throws too early | chaos creation | turnovers |

No archetype should become a fixed class.

---

# Part XVII — Phase Milestones

## Phase 0 — Contract And Evidence Index

- Keep this README current.
- Keep AGENTS.md current.
- Organize source domains.
- Preserve Lua source under `Lua`.
- Preserve VMFs under `Maps`.
- Preserve FGD under `Maps/Shared/eft.fgd`.
- Curate gameplay evidence under `Assets`.
- Build `Tools/Indexer/` to make the repo LLM-readable working memory.
- Record conflicts between original contract, Lua, maps, evidence, and intended remake behavior.

## Phase 1 — Map Intelligence Pipeline

- Build `Tools/Map Analyzer/`.
- Organize canonical map domains.
- Preserve read-only VMFs.
- Parse VMF/FGD.
- Generate map analysis.
- Generate Virtual Perception artifacts.
- Validate first on Slam Dunk.
- Validate second on Bloodbowl.

Success condition: agents can reason about how a map likely plays from evidence, not memory.

## Phase 2 — s&box Project Scaffold

- Create minimal buildable EFT2 project under `Game/`.
- Establish `.sbproj`, source structure, startup scene, and assembly globals.
- Boot in editor/game.
- Add no fake gameplay placeholders that obscure missing work.

## Phase 3 — Core Loop Prototype

One arena, not full Bloodbowl yet.

Required:

- red/blue teams
- spawn points
- one ball
- basic movement at EFT speeds
- automatic pickup
- carrier speed penalty
- tackle
- knockdown
- fumble
- goal trigger
- ball reset
- minimal HUD
- telemetry hooks

Success condition: the prototype produces scrums, turnovers, and short possessions before it looks beautiful.

## Phase 4 — Bloodbowl Gameplay Vertical Slice

Bloodbowl remains the first full gameplay vertical slice.

Required:

- preserve open-field swarm behavior
- preserve spawns/ball origin
- preserve pits/hazards/resets
- preserve hybrid scoring
- modernize stadium presentation
- tune movement/collision until rhythm resembles live play
- validate with telemetry and human feel

## Phase 5 — Full Core Mechanic Parity

- dive tackle
- dive ball pickup
- throw windup/release
- head-on resolution
- power struggle design fork
- punch/cross-counter
- knockdown recovery/immunity layers
- wall stop/wall slam
- jump pads
- hazards/water/void resets
- score types
- speedball/waterball/iceball/etc.

## Phase 6 — Map Grammar And Conversion

- define VMF entity to s&box component mapping
- convert canonical maps in priority order
- preserve scoring identity
- preserve powerup identity
- validate by entity counts, geometry, route behavior, and live play

## Phase 7 — Bots And Match Population

- port bots after human core loop feels right
- bots create pressure, not perfect play
- consume map intelligence where useful
- validate against possession/tackle/goal/throw metrics

## Phase 8 — Remaster Presentation

- modern models/materials/lighting
- animation/VFX/sound
- HUD/minimap/action text
- spectator tools
- team identity
- map dressing
- social/arcade texture

## Phase 9 — Telemetry, Replay, And Tuning

- match recorder
- replay/event viewer
- metrics dashboards
- map dossiers
- bot tuning
- drift reports
- validation fixtures

---

# Part XVIII — Golden Targets

## Map Intelligence Golden Target: Slam Dunk

Slam Dunk is first for map analysis because it exercises:

- verticality
- platforms
- jump/push triggers
- speedball/powerup logic
- hoop/ring scoring
- multiple scoring modes
- shot vs dunk routes
- high-energy clutch scoring

Expected analyzer outputs:

- raw entities
- FGD semantics
- trigger volumes
- goal complexes
- spawn clusters
- jump/push regions
- powerup regions
- vertical layers
- route reads
- line-of-sight/occlusion if possible
- gameplay profile
- uncertainty report

## Gameplay Golden Target: Bloodbowl

Bloodbowl is first for full gameplay feel because it is:

- open
- readable
- speed-dominant
- flat swarm reference
- hybrid scoring
- hazard/reset visible
- supported by live POV evidence
- visually iconic as stadium/field/goal experience

Bloodbowl should feel fast, open, intercept-heavy, and scrum-driven.

---

# Part XIX — Open Questions

Keep this section current. Resolved questions should become contract decisions above.

## Q-001 Bloodbowl Version

Should EFT2 Bloodbowl follow v5, v6, 2017 POV feel, or a deliberate hybrid?

## Q-002 Throw Movement

Should EFT2 use frozen throw windup, moving-start throw windup, or a source-confirmed hybrid?

## Q-003 Power Struggle

Should EFT2 support:

- original mash-style
- Publish 429 seeded-key style
- Source 2-native velocity/timing-only style
- server-configurable modes

## Q-004 Items

Which legacy items should return, and when?

## Q-005 Powerups

Which ball powerups launch in the first public slice?

## Q-006 Scale Conversion

Should EFT2 preserve Hammer Units literally or define calibrated Source 2 equivalents by feel?

## Q-007 Bots At Launch

Should bots ship with the first public slice or after human multiplayer is stable?

## Q-008 Map Order

After Bloodbowl and Slam Dunk, what is the conversion order?

Candidates:

- Tunnel
- Baseball Dash
- Temple Sacrifice
- Skystep
- Soccer
- Space Jump

## Q-009 Competitive Format

Should official EFT2 competitive baseline be 4v4, 5v5, or support both equally?

## Q-010 Presentation Tone

How far should the remake push modern style before it risks losing arcade/goofy readability?

---

# Appendix A — Machine-Readable Constants

```yaml
meta:
  source: "EFT2 README"
  target_platform: "sbox_source2"
  inheritance: "gmod_source1_eft"
  rule: "preserve behavioral outcomes over literal numeric values when engine conversion diverges"

units:
  hu: "Hammer Units / inherited Source spatial unit"
  hu_s: "Hammer Units per second equivalent"
  hu_s2: "Hammer Units per second squared equivalent"

physics_targets:
  gravity: 600
  friction: 6.0
  accelerate: 5.0
  airaccelerate: 10.0
  conversion_policy: "calibrate in Source 2 until player-perceived timing matches"

speeds:
  base_max: 350.0
  carrier_normal: 262.5
  carrier_pity: 315.0
  strafe_only: 160.0
  charge_threshold: 300.0
  curve_boost: "small player-generated speed advantage; preserve readability"

movement:
  zero_to_charge_seconds: 1.0
  zero_to_max_seconds: 1.5
  jump_vertical_speed: 200
  jump_cooldown: 0.3
  grounded_required_for_tackle: true
  airborne_can_tackle: false

tackle:
  threshold_speed: 300.0
  knockdown_duration: 2.75
  force_multiplier: 1.65
  attacker_recoil: -0.03
  post_hit_immunity: 0.45
  per_attacker_immunity: 2.0
  global_immunity_model: "review inherited clock behavior"
  damage:
    charge: 5
    punch: 25

dive:
  trigger: "secondary attack while charging, grounded, not carrying"
  extra_speed: 100
  upward_boost: 320
  turn_rate_deg_s: 90
  ball_pickup_allowed: true
  landing_penalty_after_ball_intercept: 0.5
  always_risky: true

punch:
  state_duration: 0.5
  cross_counter_window: 0.2
  force: 360

throwing:
  full_windup: 1.0
  impulse: 1100
  arc_type: "gravity"
  movement_model: "open question: frozen vs moving-start"
  speedball_windup_multiplier: 0.5

ball:
  mass: 25
  damping_linear: 0.01
  damping_angular: 0.25
  bounce_reduction: 0.75
  fumble_velocity:
    horizontal_multiplier: 1.75
    vertical_pop: 128
  pickup:
    automatic: true
    requires_key: false
    knocked_down_can_pickup: false
  immunity:
    general_after_drop: 1.0
    team_pass_ball: 0.2
    team_pass_carry_item: 0.25

collision:
  opponents: "solid with tackle logic"
  teammates: "pass-through or non-griefing"
  knocked_down: "solid/obstacle if source behavior supports it"
  modes_to_preserve_conceptually:
    - normal
    - passthrough
    - avoid

scoring:
  goal_value: 1
  scoretype_none: 0
  scoretype_touch: 1
  scoretype_throw: 2
  scoretype_both: 3
  post_goal_slowmo_seconds: 2.5
  post_goal_timescale: 0.1

match:
  goal_cap: 10
  match_time_seconds: 900
  warmup_seconds: 30
  respawn_delay_seconds: 5.0
  ball_reset_timer_seconds: 20
  pity:
    trigger_deficit: 4
    carrier_speed_multiplier: 0.90

telemetry_events:
  - TackleResolve
  - PossessionTransfer
  - BallLoose
  - BallReset
  - PlayerKnockdown
  - PlayerRecovered
  - GoalScored
  - ThrowAttempt
  - DiveAttempt
  - HeadOn
  - HazardContact
  - PowerupActivated

excluded_by_default:
  - fixed_formations
  - downs
  - stoppages_after_tackle
  - safe_pickup_key
  - tackle_aim_assist
  - throw_path_guide
  - perfect_bots
```

---

# Appendix B — Map Grammar Tags

Map Analyzer and future map dossiers should use tags like:

```yaml
map_grammar_tags:
  scoring:
    - touch_only
    - throw_only
    - hybrid_scoring
    - precision_throw
    - ring_goal
    - endzone_goal
  terrain:
    - flat_swarm
    - open_field_intercept
    - vertical_platform
    - sky_fall_reset
    - corridor_chokepoint
    - ramp_route
    - obstacle_juke
  movement:
    - jump_pad_route
    - push_trigger_route
    - bunnyhop_sensitive
    - low_gravity
    - water_route
  pressure:
    - high_scoring
    - low_scoring_precision
    - clutch_shot_timing
    - goal_line_stand
    - scrum_heavy
    - reset_heavy
  powerups:
    - speedball_tempo
    - waterball_route
    - iceball_chaos
    - scoreball_variant
  hazards:
    - hazard_regulated
    - pit_reset
    - lava_reset
    - spike_death
    - void_pressure
  obstruction:
    - rotating_obstruction_shot
    - ring_blocker
    - pillar_juke
```

---

# Appendix C — Agent Reminder

Before changing gameplay code, map conversion, or analyzer interpretation:

1. Identify the relevant C/P/M/S IDs.
2. Inspect source evidence.
3. Decide whether the change preserves behavior, not just code similarity.
4. Record uncertainty.
5. Prefer a small validated slice over broad fake architecture.

The definitive test:

> EFT2 is not defined by copied code. EFT2 is defined by a repeating human experience: constant pressure, instant retargeting, unstable possession, sudden resolution, and map-authored chaos. If the remake recreates those experiences, it is EFT. If it recreates mechanics but not the experience, it is not.
