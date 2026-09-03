# Adapter: Cursor

How Tabouleh's core concepts map into Cursor's rules mechanism.

> **Experimental — not exercised on a real project.** Cursor has no
> subagent primitive, so it cannot run the independent Review pass as a
> genuinely separate context; it only approximates it with a fresh chat.
> Wherever the workflow leans on that independence, this adapter is weaker
> than the Claude Code one, and it's labelled as such throughout rather
> than papered over.

## Mapping

| Tabouleh concept | Cursor mechanism |
|---|---|
| `core/RULES.md` + `core/WORKFLOW.md` | Content inlined into `.cursor/rules/tabouleh.mdc` (or a legacy `.cursorrules` file — see below), applied project-wide |
| Planner, Implementer, Reviewer | No native sub-agent/role separation in Cursor the way Claude Code's `.claude/agents/` provides it — see "Role separation" below for how to approximate it |
| Ticket | A markdown file (e.g. `tickets/<slug>.md`), created from `core/templates/ticket.template.md`, referenced in chat when starting work |
| Project Audit | A markdown file (e.g. `PROJECT_AUDIT.md` at project root), included as an `@file` reference or inlined into the rules file |
| Project Context | Cursor's own project context plus the rules file — Tabouleh doesn't add new machinery here |
| Recipes | Referenced by relative path into the attached `tabouleh/` repo from the rules file or pulled in via `@file` when relevant |

## Rules file format

Cursor supports both the newer `.cursor/rules/*.mdc` format (preferred —
supports multiple scoped rule files with frontmatter controlling when they
apply) and the older single `.cursorrules` file. Use
[`cursorrules.template`](cursorrules.template) either way:

- **Preferred:** save it as `.cursor/rules/tabouleh.mdc` with `alwaysApply:
  true` in the frontmatter, so the Rules and the workflow are always in
  context regardless of what file is open.
- **Legacy:** save it as `.cursorrules` at the project root if the project
  hasn't migrated to the newer format.

## Role separation

Cursor doesn't have a first-class equivalent of Claude Code's per-agent
tool permissions or a subagent primitive to spawn — there's no mechanism
here that gets as close to real independence as the Claude Code adapter's
Agent-tool invocation does. Two ways to approximate the role structure,
in preference order:

1. **Separate chats (default).** Open a fresh Cursor chat for the Review
   phase, and give it *only* the Ticket file and the diff to review —
   don't carry the Implement/Self-review conversation into it, and don't
   frame it with edit access. This is the closest approximation available
   in Cursor to a context that never saw the implementation reasoning,
   which is the actual thing that makes a review independent — not just
   "asked to check its own work" phrased as a separate step. Default to
   this even for solo, low-stakes projects; the fresh-context benefit
   doesn't disappear just because no one else is reviewing alongside you.
2. **Sequential, single-session** (fallback for trivial Tickets only):
   work through Ticket → Implement → Self-review → Review as explicit
   phases in one conversation, with the rules file instructing Cursor to
   announce which phase it's in and self-enforce that phase's boundaries
   (e.g. "I am now in Review — I will not edit files, only report findings
   against the Ticket"). This relies entirely on instruction-following,
   not a tool-level gate or a fresh context — treat its "read-only" and
   "independent" both as conventions, not guarantees, and don't reach for
   it just to save the cost of opening a second chat.

## Parallel Line

Cursor has no subagent primitive to spawn into — the same gap as Role
separation above, and it applies here too. There's no way to get the real
version described in
[`PARALLEL_LINE.md`](../../advanced/PARALLEL_LINE.md) (one tool call
spawning N concurrent, isolated agents). The honest approximation:

1. Still create one `git worktree` per Ticket, per `PARALLEL_LINE.md`'s
   naming convention — this part works the same regardless of tool, since
   it's just git.
2. Open one separate Cursor window per worktree (Cursor can open a
   worktree directory as its own window), and start one Ticket per window
   manually.
3. You are the coordination layer Claude Code's Agent tool would
   otherwise be — nothing here tracks claims or prevents you from
   accidentally opening the same Ticket twice. Watch the `Worktree` field
   in each Ticket yourself.
4. Review each one per the separate-chat approach above, then merge back
   per `PARALLEL_LINE.md` manually.

This is meaningfully more manual than the Claude Code version — worth
knowing going in, not something to discover halfway through.

## Setup

See [`setup/attach.md`](../../setup/attach.md) for the full walkthrough.
The short version: symlink or submodule `tabouleh/` into the project, run
`cursorrules.template` through the project's Project Audit to produce a
real rules file, and place it per the format guidance above.
