# Dashboard Settings Work

Use the dashboard path only for durable settings or periodic-job changes that are not covered by `shub` or the HTTP API.

Examples

- spider Raw Settings edits
- project-level durable settings
- periodic job create or update flows

Blocked path

- If `playwright-cli` is unavailable, stop and report that as the blocker.

Safety checklist

1. Resolve the target first.
2. Refuse an implicit production write.
3. Capture the current value before editing.
4. Summarize the exact mutation and wait for explicit user approval.
5. Apply the change only after approval.
6. Record the resulting value and the dashboard URL used.

Before and after record

- Prefer textual capture of the setting value before and after the change.
- Record the dashboard URL used for the edit.
- Only use screenshots when the relevant value cannot be captured reliably as text.

Target rules

- Staging periodic jobs live under `https://app.zyte.com/p/831071/periodic`.
- Production periodic jobs live under `https://app.zyte.com/p/251988/periodic`.
- For other persistent settings, navigate from the resolved project dashboard and the specific spider or project settings page.

Approval template

State all of the following before a write:

- environment and project id
- page or object being edited
- current value
- requested new value
- surface: `playwright-cli`

If the user did not explicitly ask for production, stop instead of mutating production.

