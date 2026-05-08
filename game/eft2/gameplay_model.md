# EFT2 Gameplay Model

This note maps the first s&box core-loop prototype to the inherited GMod Lua behavior. It is a working implementation bridge, not a replacement for the root `README.md`.

## Source Model

| Domain | Lua source | Inherited behavior | Prototype mapping |
|---|---|---|---|
| Teams | `lua/gamemode/shared.lua` | `TEAM_RED` is Red Rhinos. `TEAM_BLUE` is Blue Bulls. | `TeamId.red_rhinos`, `TeamId.blue_bulls`; display names stay official. |
| Base movement | `lua/gamemode/player_class/class_default.lua`, `lua/gamemode/shared.lua` | EFT class speed is 350. Forward movement accelerates toward current max speed; strafe-only movement is capped lower. | `PlayerMovement.BaseMaxSpeed = 350`; provisional wish-velocity acceleration preserves charge economy but is not exact Source 1 movement. |
| Charge | `lua/gamemode/sh_globals.lua`, `lua/gamemode/obj_player.lua`, `lua/gamemode/states/movement.lua` | Charge threshold is 300. A player can charge only while in movement state, grounded, non-crouching, non-carrier, low water, and moving forward. | `PlayerMovement.IsCharging` requires non-carrier, grounded, and flat speed >= 300. Forward-key, crouch, and water gates are deferred. |
| Jump | `lua/gamemode/player_class/class_default.lua` | EFT jump power is 278. | `PlayerMovement.JumpVerticalSpeed = 278`. |
| Carrier slowdown | `lua/entities/entities/prop_ball/shared.lua` | The ball applies a 0.75 max-speed multiplier to carriers, or 0.9 during pity. | `PlayerMovement.CarrierSpeed = 262.5`; pity is deferred. |
| Auto pickup | `lua/entities/entities/prop_ball/init.lua`, `lua/gamemode/states/knockeddown.lua` | Ball pickup is contact-driven. Knocked-down players cannot pick up. | `Ball.TryAutomaticPickup` uses proximity/contact-style pickup and `PlayerMovement.CanPickup`. |
| Fumble | `lua/entities/entities/prop_ball/init.lua` | Dropping/fumbling clears carrier, blocks the previous carrier for 1 second, and launches the ball with carrier velocity * 1.75 plus z 128. | `Ball.FumbleFrom` matches multiplier/pop and blocks only the previous carrier. |
| Tackle | `lua/gamemode/obj_player.lua`, `lua/gamemode/states/movement.lua` | `ChargeHit` launches target using attacker speed * 1.65, applies short charge immunity, may knock down, and applies attacker recoil velocity * -0.03. Carriers do not charge-hit. | `GameSystem.ResolveTackles` is host-side, excludes carriers through `IsCharging`, launches target, forces carrier fumble, and applies attacker recoil. |
| Knockdown | `lua/gamemode/obj_player.lua`, `lua/gamemode/states/knockeddown.lua`, `lua/gamemode/states/knockdownrecover.lua` | Default knockdown duration is 2.75. Knocked-down movement is stopped and pickup is disabled. Recovery has a separate get-up texture. | `PlayerMovement.KnockDown` uses 2.75 seconds and disables movement/pickup; ragdoll, wallslam, and separate recovery state are deferred. |
| Scoring | `lua/entities/entities/trigger_goal.lua` | A goal trigger belongs to a defended side; the opposite team scores when their carrier touches it. | `GoalTrigger.ScoringTeam` stores the team awarded by the trigger. The graybox places Red Rhinos scoring at the Blue Bulls end and Blue Bulls scoring at the Red Rhinos end. |
| Ball reset | `lua/entities/entities/prop_ball/init.lua`, `lua/entities/entities/trigger_ballreset.lua` | Ball can return home from reset triggers, water, sky, or timeout cases. | `BallResetTrigger` and out-of-arena checks reset the active ball to center. Timeout/water/sky behavior is deferred. |

## Current Core Loop

The implemented loop is:

```text
spawn -> move -> touch ball -> become carrier -> slow down -> get tackled -> fumble -> loose ball -> pickup -> score/reset
```

The host owns the canonical ball state. Player ownership does not transfer the ball. Tackle, fumble, scoring, reset, and telemetry emission resolve through `GameSystem` and `Ball`.

## Deferred Legacy Detail

These are intentionally not complete in the first proving ground:

- exact `GM:DefaultMove` acceleration, turn penalty, strafe cap, and air/swim movement multipliers
- crouch, waterlevel, forward-key, and state-integer gates for charge
- head-on speed comparison, close-speed contest, and future `P-060` skill expression
- dive, punch, throw windup, throw scoring, power struggle, and wallslam
- ragdoll visuals and the separate knockdown recovery state/vector
- charge and knockdown immunity tables per attacker/target
- pity speed multiplier
- sky/water/timeout ball return logic
- bot variance and bot-only charge behavior

The next tuning prompt should work through movement, collision, tackle feel, and ball retarget timing before adding more systems.
