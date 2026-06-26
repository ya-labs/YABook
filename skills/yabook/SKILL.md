---
name: yabook
description: Apply YA LABS YABook standards for GitHub workflow, documentation, AI usage, project initialization, issue creation, issue classification, branch creation, pull requests, merges, releases, labels, GitHub Projects, Size estimation, and compliance checks. Use when the user invokes $yabook, asks to create or review issues/branches/PRs/releases/commits, asks for labels or Size, asks to create a batch of issues, asks to initialize a repository with YA LABS standards, or asks to load YABook context for the current conversation.
---

# YABook

## Overview

Use this skill to apply YA LABS organizational standards without copying the entire handbook into context.

The YABook documentation remains the human source of truth. This skill is the operational interface for agents.

## Required Workflow

Before producing or changing anything:

1. Read the local `AGENTS.md` when available.
2. Inspect the repository state before assuming stack, branch, issue, or workflow.
3. Use documented YABook formats as the source of truth for generated artifacts.
   Do not copy historical issue, PR, branch, or commit formats from the project
   when they differ from the documented YABook pattern, unless the user
   explicitly asks to preserve that project-specific legacy format.
4. Use YABook as the default when the project follows YA LABS and has no local exception.
5. Warn before acting outside the documented pattern.
6. Keep outputs short, practical, and in Brazilian Portuguese unless the user asks otherwise.

## GitHub Write Safety

Without `$yabook do`, do not create, edit, delete, publish, move in Projects,
apply labels, open PRs, merge, push, assign, or otherwise mutate GitHub state.

Only mutate GitHub state when the active command is `$yabook do` or one of its
documented aliases such as `$yabook create`.

Commands such as `$yabook issue`, `$yabook pr`, `$yabook branch name`,
`$yabook commit message`, `$yabook status`, `$yabook check`, and `$yabook review`
must generate text, inspect context, or report findings only. They must not run
GitHub write commands, even if the requested artifact appears obvious.

Even with `$yabook do`, create or execute only the artifacts explicitly requested
by the user. Never merge unless the user explicitly asks for merge.

## Command Routing

When the user invokes `$yabook`, route the request through [commands.md](references/commands.md).

Common commands:

- `$yabook help`
- `$yabook load`
- `$yabook init`
- `$yabook do`
- `$yabook status`
- `$yabook check`
- `$yabook issue`
- `$yabook issue classify`
- `$yabook branch name`
- `$yabook commit message`
- `$yabook pr`
- `$yabook release`
- `$yabook docs`
- `$yabook review`

Use aliases listed in `commands.md` when the user writes a shorter variant.

Support chained commands with `&`, for example `$yabook init & load & commit msg`. Execute each segment from left to right, reuse context collected by earlier segments, and keep the response grouped and concise.

## References

Load only the reference needed for the current task:

- [commands.md](references/commands.md): command grammar, aliases, and expected outputs.
- [github.md](references/github.md): issues, branches, commits, PRs, labels, Projects, releases, `main`, `dev`.
- [documentacao.md](references/documentacao.md): project documentation structure, Markdown vs GitHub, pruning.
- [ia.md](references/ia.md): AI contract, context economy, broad vs directed reading.
- [init.md](references/init.md): `$yabook init` behavior and safe adoption rules.
- [session.md](references/session.md): `$yabook load` behavior and full session cache.

## After `$yabook load`

When the session is loaded in the current conversation:

- use [session.md](references/session.md) as the main source for routine commands;
- do not re-read `github.md` or `session.md` for `issue`, `issue classify`, `branch name`, `commit message`, `pr`, `release`, or `status`;
- still inspect Git state and `git diff` when the artifact depends on the current change;
- still read `AGENTS.md` during load and apply local overrides over generic YABook rules;
- re-read other references only for `init`, `docs`, `check`, `review`, `do`, or when context is incomplete.

## Core Patterns

Use these patterns directly before loading references:

- Issue title: objective, without type prefix.
- Issue labels: type and area.
- Issue `Size`: GitHub Project field from `1` to `5`, never a label.
- Branch: `numero-descricao-curta`.
- Commit: `tipo: descrição curta`.
- PR title: objective, without type prefix.
- PR body: `Resumo rápido`, `O que mudou`, `Observações`, and optional `<details>` with `Informações para IA`.
- Traceability: Issue -> Branch -> Commit -> Pull Request -> Merge.

Size scale:

- `1`: quick adjustment, low risk, evident scope.
- `2`: small task, few files or low uncertainty.
- `3`: medium task, normal implementation or review.
- `4`: large task, multiple parts, relevant analysis or coordination.
- `5`: very large task, high uncertainty, candidate for splitting.

If suggesting `Size 5`, also suggest how to split the work.

## Context Rules

For commands that depend on current work, inspect:

- conversation context;
- `git status --short --branch`;
- current branch name;
- `git diff --stat`;
- `git diff`, when needed to understand the actual change.

For GitHub operations, inspect existing issue, PR, labels, Project, and repository conventions when tools are available.

For `$yabook do`, create or execute only the artifacts explicitly requested by the user. Merge only when the user explicitly asks for merge.

For squash merge, include the Pull Request number in the squash commit subject and include the commit history from the source branch against the target branch in the squash commit body.

Do not invent facts. When context is missing, state the assumption or ask for the missing decision.

## Output Rules

- Prefer the exact artifact requested.
- Keep human-facing text objective and short.
- Put long AI context in `<details>` only when it materially helps execution.
- Do not add validation sections to issues unless they change execution or review.
- Always keep traceability: Issue -> Branch -> Commit -> Pull Request -> Merge.
- When working in a repository that follows YABook and you changed files, end the final response with a suggested commit message for those changes.
