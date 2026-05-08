from __future__ import annotations

from pathlib import Path
from typing import Any

from schemas import MARKDOWN_BANNER, dumps


class OutputWriter:
    """Resolves all writes against an output root and refuses anything else."""

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir.resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _resolve(self, name: str) -> Path:
        target = (self.output_dir / name).resolve()
        if self.output_dir not in target.parents and target != self.output_dir:
            raise ValueError(f"refusing to write outside output dir: {target}")
        return target

    def write_json(self, name: str, data: dict[str, Any]) -> Path:
        target = self._resolve(name)
        target.write_text(dumps(data), encoding="utf-8")
        return target

    def write_md(self, name: str, body: str, *, with_banner: bool = True) -> Path:
        target = self._resolve(name)
        text = (MARKDOWN_BANNER + "\n" + body.rstrip() + "\n") if with_banner else (body.rstrip() + "\n")
        target.write_text(text, encoding="utf-8")
        return target


def safe_read_text(path: Path, max_bytes: int = 1_000_000) -> tuple[str | None, str | None]:
    """Returns (text, warning). text is None if skipped."""
    try:
        size = path.stat().st_size
    except OSError as e:
        return None, f"stat_failed:{path}:{e}"
    if size > max_bytes:
        return None, f"file_too_large:{path}:{size}"
    try:
        return path.read_text(encoding="utf-8", errors="replace"), None
    except OSError as e:
        return None, f"read_failed:{path}:{e}"


BINARY_EXTS = {
    ".vmf", ".vmx", ".vtf", ".vmt", ".mdl", ".bsp", ".phy", ".vvd",
    ".mp4", ".mov", ".mkv", ".avi", ".webm",
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tga",
    ".zip", ".7z", ".tar", ".gz", ".rar",
    ".dll", ".exe", ".so", ".dylib", ".pdb",
    ".wav", ".mp3", ".ogg",
}


def is_binary(path: Path) -> bool:
    return path.suffix.lower() in BINARY_EXTS
