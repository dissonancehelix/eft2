from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

def inspect_recast(root: Path | None = None) -> dict[str, Any]:
    root = root or Path(".")
    candidates = ["recast", "RecastDemo", "recast-cli"]
    found = []
    for candidate in candidates:
        path = shutil.which(candidate)
        if path:
            found.append({"name": candidate, "path": path})
    source_candidates = []
    for name in ["recastnavigation-main", "recastnavigation", "Recast", "Recast Navigation"]:
        path = root / name
        if path.exists():
            source_candidates.append({
                "name": name,
                "path": _rel(path),
                "has_recast": (path / "Recast").exists(),
                "has_detour": (path / "Detour").exists(),
                "has_demo": (path / "RecastDemo").exists(),
            })
    if found:
        status = "binary_available_pending_wiring"
    elif source_candidates:
        status = "source_available_pending_build"
    else:
        status = "pending_recast_integration"
    return {
        "available": bool(found),
        "binaries": found,
        "source_references": source_candidates,
        "status": status,
        "learned_integration_shape": {
            "input_required": "triangle mesh exported from VMF brush geometry",
            "build_flow": [
                "compute navmesh bounds from exported geometry",
                "rasterize triangles into a heightfield",
                "filter walkable spans by slope, height, radius, and climb",
                "partition walkable regions",
                "build contours and polygon mesh",
                "initialize Detour navmesh and query layer",
            ],
            "from_reference": "recastnavigation-main README/Docs/RecastDemo source, when present",
        },
        "needed_next": [
            "replace AABB placeholder OBJ with real triangulated VMF brush mesh export",
            "prefer s&box Scene.NavMesh/NavMeshAgent APIs for in-game bots once EFT2 scenes exist",
            "feed s&box/Recast path queries back into route_graph.json and line_of_sight.json without faking metrics",
        ],
    }


def export_intermediate(map_name: str, map_dir: Path, world_solids: list[dict[str, Any]], brush_entities: list[dict[str, Any]]) -> dict[str, Any]:
    export_path = map_dir / "Analysis" / "recast_geometry.obj"
    vertices = []
    faces = []
    for solid in world_solids[:500]:
        mesh = solid.get("mesh") or {}
        triangles = mesh.get("triangles", [])
        if not triangles:
            continue
        for tri in triangles:
            start = len(vertices) + 1
            vertices.extend(tri)
            faces.append([start, start + 1, start + 2])
    lines = [f"# Recast-friendly brush-plane triangle geometry for {map_name}"]
    for v in vertices:
        lines.append(f"v {v[0]} {v[1]} {v[2]}")
    for f in faces:
        lines.append("f " + " ".join(str(i) for i in f))
    export_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {
        "geometry_exported": str(export_path).replace("\\", "/"),
        "export_format": "obj_brush_plane_triangles",
        "exported_vertices": len(vertices),
        "exported_faces": len(faces),
        "note": "Triangle export reconstructed from convex VMF brush planes. This is suitable as a stronger offline Recast/s&box-nav preview input, but should still be checked against Source/s&box collision after port.",
    }


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(Path.cwd())).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")
