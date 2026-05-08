"""EFT2 Contract Validator.

Checks docs, code, and tooling outputs against the EFT2 game contract defined
in README.md.

Run from repo root:

    python "tools/contract validator/validate_contract.py" --help
    python "tools/contract validator/validate_contract.py" --root .
    python "tools/contract validator/validate_contract.py" --root . --strict
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
GENERATOR = "tools/contract validator"
SCHEMA_VERSION = 1

# ---------------------------------------------------------------------------
# Contract ID patterns
# ---------------------------------------------------------------------------

# Matches: C-001, P-010, M-001, S-001, E-001 (any digit count)
CONTRACT_ID_RE = re.compile(r"\b([CPMSЕ]-\d{3,})\b")

# ---------------------------------------------------------------------------
# Mechanic anchors — must appear somewhere in the codebase / docs
# (once implementation files exist; missing from stubs → warning not failure)
# ---------------------------------------------------------------------------

MECHANIC_ANCHORS: list[dict[str, Any]] = [
    {"id": "volatile_possession",  "terms": ["volatile", "possession"],        "contract_refs": ["C-001", "C-002"]},
    {"id": "automatic_pickup",     "terms": ["automatic", "pickup", "autograb"],"contract_refs": ["P-950"]},
    {"id": "carrier_danger",       "terms": ["carrier", "danger"],             "contract_refs": ["C-002"]},
    {"id": "head_on_skill",        "terms": ["head.on", "headon", "head_on"],  "contract_refs": ["P-060"]},
    {"id": "knockdown_recovery",   "terms": ["knockdown", "recovery"],         "contract_refs": ["C-011"]},
    {"id": "dive",                 "terms": ["dive", "diving"],                "contract_refs": ["C-009"]},
    {"id": "throw_commit",         "terms": ["throw", "commit"],               "contract_refs": ["C-009"]},
    {"id": "jumppad",              "terms": ["jumppad", "jump_pad"],           "contract_refs": []},
    {"id": "ballreset",            "terms": ["ballreset", "ball_reset"],       "contract_refs": []},
    {"id": "scrum",                "terms": ["scrum"],                         "contract_refs": ["C-007"]},
]

# ---------------------------------------------------------------------------
# Known bad state patterns — P-900 violations
# These are regex patterns searched in code files; any match is a finding.
# ---------------------------------------------------------------------------

BAD_STATE_PATTERNS: list[dict[str, Any]] = [
    {
        "id": "sticky_possession",
        "description": "Sticky/locked possession — ball cannot change hands freely",
        "pattern": re.compile(r"sticky.?possess|lock.?possess|possess.*lock", re.IGNORECASE),
        "contract_refs": ["P-900"],
        "severity": "error",
    },
    {
        "id": "no_voluntary_drop",
        "description": "Voluntary ball drop explicitly disabled",
        "pattern": re.compile(r"cannot.?drop|no.?drop|drop.*disabled|disable.*drop", re.IGNORECASE),
        "contract_refs": ["P-900"],
        "severity": "error",
    },
    {
        "id": "permanent_knockdown",
        "description": "Knockdown with no recovery path",
        "pattern": re.compile(r"permanent.?knock|knock.*permanent|no.?recover", re.IGNORECASE),
        "contract_refs": ["P-900"],
        "severity": "warning",
    },
    {
        "id": "timer_based_possession",
        "description": "Automatic possession timeout (kills volatility)",
        "pattern": re.compile(r"possess.*timeout|timeout.*possess|auto.*possess.*expire", re.IGNORECASE),
        "contract_refs": ["P-900", "C-001"],
        "severity": "warning",
    },
]

# ---------------------------------------------------------------------------
# Files/folders to scan for ID references and bad-state patterns
# ---------------------------------------------------------------------------

SCAN_TARGETS = [
    "README.md",
    "AGENTS.md",
    "tools/",
    "game/",
    "lua/",
]

# Binary / large extensions to skip during text scan
SKIP_EXTENSIONS = {
    ".vmf", ".vtf", ".mdl", ".bsp", ".mp4", ".mov", ".mkv", ".avi",
    ".png", ".jpg", ".jpeg", ".gif", ".wav", ".mp3", ".ogg",
    ".exe", ".dll", ".so", ".zip", ".7z",
}

MAX_FILE_BYTES = 1_000_000  # Skip files > 1 MB


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _iter_text_files(root: Path, targets: list[str]):
    """Yield (path, text) for every scannable text file under the given targets."""
    for target in targets:
        p = root / target
        if p.is_file():
            yield from _read_file(p)
        elif p.is_dir():
            for child in sorted(p.rglob("*")):
                if child.is_file():
                    yield from _read_file(child)


def _read_file(path: Path):
    if path.suffix.lower() in SKIP_EXTENSIONS:
        return
    try:
        size = path.stat().st_size
    except OSError:
        return
    if size > MAX_FILE_BYTES:
        return
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        yield path, text
    except OSError:
        return


def _rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


# ---------------------------------------------------------------------------
# Check 1: Contract ID extraction from README.md
# ---------------------------------------------------------------------------

def extract_contract_ids(readme: Path) -> set[str]:
    """Return all contract IDs defined in README.md (section headings only)."""
    if not readme.exists():
        return set()
    text = readme.read_text(encoding="utf-8", errors="replace")
    # IDs in H2/H3 headings are "defined" in the contract.
    heading_re = re.compile(r"^#{1,3} +([CPMSE]-\d{3,})", re.MULTILINE)
    return {m.group(1) for m in heading_re.finditer(text)}


def check_id_coverage(root: Path, contract_ids: set[str]) -> list[dict[str, Any]]:
    """For each contract ID, check how many non-README files reference it."""
    findings: list[dict[str, Any]] = []
    if not contract_ids:
        return findings

    # Count references outside README.md
    id_refs: dict[str, list[str]] = {cid: [] for cid in contract_ids}

    for path, text in _iter_text_files(root, SCAN_TARGETS):
        rel_path = _rel(path, root)
        if rel_path == "README.md":
            continue
        for cid in contract_ids:
            if cid in text:
                id_refs[cid].append(rel_path)

    for cid, refs in sorted(id_refs.items()):
        if not refs:
            findings.append({
                "check": "id_coverage",
                "severity": "warning",
                "id": cid,
                "message": f"Contract ID {cid} is defined in README.md but referenced nowhere else in the repo.",
                "referenced_in": [],
            })
        else:
            findings.append({
                "check": "id_coverage",
                "severity": "ok",
                "id": cid,
                "message": f"Contract ID {cid} referenced in {len(refs)} file(s).",
                "referenced_in": refs,
            })
    return findings


# ---------------------------------------------------------------------------
# Check 2: Mechanic anchor presence
# ---------------------------------------------------------------------------

def check_mechanic_anchors(root: Path) -> list[dict[str, Any]]:
    """Check that key mechanic terms appear somewhere in the codebase / docs.

    Excludes the validator's own source files to avoid false positives from
    anchor-definition strings.
    """
    findings: list[dict[str, Any]] = []
    validator_dir = HERE.resolve()
    output_dir = (HERE / "Output").resolve()

    # Build a combined corpus of all scannable text
    corpus: dict[str, str] = {}
    for path, text in _iter_text_files(root, SCAN_TARGETS):
        rp = path.resolve()
        # Skip this tool's own source and generated outputs
        try:
            rp.relative_to(validator_dir)
            continue
        except ValueError:
            pass
        corpus[_rel(path, root)] = text.lower()

    for anchor in MECHANIC_ANCHORS:
        matched_files: list[str] = []
        for rel_path, text_lower in corpus.items():
            if all(term.lower() in text_lower for term in anchor["terms"]):
                matched_files.append(rel_path)

        if not matched_files:
            # Missing from stubs → warning (not error) until game/ is built
            findings.append({
                "check": "mechanic_anchor",
                "severity": "warning",
                "anchor": anchor["id"],
                "terms": anchor["terms"],
                "contract_refs": anchor["contract_refs"],
                "message": (
                    f"Mechanic anchor '{anchor['id']}' (terms: {anchor['terms']}) "
                    f"not found in any scanned file. "
                    f"Expected once game/ is implemented."
                ),
                "found_in": [],
            })
        else:
            findings.append({
                "check": "mechanic_anchor",
                "severity": "ok",
                "anchor": anchor["id"],
                "contract_refs": anchor["contract_refs"],
                "message": f"Mechanic anchor '{anchor['id']}' found.",
                "found_in": matched_files,
            })

    return findings


# ---------------------------------------------------------------------------
# Check 3: Bad state patterns (P-900)
# ---------------------------------------------------------------------------

def check_bad_states(root: Path) -> list[dict[str, Any]]:
    """Scan code for patterns that suggest P-900 violations.

    Scans game/ (primary target) and Tools/ but excludes the validator's own
    source files to avoid false positives from pattern-definition strings.
    """
    findings: list[dict[str, Any]] = []

    # Resolve the validator's own directory so we can skip it.
    validator_dir = HERE.resolve()

    for path, text in _iter_text_files(root, ["game/", "tools/"]):
        # Skip this tool's own source files — pattern definitions are not violations.
        try:
            path.resolve().relative_to(validator_dir)
            continue
        except ValueError:
            pass
        rel_path = _rel(path, root)
        for bsp in BAD_STATE_PATTERNS:
            for match in bsp["pattern"].finditer(text):
                line_no = text[: match.start()].count("\n") + 1
                findings.append({
                    "check": "bad_state",
                    "severity": bsp["severity"],
                    "bad_state_id": bsp["id"],
                    "description": bsp["description"],
                    "contract_refs": bsp["contract_refs"],
                    "file": rel_path,
                    "line": line_no,
                    "match": match.group(0),
                    "message": (
                        f"Possible P-900 violation '{bsp['id']}' in {rel_path}:{line_no} — "
                        f"matched '{match.group(0)}'"
                    ),
                })

    return findings


# ---------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------

def render_report_md(findings: list[dict[str, Any]], root: Path) -> str:
    lines = ["# EFT2 Contract Validation Report", ""]
    lines.append(f"Generated by `{GENERATOR}` — {datetime.now(timezone.utc).isoformat()}")
    lines.append("")

    errors = [f for f in findings if f.get("severity") == "error"]
    warnings = [f for f in findings if f.get("severity") == "warning"]
    ok = [f for f in findings if f.get("severity") == "ok"]

    lines.append(f"**Findings:** {len(errors)} error(s), {len(warnings)} warning(s), {len(ok)} ok")
    lines.append("")

    if errors:
        lines.append("## Errors (must fix)")
        for f in errors:
            lines.append(f"- **[{f.get('check','?')}]** {f['message']}")
        lines.append("")

    if warnings:
        lines.append("## Warnings")
        for f in warnings:
            lines.append(f"- [{f.get('check','?')}] {f['message']}")
        lines.append("")

    lines.append("## Coverage summary")
    id_findings = [f for f in findings if f.get("check") == "id_coverage"]
    covered = [f for f in id_findings if f.get("severity") == "ok"]
    gaps = [f for f in id_findings if f.get("severity") == "warning"]
    lines.append(f"- Contract IDs covered: {len(covered)}")
    lines.append(f"- Contract IDs with no external reference: {len(gaps)}")
    if gaps:
        lines.append("  - " + ", ".join(f["id"] for f in gaps))
    lines.append("")

    lines.append("## Mechanic anchor summary")
    anchor_ok = [f for f in findings if f.get("check") == "mechanic_anchor" and f.get("severity") == "ok"]
    anchor_miss = [f for f in findings if f.get("check") == "mechanic_anchor" and f.get("severity") != "ok"]
    lines.append(f"- Anchors found: {len(anchor_ok)}")
    lines.append(f"- Anchors missing: {len(anchor_miss)}")
    if anchor_miss:
        lines.append("  - " + ", ".join(f["anchor"] for f in anchor_miss))
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="EFT2 Contract Validator — checks repo against the EFT2 game contract."
    )
    p.add_argument("--root", type=Path, default=Path.cwd(),
                   help="Repository root (defaults to current working directory).")
    p.add_argument("--output", type=Path, default=None,
                   help="Output directory (defaults to <validator dir>/Output).")
    p.add_argument("--strict", action="store_true",
                   help="Exit nonzero if any contract ID coverage gaps exist.")
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args(argv)

    root = args.root.resolve()
    output_dir = (args.output or (HERE / "Output")).resolve()

    if not root.is_dir():
        print(f"ERROR: --root not a directory: {root}", file=sys.stderr)
        return 2

    output_dir.mkdir(parents=True, exist_ok=True)

    if args.verbose:
        print(f"Validating repo: {root}")

    readme = root / "README.md"
    contract_ids = extract_contract_ids(readme)

    if args.verbose:
        print(f"  Contract IDs found in README.md: {len(contract_ids)}")

    findings: list[dict[str, Any]] = []
    findings.extend(check_id_coverage(root, contract_ids))
    findings.extend(check_mechanic_anchors(root))
    findings.extend(check_bad_states(root))

    # Write JSON report
    report = {
        "generated_by": GENERATOR,
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "contract_ids_defined": sorted(contract_ids),
        "finding_count": len(findings),
        "error_count": sum(1 for f in findings if f.get("severity") == "error"),
        "warning_count": sum(1 for f in findings if f.get("severity") == "warning"),
        "ok_count": sum(1 for f in findings if f.get("severity") == "ok"),
        "findings": findings,
    }

    json_path = output_dir / "CONTRACT_REPORT.json"
    json_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    md_path = output_dir / "CONTRACT_REPORT.md"
    md_path.write_text(render_report_md(findings, root), encoding="utf-8")

    errors = report["error_count"]
    warnings = report["warning_count"]
    print(f"{GENERATOR}: {errors} error(s), {warnings} warning(s) — reports in {output_dir}")

    if args.verbose:
        for f in findings:
            if f.get("severity") in ("error", "warning"):
                print(f"  [{f['severity'].upper()}] {f['message']}")

    if errors > 0:
        return 1
    if args.strict and warnings > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
