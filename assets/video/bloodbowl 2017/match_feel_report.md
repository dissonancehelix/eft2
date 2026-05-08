# EFT2 Match Feel Evidence: Video + Replay Logs

Analysis artifact. Keep out of Git unless promoted into the root contract.

## Video Index

- Source: `Assets\Video\Bloodbowl Gameplay 2017`
- Duration: 20:58, 1280x720, 30 fps.
- Extracted frame index: `video-analysis\bloodbowl_pov\frames_10s`, one image every 10 seconds.
- Contact sheets: `video-analysis\bloodbowl_pov\contact_sheets\contact_01.jpg` through `contact_04.jpg`.

## Replay Log Corpus

| Log | Map | Min | Events | Tackles/min | Poss gains/min | Throws/min | Goals | Resets | Median round sec | Median possession sec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `match_20260224_034541.json` | unknown | 16.3 | 1077 | 42.0 | 14.3 | 3.0 | 5 | 1 | 179.99 |  |
| `match_20260224_040501.json` | unknown | 18.0 | 1381 | 40.8 | 16.2 | 1.2 | 14 | 8 | 57.93 |  |
| `match_20260224_042240.json` | unknown | 16.8 | 1167 | 42.6 | 15.1 | 3.6 | 7 | 1 | 102.64 |  |
| `match_20260224_043940.json` | unknown | 16.2 | 1376 | 57.1 | 19.4 | 1.6 | 4 | 0 | 112.69 |  |
| `match_20260224_051049.json` | unknown | 16.2 | 1023 | 40.8 | 13.4 | 2.9 | 4 | 1 | 83.97 |  |
| `match_20260302_033228.json` | eft_slamdunk_v6 | 15.8 | 1454 | 51.9 | 16.2 | 1.2 | 2 | 1 | 274.81 | 1.14 |
| `match_20260302_035118.json` | eft_soccer_b4 | 17.9 | 1537 | 43.9 | 14.2 | 0.7 | 13 | 1 | 47.74 | 0.91 |
| `match_20260302_040931.json` | eft_bloodbowl_v5 | 17.3 | 1784 | 49.4 | 18.2 | 0.7 | 10 | 5 | 46.76 | 0.88 |
| `match_20260302_042605.json` | eft_tunnel_v2 | 16.0 | 1542 | 57.5 | 15.3 | 0.9 | 3 | 3 | 374.41 | 1.38 |
| `match_20260302_044320.json` | eft_baseballdash_v3 | 16.6 | 1516 | 45.8 | 16.9 | 2.4 | 6 | 2 | 64.94 | 0.95 |
| `match_20260302_050140.json` | eft_slamdunk_v6 | 16.2 | 1478 | 48.8 | 16.6 | 1.5 | 4 | 1 | 231.73 | 1.03 |
| `match_20260302_051843.json` | eft_legoland_v2 | 16.4 | 1256 | 46.7 | 9.7 | 0.5 | 5 | 4 | 128.22 | 1.58 |

## Cross-Match Tempo Bands

- `tackle_success`: median 46.2/min, range 40.8-57.5/min.
- `possession_gain`: median 15.8/min, range 9.7-19.4/min.
- `possession_loss`: median 10.8/min, range 0.0-16.9/min.
- `throw`: median 1.4/min, range 0.5-3.6/min.
- `throw_received`: median 0.5/min, range 0.0-2.1/min.
- `head_on`: median 0.8/min, range 0.0-1.6/min.
- `goal`: median 0.3/min, range 0.1-0.8/min.
- `ball_reset`: median 0.1/min, range 0.0-0.4/min.
- `respawn`: median 6.4/min, range 4.0-15.5/min.

## Bloodbowl Log Anchor

- Log: `match_20260302_040931.json` (`eft_bloodbowl_v5`), 17.3 minutes.
- Tackle density: 855 tackles, 49.4/min, about one every 1.2 seconds.
- Possession churn: 315 gains and 293 losses; median measured possession window 0.88 seconds, 75th percentile 2.09 seconds.
- Throws are rare: 12 throws, 0.7/min; median throw force 1075.00, median power 0.95.
- Head-ons are decisive but less common than normal tackles: 28 events, median speed margin 5.65 units/sec.
- Scoring cadence: 10 goals over 17.3 min; median scoring round length 46.76 sec.
- Resets: 5 ball resets, enough to matter but not a constant interruption.
- Typical event-context player count: median 9.00, 75th percentile 10.00; logs usually see clustered near-ball crises.

## Initial Port-Feel Claims To Test

- A normal Bloodbowl-like match should produce tackle events at very high frequency; if early EFT2 prototypes are below roughly 40 tackles/min with bots, pressure is probably too sparse or collision resolution is too gentle.
- Possession should often be measured in seconds, not possessions-as-drives. Median measured possession in the Bloodbowl log is only a few seconds.
- Throws should remain commitment plays. The logs show throws as low-frequency compared to tackles and possession gains.
- Score events do not require long football drives; rounds can end quickly when pressure fails to reform.
- Ball resets exist, but should not dominate the rhythm.
- Head-on outcomes need fine speed/margin sensitivity: logged margins can be single-digit units/sec.

## Video Watch Notes So Far

- Camera is close third-person chase, usually behind and slightly above the player, low enough that players and impacts feel large against the stadium scale.
- HUD state is dense but peripheral: top-left minimap, top scoreboards, bottom HP/charge/round/time, right-side event text.
- Play alternates between midfield spread and sudden compact pileups; the port should preserve both the readable chase lanes and the messy collision knots.
- Knockdown downtime is visually important: bodies on the field are part of spatial readability and comedy, not just a hidden status flag.
- Bloodbowl pits/holes are not decoration. They repeatedly shape routes, resets, avoidance, and goal-line danger.
- Touchdown overlays are loud, full-width, and deliberately disruptive; score celebration temporarily dominates the screen.
- The match contains menu/scoreboard interruptions and grayscale/death/spectator-looking states; the remaster needs clean versions of those transitions, not just the active-running camera.
