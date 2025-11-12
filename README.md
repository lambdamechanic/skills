Skills Repository (Anthropic Format)

Overview
- Consolidated collection of skills in the same layout as anthropics/skills.
- Each skill lives at `<folder>/SKILL.md` (top‑level) with YAML front‑matter (`name`, `description`) followed by guidance and examples.
- Intended for use with the `sk` tool to discover, install, and manage skills per project.

Sources
- Seeded from three local repos in this workspace:
  - `../sk/skills/*`
  - `../dumbwaiter/skills/*`
  - `../isura` (none found today)
- If multiple repos contain a skill with the same name, we merge them. When there are conflicts, the version from `sk` takes precedence.

Using With sk
- sk repo: https://github.com/lambdamechanic/sk
- Install a skill from this repo after you publish it (example installs the `bd` skill):
  - `sk install lambdamechanic/skills --path bd`
- For local testing without publishing, point sk at this folder:
  - `sk install file://$PWD --path bd`

Format Reference
- Anthropic’s canonical format and expectations are documented in their skills repo:
  - https://github.com/anthropics/skills

Maintenance
- Add new skills as `<folder>/SKILL.md` (top‑level directory per skill).
- Keep front‑matter current; use clear, actionable guidance in the body.
- Avoid duplication—prefer updating an existing skill over creating a near‑duplicate.
