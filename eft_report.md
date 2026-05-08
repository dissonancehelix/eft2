# Extreme Football Throwdown, decoded for a remaster

Extreme Football Throwdown is not the ragdoll-football slapstick its trailers sold — it is a tightly-tuned, fighting-game-adjacent contact sport whose entire design philosophy lives in one watershed patch (JetBoom's 2017 "Publish 429") and whose surviving culture is a small, mechanically literate inner circle that argued for years over knockdown clocks, bhop physics, and macro-able power struggles. **The single most important finding for the remaster: several attribution and version assumptions in the user's contract appear to be wrong, and the game's "soul" is encoded in patch-note-level numbers, not the broad strokes.** What follows distinguishes what the developer actually built, what veterans actually felt, and where a Source 2 port could quietly betray the sport.

Sources are heavily skewed toward two archives — the now read-only NoxiousNet forum and Steam Workshop comments on the JetBoom gamemode page — because EFT generated almost no Reddit, no Twitch ecosystem, no tournament VOD corpus, and one (1) viable Twitch→YouTube VOD by Jugs Linterfins. Where evidence is thin or absent, this report says so explicitly.

## Lineage and naming — three things the contract likely has wrong

**The canonical upstream repo is `JetBoom/extremefootballthrowdown`, not `dissonancehelix/extremefootballthrowdown`.** The dissonancehelix URL the user supplied could not be located on the public web; the GitHub user `dissonancehelix` exists (avatar ID 11387750) but appears in JetBoom's repo only as a 2015-era bug reporter (Issues #16 and #44) who collaborates with a mapper named "Benjy." The same handle "dissonance" surfaces on the Sunrust "Extreme Football League" 2022 tournament roster as part of the winning team **𝕿𝖍𝖊 𝕹𝖚𝖙𝖘 (Joxey, dissonance, grimace, mango)** and is also the mapper credited (as "dissident93" / "dissident") for `eft_cosmic_arena`, `eft_slamdunk`, `eft_legoland`, `eft_baseballdash`, `eft_spacejam`. **Best inference: dissonancehelix is a top-tier player and active mapper who maintains a private fork — most likely the live "Reconstructed Extreme Football Throwdown" server at `66.227.195.229:27015` whose tag string is `ver:240422` (April 22, 2024). That fork is what the user's "rmx" framing almost certainly refers to, and it is not publicly indexed.** The user should treat their existing source tree as a **community fork by a tournament-winning player**, not as the original canonical codebase.

**"v4 / v5 / v6 / rmx" are map-version suffixes, not gamemode versions.** Maps named `eft_castle_warfare_v6`, `eft_slamdunk_v6`, `eft_spacejump_v6`, `eft_hexa_v5`, `eft_temple_sacrifice_v4`, and so on are individually-revisioned community maps. The gamemode itself has no v4/v5/v6 tags or releases on the upstream repo (91 commits, master branch only, no Releases page). The single watershed *gamemode* version axis the community actually argues about is **"Publish 429 — EFT 2017 update,"** posted to the NoxiousNet forum in topic 15218. Veterans split bitterly over it (see §The 2017 schism below). "rmx" as a gamemode suffix appears nowhere in indexed public text and is most likely the dissonance-helix fork's internal label.

**"Lythium" has no public connection to EFT that I could verify.** Lythium.dev is a real Garry's Mod systems developer (Pulsar Link, FPS-boost addon, EliteLupus tooling, BanEvasion) but does not appear in EFT's commits, issues, server credits, NoxiousNet roster, or YouTube. If the connection exists it is private (Discord / off-platform). The user should confirm this attribution before invoking Lythium in remaster materials.

## What JetBoom actually built — the mechanical core in his own words

JetBoom's own pitch on the 2011 Facepunch reveal thread (`t=1217955`) is the cleanest statement of design intent:

> "Momentum based movement. Turning will slow you down and it takes a small bit of time to get to full speed… The ball itself becomes powered up instead of players which means we can do stuff to both the ball and the player carrying it… Taking damage from players will turn you in to a ragdoll and throw you back. Then other players can throw your ragdoll around by hitting you on the ground. Players that are knocked down can be slammed in to and pinned to walls and ceilings. **Button mashing power struggles if two people ram head on in to each other. Whoever wins gets to do an extremely powerful hit to the other person.** Holding the ball slows you down so you can't just run it across the map yourself. **System to prevent one person being knocked down repeatedly by the same guy over and over.**"

This corroborates the user's contract on momentum, auto-attach ball, ragdoll-on-hit, head-on collision resolution, carrier penalty, and anti-stunlock — but it also reveals two pieces the contract appears to underweight: the **ball-as-anchor-and-powerup target** (powerups attach to the ball, not the player) and the **post-tackle ragdoll-knock cycle** (you can throw a downed opponent's body around with further hits). Both belong in the port.

Then **Publish 429 (NoxiousNet topic 15218)** rebuilt the entire feel:

> "Replaced power struggle system with one that can't be macro'd. Players will now get an identical list of keys to press, generated from the same random seed. Every 3 keys is part of the same bar and there are 4 bars. Press the keys in the right order as fast as possible. Whoever finishes first or has the most keys after 5 seconds will win. **Pressing the wrong key will revert the progress of the current bar so accuracy and speed is important!**"

> "Player collision system reworked. Designed to improve game flow, hit detection, and get rid of dead stops against other players. **Now have three modes: normal, pass through, and avoid.** Pass through is triggered on knock down, wall pin, dive tackling, charging, etc. Avoid is triggered when getting back up."

> "Players are further immune to knockdown if they are repeatedly hit by different players in a short time. So there's individual immunity as well as global. **Being knocked down by any source will push a clock ahead 1 second. The clock decreases over time 1:1. If the clock is ahead by 2.25 seconds, trigger 3.75s of global knockdown immunity.** Prevents body camping."

> "Players now slow down when hitting the ground by 15%. Prevents bunny hopping. Crouching is no longer possible in the air but jump height has been increased to compensate."

> "Touching the ball while dive tackling (not while already grabbing a player) will pick the ball up and return to running once you hit the ground, **making it a risky way to intercept or race for the ball. A 50% speed reduction will be incurred when hitting the ground.**"

> "Players no longer have to stop moving to begin a throw."

> "Health now regenerates much quicker. The delay before regeneration starts has been reduced from 5s to 1s and the rate has been increased from 2/s to 8/s."

> "Players now spawn according to distance from the ball spawn. Unoccupied spawns FURTHEST take priority."

> "Limited team swaps to 2 per match. Rejoining will not reset this."

**Several of these numbers should replace or refine values in the user's contract.** The ~2.75s knockdown the user lists is close to but not the same as the actual two-clock immunity system: a per-hit 1s clock (decaying 1:1), with a 2.25s cumulative threshold triggering a **3.75s global immunity window**. This is a fighting-game stagger system, not a fixed knockdown timer, and porting it as a flat duration would lose the tactical layer where defenders deliberately stagger hits *just under* the threshold to prolong stunlock while a coordinated team accidentally grants the carrier free movement by overcommitting. The dive-tackle ball pickup with **50% speed penalty on landing** is a specific risk/reward intercept tool that doesn't exist in any version-agnostic description and should be a first-class mechanic in the port. The spawn-furthest-from-ball algorithm is a documented anti-goal-camp counter that any remaster needs.

The full melee/item layer also exceeds what most surface descriptions capture. Patch notes reveal **right-click cancelability** on Melon Driver and Arcane Wand attacks ("you can also move around while attacking"), the Beatdown Stick gaining the ability to **hit the ball directly** (a goal-line-stand counter to body-blockers), and a fix to a high-ping exploit where lag compensation gave certain players abnormally long punch range. The cross-counter punch the contract describes is real, but it is one weapon in a feinting toolkit that includes Big Pole, Beatdown Stick, Melon Driver (dual-melon, three-hits-to-kill), Arcane Wand, Booze Bottle (screen-blur disorient), Smoke Bomb, Gravity Orb, Hot Potato, and a defensive Forcefield item Dr. Incognito introduced to address a perception that defense was too weak against throw-spam.

The ball powerup pantheon is also more developed than a generic "powerup" tag suggests. Maps in the workshop advertise themselves by **powerup type and timer**: Speed Ball (4s/5s/7.5s/10s variants by map), Ice Ball, Water Ball (12s/25s), Score Ball (a 1-minute-45-second hold-to-score variant on `eft_sc_oddball_arena`), Strong Arm Ball, Feather Ball, Gravity Ball, Hot Potato, and Blitz Ball. **The community's mental classification of maps is mechanical, not aesthetic — Madden's stock map description format is "Powerup type, duration, goal type, layout note,"** in that order. A remaster that treats powerups as cosmetic flair will misread the genre.

Two ConVars in the codebase encode subtle design intent that should travel forward: `eft_allowAttackWhileJumping` defaults to **0** ("Interrupts attack animation in the air") — JetBoom deliberately keeps melee a ground commitment, preserving the run-up-and-charge feel. And `eft_bonemanipulation` defaults to **1** — the engine literally inflates player skeletons to make characters "look bulkier," matching JetBoom's catchphrase **"Make sure you bulk up for the big game. I wanna see some wet cleats."** The silhouette is intentionally a chunky football-player ragdoll, not a default Source player; lose the bulking and you lose half the visual identity.

## What it actually feels like — the newcomer/veteran/nostalgia split

EFT's "feel" lives in three documentary registers, and a remaster needs to know which one it's targeting at any given moment.

**The newcomer register**, supplied by the big YouTube discovery videos, frames EFT as chaotic ragdoll slapstick. Funhaus's October 2016 description is the most-cited single line in EFT discourse: *"It's like **NFL Blitz meets American Gladiators meets Tron** meets a game that barely works and tears all of my coworkers' friendships apart."* Achievement Hunter's 2022 episode billed it as *"this bloody battle of **shoulder charges, melon launchers, and magic wands**"* with the parenthetical mantra *"It's only a game… it's only a game… we're all still friends."* Kryoz framed it as *"TACKLE PEOPLE, PUNCH PEOPLE, THROW THE BALL, RAGE AT YOUR FRIENDS AND TEAM MATES!"* This register is real and contagious — it is what made EFT briefly visible in 2016 and 2020 (the "I'm here because of callmecarson" Steam comment cohort) — but it is the **least mechanically informative** voice in the corpus. New players feel like the game is "buggy af, like i have to rub the player's body up against my enemy if i want to tackle them, my hits just dont connect" (A Robot, Aug 2021). That feeling is real: it is what happens when you don't understand the charge speed threshold, the pass-through collision state, or the punch timing window. **It is a learning curve disguised as a bug.**

**The veteran register** is patch-note-shop talk. The single sharpest piece of in-game feel description came from a NoxiousNet forum exchange about ball-carrier speed: *"it happened to me again from a ball carrier with regular walking speed that did a 180 spin and rammed me leaving question marks behind."* The "180-spin ram" — turning into and immediately charging through a defender from a near-walk — is a documented tech that produced a recognizable visual signature ("question marks behind") and triggered a balance debate where one veteran proposed *"maintain a maximum speed not above the double of the regular running speed."* The veteran vocabulary is dense: *power struggle, dive-tackle pickup, spawn bounce, ball-camp, body-camp, dog pile, big-pole block, bhop sky, spike-pit (real-Bloodbowl) vs gas-pit (rebuild)*. A 2017-era forum exchange specifically describes Tunnel as *"slim enough to be blocked by a single person with a big pole or wand. Now imagine a team of 4-5 guys doing the same. I personally don't mind it, since it's a unique way of playing EFT, but it's a common complaint."* That is the actual texture of an EFT goal-line stand — corridor geometry weaponized by item-equipped defenders, countered by Beatdown-Stick ball-knocks rather than tackles. **Scrums** as the contract uses the term map onto two distinct phenomena in veteran talk: pre-2017 "dog piles" (multi-player knockdowns producing extended stunlock) and post-2017 "clusterfucks" (a mapper's own term for `eft_neontempest_v4`'s deliberately narrow corridors).

**The nostalgia register**, the public face of EFT in 2024–2025, is pure RIP: *"Real Ogs remember this"* (Derik), *"this was the game of all time"* (SSix), *"Greatest gamemode to hit Gmod 10/10"* (Pepsy), *"god i wish i had friends to play this type of stuff with"* (sam aaron), *"this should be its own standalone source game"* (neofoid). Inside that register sits the single most pointed veteran complaint about the dev's own work: **SokerBit12 (Jan 7, 2024): "bring back the old power struggle with it, the pace of the mode was much faster and more fun, please."** That is a direct demand to revert Publish 429's anti-macro typing-test power struggle and restore the original mash-button-fast system. **A remaster has to make a choice here that the user's contract does not currently address.**

## The 2017 schism a remaster has to resolve

JetBoom's Publish 429 was an explicit **anti-cheat and anti-bug rewrite** that veterans split on. The dev's own framing: *"I really want to change the power struggle system to something not macroable, pixel detectable, or ping dependent. So far the best idea I've had is a typing test."* The fix worked technically: keys are now generated from the same random seed for both contestants, four bars of three keys, five-second window, wrong-key reverts current bar. The fix may have failed culturally: SokerBit12's complaint and the Workshop's refrain that the post-2017 game is slower/less fun suggest a portion of the veteran base prefers the **rhythm** of macro-mashing over the **fairness** of seeded-key sequences.

Adjacent debates in the same patch:
- **Bhop on Sky Metal.** The 2017 patch added a 15% landing slowdown and disabled mid-air crouch *to suppress bhop*. A NoxiousNet thread acknowledges the community was always *"split on if that's good or bad."* Some maps were genuinely designed around bhop chains skipping sections.
- **Dog-pile knockouts.** Pre-patch, multiple simultaneous hits could knock a player out for an entire round. Post-patch's faster regen (8/s, 1s delay) and the per-hit/global immunity clocks reduce this to a stagger.
- **The "RTP elite" backlash.** A senior community member wrote: *"There has been a flood of really bad suggestions lately… Ideas from the **RTP 'elite'** who, honestly, have no idea about basic game design or hold their hands over their eyes when provided with the fact that most people don't want a hardcore fast movement spellspam (final destination) type of gamemode."* This is the casual-vs-tryhard schism in plain text — a vocal minority pushing for fast item-spam, the design lead pushing back for accessibility.

For a port: **the head-on collision resolution mechanism is not a single answered question.** A faithful remaster should let server admins choose between (a) original mash-style power struggle (fast, macroable), (b) Publish 429 seeded-key typing test (fair, rhythmic but slower), or (c) a third option that uses Source 2 capabilities. Hard-coding either is a betrayal of one half of the community.

## Map identity, and why it's mechanical not thematic

Veterans classify maps by what mechanics they exercise, not by aesthetic. The Madden-authored "Map List" thread (NoxiousNet topic 14411) is the canonical tier discourse:

The map most associated with EFT is **Bloodbowl** by Madden/dissident — built on a decompiled Emirates Stadium skybox, hybrid scoring (run-in endzones plus field-goal triggers moved just outside the endzone in the v3/Bloodbowl-2 rebuild). Original versions had **spike pits filled with blood decals** flanking the field; the rebuild replaced these with toxic gas/sewage pits, which produced one of the most documented aesthetic complaints in the corpus: *"In my opinion I really liked the spike-pits before the weird gas/sewage pits. It is called bloodbowl so why not bring the spike-pits filled with blood (decals)?"* and *"Why are there still pits of shit in a football stadium."* The mapper's rebuttal: *"So, version 1? I would have done that, but nobody seemed to have an issue with the toxic pits until the BSP was finished."* For a remaster, **spike-and-blood is the canonically iconic Bloodbowl identity; gas-pits are the rebuild's compromise.** The community would notice. (I could not verify v4/v5/v6/rmx Bloodbowl specifics — only v3 and the "Bloodbowl 2" rebuild are documented in indexed text.)

**Slam Dunk** (`eft_slamdunk`, dissident93) is throw-only basketball ring goals, descended from a lerp prototype called `eft_spacejam`. Workshop description is just "Basketball inspired map," but it is consistently treated as a beloved core map ("Sweet memories 😢"); no thread frames it as a gimmick. **Skystep** is the throw-only sky paradigm — Madden's Lake Parima notes describe Skystep's identity as long-distance-throws plus jump-pad lateral traversal: *"Mix of Sky Step and Space Jump, except has run in goals. Large pathways for long distance throws. Jump pads to take you side to side."* The fact that Lake Parima had to specify "except has run in goals" tells you Skystep is the throw-only reference point — the community accepted throw-only sky maps as legitimate, not gimmicky. **Space Jump** is the sky-map sibling, repeatedly re-added to community packs by request. **Hexa** uses 7.5-second speedball rings near ball spawn. **Lake Parima** uses 12-second water ball on the sides plus a 5-second speedball lower-level — and the community openly worried about powerup-as-OP: *"you'll need to be careful that getting the water-ball power-up isn't an assured victory."*

**Tunnel** is the goal-line-stand archetype, polarizing because the corridor is single-defender-blockable. **Sky Metal** is the bhop-controversy map. **Turbines** lives or dies by a single map-specific tech: *"Map is entirely based around the spawn bounce shot, which again, has the community split if they like that or not."* **Soccer** (Axl, `eft_soccer_b4`) uses regulation-size pitch with hybrid scoring — and a player tutorial reveals the community treats **throw-through-soccer-goal as a skill flex even when run-in is allowed**: *"some people like to just throw the ball to the other team's goal and try to throw it in their goal to win the round, including me. This is hard to do though."*

The maps the community actively hated and got pulled from rotation:
- **Albino**: *"undoubtedly the least liked map on EFT, poor layout, FPS, and the snow surface texture makes turning very difficult. **It's so bad people intentionally vote for it to clear the server.**"* (the troll-vote precedent)
- **Unreality**: *"low gravity, exploitable rings, and difficult goals… **Even the mapper wants it removed.**"*
- **Omaha**: *"spawnpoints don't match, exploitable hill where people ballcamp, and only 25% is actually played on."*
- **Aether and Neon Tempest**: pulled for performance.
- **Mini Putt**: conflicted ("a lot of good EFT memories have happened here, despite the many problems and issues").

For maps the user listed — **Castle Warfare, Chamber, Big Metal, Temple Sacrifice, Skyline, Minecraft, Cosmic Arena, Countdown, Legoland, Coconut Club, Handegg** — the community generated almost no public sentiment text in indexed sources. They are background-rotation maps. Cosmic Arena has the most articulated identity: *"plays like a mix of Bloodbowl and Miniput, with the theme of something similar to Space Jump,"* with a **left-right-traveling 2-point throw ring** that requires a stopped, full-power throw. That mechanical specificity ("worth 2 points… you'd need to stop right at the goal line and make a full powered throw") is exactly the kind of map-specific design lever a port needs to preserve.

## What the community calls things — vocabulary the contract should adopt

| Term | Meaning |
|---|---|
| Power struggle | The contested-tackle minigame in head-on collision; pre-2017 mash-style, post-2017 seeded typing test |
| 180-spin ram | Walking-speed carrier rotates and immediately charges into a defender; produces "question marks" stun animation |
| Spawn bounce | Map-specific throw exploit on Turbines |
| Ballcamp / body-camp / dog pile | Defensive abuse patterns; dog-pile specifically meant pre-2017 multi-player knockout stunlock |
| Big-pole block | Defender(s) using Big Pole / Arcane Wand to body-block a corridor (Tunnel's signature pattern) |
| Speed Ball / Ice Ball / Water Ball / Score Ball / Hot Potato / Blitz Ball / Strong Arm / Feather / Gravity Ball | The powerup pantheon, attached to the ball not the player |
| Beatdown Stick / Big Pole / Melon Driver / Arcane Wand / Booze Bottle | The melee/item suite — left-click swing, right-click cancel on Melon Driver and Arcane Wand |
| Knockdown immunity | Two-clock anti-stunlock system (1s per hit, decays 1:1, 2.25s cumulative threshold triggers 3.75s global immunity) |
| Ring goal vs endzone vs score-ball | Three goal-types; maps mix-and-match |
| Snailed | Punishment status: *"JetBoom has permanently snailed this wrongdoer"* |
| Red Rhinos vs Blue Bulls | Official team identities |
| "Wet cleats" / "bulk up" | JetBoom catchphrase / patch-note voice |
| RTP elite | Sneer-term for the casual-vs-tryhard schism's tryhard pole |
| OG / Real Ogs | Self-identification for pre-2018 NoxiousNet veterans |
| "It's only a game" | Funhaus/AH meme that absorbed into mainstream EFT awareness |

Two ambient details worth preserving in the port's audio/HUD layer: **sprinting triggers a "Over here" voice taunt** ("Why can't I just sprint without that," asks Apple in the Workshop comments — a newcomer not understanding that the voice line is part of the texture, a social signaling layer), and **shift-pressing without sprinting signals for the ball with a temporary HUD triangle on the friendly carrier** (Publish 429 added: "Pressing shift to signal for the ball will no longer stop your movement and will add a temporary triangle on the HUD of a friendly ball carrier"). Coordinated teams used this; new players didn't even know it existed.

## Comparisons — what the community actually invokes

The user's contract draws Rocket League, rugby broken play, hockey turnover, and Quake/Source movement as analogies. **None of these analogies appears in the public EFT corpus I could reach.** The community's actual reference points, in rough frequency order:

- **Bloodbowl (the tabletop)** — the most-cited reference, embedded in the flagship map's name. dissident93 explicitly described `eft_cosmic_arena` as *"plays like a mix of Bloodbowl and Miniput."*
- **NFL Blitz** — Funhaus's primary external comparison
- **American Gladiators** — Funhaus's arena-spectacle reference
- **Tron** — Funhaus's neon-aesthetic reference
- **Soccer / regulation American football** — the parent genre (the gamemode .txt manifest's own description is just "American football game if there were no rules")
- **Basketball / Slam Dunk** — for the throw-only ring genre
- **Mini-golf / MiniPutt** — for novelty maps
- **Chivalry: Medieval Warfare's Arena map** — an explicit map-design source for `eft_arena_x1` and `eft_gauntlet`
- **TF2 ctf_2fort** — a base layout for `eft_sc_forts_v2`
- **Quidditch** — yes, there's a Quidditch-themed EFT map requiring custom broom props

Notable absences: **rugby is never invoked** — the community frames EFT as American football, with one flame-war exception ("stupid american football, football started in united kingdom thats the original not this shitty crap" — CORP_RP, 2024). **Rocket League, Quake movement, hockey, Speedball, Mutant League Football, Pyre, Killer Instinct** — none surface in indexed sources. The contract's analogies may still be useful for orienting the port team, but the user should know they are external impositions, not native vocabulary.

## What a port could quietly betray

Synthesizing across everything above, here are the specific port mistakes that would cost EFT its identity, ordered by how much community blowback they would generate:

The first betrayal is **collapsing the two-clock knockdown immunity into a flat duration**. The user's contract lists ~2.75s knockdown; the actual system is per-hit-1s + 2.25s-threshold + 3.75s-global-window. That layered system is what creates the staggered-tackle tactical layer veterans intuitively exploit. A flat timer makes the game feel duller without being obviously different.

The second is **shipping only one head-on collision resolution model**. Publish 429 split the community. A port that hard-codes either mash-style or seeded-key power struggle will alienate one half. Both should be available as server options; ideally a third Source-2-native option is offered.

The third is **flattening powerups into cosmetic flair**. Maps in EFT advertise themselves by powerup type and timer because the entire map identity is built around routing through powerup triggers as the carrier's only counter to the carrier-can't-rush penalty. The Speed/Ice/Water/Score/Strong Arm/Feather/Blitz/Gravity/Hot Potato pantheon, with map-specific durations, is core sport, not novelty.

The fourth is **dropping the right-click cancel and feint layer on Melon Driver and Arcane Wand**, which is what gives the melee suite its fighting-game depth. Without it, items become spam.

The fifth is **losing the dive-tackle ball-pickup mechanic with 50% landing speed penalty.** This is the contested-fumble counter and the fastest piece of EFT-specific tech. It is in the patch notes and basically nowhere in the surface descriptions.

The sixth is **dropping the bone-manipulation bulking** (`eft_bonemanipulation 1`). The bulky football-player silhouette is JetBoom's catchphrase made literal. Default-skinny ragdolls would feel wrong.

The seventh is **simplifying the three-state collision system** (normal / pass-through / avoid, triggered by knockdown/wall-pin/dive-tackle/charge/getting-up). This is what makes tackles weave through teammate ragdolls cleanly and what newcomers misread as "my hits aren't connecting." Replace it with a single collision model and the game stops feeling fluid.

The eighth is **breaking the corridor-block goal-line stand pattern** without replacing it. Tunnel's identity comes from a single defender body-blocking with Big Pole/Arcane Wand, countered by team coordination and Beatdown-Stick-can-hit-the-ball. If the port's geometry kit doesn't permit this kind of weaponized narrowness, an entire class of EFT defense disappears.

The ninth is **getting Bloodbowl's hazard aesthetic wrong**. Spike-pits-filled-with-blood is the canonically iconic version; gas-pits is the rebuild compromise that veterans complained about. The remaster has a chance to revert.

The tenth is **assuming v4/v5/v6/rmx are gamemode versions to choose between.** They are map iterations; the gamemode's actual version axis is pre- vs post-Publish-429.

Finally — and least urgent but real — **understanding that EFT is a niche game with a small competitive scene (4 teams of 4 in the documented Sunrust league) and a much larger nostalgic audience.** The remaster's audience is mostly people who want to feel what they felt in 2014–2017, plus a smaller cadre who actually played at depth. Both audiences need to be addressed; they want different things. The nostalgic crowd will be moved by JetBoom's catchphrases, the bulky silhouettes, the spike-pits, and the rhythm of mash-mode power struggle. The competitive cadre will care about the immunity clocks, the cancel windows, the dive-pickup penalty, and the throw-while-moving rule. Neither group is the same as the Funhaus audience that drives initial visibility.

## What the contract may be subtly missing

Cross-referenced against the user's own description: the user's contract appears to be working from a combination of personal play memory and a community fork (the dissonance/dissident "Reconstructed" build), not the JetBoom upstream. The "fumbles as transition generator" framing in the user's contract is reasonable but **community sources more often describe fumbles as either ball-reset-triggers (20-second timeout, ball returns to spawn) or as dive-tackle interception opportunities** — the transition-generator framing is more abstract than how players actually talk about them. The "carrier slower than defenders" framing understates the real penalty: in original namu.wiki / forum descriptions, **the carrier outright cannot use rush** ("Players holding balls or items cannot use rush"), which is a categorical disability rather than a graduated speed differential. The contract's "punches with cross-counter window" misses that the broader item layer (Melon Driver, Arcane Wand, Beatdown Stick, Big Pole) all have analogous timing windows, with the Melon Driver and Arcane Wand specifically having right-click cancels and the Beatdown Stick gaining the ability to hit the ball directly. And the contract doesn't appear to address the **two-key collision-state machine** (pass-through / avoid / normal) at all, despite this being the underlying reason the game feels fluid in skilled hands and unresponsive in newcomer hands.

## The bottom line

EFT's soul is a fighting-game stagger system wearing American football pads, hosted by a developer with a dry sense of humor on a community server that is now mostly empty, played at depth by perhaps 20 people in any given era and remembered fondly by tens of thousands. **What veterans valued: the 180-spin ram, the dive-tackle ball intercept, the right-click feint, the corridor body-block, the bhop sky-route on Sky Metal, the macro-rhythm of pre-2017 power struggle. What casual players valued: the ragdoll cathartic chaos, the friendship-destroying scrums, the JetBoom voice. What the public remembers: NFL Blitz × American Gladiators × Tron, "It's only a game," and the dim sense that this should have been a real standalone Source title.** A remaster that preserves the layered numerical mechanics, gives admins switches over the 2017 schism, restores the spike-pit Bloodbowl, keeps the bulky silhouette, and resists the urge to compare itself to Rocket League will land with both audiences. A remaster that papers over those layers with broad "you tackle people" framing will please neither.

The most useful single action the user can take next is to confirm the lineage attribution (Is dissonancehelix a fork of JetBoom's repo? Is "rmx" the Reconstructed EFT server's `ver:240422` build?) and to track down the dissonance fork's actual code, which is where the modern competitive meta lives and which is invisible from the public web.