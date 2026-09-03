# Tabouleh

Tabouleh is an opinionated planning-and-review workflow you vendor into a
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

## Quick start

New to Tabouleh and want to attach it to a project? Go to
[`setup/attach.md`](setup/attach.md) — a step-by-step walkthrough with a
copyable prompt.

## Repo map

```
tabouleh/
  core/
    RULES.md            Safety rules: what Tabouleh adds on top of the Claude Code baseline
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
    attach.md           How to wire Tabouleh into a new project
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

Tabouleh is a template repo with no "production" of its own, but its
`core/` files are load-bearing for every project that uses them. Changes
to `core/` follow the discipline in [`core/RULES.md`](core/RULES.md)
(confirmation before rewriting anything under `core/` or `adapters/`), and
the structural spine is **frozen** — see
[`core/LINE_MEETING.md`](core/LINE_MEETING.md) ("Changing this kit") for
what that means and how a change gets made when a real incident justifies
one.
