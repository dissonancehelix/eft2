"""EFT2 project-wide Indexer.

Run from repo root:

    python "Tools/Indexer/index_project.py"

The Indexer is read-only except for its own Output/ folder. It does not
mutate README.md, AGENTS.md, Maps/, Lua/, SBox/, Assets/, Game/, or any
other tool. It only recommends changes via NEXT_ACTIONS.md.
"""
from __future__ import annotations

import argparse
import sys
import traceback
from pathlib import Path
from typing import Any

# Make sibling modules importable when invoked by absolute path.
HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from exporters import OutputWriter
from schemas import IndexEnvelope, GENERATOR
import index_markdown
import index_lua
import index_maps
import index_sbox
import index_tools
import index_assets
import index_external


# --- Source map -----------------------------------------------------------

ROOT_DOMAINS: list[tuple[str, str, str, str]] = [
    ("README.md",  "EFT2 game/remake contract",                                "editable_contract",        "patch surgically"),
    ("AGENTS.md",  "agent workflow and source hierarchy contract",             "editable_contract",        "patch surgically"),
    ("Game/eft2/", "EFT2 s&box game project (eft2.sbproj); initial scaffold exists", "active_project", "implementation guided by infrastructure tools; do not add mechanics until rails are stable"),
    ("Maps/",      "canonical map domains and map analysis outputs",           "mixed",                    "VMFs read-only; analysis writable by tools"),
    ("Lua/",       "original GMod EFT source evidence",                        "read_only_source_reference", "do not mutate unless explicitly instructed"),
    ("SBox/",      "s&box docs/source/runtime/sample reference",               "external_reference",       "do not mutate or vendor into Game/"),
    ("Tools/",     "EFT2-owned infrastructure",                                "editable_tooling",         "safe to edit tool code for current task"),
    ("Assets/",    "curated gameplay/media/visual/reference material",         "curated_asset",            "edit only when curating evidence"),
    ("Tools/Indexer/Output/", "generated LLM-readable working memory",         "generated_output",         "regenerate freely"),
    ("garrysmod-master/", "temporary GMod source reference",                   "external_reference",       "temporary reference only; remove after derived indexes are generated"),
    ("FFmpeg-Builds-master/", "temporary upstream FFmpeg cross-build reference", "external_reference",     "temporary reference only; remove after derived indexes are generated"),
    ("source-sdk-2013-master/", "temporary Source SDK 2013 reference",          "external_reference",       "temporary reference only; remove after SOURCE_SDK_REFERENCE_INDEX.json generated"),
    (".gitignore", "Git ignore rules",                                         "editable_contract",        "do not edit from Indexer; recommend changes only"),
]


def build_source_map(root: Path, env: IndexEnvelope) -> dict[str, Any]:
    entries: dict[str, Any] = {}
    for path_str, purpose, policy, mutation in ROOT_DOMAINS:
        target = root / path_str.rstrip("/")
        entries[path_str] = {
            "purpose": purpose,
            "policy": policy,
            "mutation_rule": mutation,
            "exists": target.exists(),
        }
    return env.wrap({"domains": entries})


# --- Aggregate Markdown reports ------------------------------------------

def render_project_index(root: Path, summary: dict[str, Any]) -> str:
    lines = ["# EFT2 Project Index", ""]
    lines.append("Repo purpose: modern s&box / Source 2 remake of *Extreme Football Throwdown*.")
    lines.append("")
    lines.append(
        "EFT2 is not just a code port. Its infrastructure exists to make agents understand "
        "EFT's rules, feel, maps, evidence, and failure modes deeply enough to implement "
        "and modernize the game without erasing its identity."
    )
    lines.append("")
    lines.append("Phase: infrastructure rails — Game/eft2/ scaffold exists; implementation deferred until Contract Validator, Scenario Harness, and Telemetry are stable.")
    lines.append("Structure: Tools/ (infrastructure) and Game/eft2/ (s&box project, eft2.sbproj — scaffold present, mechanics deferred).")
    lines.append("Do not introduce Engine/ or Runtime/ folders or umbrella names.")
    lines.append("")
    lines.append("## Major folders")
    for path_str, purpose, policy, _ in ROOT_DOMAINS:
        target = root / path_str.rstrip("/")
        mark = "OK" if target.exists() else "missing"
        lines.append(f"- `{path_str}` — {purpose} [{policy}] ({mark})")
    lines.append("")
    lines.append("## Tools status")
    tools = summary.get("tools", {})
    for entry in tools.get("recommended_status", []):
        lines.append(f"- {entry['name']}: {entry['status']}")
    lines.append("")
    lines.append("## Maps status")
    maps = summary.get("maps", {})
    if maps.get("present"):
        lines.append(f"- canonical map domains: {maps.get('domain_count', 0)}")
        lines.append(f"- loose VMFs at Maps root: {len(maps.get('loose_vmfs', []) or [])}")
        custom = maps.get("custom_eft_fgds") or []
        lines.append(f"- custom EFT FGDs found: {len(custom)}")
        for f in custom:
            lines.append(f"  - `{f}`")
    else:
        lines.append("- Maps/ not present")
    lines.append("")
    lines.append("## Lua status")
    lua = summary.get("lua", {})
    if lua.get("present"):
        lines.append(f"- Lua files: {lua.get('file_count', 0)}")
    else:
        lines.append("- Lua/ not present")
    lines.append("")
    lines.append("## SBox reference status")
    sbox = summary.get("sbox", {})
    if sbox.get("present"):
        lines.append(f"- SBox/ present; sbproj files: {len(sbox.get('sbproj_files', []) or [])}")
    else:
        lines.append("- SBox/ not present")
    lines.append("")
    lines.append("## Assets / observation status")
    assets = summary.get("assets", {})
    if assets.get("present"):
        pending = assets.get("pending_observer_processing") or []
        lines.append(f"- pending Observer processing: {pending if pending else 'none'}")
    else:
        lines.append("- Assets/ not present")
    lines.append("")
    lines.append("## External temporary trees")
    ext = summary.get("external", {})
    for key in ("gmod", "ffmpeg"):
        e = ext.get(key) if ext else None
        if e:
            lines.append(f"- `{e['detected_path']}` — {e['file_count_approx']} files, "
                         f"gitignored={e['gitignore_covers']}")
        else:
            lines.append(f"- {key}: not present")
    lines.append("")
    lines.append("## Strongest next action")
    lines.append("Read `CURRENT_STATE.md` and `NEXT_ACTIONS.md`. Build `Tools/Observer/` next.")
    lines.append("")
    warnings = summary.get("warnings", [])
    if warnings:
        lines.append("## Warnings")
        for w in warnings:
            lines.append(f"- {w}")
    return "\n".join(lines)


def render_current_state(root: Path, summary: dict[str, Any]) -> str:
    lines = ["# EFT2 Current State", "", "Factual snapshot — not aspirational.", ""]
    checks = [
        ("Game/eft2/ scaffold present", (root / "Game" / "eft2" / "eft2.sbproj").exists()),
        ("Tools/Indexer/ present", (root / "Tools" / "Indexer").is_dir()),
        ("Tools/Map Analyzer/ present", (root / "Tools" / "Map Analyzer").is_dir()),
        ("Tools/Observer/ present", (root / "Tools" / "Observer").is_dir()),
        ("Tools/Contract Validator/ present", (root / "Tools" / "Contract Validator").is_dir()),
        ("Tools/Scenario Harness/ present", (root / "Tools" / "Scenario Harness").is_dir()),
        ("Tools/Telemetry/ present", (root / "Tools" / "Telemetry").is_dir()),
        ("Tools/Simulation/ present", (root / "Tools" / "Simulation").is_dir()),
        ("SBox/ reference tree present", (root / "SBox").is_dir()),
        ("Lua/ source reference present", (root / "Lua").is_dir()),
        ("Assets/ present", (root / "Assets").is_dir()),
        ("Maps/ present", (root / "Maps").is_dir()),
        ("garrysmod-master/ detected", (root / "garrysmod-master").is_dir()),
        ("FFmpeg-Builds-master/ detected", (root / "FFmpeg-Builds-master").is_dir()),
    ]
    for label, ok in checks:
        lines.append(f"- [{'x' if ok else ' '}] {label}")
    lines.append("")
    maps = summary.get("maps", {})
    if maps.get("present"):
        lines.append("## Map analysis snapshot")
        for d in maps.get("domains", []):
            lines.append(
                f"- {d['canonical_name']}: analysis_outputs={d['analysis_output_count']} "
                f"vp={d['virtual_perception_present']} sim={d['simulation_present']}"
            )
        lines.append("")
    warnings = summary.get("warnings", [])
    if warnings:
        lines.append("## Warnings")
        for w in warnings:
            lines.append(f"- {w}")
    lines.append("")
    lines.append(f"Generated by {GENERATOR}.")
    return "\n".join(lines)


def render_next_actions(root: Path, summary: dict[str, Any]) -> str:
    lines = ["# Next Actions", "", "Prioritized. Adjust as repo state changes.", ""]
    actions: list[str] = []

    actions.append("Review `Tools/Indexer/Output/PROJECT_INDEX.md` and `CURRENT_STATE.md`.")

    ext = summary.get("external", {}) or {}
    gmod = ext.get("gmod")
    ffmpeg = ext.get("ffmpeg")
    sdk = ext.get("source_sdk")

    if gmod and not gmod.get("gitignore_covers"):
        actions.append(
            "Add to `.gitignore` so the temporary GMod tree is not tracked:\n"
            "    ```\n    garrysmod-master/\n    garrysmod-master.zip\n    ```"
        )
    if ffmpeg and not ffmpeg.get("gitignore_covers"):
        actions.append(
            "Add to `.gitignore` so the temporary FFmpeg tree is not tracked:\n"
            "    ```\n    FFmpeg-Builds-master/\n    FFmpeg-Builds-master.zip\n    ```"
        )

    if gmod:
        actions.append(
            "Have `Tools/Map Analyzer/` consume `SOURCE1_FGD_INDEX.json` for entity ancestry, "
            "then delete `garrysmod-master/` from the workspace."
        )
    if ffmpeg and ffmpeg.get("is_only_build_infrastructure"):
        actions.append(
            "Delete `FFmpeg-Builds-master/` — it is upstream cross-build infrastructure with no "
            "prebuilt binaries usable by EFT2. Place a standalone `ffmpeg.exe` elsewhere when "
            "`Tools/Observer/` needs it."
        )
    elif ffmpeg:
        actions.append(
            "Extract any usable ffmpeg binaries from `FFmpeg-Builds-master/` to a stable tools "
            "location, then delete the rest of the tree."
        )
    if sdk:
        actions.append(
            "Delete `source-sdk-2013-master/` — key extracts (CTriggerPush semantics, "
            "NextBot header list, gamemovement constants) are now in "
            "`SOURCE_SDK_REFERENCE_INDEX.json`. No FGDs present (those came from garrysmod-master)."
        )

    maps = summary.get("maps", {}) or {}
    if maps.get("present") and not maps.get("custom_eft_fgds"):
        actions.append("Locate or author a custom `eft.fgd` for Hammer entity grammar; warning `custom_eft_fgd_missing`.")

    actions.extend([
        "Build `Tools/Observer/` so videos/screenshots become LLM-readable observation artifacts.",
        "Build `Tools/Contract Validator/` to check docs/code/tools against the EFT2 contract.",
        "Build `Tools/Scenario Harness/` to encode must-preserve EFT situations as tests.",
        "Build `Tools/Telemetry/` to define event schemas for matches and simulations.",
        "Build `Tools/Simulation/` only after the above are stable.",
        "Implement `Game/eft2/` mechanics only after Contract Validator, Scenario Harness, and Telemetry are stable — the scaffold already exists at `Game/eft2/eft2.sbproj`.",
    ])

    for i, a in enumerate(actions, 1):
        lines.append(f"{i}. {a}")
    lines.append("")
    lines.append("The Indexer is not the game builder. It is the repo memory builder.")
    return "\n".join(lines)


# --- CLI -----------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="EFT2 project-wide Indexer.")
    p.add_argument("--root", type=Path, default=Path.cwd(),
                   help="Repository root (defaults to current working directory).")
    p.add_argument("--output", type=Path, default=None,
                   help="Output directory (defaults to <indexer dir>/Output).")
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args(argv)

    root = args.root.resolve()
    output_dir = (args.output or (HERE / "Output")).resolve()

    if not root.is_dir():
        print(f"ERROR: --root not a directory: {root}", file=sys.stderr)
        return 2

    env = IndexEnvelope(repo_root=root)
    writer = OutputWriter(output_dir)

    summary: dict[str, Any] = {}

    def step(name: str, fn):
        try:
            data = fn(root, env)
            summary[name] = data
            if args.verbose:
                print(f"  [ok] {name}")
            return data
        except Exception as e:  # noqa: BLE001
            env.warn(f"step_failed:{name}:{e}")
            if args.verbose:
                traceback.print_exc()
            return None

    if args.verbose:
        print(f"Indexing repo: {root}")
        print(f"Writing to:    {output_dir}")

    contract = step("contract", index_markdown.build)
    lua = step("lua", index_lua.build)
    maps = step("maps", index_maps.build)
    sbox = step("sbox", index_sbox.build)
    tools = step("tools", index_tools.build)
    assets = step("assets", index_assets.build)
    external = step("external", index_external.build)

    # Source map.
    source_map = build_source_map(root, env)

    # Top-level summary used by aggregate writers.
    summary["warnings"] = list(env.warnings)

    # Write JSON outputs.
    if contract is not None:
        writer.write_json("CONTRACT_INDEX.json", contract)
    if lua is not None:
        writer.write_json("LUA_INDEX.json", lua)
    if maps is not None:
        writer.write_json("MAPS_INDEX.json", maps)
    if sbox is not None:
        writer.write_json("SBOX_INDEX.json", sbox)
    if tools is not None:
        writer.write_json("TOOLS_INDEX.json", tools)
    if assets is not None:
        writer.write_json("OBSERVATION_INDEX.json", assets)
        writer.write_md("MULTIMODAL_CONTEXT.md", index_assets.render_multimodal_md(assets))
    writer.write_json("SOURCE_MAP.json", source_map)

    if external:
        if external.get("gmod"):
            writer.write_json("GMOD_REFERENCE_INDEX.json", external["gmod"])
        if external.get("fgd"):
            writer.write_json("SOURCE1_FGD_INDEX.json", external["fgd"])
        if external.get("ffmpeg"):
            writer.write_json("FFMPEG_REFERENCE_INDEX.json", external["ffmpeg"])
        if external.get("source_sdk"):
            writer.write_json("SOURCE_SDK_REFERENCE_INDEX.json", external["source_sdk"])

    # Refresh warnings after all steps completed.
    summary["warnings"] = list(env.warnings)

    # Markdown aggregates.
    writer.write_md("PROJECT_INDEX.md", render_project_index(root, summary))
    writer.write_md("CURRENT_STATE.md", render_current_state(root, summary))
    writer.write_md("NEXT_ACTIONS.md", render_next_actions(root, summary))

    # Console summary.
    print(f"{GENERATOR}: wrote outputs to {output_dir}")
    print(f"  warnings: {len(env.warnings)}")
    if args.verbose:
        for w in env.warnings:
            print(f"    - {w}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
