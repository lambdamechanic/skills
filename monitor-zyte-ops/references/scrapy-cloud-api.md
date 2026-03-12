# Scrapy Cloud HTTP API

Use the API path for structured, script-friendly operations.

Preferred helper

```bash
python scripts/monitor_zyte_jobs.py --help
```

Supported first-slice operations

- `run`
- `list`
- `stop`
- `delete`
- `items`
- `logs`
- `requests`

Auth

- Use `SHUB_APIKEY`, `SCRAPINGHUB_API_KEY`, or `ZYTE_API_KEY`.
- Jobs API base: `https://app.zyte.com/api/`
- Hubstorage readbacks:
  - items: `https://storage.zyte.com/items/<job_ref>`
  - logs: `https://storage.zyte.com/logs/<job_ref>`
  - requests: `https://storage.zyte.com/requests/<job_ref>`

Surface rubric

- Use the API when the caller needs JSON output that is easy to post-process.
- Prefer `shub` instead for an operator tailing logs or doing a quick manual item export.

Dict-style guardrails

- Treat job list entries as plain mappings.
- Read fields with keys such as `id`, `state`, `spider`, `tags`, `items_scraped`, `logs`, and `updated_time`.
- Do not assume listing results expose object methods like `refresh`.
- If a workflow needs a richer job handle, fetch that explicitly with the Python client library instead of pretending the listing result is one.

Delete guardrail

- Delete is API-backed, but only after explicit user approval.
- The approval summary must name the target, job id, and exact deletion request before the helper is invoked.

Useful patterns

```bash
python scripts/monitor_zyte_jobs.py list --target staging --spider gumtree_services_for_hire --state running --count 5
python scripts/monitor_zyte_jobs.py run --target staging --spider gumtree_services_for_hire --tag codex-manual
python scripts/monitor_zyte_jobs.py stop --job 831071/7/123
python scripts/monitor_zyte_jobs.py items --job 831071/7/123 --count 20
```

Readbacks

- Prefer item export before deciding whether a crawl succeeded.
- `logs` and `requests` are supporting evidence, not the primary success signal.

