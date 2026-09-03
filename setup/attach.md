# Attaching Tabouleh to a New Project

Step-by-step instructions for wiring Tabouleh into a project that doesn't
have it yet. This is a one-time setup per project (with occasional Project
Audit updates afterward).

> **Note:** the distribution model is moving to a vendored copy pinned to
> a release tag, with a `tabouleh sync` command. Until the `attach` script
> lands, the symlink/submodule steps below still apply.

## Overview

1. Bring Tabouleh into the project as a symlink or submodule — not a copy.
2. Run a Project Audit on the project.
3. Fill in the Ticket and Project Audit templates.
4. Generate the adapter file for whichever tool the project uses.
5. Verify the attach worked before doing any real work.

## Step 1 — Bring the repo in

Choose one, from the project's root:

**Symlink** (simplest, best when Tabouleh and the project are both local
and you're fine with a machine-local link — note this doesn't travel with
a fresh clone unless the symlink itself is committed and re-creatable):

```bash
ln -s /path/to/tabouleh ./tabouleh
```

**Git submodule** (better when the project is shared/cloned by others and
needs Tabouleh to come along consistently):

```bash
git submodule add <tabouleh-repo-url> tabouleh
git submodule update --init --recursive
```

Either way, confirm `./tabouleh/core/RULES.md` resolves before continuing.

## Step 2 — Run the Project Audit

Have the agent (or do it yourself) audit the project using
[`../core/templates/project-audit.template.md`](../core/templates/project-audit.template.md)
as the format. This step is itself regular, unrestricted work per the
Rules — it's read-only investigation, no confirmation needed.

**Prompt template** (paste into the agent, in whatever tool you're using):

```
Run a Project Audit on this project using the format in
tabouleh/core/templates/project-audit.template.md. Read the codebase to
fill in Stack, Structure, Conventions, Test setup, Build/run/deploy
commands, Risky areas, and Environments. Do not guess at conventions —
point to actual examples in the codebase for each one. Save the result as
PROJECT_AUDIT.md at the project root.
```

Review the result yourself before moving on — this document is what every
future Ticket will be written against, so inaccuracies here propagate.

## Step 3 — Fill in the templates

The Project Audit is done in Step 2. The Ticket template
([`../core/templates/ticket.template.md`](../core/templates/ticket.template.md))
doesn't get filled in now — it's used per piece of work going forward.
Decide where Tickets will live in this project (e.g. `./tickets/`) and
create that directory now so the convention is established.

## Step 4 — Generate the adapter

Pick the adapter matching the tool this project uses:

**Claude Code:**
1. Read [`../adapters/claude-code/README.md`](../adapters/claude-code/README.md).
2. Copy [`../adapters/claude-code/CLAUDE.md.template`](../adapters/claude-code/CLAUDE.md.template)
   to `CLAUDE.md` at the project root, fill in every placeholder using the
   Project Audit from Step 2.
3. Create `.claude/agents/planner.md`, `.claude/agents/implementer.md`,
   and `.claude/agents/reviewer.md`, sourced from
   `tabouleh/core/roles/*.md`, with tool permissions set per the adapter
   README (planner: no write tools; implementer: full read/write/execute;
   reviewer: read-only).

**Cursor:**
1. Read [`../adapters/cursor/README.md`](../adapters/cursor/README.md).
2. Copy [`../adapters/cursor/cursorrules.template`](../adapters/cursor/cursorrules.template)
   to `.cursor/rules/tabouleh.mdc` (preferred) or `.cursorrules` (legacy),
   fill in every placeholder using the Project Audit from Step 2.

**Another tool not listed here:** there's no adapter yet. Use the Claude
Code or Cursor adapter as a reference for the pattern (pull the Rules +
the workflow into whatever context mechanism the tool reads
automatically, plus the project's Project Audit) and write a new
`adapters/<tool>/` following that shape. This is a change to Tabouleh
itself, so it follows the same confirm-before-editing-core discipline
noted in the main README.

**Prompt template** for having the agent do Steps 3–4 in one pass, once
Step 2 (the Project Audit) is already done:

```
Tabouleh is attached at ./tabouleh. The Project Audit is at
./PROJECT_AUDIT.md. Generate the adapter for [Claude Code / Cursor]
following tabouleh/setup/attach.md Step 4: produce the CLAUDE.md (and
.claude/agents/ files) or the Cursor rules file, with every placeholder
filled in from the Project Audit. Show me the generated file(s) before
writing them.
```

## Step 5 — Verify

Before starting real work:
- Confirm the generated adapter file is actually being read by the tool
  (e.g. start a fresh session/chat and ask the agent to summarize the
  Rules — it should be able to, from context alone, without being pointed
  at the file).
- Confirm the agent, asked to make a small change, produces a Ticket first
  rather than jumping straight to code.
- If either check fails, re-check that the adapter file is in the location
  and format the tool actually auto-loads (see the tool's own docs — this
  varies and changes over time).

Once verified, Tabouleh is attached. Ordinary work on this project now
starts with a Ticket, per [`../core/WORKFLOW.md`](../core/WORKFLOW.md).
