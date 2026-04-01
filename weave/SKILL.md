---
name: weave
description: Use Ataraxy Labs' weave semantic merge driver to preview merges, configure Git to use weave for supported files, and resolve Git merge conflicts with entity-level context instead of line-based conflict markers.
---

# weave

Use this skill when the user wants to use `weave` to reduce or resolve Git merge conflicts, preview whether a merge will be clean, or interpret weave conflict markers.

Core rules

- Do not turn this skill into an installation guide. Focus on using `weave` to preview merges and resolve conflicts.
- Do not install `weave` or change merge configuration unless the user asked for that outcome.
- `weave setup` edits repo-local Git config and `.gitattributes`. If the user only wants a personal or temporary setup, prefer `.git/info/attributes`.
- Use `weave` to eliminate false conflicts on independent edits. If `weave` still leaves conflict markers, treat them as real semantic conflicts and resolve them carefully.
- `weave` is for supported text files. Unsupported types, binary files, and large files fall back to ordinary line-based merge behavior.

Confirm `weave` is available

Start with:

```bash
repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"
info_attributes="$(git rev-parse --git-path info/attributes)"
command -v weave
command -v weave-driver
printf '%s\n' "$repo_root" "$info_attributes"
git status --short
```

If `weave` or `weave-driver` is missing, stop and say so clearly. Only discuss installation if the user explicitly asks for it.

Preview first

Before changing merge configuration, preview the merge result:

```bash
weave preview BRANCH
weave preview BRANCH --file path/to/file
```

Use `preview` to answer:

- which files would auto-resolve cleanly
- which files still have entity-level conflicts
- which function, class, key, or other entity actually conflicts

Preferred Git setup

For a repo-wide setup:

```bash
cd "$(git rev-parse --show-toplevel)"
weave setup
```

This configures `merge.weave.*` in Git and adds `merge=weave` patterns to `.gitattributes` for supported extensions.

To remove it later:

```bash
cd "$(git rev-parse --show-toplevel)"
weave unsetup
```

`weave unsetup` only reverts the repo-wide changes from `weave setup`. For a local-only cleanup, use the removal steps below.

Local-only setup

If the user does not want to modify tracked repo files, configure the merge driver in local Git config and add only the needed patterns to `.git/info/attributes`:

```bash
repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"
info_attributes="$(git rev-parse --git-path info/attributes)"
mkdir -p "$(dirname "$info_attributes")"
git config --local merge.weave.name "Entity-level semantic merge"
git config --local merge.weave.driver "weave-driver %O %A %B %L %P"
for pattern in \
  '*.ts' \
  '*.tsx' \
  '*.js' \
  '*.py' \
  '*.go' \
  '*.rs' \
  '*.json' \
  '*.yaml' \
  '*.yml' \
  '*.toml' \
  '*.md'
do
  pattern_re="$(printf '%s\n' "$pattern" | sed 's/[][(){}.^$?+*|\\/]/\\&/g')"
  if ! grep -qE "^${pattern_re}[[:space:]].*merge=weave([[:space:]]|$)" "$info_attributes" 2>/dev/null; then
    printf '%s merge=weave\n' "$pattern" >> "$info_attributes"
  fi
done
```

Add other patterns only when the repo needs them. `weave setup` handles the broader upstream-supported set automatically.

To remove a local-only setup later:

```bash
repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"
info_attributes="$(git rev-parse --git-path info/attributes)"
git config --local --unset-all merge.weave.name || true
git config --local --unset-all merge.weave.driver || true
if test -f "$info_attributes"; then
  tmp_attributes="$(mktemp)"
  if awk '!/[[:space:]]merge=weave([[:space:]]|$)/' "$info_attributes" > "$tmp_attributes"; then
    if test -s "$tmp_attributes"; then
      mv "$tmp_attributes" "$info_attributes"
    else
      rm -f "$info_attributes" "$tmp_attributes"
    fi
  else
    rm -f "$tmp_attributes"
  fi
fi
```

Resolving an already-conflicted merge

If Git already produced ordinary conflict markers before `weave` was configured, the clean path is:

1. Inspect whether aborting is safe. Do not throw away user edits.
2. Abort the operation if that is acceptable:

For a merge:

```bash
git merge --abort
```

For a rebase:

```bash
git rebase --abort
```

For a cherry-pick:

```bash
git cherry-pick --abort
```

3. Configure `weave`.
4. Restart the same kind of operation:

For a merge:

```bash
git merge BRANCH
```

For a rebase:

```bash
git rebase BRANCH
```

For a cherry-pick:

```bash
git cherry-pick COMMIT_OR_RANGE
```

Handling remaining weave conflicts

When `weave` still reports a conflict, inspect the file with:

```bash
weave summary path/to/file
weave summary path/to/file --json
```

This gives structured conflict context such as entity name, kind, and hint text. Resolve those markers manually, then continue with standard Git commands:

```bash
git add path/to/file
```

Continue a merge with:

```bash
git merge --continue
```

Continue a rebase with:

```bash
git rebase --continue
```

Continue a cherry-pick with:

```bash
git cherry-pick --continue
```

Useful checks

```bash
repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"
info_attributes="$(git rev-parse --git-path info/attributes)"
git config --get merge.weave.driver
grep -H -E '[[:space:]]merge=weave([[:space:]]|$)' "$repo_root/.gitattributes" "$info_attributes" 2>/dev/null
```

What `weave` is good at

- both branches add different functions to the same file
- one branch edits one entity while the other adds a different entity nearby
- both branches add different JSON or config keys in the same file

What still needs human judgment

- both branches change the same function, method, class, or key incompatibly
- one side deletes an entity that the other side modified
- unsupported, binary, or large files that fall back to line-based merge
