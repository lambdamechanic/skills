# `shub` Workflows

Use `shub` for operator-driven CLI flows:

- deploy
- schedule a one-off run
- quick log tail
- quick manual item export
- request export
- image operations

Always run from `monitor_project/`.

Common commands

```bash
cd monitor_project
uv run shub deploy staging -v
uv run shub schedule staging/<spider_name> -t codex-manual
uv run shub log -f staging/<spider_id>/<run_id>
uv run shub items staging/<spider_id>/<run_id> --tail 20
uv run shub requests staging/<spider_id>/<run_id> --tail 20
uv run shub image list staging
```

Temporary overrides

Use `-s KEY=VALUE` and `-e KEY=VALUE` for one-off job-scoped changes:

```bash
cd monitor_project
uv run shub schedule staging/<spider_name> \
  -a spider_arg=value \
  -s LOG_LEVEL=DEBUG \
  -t codex-manual
```

Do not turn a one-off debug override into a dashboard settings change unless the user explicitly asked for a durable edit.

Validation

- Do not validate success from log output alone.
- Export items first:

```bash
cd monitor_project
uv run shub items staging/<spider_id>/<run_id> > /tmp/job-items.jl
```

- Inspect item count, sample rows, and required fields first.
- Use `shub log` and `shub requests` only to explain anomalies after inspecting items.

When not to use `shub`

- Machine-friendly bulk job control or structured readbacks: use `scripts/monitor_zyte_jobs.py`.
- Persistent settings edits or periodic-job changes: use `playwright-cli` against the dashboard.

