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

<How to run tests, what's covered vs. not, test framework, how to run a
single test/file, any flaky-test or known-gaps notes.>

## Build / run / deploy commands

<The actual commands: local dev server, build, lint, type-check, deploy.
Exact, copy-pasteable.>

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
