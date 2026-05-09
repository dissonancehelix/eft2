# EFT2 Core Loop Manual Test

Use `Assets/scenes/eft2_core_loop.scene` from the `game/eft2/` s&box project.

## One Player

1. Start the scene and confirm a Red Rhinos player spawns in the graybox arena.
2. Move into the loose center ball; it should pick up automatically with no key press.
3. Confirm the HUD shows the carrier and local player state.
4. Run toward the Blue Bulls end goal; carrier speed should feel slower than non-carrier movement.
5. Enter the Red Rhinos scoring trigger at the Blue Bulls end.
6. Confirm Red Rhinos score increments, `GoalScored` appears, and the ball resets to center.
7. Fall or push the ball below the arena if possible; confirm reset/respawn behavior and `BallReset`.

## Two Players

1. Connect a second human player and confirm teams alternate between Red Rhinos and Blue Bulls.
2. Have one player pick up the ball by contact.
3. Have the opponent build charge and collide with the carrier.
4. Confirm `TackleResolve`, `BallLoose`, and `PlayerKnockdown` appear in the HUD/log.
5. Confirm the tackled carrier cannot immediately pick the ball back up while knocked down.
6. Confirm another eligible player can pick up the loose ball.
7. Wait for recovery and confirm `PlayerRecovered` appears.
8. Carry into the enemy goal and confirm score, reset, and telemetry.

## Expected Debug Events

- `PossessionTransfer`
- `BallLoose`
- `BallReset`
- `PlayerKnockdown`
- `PlayerRecovered`
- `GoalScored`
- `TackleResolve`

## Provisional Checks

- Movement is a playable approximation of inherited EFT movement, not exact Source 1 `GM:DefaultMove`.
- Multiplayer authority is intended to be host-side, but real two-client editor testing is still required.
- Head-on skill, dive, punch, power struggle, throws, items, bots, and real map conversion are intentionally absent.
