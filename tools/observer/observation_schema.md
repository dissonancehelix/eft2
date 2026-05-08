# Observation Schema

**Version:** 1  
**Status:** draft — subject to revision when Observer is implemented

---

## Observation envelope

Every observation artifact emitted by Observer wraps its contents in a standard envelope:

```json
{
  "generated_by": "Tools/Observer",
  "schema_version": 1,
  "generated_at": "<ISO-8601 timestamp>",
  "map_name": "<canonical map name>",
  "source_media": "<relative path to source file>",
  "original_filename": "<filename if different from source_media>",
  "warnings": [],
  "observations": [...]
}
```

---

## Observation record

Each record in `observations` describes one discrete moment or event extracted from source media:

```json
{
  "id": "<observation ID, e.g. obs_0001>",
  "type": "<keyframe | event | segment>",
  "timestamp_sec": 12.4,
  "frame_number": 372,
  "source_frame_path": "Virtual Perception/keyframes/obs_0001.jpg",
  "description": "<human/LLM-written description of what is visible>",
  "mechanic_tags": ["possession", "tackle", "knockdown"],
  "players_visible": "<count or unknown>",
  "ball_visible": true,
  "score_visible": "<score string or null>",
  "map_region": "<inferred region or null>",
  "confidence": "<high | medium | low>",
  "needs_human_review": false
}
```

### `type` values

| Value | Meaning |
|-------|---------|
| `keyframe` | Regular interval frame, no specific event detected |
| `event` | Frame selected because a mechanic event appears to be occurring |
| `segment` | A multi-frame range with sustained character (e.g. a carry or scrum) |

### `mechanic_tags` vocabulary

Drawn from EFT2 contract mechanics. Valid tags:

`possession`, `volatile_possession`, `carrier_danger`, `automatic_pickup`,  
`contested_carry`, `charge`, `tackle`, `head_on`, `knockdown`, `recovery`,  
`dive`, `throw`, `goal_score`, `ballreset`, `jumppad`, `powerup`,  
`scrum`, `reversal`, `clutch_interrupt`, `hazard`, `reset_pressure`

---

## Contact sheet

When Observer generates a contact sheet (a tiled image of keyframes for fast review), it also emits a sidecar JSON:

```json
{
  "generated_by": "Tools/Observer",
  "schema_version": 1,
  "contact_sheet_path": "Virtual Perception/contact_sheets/sheet_001.jpg",
  "frame_count": 24,
  "frames": [
    { "id": "obs_0001", "timestamp_sec": 0.5, "row": 0, "col": 0 },
    ...
  ]
}
```

---

## Image evidence index

`analyze_images.py` emits a repo-wide image evidence index for curated screenshots and map reference images:

```json
{
  "generated_by": "tools/observer",
  "schema_version": 1,
  "generated_at": "<ISO-8601 timestamp>",
  "source_root": "assets/image",
  "warnings": [],
  "summary": {},
  "observations": [
    {
      "source_image": "assets/image/slam dunk.jpg",
      "original_filename": "slam dunk.jpg",
      "image": {
        "width": 1920,
        "height": 1080,
        "dominant_rgb": [0, 0, 0],
        "luminance": {},
        "color_ratios": {}
      },
      "inferred_map": {
        "name": "Slam Dunk",
        "source": "filename",
        "confidence": 0.95,
        "reasons": []
      },
      "source_role": "map_poster_reference",
      "visual_tags": [],
      "readable_observations": [],
      "evidence_limits": [],
      "confidence": "high",
      "needs_human_review": false
    }
  ]
}
```

Image observations are visual/readability evidence. They do not prove timing, physics, scoring rates, or route preventability without logs, telemetry, map analysis, or director review.

---

## Pending items

- Frame extraction implementation (requires `Tools/ffmpeg.exe`)
- Vision pass integration (external; not in Observer scope)
- Event detection heuristics (future work)
- Segment boundary detection (future work)
