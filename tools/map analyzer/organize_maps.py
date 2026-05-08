from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

from exporters import utc_now, write_md

CANONICAL = {
    "eft_bloodbowl": "Bloodbowl",
    "eft_slamdunk": "Slam Dunk",
    "eft_temple_sacrifice": "Temple Sacrifice",
    "eft_spacejump": "Space Jump",
    "eft_skystep": "Skystep",
    "eft_baseballdash": "Baseball Dash",
    "eft_tunnel": "Tunnel",
    "eft_turbines": "Turbines",
    "eft_handegg": "Handegg",
    "eft_soccer": "Soccer",
    "eft_skyline": "Skyline",
    "eft_sky_metal": "Sky Metal",
    "eft_miniputt": "Mini Putt",
    "eft_minecraft": "Minecraft",
    "eft_legoland": "Legoland",
    "eft_lake_parima": "Lake Parima",
    "eft_countdown": "Countdown",
    "eft_cosmic_arena": "Cosmic Arena",
    "eft_chamber": "Chamber",
    "eft_castle_warfare": "Castle Warfare",
    "eft_big_metal": "Big Metal",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Organize loose EFT VMFs into canonical map domains.")
    parser.add_argument("--maps-root", default="maps")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true", help="Allow replacing existing target VMF files. Never edits VMF contents.")
    args = parser.parse_args()
    root = Path(args.maps_root)
    root.mkdir(exist_ok=True)
    loose = sorted(path for path in root.glob("*.vmf") if path.is_file())
    manifest_path = root / "source_manifest.json"
    manifest = _load_manifest(manifest_path)
    planned = []
    for source in loose:
        canonical, suffix = infer_map(source.name)
        if canonical:
            target = root / canonical / f"{canonical}.vmf"
        else:
            target = root / "_Unsorted" / source.name
        planned.append((source, target, canonical, suffix))
    for source, target, canonical, _suffix in planned:
        print(f"{source.name} -> {target}")
        if target.exists() and not args.force:
            print(f"  WARNING: target exists; skipping without --force: {target}")
    if args.dry_run:
        print(f"Dry run complete. Planned {len(planned)} move(s).")
        return 0
    for source, target, canonical, suffix in planned:
        status = "imported"
        if target.exists() and not args.force:
            status = "skipped_conflict"
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() and args.force:
                target.unlink()
            shutil.move(str(source), str(target))
            _ensure_domain(target.parent, canonical or "_Unsorted", target.name, source.name, suffix)
        entry_name = canonical or f"_Unsorted/{source.name}"
        final_path = target if status != "skipped_conflict" else target
        manifest[entry_name] = _manifest_entry(root, final_path, canonical, source.name, suffix, status)
    _write_maps_readme(root)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def infer_map(filename: str) -> tuple[str | None, str | None]:
    stem = Path(filename).stem.lower()
    suffix = None
    suffix_match = re.search(r"_(v\d+|r\d+|b\d+|d)$", stem)
    if suffix_match:
        suffix = suffix_match.group(1)
    candidates = sorted(CANONICAL.keys(), key=len, reverse=True)
    for key in candidates:
        if stem == key or stem.startswith(key + "_") or (key == "eft_big_metal" and stem.startswith("eft_big_metal")):
            return CANONICAL[key], suffix
    return None, suffix


def _load_manifest(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _manifest_entry(root: Path, path: Path, canonical: str | None, original: str, suffix: str | None, status: str) -> dict:
    return {
        "canonical_display_name": canonical,
        "folder_name": path.parent.name,
        "canonical_vmf_path": str(path.relative_to(root.parent)).replace("\\", "/") if path.exists() else str(path).replace("\\", "/"),
        "original_filename": original,
        "original_source_suffix": suffix,
        "file_size": path.stat().st_size if path.exists() else None,
        "sha256": _sha256(path),
        "import_timestamp": utc_now(),
        "import_status": status,
        "source_status": "read_only_reference",
    }


def _ensure_domain(domain: Path, canonical: str, vmf_name: str, original: str, suffix: str | None) -> None:
    (domain / "analysis").mkdir(exist_ok=True)
    (domain / "virtual perception").mkdir(exist_ok=True)
    (domain / "simulation").mkdir(exist_ok=True)
    if canonical != "_Unsorted":
        readme = f"""# {canonical}

## Source VMF

- Current source VMF: `{vmf_name}`
- Original filename: `{original}`
- Original source suffix: `{suffix or "none detected"}`

## Read-Only Source Policy

The VMF in this map root is an original Source 1 reference. Analysis tools may read it, but agents must not edit, reformat, normalize, or regenerate it.

Derivative/remaster work belongs in generated analysis, s&box scenes, Source 2 map outputs, or other explicit derivative files.

## Analysis Status

- [ ] Raw entities extracted
- [ ] Brush and trigger volumes extracted
- [ ] EFT entities classified
- [ ] Semantic gameplay groups inferred
- [ ] Virtual Perception artifacts generated
- [ ] Human/domain-expert review completed

Generated analysis is not hand-authored truth. Uncertain gameplay interpretations require user/domain-expert review.
"""
        if canonical == "Slam Dunk":
            readme += """
## Slam Dunk Validation Expectations

These are expectations for analyzer validation, not hard-coded claims:

- Basketball themed map.
- Platforms/verticality expected.
- Speedball/powerup placement expected if present in VMF.
- Jump pad / push trigger route expected if present in VMF.
- Hoop/scoring complex interpretation expected.
- Throw scoring versus movement-assisted slam-dunk scoring expected.
- High-energy/high-scoring/clutch-shot style expected if supported by extracted data.
"""
        write_md(domain / "README.md", readme)
    write_md(domain / "simulation" / "README.md", f"""# Simulation

Simulation is a future optional phase for {canonical}.

It may later support gameplay prediction, telemetry comparison, route usage, powerup value, and revised map understanding. No simulation is implemented in this patch.
""")


def _write_maps_readme(root: Path) -> None:
    write_md(root / "README.md", """# EFT2 Maps

`Maps/` is organized by canonical map domains, not old Source 1 filenames.

Each map folder uses the map's display name, and the root VMF inside the folder is renamed to the same canonical name. Original filenames and Source 1 suffixes are preserved in `source_manifest.json`.

The root VMF in each map domain is a read-only original source reference. Do not edit, reformat, normalize, or regenerate it.

- `Analysis/` contains generated structured map analysis.
- `Virtual Perception/` contains generated LLM-facing spatial/gameplay perception artifacts.
- `Simulation/` is reserved for future optional simulation work and is not implemented in this patch.

Slam Dunk is the first map intelligence validation target. Bloodbowl is the second validation target and the flat/open-field swarm reference.
""")


if __name__ == "__main__":
    raise SystemExit(main())
