#!/usr/bin/env python3
"""Structured helper for Monitor's Zyte Scrapy Cloud job operations."""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Iterable, Mapping
from typing import Any

APP_ZYTE_API = "https://app.zyte.com/api"
STORAGE_ZYTE_API = "https://storage.zyte.com"
TARGETS = {
    "staging": 831071,
    "production": 251988,
}


class ZyteJobsError(RuntimeError):
    """Raised when the helper cannot complete the requested operation."""


def resolve_api_key() -> str:
    for name in ("SHUB_APIKEY", "SCRAPINGHUB_API_KEY", "ZYTE_API_KEY"):
        raw = os.environ.get(name)
        if raw and raw.strip():
            return raw.strip()
    raise ZyteJobsError(
        "Missing Zyte credentials. Set SHUB_APIKEY, SCRAPINGHUB_API_KEY, or ZYTE_API_KEY first."
    )


def resolve_project_id(project: int | None, target: str | None) -> int:
    if project is not None:
        return project
    if target is not None:
        return TARGETS[target]
    raise ZyteJobsError("Provide either --project or --target.")


def parse_key_value(items: Iterable[str]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            raise ZyteJobsError(f"Expected KEY=VALUE, got {item!r}")
        key, value = item.split("=", 1)
        key = key.strip()
        if not key:
            raise ZyteJobsError(f"Expected non-empty key in {item!r}")
        parsed[key] = value
    return parsed


def parse_job_ref(job: str) -> tuple[int, str]:
    normalized = job.strip().rstrip("/")
    if normalized.startswith("https://app.zyte.com/p/"):
        normalized = normalized.removeprefix("https://app.zyte.com/p/")
    parts = normalized.split("/")
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        raise ZyteJobsError(
            f"Expected full job ref like 831071/7/123, got {job!r}"
        )
    project_id = int(parts[0])
    return project_id, "/".join(parts)


def _request(
    *,
    url: str,
    method: str,
    api_key: str,
    form_fields: list[tuple[str, str]] | None = None,
) -> Any:
    headers = {
        "Authorization": "Basic "
        + base64.b64encode(f"{api_key}:".encode("utf-8")).decode("ascii"),
        "Accept": "application/json",
    }
    data = None
    if form_fields is not None:
        data = urllib.parse.urlencode(form_fields, doseq=True).encode("utf-8")
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise ZyteJobsError(f"{exc.code} {exc.reason}: {body}") from exc
    except urllib.error.URLError as exc:
        raise ZyteJobsError(str(exc.reason)) from exc

    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return body


def jobs_api(
    *,
    endpoint: str,
    method: str,
    api_key: str,
    query: Mapping[str, Any] | None = None,
    form_fields: list[tuple[str, str]] | None = None,
) -> Any:
    url = f"{APP_ZYTE_API}/{endpoint}"
    if query:
        encoded = urllib.parse.urlencode(
            [(key, str(value)) for key, value in query.items() if value is not None],
            doseq=True,
        )
        url = f"{url}?{encoded}"
    return _request(url=url, method=method, api_key=api_key, form_fields=form_fields)


def storage_api(
    *,
    kind: str,
    api_key: str,
    job_ref: str,
    count: int | None,
    start: str | None,
    startafter: str | None,
) -> Any:
    query: list[tuple[str, str]] = [("format", "json")]
    if count is not None:
        query.append(("count", str(count)))
    if start is not None:
        query.append(("start", start))
    if startafter is not None:
        query.append(("startafter", startafter))
    url = f"{STORAGE_ZYTE_API}/{kind}/{job_ref}?{urllib.parse.urlencode(query, doseq=True)}"
    return _request(url=url, method="GET", api_key=api_key)


def print_json(payload: Any, *, pretty: bool) -> None:
    if pretty:
        json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    else:
        json.dump(payload, sys.stdout, separators=(",", ":"), sort_keys=True)
    sys.stdout.write("\n")


def add_target_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--project", type=int, help="Numeric Zyte project id.")
    parser.add_argument(
        "--target",
        choices=sorted(TARGETS),
        help="Monitor target shorthand. Resolves to a project id.",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Structured helper for Monitor Zyte job operations."
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser(
        "run",
        help="Schedule a job through run.json (mutating, but not approval-gated by itself).",
    )
    add_target_arguments(run_parser)
    run_parser.add_argument("--spider", help="Spider name.")
    run_parser.add_argument("--jobq-id", type=int, help="Optional spider id.")
    run_parser.add_argument("--units", type=int, help="Units to run.")
    run_parser.add_argument("--priority", type=int, help="Priority from 0 to 4.")
    run_parser.add_argument("--tag", action="append", default=[], help="Repeatable tag.")
    run_parser.add_argument(
        "--setting",
        action="append",
        default=[],
        help="Repeatable job setting override KEY=VALUE.",
    )
    run_parser.add_argument(
        "--arg",
        action="append",
        default=[],
        help="Repeatable spider argument KEY=VALUE.",
    )

    list_parser = subparsers.add_parser(
        "list", help="List jobs as mappings (read-only inspection)."
    )
    add_target_arguments(list_parser)
    list_parser.add_argument("--job", help="Optional full job ref.")
    list_parser.add_argument("--spider", help="Optional spider name.")
    list_parser.add_argument("--state", choices=["pending", "running", "finished", "deleted"])
    list_parser.add_argument("--has-tag", action="append", default=[])
    list_parser.add_argument("--lacks-tag", action="append", default=[])
    list_parser.add_argument("--count", type=int, help="Limit returned jobs.")

    for name in ("stop", "delete"):
        command_parser = subparsers.add_parser(
            name,
            help=(
                "Stop one or more jobs (mutating, non-persistent)."
                if name == "stop"
                else "Delete one or more jobs (destructive, approval-gated)."
            ),
        )
        command_parser.add_argument(
            "--job",
            action="append",
            required=True,
            help="Full job ref like 831071/7/123. Repeat for multiple jobs.",
        )

    for name in ("items", "logs", "requests"):
        command_parser = subparsers.add_parser(
            name, help=f"Fetch {name} for a job (read-only inspection)."
        )
        command_parser.add_argument(
            "--job", required=True, help="Full job ref like 831071/7/123."
        )
        command_parser.add_argument("--count", type=int, help="Limit returned rows.")
        command_parser.add_argument("--start")
        command_parser.add_argument("--startafter")

    return parser


def command_run(args: argparse.Namespace, api_key: str) -> Any:
    project_id = resolve_project_id(args.project, args.target)
    form_fields: list[tuple[str, str]] = [("project", str(project_id))]
    if args.spider:
        form_fields.append(("spider", args.spider))
    if args.jobq_id is not None:
        form_fields.append(("jobq_id", str(args.jobq_id)))
    if not args.spider and args.jobq_id is None:
        raise ZyteJobsError("run requires --spider or --jobq-id.")
    if args.units is not None:
        form_fields.append(("units", str(args.units)))
    if args.priority is not None:
        form_fields.append(("priority", str(args.priority)))
    for tag in args.tag:
        form_fields.append(("add_tag", tag))
    settings = parse_key_value(args.setting)
    if settings:
        form_fields.append(("job_settings", json.dumps(settings, sort_keys=True)))
    for key, value in parse_key_value(args.arg).items():
        form_fields.append((key, value))
    return jobs_api(
        endpoint="run.json",
        method="POST",
        api_key=api_key,
        form_fields=form_fields,
    )


def command_list(args: argparse.Namespace, api_key: str) -> Any:
    project_id = resolve_project_id(args.project, args.target)
    query: dict[str, Any] = {"project": project_id}
    if args.job:
        _, job_ref = parse_job_ref(args.job)
        query["job"] = job_ref
    if args.spider:
        query["spider"] = args.spider
    if args.state:
        query["state"] = args.state
    if args.count is not None:
        query["count"] = args.count
    for index, tag in enumerate(args.has_tag):
        query[f"has_tag[{index}]"] = tag
    for index, tag in enumerate(args.lacks_tag):
        query[f"lacks_tag[{index}]"] = tag
    payload = jobs_api(
        endpoint="jobs/list.json",
        method="GET",
        api_key=api_key,
        query=query,
    )
    if isinstance(payload, dict):
        jobs = payload.get("jobs", [])
        if isinstance(jobs, list):
            payload["jobs"] = [job for job in jobs if isinstance(job, dict)]
    return payload


def command_mutate(args: argparse.Namespace, api_key: str, endpoint: str) -> Any:
    form_fields: list[tuple[str, str]] = []
    project_id: int | None = None
    for raw_job in args.job:
        current_project, job_ref = parse_job_ref(raw_job)
        if project_id is None:
            project_id = current_project
        elif project_id != current_project:
            raise ZyteJobsError("All jobs in one command must belong to the same project.")
        form_fields.append(("job", job_ref))
    assert project_id is not None
    form_fields.insert(0, ("project", str(project_id)))
    return jobs_api(
        endpoint=endpoint,
        method="POST",
        api_key=api_key,
        form_fields=form_fields,
    )


def command_storage(args: argparse.Namespace, api_key: str, kind: str) -> Any:
    _, job_ref = parse_job_ref(args.job)
    return storage_api(
        kind=kind,
        api_key=api_key,
        job_ref=job_ref,
        count=args.count,
        start=args.start,
        startafter=args.startafter,
    )


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        api_key = resolve_api_key()
        if args.command == "run":
            payload = command_run(args, api_key)
        elif args.command == "list":
            payload = command_list(args, api_key)
        elif args.command == "stop":
            payload = command_mutate(args, api_key, "jobs/stop.json")
        elif args.command == "delete":
            payload = command_mutate(args, api_key, "jobs/delete.json")
        elif args.command == "items":
            payload = command_storage(args, api_key, "items")
        elif args.command == "logs":
            payload = command_storage(args, api_key, "logs")
        elif args.command == "requests":
            payload = command_storage(args, api_key, "requests")
        else:  # pragma: no cover - argparse enforces the command.
            raise ZyteJobsError(f"Unsupported command: {args.command}")
    except ZyteJobsError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print_json(payload, pretty=args.pretty)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
