"""EFT2 Lua Audit.

Maps inherited Lua source under `lua/` into stable, agent-readable behavior
blocks, system clusters, and a Lua -> s&box bridge.

This is a *draft behavior map*, not final truth. Mechanical fields are
extracted directly. Interpretive fields default to inferred + low confidence
and are flagged for human review when the heuristic cannot stand on evidence.

Run from repo root:

    python "tools/lua audit/audit_lua.py" --help
    python "tools/lua audit/audit_lua.py" --root .
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

GENERATOR = "tools/lua audit"
SCHEMA_VERSION = 1

CLUSTERS: list[dict[str, Any]] = [
    {
        "id": "player_movement_charge",
        "title": "player movement / charge",
        "path_tokens": ["movement", "sh_globals", "player_class", "obj_player",
                        "player_extension", "sv_obj_player_extend",
                        "sh_obj_player_extend"],
        "symbol_tokens": ["charge", "speed", "move", "strafe", "run", "wish"],
    },
    {
        "id": "tackle_knockdown_immunity",
        "title": "tackle / knockdown / immunity",
        "path_tokens": ["divetackle", "knockdown", "knockeddown",
                        "knockdownrecover", "spinnyknockdown",
                        "trigger_knockdown", "point_divetackletrigger",
                        "wallslam", "chargehit", "punch", "punchhit",
                        "powerstruggle", "powerstrugglehit",
                        "powerstrugglelose", "powerstrugglewin"],
        "symbol_tokens": ["tackle", "knockdown", "immune", "stun",
                          "recover", "wallslam", "punch", "powerstruggle"],
    },
    {
        "id": "ball_possession",
        "title": "ball possession / pickup / drop / fumble",
        "path_tokens": ["prop_ball", "obj_ball", "prop_balltrigger",
                        "prop_carry"],
        "symbol_tokens": ["pickup", "drop", "fumble", "carrier", "carry",
                          "possess", "ball"],
    },
    {
        "id": "throwing_passing",
        "title": "throwing / passing",
        "path_tokens": ["throw", "states/throw"],
        "symbol_tokens": ["throw", "pass", "release", "windup"],
    },
    {
        "id": "scoring_goals",
        "title": "scoring / goals",
        "path_tokens": ["prop_goal", "trigger_goal", "logic_teamscore",
                        "scoreball"],
        "symbol_tokens": ["goal", "score", "point"],
    },
    {
        "id": "round_flow",
        "title": "round flow / respawn / reset",
        "path_tokens": ["round_controller", "round_transitions",
                        "sh_roundtransitions", "preround", "sh_states",
                        "ballreset", "trigger_ballreset", "sv_match_recorder",
                        "info_player_blue", "info_player_red",
                        "info_player_spectator", "sv_spectator"],
        "symbol_tokens": ["round", "respawn", "reset", "preround",
                          "spawn", "match"],
    },
    {
        "id": "map_entities_fgd",
        "title": "map entities (FGD)",
        "path_tokens": ["entities/entities/", "trigger_abspush",
                        "trigger_jumppad", "trigger_powerup",
                        "info_observer_point", "env_teamsound",
                        "logic_norandomweapons", "prop_waterballplatform"],
        "symbol_tokens": ["trigger", "logic_", "info_", "env_"],
    },
    {
        "id": "hud_minimap_scoreboard",
        "title": "HUD / minimap / scoreboard",
        "path_tokens": ["cl_hud", "cl_draw", "cl_scoreboard",
                        "cl_deathnotice", "cl_notify", "cl_splashscreen",
                        "cl_selectscreen", "cl_help", "cl_postprocess",
                        "vgui/", "obj_viewmodel_hud"],
        "symbol_tokens": ["hud", "draw", "scoreboard", "minimap", "notice",
                          "vgui"],
    },
    {
        "id": "bots_ai",
        "title": "bots / AI",
        "path_tokens": ["sv_bots", "obj_bot", "sv_bot_pathfinding", "sv_nav",
                        "sh_nav_graph", "cl_nav_editor", "sv_nav_editor",
                        "weapon_eft_nav"],
        "symbol_tokens": ["bot", "nav", "path", "ai"],
    },
    {
        "id": "status_powerups",
        "title": "status effects / powerups",
        "path_tokens": ["status__base", "status_jersey", "status_boozed",
                        "trigger_powerup", "iceball", "speedball",
                        "waterball", "scoreball", "blitzballhit",
                        "exp_boozebottle", "explosion_arcanewand",
                        "barrelexplosion", "prop_carry_arcanewand",
                        "prop_carry_barrel", "prop_carry_beatingstick",
                        "prop_carry_bigpole", "prop_carry_boozebottle",
                        "prop_carry_car", "prop_carry_melon",
                        "prop_carry_melondriver", "hit_beatingstick",
                        "hit_bigpole", "arcanewandattack",
                        "beatingstickattack", "bigpoleattack",
                        "projectile_arcanewand"],
        "symbol_tokens": ["status", "powerup", "boozed", "jersey",
                          "iceball", "speedball", "waterball"],
    },
    {
        "id": "audio_presentation",
        "title": "audio / presentation",
        "path_tokens": ["sh_voice", "sv_emotes", "cl_rich_presence",
                        "skin.lua", "player_colours", "languages/",
                        "sh_translate", "round_transitions/slide",
                        "animationsapi/", "sh_animations", "playergibs",
                        "bloodstream", "wave"],
        "symbol_tokens": ["sound", "voice", "emote", "anim", "skin",
                          "translate", "language", "presence"],
    },
    {
        "id": "admin_debug_dev",
        "title": "admin / debug / dev utilities",
        "path_tokens": ["sv_security", "sv_gmchanger", "cl_gmchanger",
                        "sv_mapvote", "cl_mapvote", "vgui_vote",
                        "sv_downloads", "cl_manifest_data",
                        "cl_manifest_debug", "utility.lua",
                        "lib/", "class_default"],
        "symbol_tokens": ["debug", "manifest", "admin", "vote", "download",
                          "security", "gmchanger"],
    },
]

CLUSTER_TITLES = {c["id"]: c["title"] for c in CLUSTERS}

CSHARP_OWNER_HINTS: list[tuple[str, str]] = [
    ("ball_possession",          "game/eft2/Code/Ball.cs"),
    ("scoring_goals",            "game/eft2/Code/GoalTrigger.cs"),
    ("round_flow",               "game/eft2/Code/GameSystem.cs"),
    ("player_movement_charge",   "game/eft2/Code/PlayerMovement.cs"),
    ("tackle_knockdown_immunity","game/eft2/Code/PlayerMovement.cs"),
    ("throwing_passing",         "game/eft2/Code/PlayerMovement.cs"),
    ("hud_minimap_scoreboard",   "game/eft2/Code/Hud.cs"),
    ("audio_presentation",       "game/eft2/Code/Hud.cs"),
]

CSHARP_OWNER_BY_CLUSTER: dict[str, str] = {}
for cid, path in CSHARP_OWNER_HINTS:
    CSHARP_OWNER_BY_CLUSTER.setdefault(cid, path)

# Special-case map-entity ownership: each prop_ball / trigger_goal etc. may
# already have a candidate file. Detected per-block when the lua filename
# matches a C# file basename.

MANIFEST_HEADER_RE = re.compile(
    r"///\s*MANIFEST LINKS:?\s*\n((?:\s*///[^\n]*\n)+)",
    re.IGNORECASE,
)
MANIFEST_LINE_RE = re.compile(r"///\s*([^\n]+)")

CONTRACT_ID_RE = re.compile(r"\b([CPMSE]-\d{2,4})\b")

# Block extraction patterns (regex; not a real Lua parser).
FUNC_RE = re.compile(
    r"^\s*(?:local\s+)?function\s+([A-Za-z_][\w\.]*[:\.][A-Za-z_]\w*|[A-Za-z_][\w\.]*)\s*\(([^)]*)\)",
    re.MULTILINE,
)
HOOK_RE = re.compile(
    r"""hook\.Add\(\s*['"]([^'"]+)['"]\s*,\s*['"]([^'"]+)['"]\s*,\s*function\s*\(([^)]*)\)""",
    re.MULTILINE,
)
NET_RE = re.compile(
    r"""net\.Receive\(\s*['"]([^'"]+)['"]\s*,\s*function\s*\(([^)]*)\)""",
    re.MULTILINE,
)
ENT_FIELD_RE = re.compile(
    r"^\s*(ENT|SWEP|GM)\.([A-Za-z_]\w*)\s*=",
    re.MULTILINE,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def line_of(text: str, idx: int) -> int:
    return text.count("\n", 0, idx) + 1


def normalize_signature(params: str) -> str:
    return re.sub(r"\s+", "", params or "")


def short_body_hash(body: str) -> str:
    stripped = re.sub(r"--\[\[.*?\]\]", "", body, flags=re.DOTALL)
    stripped = re.sub(r"--[^\n]*", "", stripped)
    stripped = re.sub(r"\s+", " ", stripped).strip()
    return hashlib.sha1(stripped[:200].encode("utf-8")).hexdigest()[:10]


def slug(symbol: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "-", symbol or "anon").strip("-").upper()
    return s[:32] or "ANON"


def extract_manifest(text: str) -> tuple[list[str], list[str]]:
    """Return (raw_manifest_lines, contract_ids)."""
    lines: list[str] = []
    for m in MANIFEST_HEADER_RE.finditer(text):
        block = m.group(1)
        for ln in MANIFEST_LINE_RE.finditer(block):
            line = ln.group(1).strip()
            if line:
                lines.append(line)
    ids = sorted(set(CONTRACT_ID_RE.findall(text)))
    return lines, ids


def classify_cluster(relpath: str, symbol: str) -> tuple[str, str]:
    """Return (cluster_id, reason). reason is short."""
    rp = relpath.lower().replace("\\", "/")
    sym = (symbol or "").lower()
    # path tokens win first
    for c in CLUSTERS:
        for tok in c["path_tokens"]:
            if tok.lower() in rp:
                return c["id"], f"path:{tok}"
    for c in CLUSTERS:
        for tok in c["symbol_tokens"]:
            if tok.lower() in sym:
                return c["id"], f"symbol:{tok}"
    return "unclassified", "no-match"


def candidate_csharp_owner(relpath: str, cluster_id: str,
                           csharp_files: dict[str, str]) -> dict[str, Any]:
    """csharp_files: basename_lower -> repo-relative path."""
    base = Path(relpath).stem.lower()
    # Per-file basename match (prop_ball.lua -> Ball.cs)
    for needle, csname in [
        ("prop_ball", "ball.cs"),
        ("trigger_goal", "goaltrigger.cs"),
        ("prop_goal", "goaltrigger.cs"),
        ("trigger_ballreset", "ballresettrigger.cs"),
        ("info_player_blue", "spawnpoint.cs"),
        ("info_player_red", "spawnpoint.cs"),
        ("info_player_spectator", "spawnpoint.cs"),
        ("sv_match_recorder", "telemetrysink.cs"),
        ("cl_hud", "hud.cs"),
        ("cl_scoreboard", "hud.cs"),
        ("round_controller", "gamesystem.cs"),
    ]:
        if needle in relpath.lower():
            if csname in csharp_files:
                return {
                    "file": csharp_files[csname],
                    "status": "candidate_present",
                    "parity_verified": False,
                    "note": f"basename heuristic ({needle} -> {csname})",
                }
    # Cluster-level fallback
    cs_path = CSHARP_OWNER_BY_CLUSTER.get(cluster_id)
    if cs_path:
        bn = Path(cs_path).name.lower()
        if bn in csharp_files:
            return {
                "file": csharp_files[bn],
                "status": "candidate_present",
                "parity_verified": False,
                "note": f"cluster heuristic ({cluster_id})",
            }
        return {
            "file": cs_path,
            "status": "planned",
            "parity_verified": False,
            "note": "cluster suggests this owner; file not present",
        }
    return {
        "file": None,
        "status": "missing",
        "parity_verified": False,
        "note": "no cluster owner suggestion",
    }


def fgd_entities(fgd_text: str) -> list[str]:
    return sorted(set(re.findall(r"=\s*([a-z_][a-z0-9_]+)\s*:", fgd_text)))


def related_fgd_for_file(relpath: str, fgd_set: set[str]) -> list[str]:
    base = Path(relpath).stem.lower()
    return [e for e in fgd_set if e == base]


def gather_lua_files(lua_root: Path) -> list[Path]:
    out: list[Path] = []
    skip_dir_names = {"game logs"}
    for p in lua_root.rglob("*.lua"):
        rel = p.relative_to(lua_root)
        parts = {part.lower() for part in rel.parts}
        if parts & skip_dir_names:
            continue
        out.append(p)
    return sorted(out)


def extract_blocks(text: str) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    for m in FUNC_RE.finditer(text):
        symbol = m.group(1)
        params = m.group(2)
        start = m.start()
        end = min(len(text), start + 600)
        body = text[start:end]
        blocks.append({
            "kind": "function",
            "symbol": symbol,
            "params": params,
            "start": start,
            "body_excerpt": body,
        })
    for m in HOOK_RE.finditer(text):
        hook_event = m.group(1)
        hook_id = m.group(2)
        params = m.group(3)
        start = m.start()
        end = min(len(text), start + 600)
        body = text[start:end]
        blocks.append({
            "kind": "hook",
            "symbol": f"hook.Add:{hook_event}/{hook_id}",
            "params": params,
            "start": start,
            "body_excerpt": body,
        })
    for m in NET_RE.finditer(text):
        msg = m.group(1)
        params = m.group(2)
        start = m.start()
        end = min(len(text), start + 600)
        body = text[start:end]
        blocks.append({
            "kind": "net",
            "symbol": f"net.Receive:{msg}",
            "params": params,
            "start": start,
            "body_excerpt": body,
        })
    return blocks


def block_state_io(body: str) -> tuple[list[str], list[str]]:
    reads = sorted(set(re.findall(r"self:Get(\w+)\(", body)) |
                   set(re.findall(r"\bGetGlobal(\w+)\(", body)))
    writes = sorted(set(re.findall(r"self:Set(\w+)\(", body)) |
                    set(re.findall(r"\bSetGlobal(\w+)\(", body)))
    return reads, writes


def block_related_lua(body: str) -> list[str]:
    out: list[str] = []
    for m in re.finditer(r"""include\(\s*['"]([^'"]+)['"]\s*\)""", body):
        out.append(m.group(1))
    for m in re.finditer(r"""AddCSLuaFile\(\s*['"]([^'"]+)['"]\s*\)""", body):
        out.append(m.group(1))
    return sorted(set(out))


def infer_meaning(cluster_id: str, symbol: str, body: str
                  ) -> tuple[str, str, str, str, str, bool, str]:
    """Return (plain_english, gameplay_meaning, tacit_meaning,
    confidence, port_risk, needs_human_review, missing_evidence).

    Conservative: tacit_meaning is empty unless the cluster + symbol
    combination is strongly stereotyped.
    """
    sym = (symbol or "").lower()
    plain = ""
    meaning = ""
    tacit = ""
    confidence = "low"
    port_risk = "medium"
    needs = True
    missing = "first-pass heuristic; no human-validated annotation yet"

    if cluster_id == "ball_possession":
        plain = "Ball entity / carrier lifecycle behavior."
        meaning = "Possession transfer, pickup, drop, or fumble bookkeeping."
        if "fumble" in sym or "drop" in sym:
            tacit = ("Fumble is not cleanup; it creates the next contest. "
                     "Preserve volatility on transfer.")
            confidence = "medium"; port_risk = "high"; needs = False
            missing = ""
        elif "pickup" in sym or "carry" in sym or "carrier" in sym:
            tacit = ("Possession paints a target. Auto-pickup must remain "
                     "fast; carrier becomes the contested object.")
            confidence = "medium"; port_risk = "high"; needs = False
            missing = ""
    elif cluster_id == "tackle_knockdown_immunity":
        plain = "Tackle / knockdown / immunity state transition."
        meaning = "Removes a player from action and shapes recovery window."
        if "knockdown" in sym or "knockeddown" in sym or "wallslam" in sym:
            tacit = ("Knockdown is not cosmetic; it removes a player from "
                     "the next few seconds and seeds reversal density.")
            confidence = "medium"; port_risk = "high"; needs = False
            missing = ""
    elif cluster_id == "player_movement_charge":
        plain = "Player movement / speed / charge handling."
        meaning = "Locomotion mode and charge-state economy."
        if "charge" in sym:
            tacit = ("Charge is not just speed; it is threat state. "
                     "Readability of charge windup is core to head-on duels.")
            confidence = "medium"; port_risk = "high"; needs = False
            missing = ""
    elif cluster_id == "scoring_goals":
        plain = "Goal / scoring evaluation."
        meaning = "Determines when and how a score is awarded."
        port_risk = "high"
    elif cluster_id == "throwing_passing":
        plain = "Throw / pass commit and release."
        meaning = "Throw commitment and release timing."
        if "throw" in sym or "release" in sym:
            tacit = ("Throw is a commitment. Aborting commitment cheaply "
                     "would erode the meaning of the choice.")
            confidence = "medium"; port_risk = "high"; needs = False
            missing = ""
    elif cluster_id == "round_flow":
        plain = "Round / respawn / match-state flow."
        meaning = "Round phase transitions and spawn handling."
        port_risk = "medium"
    elif cluster_id == "map_entities_fgd":
        plain = "Map-authored entity behavior."
        meaning = ("FGD-defined entity behavior; map geometry is not "
                   "decoration, it shapes pressure and routes.")
        port_risk = "medium"
    elif cluster_id == "status_powerups":
        plain = "Status effect or powerup behavior."
        meaning = "Map-specific powerups influence map identity and tension."
        port_risk = "medium"
    elif cluster_id == "hud_minimap_scoreboard":
        plain = "HUD / scoreboard / minimap presentation."
        meaning = "Player-facing readability layer."
        port_risk = "low"
    elif cluster_id == "bots_ai":
        plain = "Bot AI / navigation behavior."
        meaning = ("Bot pressure and pathing; cleaner behavior is wrong if "
                   "it lowers contested interaction or reversal density.")
        port_risk = "medium"
    elif cluster_id == "audio_presentation":
        plain = "Audio / animation / presentation."
        meaning = "Cosmetic / feedback layer."
        port_risk = "low"
    elif cluster_id == "admin_debug_dev":
        plain = "Admin, debug, or developer utility."
        meaning = "Not gameplay; preserve only what diagnostics still need."
        port_risk = "low"
    else:
        plain = "Unclassified Lua block."
        meaning = "Heuristic could not place this block in a known cluster."
        missing = ("no path or symbol token matched a known cluster; "
                   "needs human classification")

    if not plain:
        plain = "Lua block."
    if not meaning:
        meaning = "No semantic interpretation inferred."
    return plain, meaning, tacit, confidence, port_risk, needs, missing


def load_id_registry(out_dir: Path) -> dict[str, str]:
    p = out_dir / "id_registry.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8")).get("ids", {})
        except Exception:
            return {}
    return {}


def save_id_registry(out_dir: Path, ids: dict[str, str]) -> None:
    p = out_dir / "id_registry.json"
    p.write_text(json.dumps({
        "generated_by": GENERATOR,
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "ids": ids,
    }, indent=2), encoding="utf-8")


def envelope(extra: dict[str, Any]) -> dict[str, Any]:
    out = {
        "generated_by": GENERATOR,
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "warnings": [],
    }
    out.update(extra)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(
        description="EFT2 Lua Audit — draft behavior map of inherited Lua.",
    )
    parser.add_argument("--root", default=".", help="Repo root (default: .)")
    parser.add_argument("--lua-dir", default="lua",
                        help="Lua scan root, repo-relative (default: lua)")
    parser.add_argument("--out", default="tools/lua audit/output",
                        help="Output dir (repo-relative)")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    lua_root = (root / args.lua_dir).resolve()
    out_dir = (root / args.out).resolve()

    if not lua_root.exists():
        print(f"[lua audit] ERROR: lua root not found: {args.lua_dir}",
              file=sys.stderr)
        return 2
    out_dir.mkdir(parents=True, exist_ok=True)

    # Inventory C# candidate owners
    csharp_dir = root / "game" / "eft2" / "Code"
    csharp_files: dict[str, str] = {}
    if csharp_dir.exists():
        for cs in csharp_dir.glob("*.cs"):
            rel = cs.relative_to(root).as_posix()
            csharp_files[cs.name.lower()] = rel

    # FGD entity set
    fgd_set: set[str] = set()
    fgd_path = root / "maps" / "shared" / "eft.fgd"
    if fgd_path.exists():
        fgd_set = set(fgd_entities(fgd_path.read_text(encoding="utf-8",
                                                     errors="replace")))

    files = gather_lua_files(lua_root)
    skipped = 0  # currently only game logs filter; counted via inventory diff
    total_lua = sum(1 for _ in lua_root.rglob("*.lua"))
    skipped = total_lua - len(files)

    id_registry = load_id_registry(out_dir)
    cluster_seq: dict[str, int] = {}
    # seed sequence from existing IDs so reruns append
    for existing_id in id_registry.values():
        m = re.match(r"LUA-([A-Z0-9_]+)-.*-(\d+)$", existing_id)
        if m:
            cid = m.group(1).lower()
            seq = int(m.group(2))
            cluster_seq[cid] = max(cluster_seq.get(cid, 0), seq)

    blocks_out: list[dict[str, Any]] = []
    cluster_blocks: dict[str, list[str]] = {c["id"]: [] for c in CLUSTERS}
    cluster_blocks["unclassified"] = []

    files_audited = 0
    files_skipped_no_blocks = 0

    for path in files:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            print(f"[lua audit] WARN: cannot read {path}: {e}",
                  file=sys.stderr)
            continue
        relpath = path.relative_to(root).as_posix()
        manifest_lines, contract_ids = extract_manifest(text)
        related_fgd = related_fgd_for_file(relpath, fgd_set)
        raw_blocks = extract_blocks(text)
        if not raw_blocks:
            files_skipped_no_blocks += 1
            continue
        files_audited += 1
        for rb in raw_blocks:
            symbol = rb["symbol"]
            params = rb["params"]
            sig = normalize_signature(params)
            if not symbol or symbol.lower().startswith("anon"):
                identity_key = (f"{relpath}::{rb['kind']}::"
                                f"anon::{short_body_hash(rb['body_excerpt'])}")
                sym_for_slug = "anon"
            else:
                identity_key = (f"{relpath}::{rb['kind']}::{symbol}::{sig}")
                sym_for_slug = symbol
            cluster_id, reason = classify_cluster(relpath, symbol)
            if identity_key in id_registry:
                block_id = id_registry[identity_key]
            else:
                cluster_seq[cluster_id] = cluster_seq.get(cluster_id, 0) + 1
                block_id = (f"LUA-{cluster_id.upper()}"
                            f"-{slug(sym_for_slug)}"
                            f"-{cluster_seq[cluster_id]:03d}")
                id_registry[identity_key] = block_id

            line = line_of(text, rb["start"])
            reads, writes = block_state_io(rb["body_excerpt"])
            related_lua = block_related_lua(rb["body_excerpt"])
            owner = candidate_csharp_owner(relpath, cluster_id, csharp_files)
            (plain, meaning, tacit, confidence, port_risk, needs,
             missing) = infer_meaning(cluster_id, symbol, rb["body_excerpt"])

            audit_quality = "inferred"
            # mechanical-only blocks: pure ENT field assignments would qualify,
            # but we extract real callable blocks — keep as inferred.

            block = {
                "id": block_id,
                "audit_quality": audit_quality,
                "identity_key": identity_key,
                "file": relpath,
                "symbol": symbol,
                "block_kind": rb["kind"],
                "line_range": [line, line],
                "cluster": cluster_id,
                "cluster_reason": reason,
                "plain_english": plain,
                "gameplay_meaning": meaning,
                "tacit_meaning": tacit,
                "state_read": reads,
                "state_written": writes,
                "related_lua": related_lua,
                "related_readme_ids": contract_ids,
                "related_fgd_entities": related_fgd,
                "related_map_concepts": [],
                "related_sbox_concepts": [],
                "inherited_manifest_links": manifest_lines,
                "csharp_owner": owner,
                "telemetry_events": [],
                "scenario_ids": [],
                "simulation_relevance": (
                    "rule grounding for tackle/knockdown timing"
                    if cluster_id == "tackle_knockdown_immunity" else
                    "rule grounding for possession volatility"
                    if cluster_id == "ball_possession" else
                    "rule grounding for round flow"
                    if cluster_id == "round_flow" else
                    "rule grounding for movement / charge economy"
                    if cluster_id == "player_movement_charge" else
                    "presentation-only; low simulation relevance"
                    if cluster_id in ("hud_minimap_scoreboard",
                                      "audio_presentation",
                                      "admin_debug_dev") else
                    "secondary rule grounding"
                ),
                "port_risk": port_risk,
                "confidence": confidence,
                "needs_human_review": needs,
                "missing_evidence": missing or None,
                "notes": "",
            }
            blocks_out.append(block)
            cluster_blocks.setdefault(cluster_id, []).append(block_id)

    save_id_registry(out_dir, id_registry)

    # Cluster summary
    cluster_summary = []
    for c in CLUSTERS:
        ids = cluster_blocks.get(c["id"], [])
        cluster_summary.append({
            "id": c["id"],
            "title": c["title"],
            "block_count": len(ids),
            "block_ids": ids,
            "candidate_csharp_owner": CSHARP_OWNER_BY_CLUSTER.get(c["id"]),
        })
    if cluster_blocks.get("unclassified"):
        cluster_summary.append({
            "id": "unclassified",
            "title": "unclassified (needs human placement)",
            "block_count": len(cluster_blocks["unclassified"]),
            "block_ids": cluster_blocks["unclassified"],
            "candidate_csharp_owner": None,
        })

    # Bridge: per-cluster bridge entries
    bridge_entries = []
    cluster_block_lookup: dict[str, list[dict[str, Any]]] = {}
    for b in blocks_out:
        cluster_block_lookup.setdefault(b["cluster"], []).append(b)
    for c in CLUSTERS + [{"id": "unclassified", "title": "unclassified"}]:
        cid = c["id"]
        bs = cluster_block_lookup.get(cid, [])
        if not bs:
            continue
        # Aggregate evidence
        files_in = sorted({b["file"] for b in bs})
        owner_pick = None
        for b in bs:
            if b["csharp_owner"]["file"]:
                owner_pick = b["csharp_owner"]
                break
        # Tacit aggregation: take first non-empty
        tacit = ""
        for b in bs:
            if b["tacit_meaning"]:
                tacit = b["tacit_meaning"]; break
        port_risks = sorted({b["port_risk"] for b in bs})
        bridge_entries.append({
            "cluster": cid,
            "title": CLUSTER_TITLES.get(cid, cid),
            "lua_evidence": {
                "block_count": len(bs),
                "files": files_in,
                "sample_ids": [b["id"] for b in bs[:8]],
            },
            "semantic_meaning": (
                bs[0]["gameplay_meaning"]
                if bs else "n/a"
            ),
            "tacit_played_meaning": tacit or (
                "Not yet annotated; needs veteran/human review."
            ),
            "sbox_surface": {
                "engine_concept": (
                    "Component + GameObjectSystem + ITriggerListener"
                    if cid in ("ball_possession", "scoring_goals",
                               "round_flow", "map_entities_fgd") else
                    "PlayerController / movement Component"
                    if cid in ("player_movement_charge",
                               "tackle_knockdown_immunity",
                               "throwing_passing") else
                    "HUD Component + scene UI"
                    if cid == "hud_minimap_scoreboard" else
                    "Sound / Animation Component"
                    if cid == "audio_presentation" else
                    "Bot AI Component + navmesh"
                    if cid == "bots_ai" else
                    "Status Component + buff system"
                    if cid == "status_powerups" else
                    "n/a"
                ),
            },
            "csharp_owner": owner_pick or {
                "file": CSHARP_OWNER_BY_CLUSTER.get(cid),
                "status": "planned" if CSHARP_OWNER_BY_CLUSTER.get(cid)
                          else "missing",
                "parity_verified": False,
            },
            "telemetry_scenario_validation": {
                "telemetry_events": [],
                "scenario_ids": [],
                "note": ("Telemetry events and scenario IDs not yet linked; "
                         "future pass should join with "
                         "tools/telemetry/events/ and "
                         "tools/scenario harness/scenarios/."),
            },
            "simulation_relevance": (
                bs[0]["simulation_relevance"]
                if bs else "n/a"
            ),
            "port_risk": (
                "high" if "high" in port_risks
                else "medium" if "medium" in port_risks
                else "low"
            ),
        })

    # ---- Write outputs ----
    audit_json = envelope({
        "lua_root": args.lua_dir,
        "lua_files_total_observed": total_lua,
        "lua_files_audited": files_audited,
        "lua_files_no_blocks": files_skipped_no_blocks,
        "lua_files_skipped_inventory": skipped,
        "block_count": len(blocks_out),
        "blocks": blocks_out,
    })
    (out_dir / "LUA_AUDIT.json").write_text(
        json.dumps(audit_json, indent=2), encoding="utf-8")

    clusters_json = envelope({
        "cluster_count": len(cluster_summary),
        "block_count": len(blocks_out),
        "clusters": cluster_summary,
    })
    (out_dir / "LUA_SYSTEM_CLUSTERS.json").write_text(
        json.dumps(clusters_json, indent=2), encoding="utf-8")

    bridge_json = envelope({
        "bridge_entry_count": len(bridge_entries),
        "entries": bridge_entries,
    })
    (out_dir / "LUA_TO_SBOX_BRIDGE.json").write_text(
        json.dumps(bridge_json, indent=2), encoding="utf-8")

    # ---- Markdown renders ----
    md = []
    md.append("# Lua Audit\n")
    md.append(f"Generated by `{GENERATOR}` at {audit_json['generated_at']}.\n")
    md.append("This is a **draft behavior map**, not final truth. ")
    md.append("Mechanical fields are extracted directly; interpretive ")
    md.append("fields default to `audit_quality: inferred` with low ")
    md.append("confidence and are flagged for human review where evidence ")
    md.append("is missing.\n")
    md.append("")
    md.append(f"- Lua files observed: **{total_lua}**")
    md.append(f"- Lua files audited (had extractable blocks): **{files_audited}**")
    md.append(f"- Lua files with no extractable blocks: **{files_skipped_no_blocks}**")
    md.append(f"- Lua files skipped by inventory filter: **{skipped}**")
    md.append(f"- Behavior blocks extracted: **{len(blocks_out)}**")
    md.append("")
    md.append("## Honesty rules\n")
    md.append("- `csharp_owner.status = candidate_present` only means a ")
    md.append("  plausible owner file exists. **Parity is not verified.**")
    md.append("- `tacit_meaning` is conservative. If empty + ")
    md.append("  `needs_human_review = true`, see `missing_evidence`.")
    md.append("- IDs are stable across reformats: identity is ")
    md.append("  `relpath :: block_kind :: symbol :: normalized_signature`.")
    md.append("")
    md.append("## Block index (first 200)\n")
    md.append("| ID | Cluster | File | Symbol | Owner | Risk | Conf | Review |")
    md.append("|---|---|---|---|---|---|---|---|")
    for b in blocks_out[:200]:
        md.append("| {id} | {cl} | `{f}` | `{s}` | {o} | {r} | {c} | {n} |".format(
            id=b["id"], cl=b["cluster"], f=b["file"], s=b["symbol"][:48],
            o=(b["csharp_owner"]["file"] or "—") + " (" +
              b["csharp_owner"]["status"] + ")",
            r=b["port_risk"], c=b["confidence"],
            n="yes" if b["needs_human_review"] else "no",
        ))
    if len(blocks_out) > 200:
        md.append("")
        md.append(f"... {len(blocks_out) - 200} more blocks in "
                  "`LUA_AUDIT.json`.")
    (out_dir / "LUA_AUDIT.md").write_text("\n".join(md) + "\n",
                                          encoding="utf-8")

    md = ["# Lua System Clusters\n",
          f"Generated by `{GENERATOR}`.\n",
          "Behavior blocks grouped into stable clusters. The first audit ",
          "pass classifies by file-path tokens first, then symbol tokens. ",
          "Anything that did not match a cluster is in `unclassified` and ",
          "needs human placement.\n",
          "| Cluster | Title | Blocks | Candidate C# owner |",
          "|---|---|---|---|"]
    for c in cluster_summary:
        md.append(f"| `{c['id']}` | {c['title']} | {c['block_count']} | "
                  f"{c['candidate_csharp_owner'] or '—'} |")
    (out_dir / "LUA_SYSTEM_CLUSTERS.md").write_text("\n".join(md) + "\n",
                                                    encoding="utf-8")

    md = ["# Lua → s&box Bridge\n",
          f"Generated by `{GENERATOR}`.\n",
          "Per-cluster bridge from Lua evidence to a candidate s&box ",
          "surface. **Candidate ownership is not parity.** Telemetry / ",
          "scenario joins are not yet wired.\n"]
    for e in bridge_entries:
        md.append(f"## {e['title']} (`{e['cluster']}`)\n")
        ev = e["lua_evidence"]
        md.append(f"- Lua evidence: {ev['block_count']} blocks across "
                  f"{len(ev['files'])} files")
        md.append(f"- Semantic meaning: {e['semantic_meaning']}")
        md.append(f"- Tacit played meaning: {e['tacit_played_meaning']}")
        md.append(f"- s&box surface: {e['sbox_surface']['engine_concept']}")
        owner = e["csharp_owner"]
        md.append(f"- C# owner candidate: `{owner.get('file') or '—'}` "
                  f"(status: {owner['status']}, "
                  f"parity_verified: {owner['parity_verified']})")
        md.append(f"- Simulation relevance: {e['simulation_relevance']}")
        md.append(f"- Port risk: {e['port_risk']}")
        md.append(f"- Telemetry / scenario validation: "
                  f"{e['telemetry_scenario_validation']['note']}")
        md.append("")
    (out_dir / "LUA_TO_SBOX_BRIDGE.md").write_text("\n".join(md) + "\n",
                                                   encoding="utf-8")

    # ---- Console summary ----
    needs_review = sum(1 for b in blocks_out if b["needs_human_review"])
    high_risk = sum(1 for b in blocks_out if b["port_risk"] == "high")
    unclassified = len(cluster_blocks.get("unclassified", []))
    print(f"[lua audit] lua files observed: {total_lua}")
    print(f"[lua audit] lua files audited:  {files_audited}")
    print(f"[lua audit] lua files no-blocks:{files_skipped_no_blocks}")
    print(f"[lua audit] blocks extracted:   {len(blocks_out)}")
    print(f"[lua audit] clusters non-empty: "
          f"{sum(1 for c in cluster_summary if c['block_count'] > 0)}")
    print(f"[lua audit] bridge entries:     {len(bridge_entries)}")
    print(f"[lua audit] needs_human_review: {needs_review}")
    print(f"[lua audit] high port risk:     {high_risk}")
    print(f"[lua audit] unclassified:       {unclassified}")
    print(f"[lua audit] outputs in:         {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
