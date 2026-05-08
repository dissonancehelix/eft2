# Bloodbowl POV Full Watch Notes

Evidence notes from `Assets\Video\Bloodbowl Gameplay 2017`.

These notes are based on:

- Full-match 5-second contact sheets in `video-analysis\bloodbowl_pov\contact_sheets_5s`.
- Full-resolution keyframes in `video-analysis\bloodbowl_pov\keyframes`.
- Replay log tempo from `Lua\game logs`, especially `match_20260302_040931.json` for Bloodbowl.

This is not a polished design document yet. It is watch evidence for building EFT2.

## Global Read

The video confirms the README contract: Bloodbowl is not a drive-based football mode. It is an arena pressure sport where the ball repeatedly passes through crowded collision space, players are constantly knocked down or forced to re-approach, and goals happen when the pressure cloud fails to reform for a few seconds.

The match is full of very short playable cycles:

`spawn/recover -> chase ball -> collide -> drop/gain -> scrum or breakaway -> goal/reset/death -> repeat`

The replay logs quantify the same feel. In the Bloodbowl log, tackles happen about once every 1.2 seconds and measured possession median is under one second. The video visually matches that: the player is usually either chasing, recovering, joining a pile, or reacting to a sudden break.

## Camera And Readability

- Camera is close third-person chase, behind and slightly above the player.
- Player body is large in frame, often occupying 15-25% of screen height.
- Camera is low enough that stadium walls, goalposts, pits, and nearby players feel huge.
- The camera frequently loses perfect tactical information. That is part of the feel: the player is in the mess, not watching a clean RTS board.
- The minimap gives tactical recovery from that chaos. It is essential because the close camera alone cannot show all threats.
- FOV/scale makes collisions legible at body scale, not just as distant dots.

Port implication: EFT2 should not start with an elegant far tactical camera. Preserve the embodied chase view first, then improve readability with HUD/minimap/spectator tools.

## HUD And Presentation

- Top-left minimap shows the field, red/blue sides, pits/holes, and clustered player dots.
- Stadium scoreboards and top floating score text both reinforce score state.
- Scores are shown as progress toward 7, for example `1/7`, `4/7`, `6/7`.
- Bottom HUD shows HP/charge style colored bars, round number, time, and team text.
- Top-right event feed is constantly meaningful: picked up ball, dropped ball, scored, joined, etc.
- Touchdowns use huge centered horizontal banners with team color and text. They deliberately interrupt the screen.
- Scoreboard overlay appears often and is translucent enough that play continues behind it.
- Chat and Steam overlay/menu interruptions are visible in the recording; these are not game design targets, but they show that live EFT was socially noisy and server-like.

Port implication: HUD should be loud where scoring/possession matters and compact where it only supports awareness. A quiet modern HUD would lose some of the sport's personality.

## Map Feel

- Bloodbowl is a stadium bowl, but the important play area is an obstacle arena.
- Pits/holes are major route shapers. Players skirt them, get knocked near them, fall around them, and reset around them.
- Goalposts are visual anchors, not just decoration.
- End zones act like danger basins. When play enters the colored end zone, the whole screen starts to feel like a crisis.
- The midfield logo area becomes a repeated scrum stage because it is open, readable, and equidistant from both goals.
- The stands/city skyline make the map feel big even though the sport happens in a compact collision band.

Port implication: Bloodbowl's first remake cannot be only a flat field. The pits and end-zone geometry are core gameplay grammar.

## Timeline Notes

| Video Time | Watch Notes |
|---:|---|
| 00:00-00:10 | Recording starts mid-match with a touchdown/score state already active. Immediate grayscale/death or spectator-looking state follows. |
| 00:15-00:30 | Play restarts into instant pressure. Blue cluster reforms around midfield and the ball. Multiple bodies are already down. |
| 00:35-00:45 | Blue-side goal/end-zone pressure. Touchdown banner appears; event feed keeps reporting pickup/drop/scoring. Scoring is abrupt and loud. |
| 00:50-01:20 | Reset into chase lanes. Player is usually behind the action, using minimap and distant ball marker to re-enter. |
| 01:25-01:45 | Red scores. `BLITZ BALL` appears with a countdown after the touchdown, showing ball-state/round modifier presentation. |
| 01:50-02:20 | Scoreboard/death/recovery state, then return to field. Midfield pileups resume quickly. |
| 02:25-03:05 | Blue pushes into red end. A touchdown at about 02:55 shows players colliding and burning in/near the end zone. |
| 03:10-03:40 | Tall obstacle/pillar/goalpost views show the camera can be partially occluded by map geometry. This is not always clean, but it adds physicality. |
| 03:45-04:25 | Long chase through midfield into goal-line pressure. Player often sees the ball as a white-ring marker at distance rather than as a clean object. |
| 04:30-04:40 | Red touchdown, scoreboard overlay, then grayscale death/spectator state. Scoreboard shows roughly 9 Red players and 8 Blue players in this moment. |
| 04:45-05:30 | Reset and midfield spread. Several players are prone; downed bodies become obstacles/readability cues. |
| 05:35-06:15 | Ball possession changes near midfield. The player repeatedly approaches from behind as other players collide ahead. |
| 06:20-07:05 | Dense pressure near the right-side pit and end-zone lane. Explosions/impact effects punctuate scrums. |
| 07:10-07:55 | Ball marker and player nameplates are crucial at medium distance. The player alternates between sprint chase and short recovery pauses. |
| 08:00-08:45 | Open-field regroup. Several players are scattered; pressure cloud reforms toward the goal-line side. |
| 08:50-09:30 | Goal-line scramble near pit and right post. Touchdown at about 09:25-09:30. Score moves into a high-scoring mid-match state. |
| 09:35-10:20 | Scoreboard/chat interruptions, then immediate return to field. A death/acid-looking overlay appears around 09:50, likely from falling/kill volume or postprocess state. |
| 10:25-11:15 | Long contested stretch. Player tracks scrums from midfield, sometimes behind red attackers, sometimes chasing loose ball marker. |
| 11:20-11:40 | Touchdown at about 11:35. The score banner dominates while players continue moving underneath. |
| 11:45-12:25 | Wide stadium/end-zone view, then reset into midfield. The ball/pickup text and minimap carry awareness more than the 3D camera alone. |
| 12:30-13:20 | Repeated tackles and a dense midfield cluster. The player spends real time prone/recovering, not instantly returning to full agency. |
| 13:25-14:05 | Red-side push and touchdown around 13:55-14:00. Scoreboard overlay follows. |
| 14:10-15:00 | Restart around midfield; open lanes collapse into end-zone pressure. The player is repeatedly just behind the possession event. |
| 15:05-15:40 | Goal-line action and Blue touchdown around 15:30-15:35. Scoreboard/death state appears soon after. |
| 15:45-16:35 | Several overlay/menu moments, then return to play. This confirms match flow needs good pause/scoreboard/spectator handling without breaking server continuity. |
| 16:40-17:25 | Midfield-to-end-zone chase. Pits continue shaping routes; players are knocked near edges and recover into chase lines. |
| 17:30-17:55 | Blue end-zone score at about 17:50-17:55. This appears to tie or bring the match close late. |
| 18:00-18:45 | Reset, chase, and another Blue touchdown at about 18:45. Full-resolution keyframe shows score at 6/7 for both teams before/around this late stretch. |
| 18:50-19:40 | Scoreboard/death, then intense late play. The player stays close to the ball near midfield and red end-zone lanes. |
| 19:45-20:10 | Final regulation pressure. At about 20:10, `OVER TIME!` appears at 6-6. |
| 20:15-20:40 | Overtime chase near red end. Touchdown/victory sequence triggers around 20:40. |
| 20:45-20:55 | Steam overlay/chat after match. `VICTORY` and post-match social noise are visible behind overlays. |

## Mechanics Visible In The Video

### Possession

- Ball possession is visually unstable. The event feed repeatedly reports pickup/drop in quick succession.
- The ball is often better understood through the marker/name/event feed than direct geometry.
- The carrier does not create a long safe possession pocket. Teammates and opponents close immediately.

Port target: possession should feel like carrying a dangerous beacon, not owning an object.

### Tackles And Knockdowns

- Bodies on the ground are constant.
- Knockdown states are long enough to be seen and to change near-ball geometry/readability.
- Recovering players often re-enter from behind the current play, which helps produce wave-like pressure.
- The video shows plenty of non-carrier collisions too; contact is broadly meaningful, not only ball-contact.

Port target: knockdown/recover must be visible, timed, and spatial, not a tiny stun flag.

### Throws

- Throws are not visually dominant compared with collision and possession churn.
- The ball occasionally arcs or pops high, but the main match texture is tackles and recovery.
- The replay logs agree: throws are low-frequency compared with tackles.

Port target: implement throwing, but do not tune the first prototype around passing. Collision pressure is primary.

### Goals

- Goals are sudden. There is often a short crisis near an end zone, then a loud touchdown banner.
- The scoring player can be surrounded, burning, falling, or amid bodies. A goal does not require a clean heroic animation.
- Touchdowns are full-screen social events, not subtle score ticks.

Port target: score detection and celebration should tolerate messy physical states.

### Resets And Death States

- Grayscale/death/spectator-looking states happen often enough to matter.
- The player sometimes watches others from a neutral/dead viewpoint before re-entering.
- Kill volumes/pits and ball reset text are part of match grammar.

Port target: death/recovery/spectator transitions should be first-class and fast, with clear state text.

### Round Modifiers

- `BLITZ BALL` appears with a countdown around early scoring.
- The match includes ball-state variety, not only one static football.

Port target: build the core ball first, but preserve a hook for ball states/mutators.

## Numbers To Carry Into Prototype Tests

From `match_20260302_040931.json`:

- Bloodbowl logged duration: about 17.3 minutes.
- Tackle density: 855 tackles, about 49.4/minute.
- Possession gains: 315, about 18.2/minute.
- Possession losses: 293, about 16.9/minute.
- Measured possession median: 0.88 seconds.
- Throws: 12, about 0.7/minute.
- Head-ons: 28; median speed margin about 5.65 units/sec.
- Goals: 10.
- Ball resets: 5.

Prototype smell tests:

- If bots plus humans are not generating dozens of tackles per minute, the field is too empty, movement too slow, collision too forgiving, or bot pressure too timid.
- If possession commonly lasts 5-10 seconds in scrums, the carrier is too safe.
- If the best strategy becomes passing chains, throwing is too safe or too cheap.
- If score attempts feel like long clean drives, Bloodbowl pressure is not working yet.
- If pits are only hazards and not route-shaping landmarks, the map conversion is too flat.

## Things To Refine With Another Pass

- Extract 1-second strips around each touchdown to measure restart timing and overlay duration.
- Compare visible Bloodbowl geometry against `Maps/Bloodbowl/Bloodbowl.vmf` after map organization.
- Track exact camera pitch/distance against player height using several full-resolution frames.
- Identify which visual effects correspond to tackle, fire, ball reset, death, and ball-state events.
- Use logs to compute possession chains by player/team and score state, then compare to video moments.
