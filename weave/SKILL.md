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
git_dir="$(git rev-parse --git-dir)"
command -v weave
command -v weave-driver
printf '%s\n' "$repo_root" "$git_dir"
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

Local-only setup

If the user does not want to modify tracked repo files, configure the merge driver in local Git config and add only the needed patterns to `.git/info/attributes`:

```bash
repo_root="$(git rev-parse --show-toplevel)"
git_dir="$(git rev-parse --git-dir)"
cd "$repo_root"
mkdir -p "$git_dir/info"
git config --local merge.weave.name "Entity-level semantic merge"
git config --local merge.weave.driver "weave-driver %O %A %B %L %P"
printf '%s\n' \
  '*.ts merge=weave' \
  '*.tsx merge=weave' \
  '*.js merge=weave' \
  '*.py merge=weave' \
  '*.go merge=weave' \
  '*.rs merge=weave' \
  '*.json merge=weave' \
  '*.yaml merge=weave' \
  '*.yml merge=weave' \
  '*.toml merge=weave' \
  '*.md merge=weave' \
  >> "$git_dir/info/attributes"
```

Add other patterns only when the repo needs them. Upstream support also includes Java, C/C++, Ruby, C#, PHP, Swift, Elixir, Bash, XML, and more.

Resolving an already-conflicted merge

If Git already produced ordinary conflict markers before `weave` was configured, the clean path is:

1. Inspect whether aborting is safe. Do not throw away user edits.
2. Abort the operation if that is acceptable:

```bash
git merge --abort
git rebase --abort
git cherry-pick --abort
```

3. Configure `weave`.
4. Restart the same kind of operation:

```bash
git merge BRANCH
git rebase UPSTREAM
git cherry-pick COMMIT_OR_RANGE
```

Use the command that matches the operation you aborted.

Handling remaining weave conflicts

When `weave` still reports a conflict, inspect the file with:

```bash
weave summary path/to/file
weave summary path/to/file --json
```

This gives structured conflict context such as entity name, kind, and hint text. Resolve those markers manually, then continue with standard Git commands:

```bash
git add path/to/file
git merge --continue
```

Or:

```bash
git rebase --continue
git cherry-pick --continue
```

Useful checks

```bash
repo_root="$(git rev-parse --show-toplevel)"
git_dir="$(git rev-parse --git-dir)"
git config --get merge.weave.driver
grep -H "merge=weave" "$repo_root/.gitattributes" "$git_dir/info/attributes" 2>/dev/null
```

What `weave` is good at

- both branches add different functions to the same file
- one branch edits one entity while the other adds a different entity nearby
- both branches add different JSON or config keys in the same file

What still needs human judgment

- both branches change the same function, method, class, or key incompatibly
- one side deletes an entity that the other side modified
- unsupported, binary, or large files that fall back to line-based merge
