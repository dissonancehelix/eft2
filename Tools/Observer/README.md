# Tools/Observer

**Status: skeleton only — implementation deferred.**

## Purpose

Observer converts raw media (videos, screenshots, keyframes, play captures) into LLM-readable observation artifacts that other tools can consume. Its output makes match footage and replay captures understandable to agents — not just as file paths, but as structured gameplay events.

## What Observer will do (when implemented)

- Accept video files (`.mp4`, `.mkv`, `.avi`, `.mov`) and screenshot directories as input
- Extract keyframes at configurable intervals or on event triggers
- Emit structured observation JSON per the schema in `observation_schema.md`
- Write outputs to the calling map domain's `Virtual Perception/` folder
- Remain read-only with respect to source media — never mutate input files

## What Observer will not do

- Observer does not run computer vision or ML inference directly — it prepares artifacts for external vision passes
- Observer does not edit VMFs, Lua, or any other source reference
- Observer does not scaffold game code

## Output schema

See `observation_schema.md`.

## CLI (placeholder)

```
python "Tools/Observer/observe_video.py" --help
```

## Integration with the pipeline

```
Assets/Video/           →  observe_video.py  →  Maps/<Map>/Virtual Perception/
Assets/Screenshots/     →  observe_video.py  →  Maps/<Map>/Virtual Perception/
```

Indexer reads `Virtual Perception/` outputs and surfaces them in `OBSERVATION_INDEX.json` and `MULTIMODAL_CONTEXT.md`.

## Dependency note

`ffmpeg.exe` will be required for frame extraction. The binary lives at `Tools/ffmpeg.exe` (gitignored). Observer will fail gracefully with a clear error when `ffmpeg.exe` is absent rather than crashing silently.

## Build order context

Observer is step 1 of the infrastructure rails. Contract Validator, Scenario Harness, and Telemetry follow. Simulation is deferred until those rails exist. `Game/eft2/` scaffold is present but EFT mechanics should not be added until the infrastructure rails are stable.
