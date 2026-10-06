# Docket

Docket makes one unit of agent work **trustworthy**.

```
Skills  = capability   how to perform a type of work
Docket  = trust        one Ticket specified, proven, independently reviewed
pstack  = scale        many trustworthy units (outside this repo — not built here)
```

Skills (thin, optional) teach *how* to do work and point into Docket
recipes. Docket owns the Ticket, Evidence, independent Review, and Done.
Orchestration, parallelism fleets, and outer-loop automation belong above
Docket (pstack) — not in this kit.

Docket is an opinionated planning-and-review workflow you vendor into a
Claude Code project: a Ticket you approve before any code is written,
Evidence recorded at Self-review, an independent review that audits that
Evidence before anything is called Done, and a procedure for improving
the workflow itself from real incidents.

It's mostly Markdown plus role definitions, with a small Python CLI
(`bin/docket` / `tooling/`) for mechanical trust gates: `verify`,
`check-scope`, `check-evidence`, plus Stage 3 `pre-review` (ordered
handoff) and `review-packet` (fresh-context Review discovery). Stage 1
defined Evidence; Stage 2 makes forged exit codes and silent scope creep
fail closed; Stage 3 makes those gates the default Self-review → Review
path. It lives in its own repo and is brought into a project (today by
symlink or submodule; a vendored-copy model is planned), which then
generates a thin adapter file — a `CLAUDE.md` — that points back at it.

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
| **Ticket** | Planner | A request becomes a Ticket: Problem, Approach, Files Touched, Acceptance Criteria (AC-1…), Rollback plan. Evidence left blank. Project Audit (incl. Verification commands) if needed. | The human approves it. No code before this. |
| **Implement** | Implementer | Execute exactly the Ticket, touching only its Files Touched. Verify → fix → re-verify. Stop at any CONFIRM-gated action. | Every approach step done, no scope creep. |
| **Self-review** | Implementer | Prove the work: fill Evidence for every AC; run `docket pre-review` (verify → check-scope → check-evidence). | `pre-review` exit 0 for the final state. |
| **Review** | Reviewer | Independent audit of Evidence + diff (use `docket review-packet` for discovery). In Claude Code a real `reviewer` subagent gets only the Ticket and diff — not the Implement conversation. Missing Evidence → send-back. Gates do not prove AC adequacy. | Pass / Send-back / Escalate. |
| **Done** | — | Evidence-backed Done (see below). Natural session boundary. | — |

**Done** means the Ticket has sufficient recorded evidence that its
acceptance criteria were satisfied, `docket pre-review` passed (verify +
scope + evidence integrity), and an independent Reviewer Pass'd adequacy —
not that the agent claims success, and not that the change is merged or
deployed. Deployment stays a separate human CONFIRM after Done.

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

- **Attach it to a project.** Run the `attach-docket` skill ("attach
  docket here"), or follow [`setup/attach.md`](setup/attach.md) by hand:
  symlink the repo, run a Project Audit of the codebase, generate
  `CLAUDE.md` and the three `.claude/agents/` role files, then verify the
  agent produces a Ticket before writing code.
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

**Stage 2–3 tooling:** see [`tooling/README.md`](tooling/README.md).
Self-review ends with `docket pre-review` (verify → check-scope →
check-evidence). Fresh Reviewers use `docket review-packet`. Gates do
**not** prove AC adequacy — Reviewer/human judgment remains.

**Not built yet (later stages):** attach/sync CLIs; trivial-Ticket fast
path and tiered Reviewer; sampling; pstack-scale parallelism; kit-level CI
(see tooling README).

## Repo map

```
docket/
  core/
    RULES.md            Safety rules: what Docket adds on top of the Claude Code baseline
    WORKFLOW.md         The workflow: ticket -> implement -> self-review -> review -> done
    LINE_MEETING.md     "Changing this kit": the core/ freeze, and how a change gets made
    CHANGELOG.md        Log of every core/ change and the incident behind it
    roles/              One file per role: planner, implementer, reviewer
    recipes/            Reusable procedures (self-review/evidence, TDD, diagnosis, ...)
    templates/          Blank Ticket (incl. Evidence) and Project Audit formats
  skills/
    verify-with-evidence/  Thin host skill → pre-review + review-packet
  tooling/
    docket/                CLI: verify, check-scope, check-evidence,
                           pre-review, review-packet
  bin/docket               Wrapper → python3 -m docket
  advanced/
    PARALLEL_LINE.md    Experimental: running multiple Tickets at once (unproven solo)
  adapters/
    claude-code/        Reference adapter: CLAUDE.md + .claude/agents/
    cursor/             Experimental adapter: .cursor rules, weaker independent review
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
