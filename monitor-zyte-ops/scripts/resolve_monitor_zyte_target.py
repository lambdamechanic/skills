#!/usr/bin/env python3
"""Resolve Monitor Zyte targets into deterministic metadata."""

from __future__ import annotations

import argparse
import json
import sys

TARGETS = {
    "staging": {
        "project_id": 831071,
        "dashboard_url": "https://app.zyte.com/p/831071",
        "periodic_jobs_url": "https://app.zyte.com/p/831071/periodic",
        "shub_target": "staging",
    },
    "production": {
        "project_id": 251988,
        "dashboard_url": "https://app.zyte.com/p/251988",
        "periodic_jobs_url": "https://app.zyte.com/p/251988/periodic",
        "shub_target": "production",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resolve Monitor Zyte staging/production metadata."
    )
    parser.add_argument("target", choices=sorted(TARGETS))
    parser.add_argument(
        "--field",
        choices=[
            "project_id",
            "dashboard_url",
            "periodic_jobs_url",
            "shub_target",
            "working_directory",
        ],
        help="Print a single field instead of the full JSON object.",
    )
    return parser.parse_args()


def build_payload(target: str) -> dict[str, object]:
    target_info = TARGETS[target]
    return {
        "target": target,
        **target_info,
        "working_directory": "monitor_project",
        "scrapinghub_alias": target_info["shub_target"],
        "requires_explicit_production_write_request": target == "production",
    }


def main() -> int:
    args = parse_args()
    payload = build_payload(args.target)
    if args.field:
        value = payload[args.field]
        if isinstance(value, str):
            print(value)
        else:
            print(json.dumps(value))
        return 0

    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
