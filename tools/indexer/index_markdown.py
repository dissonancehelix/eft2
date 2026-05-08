"""CONTRACT_INDEX.json — index Markdown contract files."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from exporters import safe_read_text
from schemas import IndexEnvelope, rel

HEADING_RE = re.compile(r"^(#{1,3})\s+(.+?)\s*$", re.MULTILINE)
CONTRACT_ID_RE = re.compile(r"\b([CPMSE]-\d{2,4})\b")
TODO_RE = re.compile(r"\b(TODO|FIXME|NEXT|XXX)\b[:\s]*(.*)", re.IGNORECASE)


def _extract(path: Path, root: Path) -> dict[str, Any] | None:
    text, warn = safe_read_text(path)
    if text is None:
        return {"path": rel(path, root), "skipped": warn}
    headings = [
        {"level": len(m.group(1)), "text": m.group(2)} for m in HEADING_RE.finditer(text)
    ]
    contract_ids = sorted(set(CONTRACT_ID_RE.findall(text)))
    todos: list[dict[str, Any]] = []
    for i, line in enumerate(text.splitlines(), 1):
        m = TODO_RE.search(line)
        if m:
            todos.append({"line": i, "marker": m.group(1).upper(), "text": m.group(2).strip()})
    return {
        "path": rel(path, root),
        "size_bytes": path.stat().st_size,
        "heading_count": len(headings),
        "headings": headings,
        "contract_ids": contract_ids,
        "todo_markers": todos,
    }


def build(root: Path, env: IndexEnvelope) -> dict[str, Any]:
    targets: list[Path] = []
    for name in ("README.md", "AGENTS.md", "PLAN.md"):
        p = root / name
        if p.exists():
            targets.append(p)
    maps_readme = root / "maps" / "README.md"
    if maps_readme.exists():
        targets.append(maps_readme)
    tools_dir = root / "tools"
    if tools_dir.is_dir():
        for sub in sorted(tools_dir.iterdir()):
            if sub.is_dir():
                rdme = sub / "README.md"
                if rdme.exists():
                    targets.append(rdme)
    files = []
    for t in targets:
        try:
            files.append(_extract(t, root))
        except OSError as e:
            env.warn(f"contract_read_failed:{rel(t, root)}:{e}")
    return env.wrap({"files": files, "file_count": len(files)})
