# EFT2 s&box Prototype Notes

This project folder contains the buildable s&box prototype for the EFT2 core loop. `gameplay_model.md` maps the first C# implementation back to the old Lua behavior so tuning can stay anchored to inherited EFT feel.

`Assets/scenes/eft2_core_loop.scene` is the first graybox proving ground. It is not a Bloodbowl or Slam Dunk conversion. It exists to test the minimum interaction loop from the root `README.md`: spawn, move, automatic pickup, carrier slowdown, tackle, knockdown, fumble, loose-ball retarget, pickup, score, and reset.

Movement is provisional. `PlayerMovement` drives s&box `PlayerController.WishVelocity` using the inherited README targets (`M-110`, `M-150`, `P-050`) rather than copying Source 1 movement exactly. The current pass preserves charge threshold and carrier speed penalty as playable constraints; later tuning should adjust acceleration, turning, collision response, and tackle feel against human play.

Networking is also a first pass. The ball is host-owned and tackle/fumble/score/reset decisions are host-side, matching the repository authority contract. Multiplayer editor validation should still verify ownership, prediction, and event timing before this is treated as production authority.

Telemetry is intentionally lightweight. `TelemetrySink` emits structured debug lines for the first core events without writing persistent match logs yet.
