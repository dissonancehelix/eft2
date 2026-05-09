from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

GENERATOR = "tools/map analyzer"
SCHEMA_VERSION = 1


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve())).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def metadata(map_name: str, source_vmf: Path, original_filename: str | None = None) -> dict[str, Any]:
    return {
        "generated_by": GENERATOR,
        "schema_version": SCHEMA_VERSION,
        "map": map_name,
        "source_vmf": str(source_vmf).replace("\\", "/"),
        "original_filename": original_filename,
        "generated_at": utc_now(),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write_text(path, json.dumps(data, indent=2, sort_keys=False) + "\n")


def write_md(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write_text(path, content.rstrip() + "\n")


def _atomic_write_text(path: Path, content: str) -> None:
    temp = path.with_name(f".{path.name}.tmp")
    temp.write_text(content, encoding="utf-8")
    last_error: OSError | None = None
    for attempt in range(5):
        try:
            temp.replace(path)
            return
        except OSError as exc:
            last_error = exc
            time.sleep(0.1 * (attempt + 1))
    try:
        if path.exists():
            path.unlink()
        temp.replace(path)
        return
    except OSError as exc:
        last_error = exc
    raise last_error
