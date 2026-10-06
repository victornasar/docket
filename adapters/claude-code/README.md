# Adapter: Claude Code

How Docket's core concepts map into Claude Code's actual mechanisms.
This is the reference adapter — the one that gets exercised.

## Mapping

| Docket concept | Claude Code mechanism |
|---|---|
| `core/RULES.md` + `core/WORKFLOW.md` | Pulled into the project's `CLAUDE.md`, read at the start of every session |
| Planner, Implementer, Reviewer | Three files under `.claude/agents/`, one per role |
| Ticket | A markdown file (e.g. `tickets/<slug>.md`), created from `core/templates/ticket.template.md` |
| Project Audit | A markdown file (e.g. `PROJECT_AUDIT.md` at project root), created from `core/templates/project-audit.template.md` |
| Project Context | The project's `CLAUDE.md` plus whatever memory files the project already keeps — Docket doesn't introduce a separate mechanism, it just makes sure the Project Audit and prior Tickets are part of what gets loaded |
| Recipes | Referenced directly from `.claude/agents/` role files or `CLAUDE.md` by relative path into the attached `docket/` repo — not copied |
| Evidence / Done | Self-review ends with `docket pre-review` (verify → check-scope → check-evidence). Reviewer gets Ticket + `review-packet`; still judges AC adequacy |
| Pre-Review gates | Mandatory before spawning reviewer; non-zero blocks handoff |
| Skills | Optional thin host skills under `docket/skills/` (e.g. `verify-with-evidence`); install per `skills/README.md` — skills invoke tooling, do not duplicate Docket |

## CLAUDE.md

Generated from [`CLAUDE.md.template`](CLAUDE.md.template): it references
(or inlines, if the project prefers a self-contained file) Docket's
`RULES.md` and `WORKFLOW.md`, then appends the project's own Project
Audit. This is the file Claude Code reads automatically, so it's the
anchor point for the whole system in this tool.

## `.claude/agents/`

Each role becomes an agent definition:

- `.claude/agents/planner.md` — sourced from
  `docket/core/roles/planner.md`, with Claude Code's agent frontmatter
  (name, description, and **no write tools** — this role plans, it doesn't
  implement) added on top.
- `.claude/agents/implementer.md` — sourced from
  `docket/core/roles/implementer.md`, with full read/write/execute tools
  scoped to the working directory.
- `.claude/agents/reviewer.md` — sourced from
  `docket/core/roles/reviewer.md`, with **read-only tools** in the
  frontmatter (no `Edit`, `Write`, or any tool that mutates files). This is
  where the Reviewer's read-only requirement gets enforced mechanically,
  not just by convention — Claude Code's permission system is the actual
  gate.

**These are meant to be invoked as real subagents, not just documented as
a mapping.** At Review (see `WORKFLOW.md`), the session that just ran
Implement/Self-review must actually call the Agent tool with the `reviewer`
subagent — e.g. "use the Agent tool to launch the `reviewer` subagent,
passing it the path to the Ticket (with Evidence filled) and the diff
against its baseline commit, and nothing else about how the
implementation was reached." The Reviewer audits Evidence — missing or
inadequate Evidence is a send-back, not a cue to invent proof. Do
**not** treat "I'll now act as Reviewer" in the same conversation as
equivalent — that's the same-context weakness this mapping exists to
avoid, and Claude Code's Agent tool is specifically what makes the real
version possible here. The Planner step can be run the same way for a
large or ambiguous request (spawn `planner` to produce a Ticket for review
before any implementation session even starts), though it's less critical
there since the human approves the Ticket regardless.

**Known gap, found in practice:** `.claude/agents/*.md` files created or
edited mid-session are not picked up as new `subagent_type` options in
that same running session — the Agent tool's available types are fixed at
session start. If a project's adapter files are generated (or changed)
during the current session, the Agent tool call to spawn e.g. `reviewer`
will fail with "Agent type not found" until a fresh session starts. The
practical workaround for the current session: fall back to the generic
`general-purpose` subagent type with the role file's content given
directly in the spawn prompt (still gets genuine context isolation, the
part that actually matters — just not a named custom type). Regenerating
the adapter and then starting a new session is the real fix.

## Parallel Line

For starting multiple approved, Files-Touched-disjoint Tickets at once
(see [`PARALLEL_LINE.md`](../../advanced/PARALLEL_LINE.md) — experimental,
not exercised on a solo operator). This is Claude Code's real mechanism
for it, not an approximation:

1. Verify the disjoint-files rule yourself before claiming anything —
   don't rely on each Implementer to notice a conflict after the fact.
2. Create one `git worktree` per Ticket being started, per
   `PARALLEL_LINE.md`'s naming convention.
3. Spawn one `implementer` subagent per Ticket via the Agent tool, each
   given its own worktree path and told to work exclusively within it —
   in a tool that supports backgrounding subagent calls, run them
   backgrounded so they actually proceed concurrently rather than one
   blocking the next.
4. As each finishes Self-review, spawn its `reviewer` subagent the same
   way Review normally works (see above), pointed at that Ticket's branch
   diff specifically.
5. On a pass, merge that Ticket's branch back per `PARALLEL_LINE.md`'s
   merge-back step, then remove its worktree.

## Confirmation gates

The Rules' CONFIRM actions map onto Claude Code's permission-prompt
behavior: commands and tools that would otherwise require a manual
approval in Claude Code (destructive bash commands, git push, etc.) are
exactly the category the Rules ask the agent to pause on regardless. The
adapter doesn't need to invent new machinery for this — it aligns the
Rules' language with the tool's existing prompts so an approval in Claude
Code corresponds to an approval the Rules would also have required.

## Setup

See [`setup/attach.md`](../../setup/attach.md) for the full walkthrough.
The short version: symlink or submodule `docket/` into the project, run
`CLAUDE.md.template` through the project's Project Audit to produce a real
`CLAUDE.md`, and create the three files under `.claude/agents/` referencing
the role files above.
