from __future__ import annotations

from typing import Any


def summarize_spatial_backend(world_solids: list[dict[str, Any]], entities: list[dict[str, Any]]) -> dict[str, Any]:
    bounded_world = sum(1 for solid in world_solids if solid.get("bounds"))
    bounded_entities = sum(1 for ent in entities if ent.get("bounds"))
    meshed_world = sum(1 for solid in world_solids if (solid.get("mesh") or {}).get("status") == "ok")
    triangle_faces = sum(len((solid.get("mesh") or {}).get("triangles", [])) for solid in world_solids)
    return {
        "status": "vmf_brush_plane_mesh",
        "world_solids_with_bounds": bounded_world,
        "world_solids_with_mesh": meshed_world,
        "entities_with_bounds": bounded_entities,
        "brush_mesh_triangles": triangle_faces,
        "mined_backend_lessons": {
            "recast": "needs triangle mesh input before reliable navmesh/path queries",
            "sbox": "uses Recast-style Scene.NavMesh, NavMeshAgent, NavMeshLink, and navmesh queries for in-game bots",
            "blender": "spatial reads should be ray/BVH-style probes over mesh geometry, not raw entity counts",
        },
        "warnings": [
            "Spatial perception now uses convex brush-plane triangles, but displacements, props, and final s&box physics collision are not represented yet."
        ],
    }
