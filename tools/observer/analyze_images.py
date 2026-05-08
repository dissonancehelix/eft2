"""EFT2 Observer image evidence pass.

This tool is intentionally conservative. It catalogs every image in a source
folder and records lightweight, reproducible visual signals that help agents
use screenshots as evidence without pretending screenshots prove timing,
physics, scoring rates, or mechanic outcomes.
"""
from __future__ import annotations

import argparse
import colorsys
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image, ImageStat


GENERATOR = "tools/observer"
SCHEMA_VERSION = 1
DEFAULT_OUTPUT = Path("tools") / "observer" / "Output"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
ARCHIVE_EXTENSIONS = {".zip", ".7z", ".rar"}

KNOWN_MAPS = {
    "baseball dash": "Baseball Dash",
    "big metal": "Big Metal",
    "bloodbowl": "Bloodbowl",
    "chamber": "Chamber",
    "coconut club": "Coconut Club",
    "cosmic arena": "Cosmic Arena",
    "handegg": "Handegg",
    "lake parima": "Lake Parima",
    "legoland": "Legoland",
    "minecraft": "Minecraft",
    "oasis": "Oasis",
    "sky step": "Skystep",
    "skystep": "Skystep",
    "skyline": "Skyline",
    "slam dunk": "Slam Dunk",
    "soccer": "Soccer",
    "space jump": "Space Jump",
    "streetball": "Streetball",
    "temple sacrifice": "Temple Sacrifice",
    "tunnel": "Tunnel",
    "turbines": "Turbines",
}

DATE_SCREENSHOT_RE = re.compile(r"^\d{4}-\d{2}-\d{2}_\d+", re.IGNORECASE)
STEAM_SCREENSHOT_RE = re.compile(r"^20\d{12}_\d+$", re.IGNORECASE)


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def normalize_name(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("_", " ").replace("-", " ")).strip().lower()


def infer_map_name(path: Path) -> tuple[str | None, str, float, list[str]]:
    base = normalize_name(path.stem)
    reasons: list[str] = []

    cleaned = re.sub(r"\b\d+\b", "", base).strip()
    if cleaned in KNOWN_MAPS:
        reasons.append("filename_matches_known_map_name")
        return KNOWN_MAPS[cleaned], "filename", 0.95, reasons

    for key, display in KNOWN_MAPS.items():
        if key in base:
            reasons.append(f"filename_contains_{key.replace(' ', '_')}")
            return display, "filename", 0.85, reasons

    return None, "unknown", 0.0, ["no_map_name_in_filename"]


def infer_source_role(path: Path, inferred_map: str | None) -> tuple[str, list[str]]:
    base = path.stem
    lower = normalize_name(base)
    if path.suffix.lower() in ARCHIVE_EXTENSIONS:
        return "archive", ["archive_file_not_analyzed_as_image"]
    if lower.startswith("slam dunk") and path.suffix.lower() == ".png":
        return "slam_dunk_detail_capture", ["named_slam_dunk_png_detail_set"]
    if DATE_SCREENSHOT_RE.match(base) or STEAM_SCREENSHOT_RE.match(base):
        return "legacy_gameplay_screenshot", ["dated_or_steam_screenshot_filename"]
    if inferred_map:
        return "map_poster_reference", ["filename_identifies_named_map_reference"]
    return "unclassified_image", ["no_filename_role_pattern_matched"]


def sample_pixels(image: Image.Image) -> list[tuple[int, int, int]]:
    img = image.convert("RGB")
    img.thumbnail((180, 180))
    if hasattr(img, "get_flattened_data"):
        return list(img.get_flattened_data())
    return list(img.getdata())


def color_ratios(pixels: list[tuple[int, int, int]]) -> dict[str, float]:
    counts: Counter[str] = Counter()
    total = max(len(pixels), 1)
    for r, g, b in pixels:
        h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        if v < 0.14:
            counts["dark"] += 1
        if v > 0.78 and s < 0.22:
            counts["bright_neutral"] += 1
        if s > 0.28 and (h < 0.045 or h > 0.94):
            counts["red"] += 1
        if s > 0.25 and 0.53 <= h <= 0.72:
            counts["blue"] += 1
        if s > 0.25 and 0.22 <= h <= 0.45:
            counts["green"] += 1
        if s > 0.25 and 0.11 <= h <= 0.18:
            counts["yellow"] += 1
        if 0.07 <= h <= 0.13 and 0.16 <= s <= 0.58 and 0.35 <= v <= 0.86:
            counts["wood_tan"] += 1
    return {name: round(count / total, 4) for name, count in sorted(counts.items())}


def dominant_rgb(image: Image.Image) -> list[int]:
    img = image.convert("RGB").resize((1, 1))
    return [int(v) for v in img.getpixel((0, 0))]


def luminance_stats(image: Image.Image) -> dict[str, float]:
    gray = image.convert("L")
    stat = ImageStat.Stat(gray)
    return {
        "mean": round(float(stat.mean[0]), 2),
        "stddev": round(float(stat.stddev[0]), 2),
    }


def build_tags(role: str, map_name: str | None, ratios: dict[str, float], width: int, height: int) -> tuple[list[str], list[str], bool]:
    tags: list[str] = [role]
    observations: list[str] = []
    needs_review = False

    if role == "map_poster_reference":
        tags.extend(["map_as_poster_clarity", "map_specific_visual_identity"])
        observations.append("Filename identifies this as a named map reference image; use as visual identity evidence, not mechanics proof.")
    elif role == "legacy_gameplay_screenshot":
        tags.extend(["legacy_gameplay_readability_evidence", "screenshot_not_timing_proof"])
        observations.append("Dated gameplay screenshot; useful for visual/readability evidence but not timing, scoring-rate, or physics proof.")
        needs_review = True
    elif role == "slam_dunk_detail_capture":
        tags.extend(["legacy_gameplay_readability_evidence", "slam_dunk_validation_evidence", "screenshot_not_timing_proof"])
        observations.append("Slam Dunk detail capture; useful for HUD, nameplate, carrier, route, and map-readability review.")
        needs_review = True

    if map_name:
        tags.append("map_inferred_from_filename")
        observations.append(f"Map association inferred from filename: {map_name}.")

    if ratios.get("red", 0) >= 0.03 and ratios.get("blue", 0) >= 0.03:
        tags.append("red_blue_team_readability_signal")
        observations.append("Pixel palette contains both red and blue regions, supporting team-readability review.")
    elif ratios.get("red", 0) >= 0.05:
        tags.append("red_team_visual_signal")
    elif ratios.get("blue", 0) >= 0.05:
        tags.append("blue_team_visual_signal")

    if ratios.get("green", 0) >= 0.18:
        tags.append("field_or_turf_visual_signal")
    if ratios.get("wood_tan", 0) >= 0.16:
        tags.append("court_or_indoor_floor_signal")
    if ratios.get("yellow", 0) >= 0.025:
        tags.append("hazard_or_goal_highlight_review_signal")
        needs_review = True
    if ratios.get("dark", 0) >= 0.18:
        tags.append("dark_contrast_review_signal")
    if width >= 1600 and height >= 900 and role != "map_poster_reference":
        tags.append("wide_gameplay_capture")
        tags.append("hud_density_review_target")
        observations.append("Wide gameplay capture likely preserves HUD/nameplate context if visible; review before using as contract evidence.")

    if map_name == "Slam Dunk":
        tags.append("basketball_theme_review_target")
        tags.append("carrier_ball_glow_review_target")
    if map_name == "Bloodbowl":
        tags.append("open_field_stadium_review_target")

    return sorted(set(tags)), observations, needs_review


def analyze_image(path: Path, root: Path, source_root: Path) -> dict[str, Any]:
    map_name, map_source, map_confidence, map_reasons = infer_map_name(path)
    role, role_reasons = infer_source_role(path, map_name)
    with Image.open(path) as image:
        width, height = image.size
        pixels = sample_pixels(image)
        ratios = color_ratios(pixels)
        tags, observations, needs_review = build_tags(role, map_name, ratios, width, height)
        lum = luminance_stats(image)
        dominant = dominant_rgb(image)

    confidence = "high" if role == "map_poster_reference" else "medium"
    if role == "unclassified_image":
        confidence = "low"
        needs_review = True

    return {
        "source_image": rel(path, root),
        "original_filename": path.name,
        "file_size": path.stat().st_size,
        "image": {
            "width": width,
            "height": height,
            "modeled_aspect_ratio": round(width / max(height, 1), 4),
            "dominant_rgb": dominant,
            "luminance": lum,
            "color_ratios": ratios,
        },
        "inferred_map": {
            "name": map_name,
            "source": map_source,
            "confidence": map_confidence,
            "reasons": map_reasons,
        },
        "source_role": role,
        "role_reasons": role_reasons,
        "visual_tags": tags,
        "readable_observations": observations,
        "evidence_limits": [
            "Screenshots support visual/readability/remake direction.",
            "Screenshots do not prove timing, physics, scoring rates, or live mechanic outcomes without logs or telemetry.",
            "Pixel-derived tags are reproducible hints and should be reviewed before becoming canon.",
        ],
        "confidence": confidence,
        "needs_human_review": needs_review,
    }


def summarize(records: list[dict[str, Any]], skipped: list[dict[str, Any]]) -> dict[str, Any]:
    by_role = Counter(r["source_role"] for r in records)
    by_map = Counter((r["inferred_map"]["name"] or "unknown") for r in records)
    tag_counts = Counter(tag for r in records for tag in r["visual_tags"])
    return {
        "image_count": len(records),
        "skipped_count": len(skipped),
        "by_source_role": dict(sorted(by_role.items())),
        "by_inferred_map": dict(sorted(by_map.items())),
        "top_visual_tags": dict(tag_counts.most_common(30)),
        "needs_human_review_count": sum(1 for r in records if r["needs_human_review"]),
    }


def render_summary(envelope: dict[str, Any]) -> str:
    summary = envelope["summary"]
    lines = [
        "# EFT2 Image Evidence Summary",
        "",
        f"Generated by `{GENERATOR}`.",
        "",
        "This is a full per-image Observer pass over `assets/image`. It records image metadata, filename/map inference, and lightweight visual signals. It does not claim gameplay timing, physics, scoring rates, or mechanic truth.",
        "",
        "## Counts",
        "",
        f"- images analyzed: {summary['image_count']}",
        f"- files skipped: {summary['skipped_count']}",
        f"- records needing human review before canon use: {summary['needs_human_review_count']}",
        "",
        "## Source Roles",
        "",
    ]
    for role, count in summary["by_source_role"].items():
        lines.append(f"- `{role}`: {count}")
    lines.extend(["", "## Inferred Maps", ""])
    for name, count in summary["by_inferred_map"].items():
        lines.append(f"- `{name}`: {count}")
    lines.extend(["", "## Visual Tags", ""])
    for tag, count in summary["top_visual_tags"].items():
        lines.append(f"- `{tag}`: {count}")
    lines.extend([
        "",
        "## Evidence Limits",
        "",
        "- Use these images for visual/readability/remake direction.",
        "- Do not use screenshots alone as timing, physics, scoring-rate, or route-preventability proof.",
        "- Promote uncertain observations only after map analysis, logs, telemetry, or director review supports them.",
    ])
    return "\n".join(lines) + "\n"


def write_outputs(root: Path, output_dir: Path, envelope: dict[str, Any]) -> None:
    out = root / output_dir
    out.mkdir(parents=True, exist_ok=True)
    (out / "IMAGE_EVIDENCE_INDEX.json").write_text(json.dumps(envelope, indent=2), encoding="utf-8")
    (out / "IMAGE_EVIDENCE_SUMMARY.md").write_text(render_summary(envelope), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze EFT2 image evidence under assets/image.")
    parser.add_argument("--root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--source", default="assets/image", help="Image source folder relative to root.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT).replace("\\", "/"), help="Output folder relative to root.")
    parser.add_argument("--map", dest="map_filter", help="Optional canonical map-name filter, e.g. 'Slam Dunk'.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    source_root = (root / args.source).resolve()
    output_dir = Path(args.output)
    if not source_root.is_dir():
        raise SystemExit(f"Source folder not found: {args.source}")

    records: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    wanted_map = normalize_name(args.map_filter) if args.map_filter else None

    for path in sorted(source_root.iterdir(), key=lambda p: p.name.lower()):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        if suffix in ARCHIVE_EXTENSIONS:
            skipped.append({"source_file": rel(path, root), "reason": "archive_not_image_record"})
            continue
        if suffix not in IMAGE_EXTENSIONS:
            skipped.append({"source_file": rel(path, root), "reason": "unsupported_extension"})
            continue
        record = analyze_image(path, root, source_root)
        if wanted_map and normalize_name(record["inferred_map"]["name"] or "") != wanted_map:
            continue
        records.append(record)

    envelope = {
        "generated_by": GENERATOR,
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_root": rel(source_root, root),
        "output_root": output_dir.as_posix(),
        "map_filter": args.map_filter,
        "warnings": [
            "This is an Observer image evidence pass, not gameplay simulation.",
            "Visual tags from pixel signals are conservative hints and require review before becoming game-contract claims.",
        ],
        "summary": summarize(records, skipped),
        "skipped_files": skipped,
        "observations": records,
    }
    write_outputs(root, output_dir, envelope)
    print(f"Analyzed {len(records)} image(s); skipped {len(skipped)} file(s).")
    print(f"Wrote {output_dir.as_posix()}/IMAGE_EVIDENCE_INDEX.json")
    print(f"Wrote {output_dir.as_posix()}/IMAGE_EVIDENCE_SUMMARY.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
