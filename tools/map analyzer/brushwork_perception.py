from __future__ import annotations

import math
from typing import Any

from vmf_geometry import build_solid_mesh


def build_brushwork_perception(world_solids: list[dict[str, Any]], brush_entities: list[dict[str, Any]]) -> dict[str, Any]:
    world_items = [_solid_item(solid, "worldspawn", None, None) for solid in world_solids]
    entity_items: list[dict[str, Any]] = []
    for ent in brush_entities:
        classname = ent.get("classname")
        targetname = ent.get("targetname")
        for solid in ent.get("solids", []):
            if not solid.get("mesh"):
                solid["mesh"] = build_solid_mesh(solid)
            entity_items.append(_solid_item(solid, classname, ent.get("id"), targetname))

    all_items = world_items + entity_items
    surfaces = [surface for item in all_items for surface in item["surfaces"]]
    ramps = [s for s in surfaces if s["surface_type"] == "ramp"]
    floors = [s for s in surfaces if s["surface_type"] == "floor"]
    walls = [s for s in surfaces if s["surface_type"] == "wall"]
    platforms = _platform_candidates(all_items)

    return {
        "status": "vmf_brushwork_perception",
        "summary": {
            "world_solids": len(world_items),
            "brush_entity_solids": len(entity_items),
            "reconstructed_solids": sum(1 for item in all_items if item["mesh_status"] == "ok"),
            "surface_count": len(surfaces),
            "floor_surfaces": len(floors),
            "ramp_surfaces": len(ramps),
            "wall_surfaces": len(walls),
            "platform_candidates": len(platforms),
            "brush_entity_classes": _count_by(item["owner_class"] for item in entity_items),
        },
        "world_solids": world_items,
        "brush_entity_solids": entity_items,
        "ramp_surfaces": sorted(ramps, key=lambda s: (s.get("center") or [0, 0, 0])[2]),
        "walkable_surfaces": sorted(floors + ramps, key=lambda s: (s.get("center") or [0, 0, 0])[2]),
        "platform_candidates": platforms,
        "material_counts": _count_by(s.get("material") or "unknown" for s in surfaces),
        "limits": [
            "Brushwork is reconstructed from convex VMF side planes.",
            "Displacements, prop collision, dynamic entity state, and final s&box collision are not represented.",
            "Brush entity origins/pivots may need Hammer validation where Source stores transformed brush solids.",
        ],
    }


def render_brushwork_markdown(map_name: str, perception: dict[str, Any]) -> str:
    summary = perception["summary"]
    lines = [
        f"# {map_name} Brushwork Perception",
        "",
        "Generated from VMF world brushes and brush entities. This is a Hammer-like geometry read, not hand-authored canon.",
        "",
        "## Summary",
        "",
        f"- world solids: {summary['world_solids']}",
        f"- brush entity solids: {summary['brush_entity_solids']}",
        f"- reconstructed solids: {summary['reconstructed_solids']}",
        f"- surfaces: {summary['surface_count']}",
        f"- floor surfaces: {summary['floor_surfaces']}",
        f"- ramp surfaces: {summary['ramp_surfaces']}",
        f"- wall surfaces: {summary['wall_surfaces']}",
        f"- platform candidates: {summary['platform_candidates']}",
        f"- brush entity classes: {summary['brush_entity_classes']}",
        "",
        "## Ramp Surfaces",
        "",
    ]
    ramps = perception.get("ramp_surfaces", [])
    if not ramps:
        lines.append("- none detected")
    for surface in ramps[:40]:
        center = _fmt_vec(surface.get("center"))
        lines.append(
            f"- solid `{surface['solid_id']}` {surface['owner_class']} center {center} "
            f"slope {surface['slope_degrees']:.1f} deg material `{surface.get('material') or 'unknown'}`"
        )

    lines.extend(["", "## Platform Candidates", ""])
    platforms = perception.get("platform_candidates", [])
    if not platforms:
        lines.append("- none detected")
    for item in platforms[:40]:
        center = _fmt_vec((item.get("bounds") or {}).get("center"))
        size = _fmt_vec((item.get("bounds") or {}).get("size"))
        lines.append(
            f"- solid `{item['solid_id']}` {item['owner_class']} center {center} "
            f"size {size} top_z {item.get('top_z'):.1f}"
        )

    lines.extend(["", "## Brush Entities", ""])
    for item in perception.get("brush_entity_solids", [])[:80]:
        center = _fmt_vec((item.get("bounds") or {}).get("center"))
        lines.append(
            f"- `{item['owner_class']}` solid `{item['solid_id']}` entity `{item.get('owner_entity_id')}` "
            f"name `{item.get('targetname') or ''}` center {center} mesh `{item['mesh_status']}`"
        )

    lines.extend(["", "## Limits", ""])
    for limit in perception.get("limits", []):
        lines.append(f"- {limit}")
    return "\n".join(lines) + "\n"


def _solid_item(solid: dict[str, Any], owner_class: str | None, owner_entity_id: Any, targetname: str | None) -> dict[str, Any]:
    mesh = solid.get("mesh") or build_solid_mesh(solid)
    surfaces = _surfaces_for_solid(solid, mesh, owner_class, owner_entity_id, targetname)
    bounds = mesh.get("bounds") or solid.get("bounds")
    return {
        "solid_id": solid.get("id"),
        "owner_class": owner_class or "unknown",
        "owner_entity_id": owner_entity_id,
        "targetname": targetname,
        "mesh_status": mesh.get("status"),
        "bounds": bounds,
        "surface_types": _count_by(s["surface_type"] for s in surfaces),
        "surfaces": surfaces,
        "warnings": mesh.get("warnings", []),
    }


def _surfaces_for_solid(solid: dict[str, Any], mesh: dict[str, Any], owner_class: str | None, owner_entity_id: Any, targetname: str | None) -> list[dict[str, Any]]:
    side_materials = {side.get("id"): side.get("material") for side in solid.get("sides", [])}
    surfaces = []
    for face in mesh.get("faces", []):
        vertices = face.get("vertices") or []
        normal = _face_normal(vertices)
        if not normal:
            continue
        center = _center(vertices)
        area = _polygon_area(vertices, normal)
        surface_type = _surface_type(normal)
        slope = _slope_degrees(normal)
        surfaces.append({
            "solid_id": solid.get("id"),
            "owner_class": owner_class or "unknown",
            "owner_entity_id": owner_entity_id,
            "targetname": targetname,
            "side_id": face.get("side_id"),
            "material": side_materials.get(face.get("side_id")),
            "surface_type": surface_type,
            "normal": normal,
            "slope_degrees": slope,
            "center": center,
            "area": area,
            "vertex_count": len(vertices),
        })
    return surfaces


def _surface_type(normal: list[float]) -> str:
    z = normal[2]
    if z >= 0.9:
        return "floor"
    if z <= -0.9:
        return "ceiling_or_underside"
    if 0.18 <= z < 0.9:
        return "ramp"
    if -0.18 < z < 0.18:
        return "wall"
    return "steep_underside"


def _slope_degrees(normal: list[float]) -> float:
    z = max(-1.0, min(1.0, normal[2]))
    return math.degrees(math.acos(abs(z)))


def _platform_candidates(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates = []
    for item in items:
        bounds = item.get("bounds")
        if not bounds:
            continue
        size = bounds.get("size") or [0, 0, 0]
        if size[0] < 96 or size[1] < 96:
            continue
        if not any(s["surface_type"] in {"floor", "ramp"} for s in item["surfaces"]):
            continue
        candidates.append({
            "solid_id": item["solid_id"],
            "owner_class": item["owner_class"],
            "owner_entity_id": item.get("owner_entity_id"),
            "targetname": item.get("targetname"),
            "bounds": bounds,
            "top_z": bounds["max"][2],
            "surface_types": item["surface_types"],
        })
    return sorted(candidates, key=lambda i: ((i.get("bounds") or {}).get("center") or [0, 0, 0])[2])


def _face_normal(vertices: list[list[float]]) -> list[float] | None:
    if len(vertices) < 3:
        return None
    a, b, c = vertices[:3]
    normal = _cross(_sub(b, a), _sub(c, a))
    length = math.sqrt(_dot(normal, normal))
    if length <= 1e-9:
        return None
    return [normal[i] / length for i in range(3)]


def _center(points: list[list[float]]) -> list[float]:
    return [sum(p[i] for p in points) / len(points) for i in range(3)]


def _polygon_area(vertices: list[list[float]], normal: list[float]) -> float:
    if len(vertices) < 3:
        return 0.0
    total = [0.0, 0.0, 0.0]
    for i, current in enumerate(vertices):
        nxt = vertices[(i + 1) % len(vertices)]
        total = _add(total, _cross(current, nxt))
    return abs(_dot(total, normal)) * 0.5


def _count_by(values) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: kv[0]))


def _fmt_vec(value: list[float] | None) -> str:
    if not value:
        return "unknown"
    return "(" + ", ".join(f"{v:.1f}" for v in value) + ")"


def _sub(a: list[float], b: list[float]) -> list[float]:
    return [a[i] - b[i] for i in range(3)]


def _add(a: list[float], b: list[float]) -> list[float]:
    return [a[i] + b[i] for i in range(3)]


def _dot(a: list[float], b: list[float]) -> float:
    return sum(a[i] * b[i] for i in range(3))


def _cross(a: list[float], b: list[float]) -> list[float]:
    return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]
