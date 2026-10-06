# Project Audit: <project name>

<!--
The pre-work audit of a project, done once when Docket is attached and
updated whenever a Ticket touches an area this document doesn't yet cover.
Referenced by every Ticket written for this project afterward — a Ticket's
Approach should be able to say "follows existing convention documented
here" instead of re-discovering it each time.
-->

**Last updated:**
**Updated by:**

## Stack

<Languages, frameworks, major libraries, runtime versions, package
manager.>

## Structure

<How the codebase is organized — directory layout and what lives where.
Enough that "where does X belong" has an obvious answer.>

## Conventions

<Naming conventions, code style, patterns the project already uses for
common things (error handling, API responses, state management, etc.) so a
Ticket's Approach can follow them instead of inventing new ones.>

## Test setup

<How tests are organized: framework, what's covered vs. not, how to run a
single test/file, flaky-test or known-gaps notes. Exact commands belong in
Verification below — don't invent a second conflicting command list.>

## Verification

<!--
Canonical commands agents must use during Self-review. Only list commands
that actually exist. Prefer one umbrella command (e.g. `pnpm verify`) when
the project has it, rather than inventing a split. Omit subsections that
don't apply — do not invent typecheck/lint/build if the project has none.
-->

### Canonical (preferred if present)

```text
command: <e.g. pnpm verify — or N/A>
purpose: <what it runs>
```

### Test

```text
command: <or N/A — not supported / covered by Canonical>
purpose:
```

### Typecheck

```text
command: <or N/A>
purpose:
```

### Lint

```text
command: <or N/A>
purpose:
```

### Format

```text
command: <or N/A — check-only if available>
purpose:
```

### Build

```text
command: <or N/A>
purpose:
```

## Build / run / deploy commands

<Local dev server, deploy, and other non-verify runbooks. Exact,
copy-pasteable. Keep verification commands in Verification above so
Self-review has one place to look.>

## Risky areas

<Fragile code, areas with little/no test coverage, shared state that's
easy to break, anything an Implementer should be extra careful editing.
This section directly informs which Tickets need extra scrutiny or a more
conservative approach.>

## Environments

<What environments exist (local/dev/staging/prod or equivalent), how
they're distinguished, and which ones are safe for the agent to interact
with directly vs. which require confirmation per RULES.md (e.g.
production, any environment with real user data).>

## Existing Rules exceptions or additions

<Most projects use core/RULES.md as-is. If this project has additional
rules beyond the universal set — a stricter gate, an extra BLOCK — note
them here. This document cannot remove or weaken anything in
core/RULES.md, only add to it.>
