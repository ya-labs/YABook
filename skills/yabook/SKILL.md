---
name: yabook
description: Intelligently orchestrate the YA LABS Method through natural-language intent, safe command routing, issue-driven development, GitHub workflow, documentation, project initialization, collaborative planning, diagnosis, roadmaps, conversation step tracking, branches, pull requests, releases, Projects, Size estimation, and compliance checks. Use when the user invokes $yabook, wants to develop the current issue, describes a goal without knowing the command, uses a mismatched command, needs the correct YA LABS path, initializes or diagnoses a project, plans a version, discusses scope, tracks steps, or creates and reviews GitHub artifacts.
---

# YABook

## Overview

Use this skill to apply YA LABS organizational standards without copying the entire handbook into context.

The YABook Handbook remains the human source of truth. The YABook Skill is the intelligent orchestrator of the YA LABS Method.

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

## YABook Command Safety

The `do` gate applies only when the user invokes a `$yabook` command.
Natural-language requests that do not invoke `$yabook` remain ordinary direct
requests and may authorize the requested change, except for Git mutations.

In YA LABS repositories, Git mutations require an explicit
`$yabook do <ação>` call or the scoped `$yabook dev` authorization, even when a
direct natural-language request clearly asks for branch, commit, merge, tag,
fetch, pull, push, or another Git change. Read-only Git inspection remains
allowed.

`$yabook dev` is a documented scoped exception: it authorizes the Git and
GitHub prerequisites needed to implement the current issue, but not commit, PR,
merge, or release unless a chained command explicitly authorizes them.

Within the YABook command grammar, mutate state only when the active command
starts with `$yabook do`, uses a documented alias such as `$yabook create`, or
uses `$yabook dev` within its implementation scope.

The global Git gate includes local and remote mutations. Read-only inspection is
allowed without `do`; branch creation or switching, staging, commits, stash,
history changes, tags, fetch, pull, push, and equivalent mutations require an
explicit `do` action. Apply [git.md](references/git.md).

Commands such as `$yabook issue`, `$yabook pr`, `$yabook branch name`,
`$yabook init`, `$yabook diagnose`, `$yabook plan`, `$yabook commit message`,
`$yabook status`, `$yabook check`, and `$yabook review` must generate text,
inspect context, ask questions, or report findings only.

Before a relevant direct change, inspect the branch and related issue. If the
repository is on `main`, `dev`, a release branch, or another incompatible branch,
block the change and instruct the user to repeat the action with
`$yabook bypass <ação>`. A plain confirmation is not sufficient.

`$yabook bypass <ação>` authorizes the attached direct action outside the normal
issue/branch flow for that request only. It does not replace `$yabook do` for
YABook artifact commands, does not authorize merge implicitly, and does not
disable destructive-operation safeguards.

Even with `$yabook do`, create or execute only the artifacts explicitly requested
by the user. Never merge unless the user explicitly asks for merge.

Bare `$yabook do` may authorize exactly one pending contextual action proposed
in the immediately previous response. `$yabook continue` rejects an optional
checkpoint and resumes the original request without that Git mutation.
When the checkpoint interrupted an already authorized `do` workflow, resuming
includes its minimal prerequisites, such as pushing the PR head branch.

## Command Routing

When the user invokes `$yabook`, route the request through [commands.md](references/commands.md).

When `$yabook` is followed by natural language, an incompatible command, or an
unclear goal, apply [orquestracao.md](references/orquestracao.md). Infer and run
safe read-only commands until a material decision or write is required. Never
infer `do`.

Common commands:

- `$yabook help`
- `$yabook load`
- `$yabook init`
- `$yabook diagnose`
- `$yabook plan start v1`
- `$yabook discuss`
- `$yabook plan status`
- `$yabook plan next`
- `$yabook plan roadmap`
- `$yabook plan review`
- `$yabook steps`
- `$yabook bypass`
- `$yabook sync`
- `$yabook do`
- `$yabook continue`
- `$yabook dev`
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

## Implicit Session Load

On the first operational `$yabook` command in a conversation:

1. Read `session.md` completely.
2. Read the repository `AGENTS.md` when available.
3. Inspect the current branch, `git status --short --branch`, and `git diff --stat`.
4. Keep that context as the session cache.
5. Execute the requested command without producing a separate load response.

Do not repeat the implicit load for later commands in the same conversation.
`$yabook help` is the only exception and may respond without repository context.
`$yabook load` remains available to load explicitly or refresh the cache after
the repository, branch, workflow, or relevant local rules change.

## References

Load only the reference needed for the current task:

- [commands.md](references/commands.md): command grammar, aliases, and expected outputs.
- [github.md](references/github.md): issues, branches, commits, PRs, labels, Projects, releases, `main`, `dev`.
- [git.md](references/git.md): read-only Git inspection, mutation gate, and authorization scope.
- [help.md](references/help.md): contextual help for commands, command families, and natural-language goals.
- [documentacao.md](references/documentacao.md): project documentation structure, Markdown vs GitHub, pruning.
- [dev.md](references/dev.md): issue-driven implementation and its scoped authorization.
- [ia.md](references/ia.md): AI contract, context economy, broad vs directed reading.
- [init.md](references/init.md): `$yabook init` behavior and safe adoption rules.
- [orquestracao.md](references/orquestracao.md): intent routing, command correction, guidance, and autonomy limits.
- [planejamento.md](references/planejamento.md): diagnosis, collaborative planning, version documents, roadmap, and next-step behavior.
- [discuss.md](references/discuss.md): general-purpose discussion before planning or execution.
- [steps.md](references/steps.md): conversation-scoped checklists and step tracking.
- [session.md](references/session.md): `$yabook load` behavior and full session cache.
- [sync.md](references/sync.md): compare and synchronize the installed skill with a local or remote YABook source.

## After `$yabook load`

When the session is loaded in the current conversation:

- use [session.md](references/session.md) as the main source for routine commands;
- do not re-read `github.md` or `session.md` for `issue`, `issue classify`, `branch name`, `commit message`, `pr`, `release`, or `status`;
- still inspect Git state and `git diff` when the artifact depends on the current change;
- still read `AGENTS.md` during load and apply local overrides over generic YABook rules;
- read `planejamento.md` for `diagnose`, every `plan` command, and `do plan`;
- read `discuss.md` for `discuss` and its `plan discuss` compatibility alias;
- read `steps.md` for every `steps` command and while a checklist is active;
- read `sync.md` for `sync` and `do sync`;
- read `help.md` for every `help` request;
- read `orquestracao.md` for natural-language intent, command correction, or composed routing;
- read `git.md` whenever a request may inspect or mutate Git;
- read `dev.md` for `dev` and any chain that includes it;
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
- Traceability: new demand -> Issue -> Branch -> implementation -> Commit -> Pull Request -> Merge.

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

For `$yabook do branch` and branch preparation inside `$yabook dev`, require an
unambiguous issue and prefer GitHub's native `createLinkedBranch` mutation.
Confirm the result through the issue's `linkedBranches` connection before
reporting success. A branch created only through Git is not a confirmed issue
link; report that limitation and the manual fallback explicitly.

Before any checkpoint warning or Git-dependent decision, refresh the current Git
state. Never rely only on conversation cache or results from an earlier turn.

For `$yabook do plan`, the documented planning issue and branch are part of the
requested operation when compatible traceability does not already exist. Edit
planning files, but never commit automatically.

For squash merge, include the Pull Request number in the squash commit subject and include the commit history from the source branch against the target branch in the squash commit body.

Do not invent facts. When context is missing, state the assumption or ask for the missing decision.

## Output Rules

- Prefer the exact artifact requested.
- Keep human-facing text objective and short.
- While a `steps` checklist is active, repeat its compact status at the end of every response.
- While a checklist is active, evaluate relevant deviations, recalculate
  objective pending steps, preserve completed history, and request confirmation
  before changing scope, goals, or user decisions.
- Put long AI context in `<details>` only when it materially helps execution.
- Do not add validation sections to issues unless they change execution or review.
- Always keep traceability: new demand -> Issue -> Branch -> implementation -> Commit -> Pull Request -> Merge.
- When working in a repository that follows YABook and you changed files, end the final response with a suggested commit message for those changes.
