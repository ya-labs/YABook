---
name: yabook
description: Apply YA LABS YABook standards for GitHub workflow, documentation, AI usage, project initialization, issues, branches, commits, pull requests, releases, labels, Projects, and compliance checks. Use when the user invokes $yabook or asks to create/review issue titles or bodies, PR titles or descriptions, commit messages, branch names, release notes, project documentation structure, AGENTS.md guidance, or to initialize a repository with YA LABS standards.
---

# YABook

## Overview

Use this skill to apply YA LABS organizational standards without copying the entire handbook into context.

The YABook documentation remains the human source of truth. This skill is the operational interface for agents.

## Required Workflow

Before producing or changing anything:

1. Read the local `AGENTS.md` when available.
2. Inspect the repository state before assuming stack, branch, issue, or workflow.
3. Use local project rules first when they explicitly override YABook.
4. Use YABook as the default when the project follows YA LABS and has no local exception.
5. Warn before acting outside the documented pattern.
6. Keep outputs short, practical, and in Brazilian Portuguese unless the user asks otherwise.

## Command Routing

When the user invokes `$yabook`, route the request through [commands.md](references/commands.md).

Common commands:

- `$yabook help`
- `$yabook init`
- `$yabook status`
- `$yabook check`
- `$yabook issue`
- `$yabook branch name`
- `$yabook commit message`
- `$yabook pr`
- `$yabook release`
- `$yabook docs`
- `$yabook review`

Use aliases listed in `commands.md` when the user writes a shorter variant.

## References

Load only the reference needed for the current task:

- [commands.md](references/commands.md): command grammar, aliases, and expected outputs.
- [github.md](references/github.md): issues, branches, commits, PRs, labels, Projects, releases, `main`, `dev`.
- [documentacao.md](references/documentacao.md): project documentation structure, Markdown vs GitHub, pruning.
- [ia.md](references/ia.md): AI contract, context economy, broad vs directed reading.
- [init.md](references/init.md): `$yabook init` behavior and safe adoption rules.

## Context Rules

For commands that depend on current work, inspect:

- conversation context;
- `git status --short --branch`;
- current branch name;
- `git diff --stat`;
- `git diff`, when needed to understand the actual change.

For GitHub operations, inspect existing issue, PR, labels, Project, and repository conventions when tools are available.

Do not invent facts. When context is missing, state the assumption or ask for the missing decision.

## Output Rules

- Prefer the exact artifact requested.
- Keep human-facing text objective and short.
- Put long AI context in `<details>` only when it materially helps execution.
- Do not add validation sections to issues unless they change execution or review.
- Always keep traceability: Issue -> Branch -> Commit -> Pull Request -> Merge.
