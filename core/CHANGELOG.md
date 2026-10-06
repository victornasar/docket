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

## 2026-10-06 — Stage 3: pre-review gates as the default inner loop

**Triggering project:** Docket kit (Stage 2 complete; adversarial leftover
was habit — agents could skip gates before Review).

**What happened:** Tooling existed, but skill/adapters did not make
verify → check-scope → check-evidence the mandatory default handoff.
Cursor Review still risked depending on chat memory.

**Fix:** `docket pre-review` (ordered gates; non-zero blocks handoff);
`docket review-packet` for fresh-context Review discovery; skill,
self-review recipe, WORKFLOW, roles, and both adapters require
pre-review before Review. No Evidence schema redesign. No CI in this
template repo (documented why). Semantic adequacy remains Reviewer/human.

**Files changed:** `tooling/docket/pre_review.py`, `review_packet.py`,
`cli.py`, `tooling/tests/test_pre_review.py`, `tooling/README.md`,
`skills/verify-with-evidence/SKILL.md`, `core/recipes/recipe-self-review.md`,
`core/WORKFLOW.md`, roles, adapters, this changelog.

---

## 2026-10-06 — Stage 2: mechanical trust gates (verify / scope / evidence)

**Triggering project:** Docket kit (adversarial audit of Stage 1). Stage 1
made Done an evidence state in prose, but an adversarial agent could still
type `exit: 0`, omit ACs, leave scope, or reuse stale green runs.

**What happened:** Evidence was forgeable Markdown. Scope was eyeballed.
No command actually captured Project Audit verification.

**Fix:** Python CLI under `tooling/` + `bin/docket`:

- `docket verify` — runs Audit canonical command; writes log + attestation
  (`exit`, `git_head`, `tree_fingerprint`)
- `docket check-scope` — diff since Ticket **Baseline** ⊆ Files Touched
- `docket check-evidence` — structural Evidence + Markdown must match
  attestation + freshness (stale after implementation edits)

Ticket Project verify fields extended for attestation binding. Reviewer
wording clarified: spot-check re-runs ≠ inventing Evidence. pytest suite
in `tooling/tests/`. Does **not** prove AC adequacy (Reviewer judgment).

**Files changed:** `tooling/**`, `bin/docket`, `core/WORKFLOW.md`,
`core/templates/ticket.template.md`, roles, `recipe-self-review.md`,
`skills/verify-with-evidence/SKILL.md`, `README.md`, adapters/setup as
needed, `LINE_MEETING.md`, this changelog.

---

## 2026-10-06 — Done was a process state, not an evidence state

**Triggering project:** Docket kit itself (agent-trust audit, 2026-10-06),
grounded also in vitals Ticket 19 and related review incidents where
implementation could satisfy a narrative Self-review without recorded
proof, and where shape/spec misses were caught only after expensive
independent review cycles.

**What happened:** `WORKFLOW.md` defined Done as criteria "verifiably met"
and "a human can merge without re-checking," but Self-review and Review
only required checklist prose — no Ticket schema for criterion → method →
result → evidence. Agents could claim success; Reviewers could pass on
code that "looked right." Scope was reviewed by eye (`git diff --stat`),
not mechanically. Trust came from process and instruction-following.

**Why the gap existed:** the kit optimized for specify → constrain →
review, and never made "prove" a first-class handoff artifact. Recipes
said "check against the actual result" without a place to record that
check. No freeze-exception path had been used for a trust-model fix.

**Fix (Stage 1 — schema + workflow only; narrow freeze exception in
[`LINE_MEETING.md`](LINE_MEETING.md)):** Ticket Evidence section; Project
Audit Verification commands; Self-review / Implementer / Reviewer /
WORKFLOW Done require recorded evidence; Reviewer audits evidence and
send-backs when it is missing or inadequate; thin
`skills/verify-with-evidence` skill points at the self-review recipe.
Scope remains manually reviewed (Stage 2 will add deterministic
`check-scope`). No claim of mechanical enforcement.

**Files changed:** `core/LINE_MEETING.md`, `core/WORKFLOW.md`,
`core/templates/ticket.template.md`,
`core/templates/project-audit.template.md`,
`core/roles/implementer.md`, `core/roles/reviewer.md`,
`core/roles/planner.md`, `core/recipes/recipe-self-review.md`,
`core/recipes/recipe-ticket-writing.md`,
`core/recipes/recipe-code-review.md`, `README.md`,
`adapters/claude-code/CLAUDE.md.template`,
`adapters/claude-code/README.md`,
`adapters/cursor/cursorrules.template`,
`adapters/cursor/README.md`, `skills/verify-with-evidence/SKILL.md`
(new), `skills/README.md` (new), `setup/attach.md`.

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
