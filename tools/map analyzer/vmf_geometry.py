from __future__ import annotations

import math
from typing import Any

EPSILON = 0.01


def bounds_from_solids(solids: list[dict[str, Any]], origin: list[float] | None = None) -> dict[str, Any] | None:
    points: list[list[float]] = []
    for solid in solids:
        for side in solid.get("sides", []):
            points.extend(side.get("plane_points", []))
    if not points:
        return None
    if origin:
        points = [[p[0] + origin[0], p[1] + origin[1], p[2] + origin[2]] for p in points]
    mins = [min(p[i] for p in points) for i in range(3)]
    maxs = [max(p[i] for p in points) for i in range(3)]
    size = [maxs[i] - mins[i] for i in range(3)]
    center = [(mins[i] + maxs[i]) / 2 for i in range(3)]
    volume = size[0] * size[1] * size[2]
    warnings = []
    if len(points) < 8:
        warnings.append("Bounds inferred from fewer than 8 plane points; precision is limited.")
    return {
        "min": mins,
        "max": maxs,
        "center": center,
        "size": size,
        "z_range": [mins[2], maxs[2]],
        "aabb_volume": volume,
        "source_point_count": len(points),
        "warnings": warnings,
    }


def build_solid_mesh(solid: dict[str, Any]) -> dict[str, Any]:
    planes = [_plane_from_points(side.get("plane_points", []), side.get("id")) for side in solid.get("sides", [])]
    planes = [plane for plane in planes if plane]
    warnings = []
    if len(planes) < 4:
        return {"status": "failed", "vertices": [], "faces": [], "triangles": [], "warnings": ["Solid has fewer than 4 valid planes."]}

    candidates = _plane_intersections(planes)
    inside = _inside_points(candidates, planes)
    orientation = "vmf_plane_order"
    if len(inside) < 4:
        flipped = [{**plane, "normal": [-v for v in plane["normal"]], "distance": -plane["distance"]} for plane in planes]
        flipped_inside = _inside_points(candidates, flipped)
        if len(flipped_inside) > len(inside):
            planes = flipped
            inside = flipped_inside
            orientation = "flipped_plane_order"
    vertices = _dedupe_points(inside)
    if len(vertices) < 4:
        return {
            "status": "failed",
            "vertices": vertices,
            "faces": [],
            "triangles": [],
            "warnings": ["Could not reconstruct convex brush vertices from side planes."],
        }

    faces = []
    triangles = []
    for plane in planes:
        face_vertices = [v for v in vertices if abs(_dot(plane["normal"], v) - plane["distance"]) <= 0.2]
        face_vertices = _dedupe_points(face_vertices)
        if len(face_vertices) < 3:
            continue
        ordered = _sort_face_vertices(face_vertices, plane["normal"])
        start_index = len(triangles)
        for i in range(1, len(ordered) - 1):
            triangles.append([ordered[0], ordered[i], ordered[i + 1]])
        faces.append({
            "side_id": plane["side_id"],
            "vertex_count": len(ordered),
            "vertices": ordered,
            "triangle_count": len(triangles) - start_index,
        })

    if not triangles:
        warnings.append("Brush vertices were found, but no faces could be triangulated.")
    bounds = bounds_from_points(vertices)
    return {
        "status": "ok" if triangles else "partial",
        "orientation": orientation,
        "vertices": vertices,
        "faces": faces,
        "triangles": triangles,
        "bounds": bounds,
        "warnings": warnings,
    }


def build_world_mesh(world_solids: list[dict[str, Any]]) -> dict[str, Any]:
    solids = []
    triangle_count = 0
    failed = 0
    partial = 0
    for solid in world_solids:
        mesh = build_solid_mesh(solid)
        solid["mesh"] = mesh
        status = mesh.get("status")
        if status == "failed":
            failed += 1
        elif status == "partial":
            partial += 1
        triangle_count += len(mesh.get("triangles", []))
        solids.append({
            "solid_id": solid.get("id"),
            "status": status,
            "vertex_count": len(mesh.get("vertices", [])),
            "face_count": len(mesh.get("faces", [])),
            "triangle_count": len(mesh.get("triangles", [])),
            "bounds": mesh.get("bounds"),
            "warnings": mesh.get("warnings", []),
        })
    return {
        "status": "brush_plane_mesh",
        "solid_count": len(world_solids),
        "reconstructed_solids": sum(1 for item in solids if item["status"] == "ok"),
        "partial_solids": partial,
        "failed_solids": failed,
        "triangle_count": triangle_count,
        "solids": solids,
        "warnings": ["Meshes are reconstructed from convex VMF brush planes; displacement and complex prop geometry are not included."],
    }


def bounds_from_points(points: list[list[float]]) -> dict[str, Any] | None:
    if not points:
        return None
    mins = [min(p[i] for p in points) for i in range(3)]
    maxs = [max(p[i] for p in points) for i in range(3)]
    size = [maxs[i] - mins[i] for i in range(3)]
    center = [(mins[i] + maxs[i]) / 2 for i in range(3)]
    return {
        "min": mins,
        "max": maxs,
        "center": center,
        "size": size,
        "z_range": [mins[2], maxs[2]],
        "aabb_volume": size[0] * size[1] * size[2],
        "source_point_count": len(points),
        "warnings": [],
    }


def distance2(a: list[float], b: list[float]) -> float:
    return sum((a[i] - b[i]) ** 2 for i in range(3))


def aabb_triangles(bounds: dict[str, Any]) -> tuple[list[list[float]], list[list[int]]]:
    mn = bounds["min"]
    mx = bounds["max"]
    verts = [
        [mn[0], mn[1], mn[2]],
        [mx[0], mn[1], mn[2]],
        [mx[0], mx[1], mn[2]],
        [mn[0], mx[1], mn[2]],
        [mn[0], mn[1], mx[2]],
        [mx[0], mn[1], mx[2]],
        [mx[0], mx[1], mx[2]],
        [mn[0], mx[1], mx[2]],
    ]
    tris = [
        [0, 1, 2], [0, 2, 3],
        [4, 6, 5], [4, 7, 6],
        [0, 4, 5], [0, 5, 1],
        [1, 5, 6], [1, 6, 2],
        [2, 6, 7], [2, 7, 3],
        [3, 7, 4], [3, 4, 0],
    ]
    return verts, tris


def mesh_segment_hits(start: list[float], end: list[float], solids: list[dict[str, Any]], limit: int = 25) -> list[dict[str, Any]]:
    hits = []
    direction = [end[i] - start[i] for i in range(3)]
    for solid in solids:
        mesh = solid.get("mesh") or {}
        triangles = mesh.get("triangles", [])
        if not triangles:
            continue
        for tri in triangles:
            distance = _segment_triangle_distance(start, direction, tri)
            if distance is None:
                continue
            hits.append({
                "solid_id": solid.get("id"),
                "distance_fraction": distance,
                "sample_triangle": tri,
            })
            break
        if len(hits) >= limit:
            break
    return sorted(hits, key=lambda item: item["distance_fraction"])


def segment_intersects_aabb(start: list[float], end: list[float], bounds: dict[str, Any]) -> bool:
    t_min = 0.0
    t_max = 1.0
    mn = bounds["min"]
    mx = bounds["max"]
    direction = [end[i] - start[i] for i in range(3)]
    for axis in range(3):
        if math.isclose(direction[axis], 0.0, abs_tol=1e-9):
            if start[axis] < mn[axis] or start[axis] > mx[axis]:
                return False
            continue
        inv = 1.0 / direction[axis]
        t1 = (mn[axis] - start[axis]) * inv
        t2 = (mx[axis] - start[axis]) * inv
        if t1 > t2:
            t1, t2 = t2, t1
        t_min = max(t_min, t1)
        t_max = min(t_max, t2)
        if t_min > t_max:
            return False
    return True


def segment_aabb_hits(start: list[float], end: list[float], solids: list[dict[str, Any]], limit: int = 25) -> list[dict[str, Any]]:
    hits = []
    for solid in solids:
        bounds = solid.get("bounds")
        if not bounds:
            continue
        if segment_intersects_aabb(start, end, bounds):
            hits.append({
                "solid_id": solid.get("id"),
                "center": bounds.get("center"),
                "size": bounds.get("size"),
            })
            if len(hits) >= limit:
                break
    return hits


def _plane_from_points(points: list[list[float]], side_id: Any) -> dict[str, Any] | None:
    if len(points) < 3:
        return None
    a, b, c = points[:3]
    normal = _cross(_sub(b, a), _sub(c, a))
    length = math.sqrt(_dot(normal, normal))
    if length <= 1e-9:
        return None
    normal = [normal[i] / length for i in range(3)]
    return {"normal": normal, "distance": _dot(normal, a), "side_id": side_id}


def _plane_intersections(planes: list[dict[str, Any]]) -> list[list[float]]:
    points = []
    for i in range(len(planes)):
        for j in range(i + 1, len(planes)):
            for k in range(j + 1, len(planes)):
                point = _intersect_three_planes(planes[i], planes[j], planes[k])
                if point:
                    points.append(point)
    return points


def _intersect_three_planes(a: dict[str, Any], b: dict[str, Any], c: dict[str, Any]) -> list[float] | None:
    n1, n2, n3 = a["normal"], b["normal"], c["normal"]
    denom = _dot(n1, _cross(n2, n3))
    if abs(denom) < 1e-7:
        return None
    term1 = _mul(_cross(n2, n3), a["distance"])
    term2 = _mul(_cross(n3, n1), b["distance"])
    term3 = _mul(_cross(n1, n2), c["distance"])
    return _mul(_add(_add(term1, term2), term3), 1.0 / denom)


def _inside_points(points: list[list[float]], planes: list[dict[str, Any]]) -> list[list[float]]:
    inside = []
    for point in points:
        if all(_dot(plane["normal"], point) - plane["distance"] <= EPSILON for plane in planes):
            inside.append(point)
    return inside


def _dedupe_points(points: list[list[float]], ndigits: int = 4) -> list[list[float]]:
    seen = {}
    for point in points:
        key = tuple(round(v, ndigits) for v in point)
        seen[key] = [float(key[0]), float(key[1]), float(key[2])]
    return list(seen.values())


def _sort_face_vertices(points: list[list[float]], normal: list[float]) -> list[list[float]]:
    center = [sum(p[i] for p in points) / len(points) for i in range(3)]
    axis = [1.0, 0.0, 0.0] if abs(normal[0]) < 0.9 else [0.0, 1.0, 0.0]
    u = _normalize(_cross(normal, axis))
    v = _cross(normal, u)
    return sorted(points, key=lambda p: math.atan2(_dot(_sub(p, center), v), _dot(_sub(p, center), u)))


def _segment_triangle_distance(start: list[float], direction: list[float], tri: list[list[float]]) -> float | None:
    v0, v1, v2 = tri
    edge1 = _sub(v1, v0)
    edge2 = _sub(v2, v0)
    h = _cross(direction, edge2)
    det = _dot(edge1, h)
    if abs(det) < 1e-7:
        return None
    inv_det = 1.0 / det
    s = _sub(start, v0)
    u = inv_det * _dot(s, h)
    if u < -1e-6 or u > 1.0 + 1e-6:
        return None
    q = _cross(s, edge1)
    v = inv_det * _dot(direction, q)
    if v < -1e-6 or u + v > 1.0 + 1e-6:
        return None
    t = inv_det * _dot(edge2, q)
    if t < -1e-6 or t > 1.0 + 1e-6:
        return None
    return t


def _sub(a: list[float], b: list[float]) -> list[float]:
    return [a[i] - b[i] for i in range(3)]


def _add(a: list[float], b: list[float]) -> list[float]:
    return [a[i] + b[i] for i in range(3)]


def _mul(a: list[float], scalar: float) -> list[float]:
    return [a[i] * scalar for i in range(3)]


def _dot(a: list[float], b: list[float]) -> float:
    return sum(a[i] * b[i] for i in range(3))


def _cross(a: list[float], b: list[float]) -> list[float]:
    return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]


def _normalize(a: list[float]) -> list[float]:
    length = math.sqrt(_dot(a, a))
    if length <= 1e-9:
        return [0.0, 0.0, 0.0]
    return [a[i] / length for i in range(3)]


def cluster_points(items: list[dict[str, Any]], radius: float = 768.0) -> list[dict[str, Any]]:
    clusters: list[dict[str, Any]] = []
    for item in items:
        origin = item.get("origin")
        if not origin:
            continue
        best = None
        best_dist = None
        for cluster in clusters:
            d = distance2(origin, cluster["center"])
            if d <= radius * radius and (best_dist is None or d < best_dist):
                best = cluster
                best_dist = d
        if best is None:
            clusters.append({"items": [item], "center": list(origin)})
        else:
            best["items"].append(item)
            n = len(best["items"])
            best["center"] = [(best["center"][i] * (n - 1) + origin[i]) / n for i in range(3)]
    output = []
    for idx, cluster in enumerate(clusters, start=1):
        ids = [item.get("id") for item in cluster["items"]]
        output.append({
            "cluster_id": idx,
            "center": cluster["center"],
            "count": len(cluster["items"]),
            "source_entity_ids": ids,
        })
    return output
