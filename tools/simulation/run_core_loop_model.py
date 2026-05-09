"""Run the deterministic EFT2 core-loop rule model."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from core_loop_model import CoreLoopModel, result_to_dict


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the EFT2 core-loop rule model without bots or real-map conversion.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument("--output", help="Optional output JSON path.")
    args = parser.parse_args()

    result = CoreLoopModel().run_scripted_core_loop()
    data = result_to_dict(result)

    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print("EFT2 core-loop model")
        print(f"Score: red_rhinos={data['score']['red_rhinos']} blue_bulls={data['score']['blue_bulls']}")
        print("Events:")
        for event in data["events"]:
            print(f"  {event['tick']:04d} {event['event']} {event['payload']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
