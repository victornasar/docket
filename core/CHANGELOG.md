# Changelog

The running log of `core/` changes and the incidents behind them (see
[`LINE_MEETING.md`](LINE_MEETING.md)) — real weaknesses found while doing
real work on an attached project, and the specific fix each one led to.
Every entry answers "why does this rule exist." Deliberate feature
additions to Docket (planned, not incident-driven) aren't logged here —
they don't need the "what happened" half of the format, just normal design
write-up in their own file.

**Vocabulary note:** the project was renamed from Tabouleh to Docket on
2026-09-03. Entries dated before then also use the earlier kitchen-brigade
vocabulary — Executive Chef = Planner, Line Cook = Implementer, Expediter =
Reviewer, The Pass = the workflow (`WORKFLOW.md`), Mise en Place = Project
Audit, Kitchen Rules = Rules (`RULES.md`). The events they describe are
unchanged; only the terms were renamed.

Newest first.

---

## 2026-08-14 — No step between architecture and code for new shapes

**Triggering project:** vitals, Ticket 19, send-back #1 — the
`GymEntryDTO` that silently dropped `GymEntry`'s legacy `arms`/`thighs`
fields.

**What happened:** the Ticket's Approach described the export feature at
an architecture level ("build DTOs mirroring the models, encode as
JSON") but never went one level deeper into the actual field-by-field
shape of `GymEntryDTO` against the real `GymEntry` source. The DTO got
built from a skim of "the current fields," missing two real ones. An
independent Expediter pass caught it — but the cost of that catch (a
full send-back cycle) was avoidable: a few minutes spent on the actual
shape before Fire would have caught it for free.

**Why the gap existed:** Tabouleh's Ticket format has Problem,
Approach, Files Touched, Acceptance Criteria — nothing that names the
specific layer between "what are we building" and "what does the code
say," which is exactly where this kind of miss lives. Read (and
independently evaluated against this same incident) Dex Horthy's [Why
Software Factories Fail](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/wsff.md),
which names this same gap as "program design" and argues it's commonly
skipped industry-wide, not specific to Tabouleh.

**Fix:** new `core/recipes/recipe-program-design.md` — field/type
mapping against real source, call-stack sketch for control-flow changes,
per-file "what changes here" notes, scoped only to Tickets that
introduce a new type, data-transformation boundary, or call-flow change
(not every Ticket — most don't need it). Cross-linked from
`roles/executive-chef.md` and `templates/ticket.template.md`'s Approach
section.

**Files changed:** `core/recipes/recipe-program-design.md` (new),
`core/roles/executive-chef.md`, `core/templates/ticket.template.md`.

## 2026-08-13 — Independent review cost ~287k tokens on one Ticket

**Triggering project:** vitals, Ticket 19 (data export). Three independent
Expedite subagent calls — testing the Expediter independence fix live —
reported 69,763 + 126,046 + 91,609 tokens respectively, ~287k total,
almost the entire session's token usage for that stretch of work.

**What happened:** each Expedite pass, including the third — which was
re-verifying a one-line documentation fix after two substantive rounds
had already done the real investigation — ran a full from-scratch
investigation and reported it as a complete narrated log (every command,
every file read, full reasoning). The rigor was real and caught real
issues in rounds 1 and 2; round 3's cost was disproportionate to what it
actually needed to check.

**Why the gap existed:** nothing in `expediter.md` or `THE_PASS.md`
distinguished "how thorough the check needs to be" from "how long the
report of the check needs to be," or said later retry rounds could scope
down once the first round had already mapped the territory. Independence
was specified; proportionality wasn't.

**Fix:** `roles/expediter.md` gained a "Keep the report proportional"
section — verdict + itemized findings by default, full evidence only
when actually needed, and later attempts re-verify what changed rather
than re-deriving everything. `THE_PASS.md`'s loopback policy gained the
same scoping guidance, plus a new note that Serve is a natural session
boundary — carrying a finished Ticket's full history into unrelated
future work costs context for no benefit.

**Files changed:** `core/roles/expediter.md`, `core/THE_PASS.md`.

## 2026-08-13 — Freshly-created `.claude/agents/` files aren't spawnable mid-session

**Triggering project:** vitals, Ticket 19 — the first live test of the
Expediter independence fix.

**What happened:** vitals never actually had its Claude Code adapter
files generated (`CLAUDE.md`, `.claude/agents/`) — only symlinked and
given a Mise en Place. Generated them mid-session specifically to spawn a
real `expediter` subagent for Ticket 19's Expedite stage. The Agent tool
call failed: `Agent type 'expediter' not found. Available agents: ...` —
the newly-written file wasn't recognized as a `subagent_type` option in
the already-running session.

**Why the gap existed:** the Claude Code adapter documented spawning
`.claude/agents/*.md` role files as subagents without ever having been
exercised against a project whose adapter files were generated *during*
the same session that then tried to use them — every prior use assumed
the adapter was already in place from a previous session.

**Fix:** didn't change the underlying mechanism (nothing to fix there —
this is a real Claude Code session-lifecycle behavior, not a bug in the
adapter's design). Documented the limitation and its workaround directly
in `adapters/claude-code/README.md`: fall back to `general-purpose` with
the role file's content given directly in the spawn prompt for the
current session (still achieves genuine context isolation), and
regenerate + start a fresh session for the real named-type version going
forward.

**Files changed:** `adapters/claude-code/README.md`.

## 2026-08-13 — Expediter reviewing its own work in the same context

**Triggering project:** vitals, discovered mid-conversation while
reviewing how Tickets 1–10 had actually been executed, not from a single
specific Ticket's failure.

**What happened:** Every Expedite stage across vitals' first ten Tickets
ran in the same conversation that had just finished Fire and Plate for
that Ticket — a role switch, not an independent review. The Expediter
therefore always had full memory of its own implementation reasoning
going into the "independent" check.

**Why the gap existed:** `.claude/agents/expediter.md` existed in the
Claude Code adapter from the start, but nothing in `THE_PASS.md` or the
adapter actually instructed spawning it as a real subagent — the mapping
was documented but never exercised, so the same-context version became
the default by omission.

**Fix:** `THE_PASS.md`'s Expedite stage and `roles/expediter.md` now state
the independence requirement directly, at the source. The Claude Code
adapter (`README.md` + `CLAUDE.md.template`) now instructs actually
calling the Agent tool with the `expediter` subagent, given only the
Ticket and the diff. The Cursor adapter's default recommendation flipped
from "same-session role-switch, fine for solo projects" to "separate
chat by default" — Cursor has no subagent primitive, so this is a weaker
approximation, documented as such rather than presented as equivalent.

**Files changed:** `core/THE_PASS.md`, `core/roles/expediter.md`,
`adapters/claude-code/README.md`, `adapters/claude-code/CLAUDE.md.template`,
`adapters/cursor/README.md`, `adapters/cursor/cursorrules.template`.
