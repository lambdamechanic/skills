---
name: pr-watch
description: Use the local pr-watch CLI/daemon to watch GitHub pull request activity, wait for PR changes, and fetch normalized event deltas without manually managing webhook forwarding or event subscriptions.
---

# pr-watch

Use this skill when you need local, agent-friendly visibility into GitHub pull request conversation, review, and CI activity.

Core rules

- Do not ask the user which GitHub webhook events to subscribe to. `pr-watch` manages the required event set internally.
- Treat watched orgs and repos as configuration. Add or remove explicit targets instead of assuming defaults.
- Prefer machine-friendly commands: `wait`, `events`, `status`, `list`, and `list-targets`.
- Keep the last seen `seq` cursor and reuse it with `--since-cursor` so you only fetch deltas.
- Use `pr-watch` if it is installed on `PATH`. Inside the source repo, use `cargo run --` as the fallback.

Preflight

Start with:

```bash
pr-watch doctor
```

Use `doctor` when setup is uncertain. It reports:

- whether `gh` is installed
- whether the `cli/gh-webhook` extension is available
- whether GitHub auth is present
- whether org forwarding may require `admin:org_hook`

Do not install extensions or change auth automatically unless the user explicitly asks.

Standard workflow

1. Start the daemon in a persistent shell session:

```bash
pr-watch daemon
```

2. Add the required targets:

```bash
pr-watch add-target org ORG
pr-watch add-target repo OWNER/REPO
```

3. Confirm daemon and forwarder state:

```bash
pr-watch status
pr-watch list
pr-watch list-targets
```

4. Wait for PR activity:

```bash
pr-watch wait OWNER/REPO PR_NUMBER --since-cursor LAST_SEQ --timeout 300
```

5. Fetch the full delta after wake-up:

```bash
pr-watch events OWNER/REPO PR_NUMBER --since-cursor LAST_SEQ
```

6. Persist the highest returned `seq` and reuse it on the next `wait` or `events` call.

Single-shot pattern

When the task is "wait for PR activity, then inspect the delta", use this procedure directly from the skill:

1. Check daemon health with `pr-watch status`.
2. If the daemon is unavailable, run `pr-watch doctor` and report the blocker clearly.
3. Inspect `pr-watch list-targets`.
4. If neither a matching repo target nor a covering org target exists, add `pr-watch add-target repo OWNER/REPO`.
5. Run:

```bash
pr-watch wait OWNER/REPO PR_NUMBER --timeout 300 [--since-cursor CURSOR]
```

6. If `wait` succeeds and returns an event with `seq = N`:
   Use `CURSOR` if one was provided.
   Otherwise fetch the delta with `pr-watch events OWNER/REPO PR_NUMBER --since-cursor N-1`.
7. Return a concise machine-friendly result that includes:
   - `status`
   - `repo`
   - `pr_number`
   - `since_cursor`
   - `next_cursor`
   - `wait_event`
   - `events`

Fallback in the source repo:

```bash
cargo run -- doctor
cargo run -- status
cargo run -- list-targets
cargo run -- add-target repo OWNER/REPO
cargo run -- wait OWNER/REPO PR_NUMBER --timeout 300 [--since-cursor CURSOR]
cargo run -- events OWNER/REPO PR_NUMBER [--since-cursor CURSOR]
```

Operating notes

- Run `daemon` in its own long-lived terminal session. Use separate short-lived commands for `wait`, `events`, and target management.
- If `status` or `list` shows the daemon is unavailable, start it instead of retrying control commands blindly.
- If `add-target` fails with GitHub `404`, assume missing webhook or admin access on that org or repo until proven otherwise.
- `wait` exits `0` when it receives a new matching event.
- `wait` exits `2` on timeout. Treat that as "no new event yet," not a hard failure.
- `events` returns normalized event history for the PR and ignores unrelated non-PR events.

Limitations

- Forwarding is only org-scoped or repo-scoped because `gh webhook forward` works that way.
- Org forwarding may require `admin:org_hook`.
- `check_run` and `workflow_run` association is only as good as the PR linkage GitHub includes in the webhook payload.
- For detailed live CI observation on a single PR, `gh run watch` or `gh pr checks --watch` can still be useful alongside `pr-watch`.

Cleanup

```bash
pr-watch stop-forwarder ID
pr-watch remove-target org ORG
pr-watch remove-target repo OWNER/REPO
pr-watch stop
```
