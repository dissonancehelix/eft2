# Tools/Observer

**Status: image evidence pass implemented; video/media event extraction remains deferred.**

## Purpose

Observer converts raw media (videos, screenshots, keyframes, play captures) into LLM-readable observation artifacts that other tools can consume. Its output makes match footage and replay captures understandable to agents — not just as file paths, but as structured gameplay events.

## What Observer can do now

- Analyze image folders such as `assets/image/`
- Emit a full per-image evidence index and summary
- Infer map association from filenames when possible
- Record dimensions, palette/readability signals, visual tags, confidence, and human-review flags
- Keep screenshot claims evidence-bound: visual/readability evidence only, not timing or mechanics proof
- Remain read-only with respect to source media

## Image CLI

```powershell
python "tools/observer/analyze_images.py" --help
python "tools/observer/analyze_images.py" --root . --source "assets/image"
python "tools/observer/analyze_images.py" --root . --source "assets/image" --map "Slam Dunk"
```

Outputs:

```text
tools/observer/Output/IMAGE_EVIDENCE_INDEX.json
tools/observer/Output/IMAGE_EVIDENCE_SUMMARY.md
```

## What Observer will do later

- Accept video files (`.mp4`, `.mkv`, `.avi`, `.mov`) and screenshot directories as input
- Extract keyframes at configurable intervals or on event triggers
- Emit structured observation JSON per the schema in `observation_schema.md`
- Write outputs to the calling map domain's `virtual perception/` folder
- Remain read-only with respect to source media — never mutate input files

## What Observer will not do

- Observer does not run heavy computer vision or ML inference directly — the current image pass records reproducible metadata and conservative pixel/readability signals
- Observer does not edit VMFs, Lua, or any other source reference
- Observer does not scaffold game code

## Output schema

See `observation_schema.md`.

## Video CLI (placeholder)

```
python "tools/observer/observe_video.py" --help
```

## Integration with the pipeline

```
assets/image/           →  analyze_images.py →  tools/observer/Output/
assets/Video/           →  observe_video.py  →  maps/<Map>/virtual perception/
assets/Screenshots/     →  observe_video.py  →  maps/<Map>/virtual perception/
```

Indexer reads `virtual perception/` outputs and surfaces them in `OBSERVATION_INDEX.json` and `MULTIMODAL_CONTEXT.md`.

## Dependency note

`Pillow` is used for image metadata and palette signals. `ffmpeg.exe` will be required later for video frame extraction. Observer should fail gracefully with a clear error when an optional media dependency is absent rather than crashing silently.

## Build order context

Observer is an infrastructure rail for turning media into durable evidence. Contract Validator, Scenario Harness, Telemetry, and Simulation consume the evidence contracts later. `game/eft2/` scaffold is present but EFT mechanics should not be added by Observer work.
