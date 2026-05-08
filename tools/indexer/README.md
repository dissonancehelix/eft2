# Tools/Indexer

The Indexer is the first project-wide LLM working-memory tool for EFT2. It reads
the repository and emits structured JSON/Markdown summaries that future agents
(Claude, Codex, and later tools) can use as a fast on-ramp.

> The Indexer is not the game builder. It is the repo memory builder.

EFT2 is not just a code port. Its infrastructure exists to make agents understand
EFT's rules, feel, maps, evidence, and failure modes deeply enough to implement
and modernize the game without erasing its identity.

The named project structure is `tools/` (infrastructure) and `game/` (future
playable s&box project). Do not introduce "Engine" or "Runtime" as umbrella names
for the infrastructure layer — "Engine" conflicts with s&box/Source 2 terminology,
and "Runtime" implies only shipped game code rather than the full analysis,
observation, validation, and simulation pipeline.

## Purpose

Convert the repository into LLM-readable working memory:

```text
Source material
  -> project-owned tools
  -> JSON/Markdown artifacts
  -> better agent understanding
  -> better code and validation
```

## What it reads

- `README.md`, `AGENTS.md`, `PLAN.md` (if present), `maps/README.md`, `Tools/*/README.md`
- `lua/` — first-pass keyword classifier (mechanic tags, function names, hooks)
- `maps/` — canonical map domains, observed analysis output counts, custom EFT FGDs
- `sbox/` — shallow priority scan (`*.sbproj`, components, networking, triggers, navigation, scenes, player controllers, UI/HUD)
- `tools/` — tool inventory and missing recommended tools
- `assets/` — videos, screenshots, observation artifacts; flags raw media as pending Observer
- `garrysmod-master/` — temporary GMod source reference; emits `GMOD_REFERENCE_INDEX.json` + `SOURCE1_FGD_INDEX.json`
- `FFmpeg-Builds-master/` — temporary upstream FFmpeg cross-build reference; emits `FFMPEG_REFERENCE_INDEX.json` and a deletion recommendation when only build infrastructure is present

## What it writes

All outputs go under `tools/indexer/Output/`:

- `PROJECT_INDEX.md` — one-screen repo snapshot (includes current readiness section)
- `CURRENT_STATE.md` — factual checklist
- `SOURCE_MAP.json` — domain → policy/mutation rule
- `CONTRACT_INDEX.json` — headings, contract IDs, TODO markers in contract docs
- `LUA_INDEX.json` — Lua file classification by mechanic
- `MAPS_INDEX.json` — canonical map domains, FGD discovery, provenance
- `SBOX_INDEX.json` — shallow s&box reference index
- `TOOLS_INDEX.json` — tool inventory + missing tools
- `OBSERVATION_INDEX.json` + `MULTIMODAL_CONTEXT.md` — observation material
- `GMOD_REFERENCE_INDEX.json` — only if `garrysmod-master/` is present
- `SOURCE1_FGD_INDEX.json` — only if FGDs are present under that tree
- `FFMPEG_REFERENCE_INDEX.json` — only if `FFmpeg-Builds-master/` is present

Every JSON output starts with the standard envelope:

```json
{
  "generated_by": "Tools/Indexer",
  "schema_version": 1,
  "generated_at": "...",
  "repo_root": "...",
  "warnings": []
}
```

Every Markdown output starts with a generated-by banner.

## Safety policy

The Indexer is read-only **except** for `tools/indexer/` and `tools/indexer/Output/`.

It must not edit:

- `README.md`, `AGENTS.md`, `PLAN.md`
- `.gitignore` (reports status only; does not edit)
- `game/`, `maps/`, `lua/`, `sbox/`, `assets/`, other `Tools/*`
- VMFs, Lua, FGDs, raw media

If a file cannot be read, a warning is recorded and the run continues. Missing
optional folders are reported as `pending`/`missing`, not failures.

## Commands

```powershell
python "tools/indexer/index_project.py" --help
python "tools/indexer/index_project.py"
python "tools/indexer/index_project.py" --root . --output "tools/indexer/Output" --verbose
```

Exit code is non-zero only for catastrophic failures (e.g. invalid `--root`).

## Usage pattern

```text
Run tools/indexer/index_project.py.
Read tools/indexer/Output/CURRENT_STATE.md and PROJECT_INDEX.md.
Wait for the user's prompt. The Indexer reports state — it does not prescribe tasks.
```

## Relationship to other tools

The Indexer is the foundation of the long-term tool loop:

```text
README / AGENTS
  -> Indexer            (this tool)
  -> Map Analyzer       (already exists; will consume SOURCE1_FGD_INDEX.json)
  -> Observer           (videos / screenshots -> structured observations)
  -> Telemetry          (event schemas)
  -> Scenario Harness   (must-preserve EFT situations)
  -> Simulation         (controlled gameplay/map sim, learning loops)
  -> Contract Validator (drift detection)
  -> better prompts, better code, better map understanding
```

The Indexer does not implement any of those. It only inventories the repo and
reports what is present, what is absent, and what is blocked.

## Implementation notes

- Python standard library only.
- One short docstring per module describes the output it produces.
- File reads are size-capped (default 1 MB); binary extensions are size-only.
- Writes are confined to the resolved output directory by `OutputWriter`.
- Outputs are deterministic where practical (sorted file lists, stable keys).
