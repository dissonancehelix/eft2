from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any


def inspect_geometry_backends(root: Path | None = None) -> dict[str, Any]:
    root = root or Path(".")
    found = []
    source_candidates = {
        "blender-main": {
            "backend": "Blender",
            "role": "temporary source reference for mesh/raycast/spatial-processing ideas",
            "durable_tool_domain": False,
        },
        "recastnavigation-main": {
            "backend": "Recast/Detour",
            "role": "temporary source reference for navmesh and path-query integration",
            "durable_tool_domain": False,
        },
        "Blender": {
            "backend": "Blender",
            "role": "temporary source/reference folder",
            "durable_tool_domain": False,
        },
        "Recast": {
            "backend": "Recast/Detour",
            "role": "temporary source/reference folder",
            "durable_tool_domain": False,
        },
        "Recast Navigation": {
            "backend": "Recast/Detour",
            "role": "temporary source/reference folder",
            "durable_tool_domain": False,
        },
        "recastnavigation": {
            "backend": "Recast/Detour",
            "role": "temporary source/reference folder",
            "durable_tool_domain": False,
        },
    }
    for name, info in source_candidates.items():
        path = root / name
        if path.exists():
            found.append({**info, "name": name, "path": _rel(path)})

    executables = []
    for name in ["blender", "recast", "RecastDemo", "recast-cli"]:
        path = shutil.which(name)
        if path:
            executables.append({"name": name, "path": path})

    if executables:
        status = "optional_backend_binary_available"
    elif found:
        status = "source_references_found_pending_integration"
    else:
        status = "vmf_only"

    return {
        "status": status,
        "source_references": found,
        "executables": executables,
        "active_geometry_mode": "vmf_brush_plane_mesh",
        "policy": "Optional geometry/navigation references are internal inputs only; Tools/Map Analyzer remains the durable project-owned interface.",
        "notes": [
            "Blender source was not copied or required by the analyzer.",
            "Recast/Detour source was inspected as the intended navmesh/path-query direction, but no navmesh build is active yet.",
            "Current geometry reconstructs convex brush meshes from VMF side planes, then falls back to bounds only where reconstruction fails.",
        ],
    }


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(Path.cwd())).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")
