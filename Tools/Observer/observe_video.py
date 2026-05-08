"""Tools/Observer — EFT2 media observation tool.

STATUS: skeleton only. Frame extraction and CV passes are not yet implemented.

Run from repo root:

    python "Tools/Observer/observe_video.py" --help

When implemented, Observer will convert videos, screenshots, keyframes, and
play captures into LLM-readable observation artifacts written to each map
domain's Virtual Perception/ folder.

See Tools/Observer/observation_schema.md for the output schema.
"""
from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="observe_video",
        description=(
            "EFT2 Observer — convert match media into LLM-readable observation artifacts.\n\n"
            "STATUS: skeleton only — implementation pending.\n\n"
            "Observer will extract keyframes from videos and screenshots, tag them with\n"
            "EFT mechanic labels, and write structured JSON to the target map domain's\n"
            "Virtual Perception/ folder. It does not mutate source media."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--input", "-i", metavar="PATH",
        help="Path to a video file or screenshot directory to process.",
    )
    p.add_argument(
        "--map", "-m", metavar="MAP_NAME",
        help="Canonical map name (e.g. 'Slam Dunk'). Output goes to Maps/<MAP>/Virtual Perception/.",
    )
    p.add_argument(
        "--output", "-o", metavar="DIR",
        help="Override output directory (default: Maps/<MAP>/Virtual Perception/).",
    )
    p.add_argument(
        "--interval", type=float, default=2.0, metavar="SECONDS",
        help="Keyframe extraction interval in seconds (default: 2.0). Unused until implemented.",
    )
    p.add_argument(
        "--ffmpeg", metavar="PATH",
        help="Path to ffmpeg.exe (default: Tools/ffmpeg.exe). Unused until implemented.",
    )
    p.add_argument(
        "--dry-run", action="store_true",
        help="Print what would be done without writing any files.",
    )
    p.add_argument(
        "--verbose", action="store_true",
        help="Print progress detail.",
    )

    args = p.parse_args(argv)

    print("Tools/Observer: skeleton only — implementation pending.", file=sys.stderr)
    print(
        "When implemented, Observer will extract keyframes and emit structured observation\n"
        "JSON to Maps/<map>/Virtual Perception/ per observation_schema.md.",
        file=sys.stderr,
    )
    print("See Tools/Observer/README.md for the full design.", file=sys.stderr)

    if args.input or args.map:
        print(
            "\nArguments received (not processed — implementation pending):",
            file=sys.stderr,
        )
        if args.input:
            print(f"  --input  {args.input}", file=sys.stderr)
        if args.map:
            print(f"  --map    {args.map}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
