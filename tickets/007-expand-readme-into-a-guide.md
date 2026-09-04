# Ticket: Expand the README into a usage guide

**Status:** done
**Owner (Implementer):** Claude (this session)
**Retry count:** 0
**Related project audit:** N/A — this repo
**Worktree:** (blank)

**Depends on:** 001–006 (the whole rename/reposition — this builds on the
post-006 README).

## Problem

The post-006 README defines Docket and lays out the repo, but a reader
still has to open `WORKFLOW.md`, `roles/`, and `RULES.md` to learn how the
thing actually runs and what they can do with it. Add two sections so the
README works as a standalone guide: **How it works** (the five-stage loop,
the roles, the Rules framing) and **What you can do with it** (attach, run
work through it, parallel line, evolve the kit — plus what's deferred).

This is not a `core/` change — README is not the frozen spine.

## Approach

Rewrite `README.md` to the content below. Everything through "The mental
model" is unchanged; "Quick start" is absorbed into "What you can do with
it"; "Repo map", "Reading order", "Scope" are unchanged. Two new sections
are inserted between "The mental model" and "Repo map".

```markdown
# Docket

Docket is an opinionated planning-and-review workflow you vendor into a
Claude Code project: a Ticket you approve before any code is written, an
independent review pass before anything is called done, and a procedure
for improving the workflow itself from real incidents.

It's a small set of Markdown documents plus role definitions — nothing
executes, there's no runtime. It lives in its own repo and is brought into
a project (today by symlink or submodule; a vendored-copy model is
planned), which then generates a thin adapter file — a `CLAUDE.md` — that
points back at it.

**On "works anywhere":** the `core/` documents are plain Markdown with no
Claude-specific syntax, so porting the workflow to another tool is
possible in principle. In practice only the Claude Code adapter is
exercised. A Cursor adapter exists but is experimental and can't run the
independent review pass as a genuinely separate context — it approximates
it with a separate chat. "Portable" and "model-agnostic" are the
aspiration, not a delivered feature.

## The mental model

We borrowed the structure of a kitchen brigade: a planner turns a request
into a Ticket, an implementer executes exactly that Ticket, an independent
checker reviews the result against it, and there's a checkpoint before
anything ships. The documents use plain terms — Planner, Implementer,
Reviewer, Ticket, the workflow — the brigade is just where the shape came
from.

## How it works

Every piece of work moves through five stages. Nothing advances until the
current stage's exit gate is met.

```
TICKET → IMPLEMENT → SELF-REVIEW → REVIEW → DONE
```

| Stage | Owner | What happens | Exit gate |
|---|---|---|---|
| **Ticket** | Planner | A request becomes a Ticket: Problem, Approach, Files Touched, Acceptance Criteria (a checklist), Rollback plan. A Project Audit is run first if the area isn't already covered. | The human approves it. No code before this. |
| **Implement** | Implementer | Execute exactly the Ticket, touching only its Files Touched. Stop at any CONFIRM-gated action. | Every approach step done, no scope creep. |
| **Self-review** | Implementer | Check your own work against the Ticket — walk each acceptance criterion, diff against Files Touched, run tests, scan for leftovers. | Self-checklist passes. |
| **Review** | Reviewer | An independent check against the Ticket. In Claude Code this is a real `reviewer` subagent given only the Ticket and the diff — not the conversation that produced them. | Pass / Send-back / Escalate. |
| **Done** | — | Criteria verifiably met, no open Reviewer feedback. A human can merge without re-checking. A natural session boundary. | — |

**Send-back loop:** the Reviewer returns itemized feedback and the work
goes back to Implement. After two send-backs on the same Ticket it
escalates to the human instead — two failures usually means the Ticket
itself is underspecified, which is a planning problem, not another
implementation attempt.

**The three roles.** Planner writes Tickets, reads anything, runs nothing
that changes state, and can't approve its own Ticket. Implementer has full
read/write/execute but only within the Ticket's Files Touched —
"while I'm in here" fixes are off-limits, noted for a new Ticket instead.
Reviewer is read-only; its independence is the point, so it runs as a
separate context that never saw the implementation reasoning.

**The Rules.** [`core/RULES.md`](core/RULES.md) assumes the Claude Code
host already enforces the basics (credentials, permanent deletion, sending
messages, publishing) and lists only what Docket adds on top: editing
`core/`/`adapters/` files, read-before-write, dependency and CI changes,
the database-migration gradation, rollback discipline, scope boundaries,
and the parallel-execution invariant. Three responses: **CONFIRM** (stop,
describe it, get an explicit yes), **BLOCK** (nothing unlocks it),
**ESCALATE** (hand back to the human).

## What you can do with it

- **Attach it to a project.** `setup/attach.md` walks it: symlink the
  repo, run a Project Audit of the codebase, generate `CLAUDE.md` and the
  three `.claude/agents/` role files, verify the agent produces a Ticket
  before writing code.
- **Run work through it.** Describe a change; the session (as Planner)
  writes a Ticket and shows it to you; you approve or adjust; it
  implements, self-reviews, spawns the Reviewer, and returns Pass /
  Send-back / Escalate. You merge on Done.
- **Run several Tickets at once.** [`advanced/PARALLEL_LINE.md`](advanced/PARALLEL_LINE.md)
  — a worktree per Ticket, pairwise-disjoint Files Touched, a merge-back
  stage. Experimental; not exercised on a single operator.
- **Evolve the kit.** When real use exposes a process gap, that's a
  `core/` change through "Changing this kit" — grounded in the incident,
  approved by the human, logged in `CHANGELOG.md`.

**Not built yet:** a lightweight checkpoint at Ticket-approval and a
tiered Reviewer (skip the expensive subagent for trivial Tickets); and the
tooling — a vendored-copy `docket sync`, an `attach` script, semver +
`RELEASES.md`.

## Repo map

```
docket/
  core/
    RULES.md            Safety rules: what Docket adds on top of the Claude Code baseline
    WORKFLOW.md         The workflow: ticket -> implement -> self-review -> review -> done
    LINE_MEETING.md     "Changing this kit": the core/ freeze, and how a change gets made
    CHANGELOG.md        Log of every core/ change and the incident behind it
    roles/              One file per role: planner, implementer, reviewer
    recipes/            Reusable procedures (safe migration, TDD, diagnosis, ...)
    templates/          Blank Ticket and Project Audit formats
  advanced/
    PARALLEL_LINE.md    Experimental: running multiple Tickets at once (unproven solo)
  adapters/
    claude-code/        Reference adapter: CLAUDE.md + .claude/agents/
    cursor/             Experimental adapter: .cursor rules, no true independent review
  setup/
    attach.md           How to wire Docket into a new project
```

## Reading order

1. This README
2. [`core/RULES.md`](core/RULES.md) — the safety rules, and what they
   assume the host already enforces
3. [`core/WORKFLOW.md`](core/WORKFLOW.md) — the workflow every piece of
   work goes through
4. [`core/roles/`](core/roles/) — what each role does and doesn't do
5. [`adapters/claude-code/`](adapters/claude-code/) — the reference
   adapter (or [`adapters/cursor/`](adapters/cursor/), experimental)

## Scope

Docket is a template repo with no "production" of its own, but its
`core/` files are load-bearing for every project that uses them. Changes
to `core/` follow the discipline in [`core/RULES.md`](core/RULES.md)
(confirmation before rewriting anything under `core/` or `adapters/`), and
the structural spine is **frozen** — see
[`core/LINE_MEETING.md`](core/LINE_MEETING.md) ("Changing this kit") for
what that means and how a change gets made when a real incident justifies
one.
```

## Files touched

- `README.md`

## Acceptance criteria

- [ ] `README.md` has a `## How it works` section with the five-stage
      table (Ticket / Implement / Self-review / Review / Done, with owner
      and exit gate per row), the send-back-loop paragraph, the
      three-roles paragraph, and the Rules-framing paragraph.
- [ ] `README.md` has a `## What you can do with it` section covering:
      attach, run work through it, the parallel line (linked, marked
      experimental), evolve the kit, and a "not built yet" list.
- [ ] The old `## Quick start` section is gone (absorbed into "What you
      can do with it").
- [ ] Everything from the title through `## The mental model`, and the
      `## Repo map` / `## Reading order` / `## Scope` sections, is
      unchanged from the current README.
- [ ] Every markdown link in `README.md` resolves.
- [ ] No content contradicts `core/WORKFLOW.md`, `core/roles/*`, or
      `core/RULES.md` (the README summarizes them; it must not drift).

## Rollback plan

Single commit. `git revert <sha>` restores the leaner README.

## Rules check

- No BLOCK action. `README.md` is not under `core/` or `adapters/`, so
  RULES.md §2's confirm-gate doesn't formally apply, but this Ticket's
  approval covers it regardless. Read-before-write observed. Not a `core/`
  change — the freeze doesn't apply.

## Notes for the Reviewer

Reviewed in isolated context — PASS on all 6 criteria, no drift from core/. Two non-blocking notes: the Review-row exit gate lists outcomes not a gate phrasing; the host-baseline / Docket-additions lists are illustrative, not exhaustive.
