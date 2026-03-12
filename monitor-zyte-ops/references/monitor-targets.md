# Monitor Targets

Use `scripts/resolve_monitor_zyte_target.py staging|production` for deterministic target metadata.

Current Monitor targets

- `staging`
  - project id: `831071`
  - dashboard: `https://app.zyte.com/p/831071`
  - periodic jobs: `https://app.zyte.com/p/831071/periodic`
  - `shub` alias: `staging`
- `production`
  - project id: `251988`
  - dashboard: `https://app.zyte.com/p/251988`
  - periodic jobs: `https://app.zyte.com/p/251988/periodic`
  - `shub` alias: `production`

Repo conventions

- `shub` commands run from `monitor_project/`.
- The project aliases above come from `monitor_project/scrapinghub.yml`.
- Use `uv run shub ...` inside the repo environment.

Credentials

- `SHUB_APIKEY` is the preferred environment variable.
- `SCRAPINGHUB_API_KEY` and `ZYTE_API_KEY` are accepted fallbacks for API-backed helpers.
- Persistent dashboard work additionally requires `playwright-cli`.

Safety

- Any production write must be explicitly requested as production.
- If the user did not explicitly request production and the action would mutate production, stop and explain the blocker.

