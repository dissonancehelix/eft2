"""TOOLS_INDEX.json — inventory Tools/, flag missing recommended tools."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from exporters import safe_read_text
from schemas import IndexEnvelope, rel

RECOMMENDED = [
    "Indexer",
    "Map Analyzer",
    "Observer",
    "Contract Validator",
    "Scenario Harness",
    "Telemetry",
    "Simulation",
]

DOCSTRING_RE = re.compile(r'^\s*(?:"""|\'\'\')(.*?)(?:"""|\'\'\')', re.DOTALL)


def _first_doc_line(path: Path) -> str | None:
    text, _ = safe_read_text(path, max_bytes=200_000)
    if not text:
        return None
    m = DOCSTRING_RE.match(text)
    if not m:
        return None
    return m.group(1).strip().splitlines()[0] if m.group(1).strip() else None


def _readme_first_section(path: Path) -> str | None:
    text, _ = safe_read_text(path, max_bytes=200_000)
    if not text:
        return None
    lines = []
    for line in text.splitlines():
        if line.strip().startswith("#") and lines:
            break
        lines.append(line)
        if len(lines) > 20:
            break
    return "\n".join(lines).strip() or None


def _index_tool(tool_dir: Path, root: Path) -> dict[str, Any]:
    py_modules = []
    for py in sorted(tool_dir.glob("*.py")):
        py_modules.append({
            "path": rel(py, root),
            "first_docstring_line": _first_doc_line(py),
        })
    output_dir = tool_dir / "Output"
    return {
        "name": tool_dir.name,
        "path": rel(tool_dir, root),
        "readme": rel(tool_dir / "README.md", root) if (tool_dir / "README.md").exists() else None,
        "readme_summary": _readme_first_section(tool_dir / "README.md") if (tool_dir / "README.md").exists() else None,
        "python_module_count": len(py_modules),
        "python_modules": py_modules,
        "has_output_dir": output_dir.is_dir(),
        "output_dir": rel(output_dir, root) if output_dir.is_dir() else None,
    }


def build(root: Path, env: IndexEnvelope) -> dict[str, Any]:
    tools_root = root / "tools"
    if not tools_root.is_dir():
        env.warn("tools_dir_missing")
        return env.wrap({"present": False, "tools": []})

    present_names: list[str] = []
    tools: list[dict[str, Any]] = []
    for sub in sorted(tools_root.iterdir()):
        if sub.is_dir():
            present_names.append(sub.name)
            tools.append(_index_tool(sub, root))

    missing = [n for n in RECOMMENDED if n not in present_names]
    return env.wrap({
        "tools_root": rel(tools_root, root),
        "tool_count": len(tools),
        "present_tools": present_names,
        "missing_recommended_tools": missing,
        "recommended_status": [
            {"name": n, "status": "present" if n in present_names else "pending"}
            for n in RECOMMENDED
        ],
        "tools": tools,
    })
