from __future__ import annotations

import argparse
import traceback
from pathlib import Path

from analyze_map import analyze_map
from exporters import write_md


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze every organized EFT map domain.")
    parser.add_argument("--maps-root", default="Maps")
    args = parser.parse_args()
    root = Path(args.maps_root)
    failures = 0
    for map_dir in sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith("_")):
        try:
            analyze_map(map_dir)
        except Exception as exc:
            failures += 1
            report = f"# Error Report\n\n`{type(exc).__name__}`: {exc}\n\n```text\n{traceback.format_exc()}\n```\n"
            write_md(map_dir / "Analysis" / "error_report.md", report)
            print(f"FAILED {map_dir}: {exc}")
    print(f"Batch complete with {failures} failure(s).")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
