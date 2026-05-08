from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


TOKEN_RE = re.compile(r'"(?:\\.|[^"\\])*"|[{}]|[^\s{}"]+')


@dataclass
class VmfNode:
    name: str
    keyvalues: dict[str, Any] = field(default_factory=dict)
    children: list["VmfNode"] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "keyvalues": self.keyvalues,
            "children": [child.to_dict() for child in self.children],
        }


def _unquote(token: str) -> str:
    if len(token) >= 2 and token[0] == '"' and token[-1] == '"':
        return token[1:-1].replace('\\"', '"')
    return token


def parse_vmf(path: Path) -> VmfNode:
    text = path.read_text(encoding="utf-8", errors="replace")
    tokens = [_unquote(match.group(0)) for match in TOKEN_RE.finditer(text)]
    root = VmfNode("root")
    stack = [root]
    pending_block: str | None = None
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token == "{":
            if pending_block is None:
                pending_block = "anonymous"
            node = VmfNode(pending_block)
            stack[-1].children.append(node)
            stack.append(node)
            pending_block = None
            i += 1
        elif token == "}":
            if len(stack) > 1:
                stack.pop()
            pending_block = None
            i += 1
        else:
            if i + 1 < len(tokens) and tokens[i + 1] == "{":
                pending_block = token
                i += 1
            elif i + 1 < len(tokens):
                key = token
                value = tokens[i + 1]
                existing = stack[-1].keyvalues.get(key)
                if existing is None:
                    stack[-1].keyvalues[key] = value
                elif isinstance(existing, list):
                    existing.append(value)
                else:
                    stack[-1].keyvalues[key] = [existing, value]
                i += 2
            else:
                i += 1
    return root


def nodes_named(node: VmfNode, name: str) -> list[VmfNode]:
    out = []
    if node.name == name:
        out.append(node)
    for child in node.children:
        out.extend(nodes_named(child, name))
    return out


def extract_entities(root: VmfNode) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    entities: list[dict[str, Any]] = []
    world_solids: list[dict[str, Any]] = []
    for child in root.children:
        if child.name == "world":
            world_solids = [_solid_to_dict(solid) for solid in child.children if solid.name == "solid"]
        elif child.name == "entity":
            entities.append(_entity_to_dict(child))
    return entities, world_solids


def _entity_to_dict(node: VmfNode) -> dict[str, Any]:
    solids = [_solid_to_dict(child) for child in node.children if child.name == "solid"]
    outputs = []
    for child in node.children:
        if child.name == "connections":
            outputs.extend(_connections_to_outputs(child))
    return {
        "id": _maybe_int(node.keyvalues.get("id")),
        "classname": node.keyvalues.get("classname", ""),
        "targetname": node.keyvalues.get("targetname"),
        "origin": parse_vector(node.keyvalues.get("origin")),
        "angles": parse_vector(node.keyvalues.get("angles")),
        "keyvalues": dict(node.keyvalues),
        "outputs": outputs,
        "solids": solids,
    }


def _solid_to_dict(node: VmfNode) -> dict[str, Any]:
    return {
        "id": _maybe_int(node.keyvalues.get("id")),
        "keyvalues": dict(node.keyvalues),
        "sides": [_side_to_dict(child) for child in node.children if child.name == "side"],
    }


def _side_to_dict(node: VmfNode) -> dict[str, Any]:
    plane = node.keyvalues.get("plane")
    return {
        "id": _maybe_int(node.keyvalues.get("id")),
        "plane": plane,
        "plane_points": parse_plane_points(plane),
        "material": node.keyvalues.get("material"),
        "keyvalues": dict(node.keyvalues),
    }


def _connections_to_outputs(node: VmfNode) -> list[dict[str, str]]:
    outputs = []
    for key, value in node.keyvalues.items():
        values = value if isinstance(value, list) else [value]
        for raw in values:
            parts = str(raw).split(",")
            outputs.append({"output": key, "raw": raw, "parts": parts})
    return outputs


def parse_vector(raw: Any) -> list[float] | None:
    if raw is None:
        return None
    parts = str(raw).strip().split()
    if len(parts) < 3:
        return None
    try:
        return [float(parts[0]), float(parts[1]), float(parts[2])]
    except ValueError:
        return None


def parse_plane_points(raw: Any) -> list[list[float]]:
    if not raw:
        return []
    groups = re.findall(r"\(([^)]+)\)", str(raw))
    points: list[list[float]] = []
    for group in groups:
        try:
            vals = [float(part) for part in group.split()]
        except ValueError:
            continue
        if len(vals) == 3:
            points.append(vals)
    return points


def _maybe_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None

