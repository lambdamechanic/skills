---
name: monitor-zyte-ops
description: "Use for Monitor-specific Zyte Scrapy Cloud operations: deploys, ad hoc runs, machine-friendly job control, exported-items-first validation, dashboard-only settings changes, and fetch/proxy diagnosis handoff."
---

# monitor-zyte-ops

Use this skill for Monitor-specific Zyte Scrapy Cloud work.

Use cases

- Deploying or scheduling Monitor spiders on staging or production
- Inspecting jobs in a machine-friendly way
- Deleting jobs after explicit user approval
- Changing durable spider or project settings in the Zyte dashboard
- Validating whether a crawl really succeeded
- Routing fetch/proxy diagnosis to the existing `fetch-test-spider` workflow

Locating the bundled scripts

The scripts named below live in this skill's `scripts/` directory, but its location
varies by checkout: most repos keep the skill under `.agents/skills/`, while some
worktrees use `skills/`. Resolve it from the git root instead of guessing a relative
path. Because these shells do not persist environment between commands, include the
two `SCRIPTS=` lines in the same command block whenever you invoke a bundled script:

```
SCRIPTS="$(git rev-parse --show-toplevel)/.agents/skills/monitor-zyte-ops/scripts"
[ -d "$SCRIPTS" ] || SCRIPTS="$(git rev-parse --show-toplevel)/skills/monitor-zyte-ops/scripts"
uv run python "$SCRIPTS/monitor_zyte_jobs.py" --pretty list
```

Do not use bare `scripts/...`, `skills/...`, or `../skills/...` paths — they fail
because the skill is not at a fixed location relative to your working directory.

Start here

1. Resolve the target first: `uv run python "$SCRIPTS/resolve_monitor_zyte_target.py" staging|production` (resolve `$SCRIPTS` as above).
2. Choose the surface:
   - `shub` for deploys, ad hoc runs, log tails, quick manual item export, and image operations
   - `monitor_zyte_jobs.py` for machine-friendly `run`, `list`, `stop`, `delete`, `items`, `logs`, and `requests`
   - `playwright-cli` for persistent dashboard-only edits such as Raw Settings and periodic jobs
3. Stop immediately if a required dependency is unavailable.

Blocked paths

- If `SHUB_APIKEY`, `SCRAPINGHUB_API_KEY`, and `ZYTE_API_KEY` are all missing, stop before any `shub` or API-backed job operation.
- If `playwright-cli` is unavailable, stop before any dashboard write or read-modify-write flow.
- If the `fetch-test-spider` skill is unavailable, stop before improvising a proxy/fetch diagnosis flow.

Surface rules

- `shub` commands run from `monitor_project/`, never the repo root.
- A one-off debug run stays temporary. Use `shub schedule -s KEY=VALUE` or API `job_settings`; do not persist that change in the dashboard.
- Persistent settings and periodic-job edits are dashboard work, not `shub` work.
- Scrapy Cloud listing responses are dict-shaped mappings. Use keyed lookups, not object methods.

Operation triage

- Classify the requested action before deciding whether approval is needed.
- `read-only inspection`:
  - target resolution
  - job listing and job-detail lookups
  - items, logs, and requests retrieval
  - `shub log`, `shub items`, and other dashboard/API reads that do not change Zyte state
- `ephemeral job control`:
  - deploys
  - ad hoc runs or schedules
  - stopping an in-flight job
  - other one-off runtime actions that do not persist project or spider configuration
- `destructive or persistent mutation`:
  - delete operations
  - durable spider or project settings edits
  - periodic-job edits
  - Raw Settings writes
  - any other action that deletes data or persists configuration in Zyte

Approval rules

- Read-only inspection never needs approval. Fetching details about existing runs is always read-only.
- For ephemeral job control, do not ask for a second approval when the user already asked for that concrete action. If the target or impact is ambiguous, stop and clarify instead of guessing.
- Before any destructive or persistent mutation, summarize:
  - target environment and project id
  - object being changed or deleted
  - exact mutation
  - surface being used
- Wait for explicit user approval in-thread before proceeding.
- Do not treat an ambiguous request as approval for a destructive action or a production write.

Validation rules

- Treat exported items as the primary success artifact.
- Fetch or export items before deciding a crawl succeeded.
- Use logs, stats, and job metadata only as supporting context.
- For fetch/proxy diagnosis, route to `fetch-test-spider` and inspect `items.jsonl` for `success: true` plus a 2xx `status_code`.

Read only what you need

- Read `references/monitor-targets.md` for project ids, dashboard URLs, and the `monitor_project/` rule.
- Read `references/shub.md` for operator CLI workflows.
- Read `references/scrapy-cloud-api.md` for structured API operations and dict-style handling.
- Read `references/dashboard-settings.md` for dashboard-only settings and periodic-job guardrails.
