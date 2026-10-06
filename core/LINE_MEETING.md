# Changing this kit

**The structural spine is frozen.** `RULES.md`, `WORKFLOW.md`, `roles/`,
and `templates/` get no new stages, roles, rule sections, or structural
files until at least three more projects — varied stack, scale, and
ideally operator — have run the kit end to end. `recipes/` is the one
exception: a new recipe may be added if it's adapted from an established
external source or proven on real work, never invented speculatively.
`CHANGELOG.md` records which projects count toward the three.

## Freeze exceptions

Exceptions are rare, named, and narrow. They do not lift the freeze
generally. After the permitted edits land, the spine is frozen again.

### 2026-10-06 — Stage 1 evidence-backed Done

**Exception granted** for Stage 1 evidence-backed Done because the existing
trust model lacked an explicit proof/evidence state: Done was a workflow
state ("Reviewer said Pass") rather than an evidence state. Grounded in
the 2026-10 agent-trust audit and earlier vitals incidents where
implementation could diverge from expectations without recorded proof.

**Permitted under this exception only:**
- Ticket Evidence structure
- Self-review / Reviewer / Done exit criteria for evidence
- Project Audit verification-command structure
- Matching role, recipe, adapter, and README documentation of the trust model

**Not permitted under this exception:** new stages or roles; Ticket redesign
beyond Evidence; parallelism/orchestration; telemetry; databases;
deterministic tooling (`check-scope`, etc.); outer-loop automation.

See [`CHANGELOG.md`](CHANGELOG.md) entry dated 2026-10-06. After that
change set, the structural spine is frozen again under the policy above.

### 2026-10-06 — Stage 2 deterministic trust gates

**Exception granted** (narrow) to wire Stage 2 tooling into the Evidence /
Done / Self-review / Reviewer docs and Ticket Project-verify fields
(`git_head`, `tree_fingerprint`, `attestation`, **Baseline:**), without
new workflow stages or roles. Adds executable `tooling/` + `bin/docket`.
Does not productionize parallelism or expand into pstack.

See [`CHANGELOG.md`](CHANGELOG.md) Stage 2 entry. Spine frozen again after.

### 2026-10-06 — Stage 3 pre-review habit

**Exception granted** (narrow) for WORKFLOW / role / adapter / recipe text
making `docket pre-review` the mandatory Self-review → Review handoff, plus
`review-packet` for fresh-context Review. No new stages/roles. No Evidence
schema redesign. Spine frozen again after.

---

Any change to `core/` still has to trace to a real incident on real work,
not a brainstormed improvement. To make one: **name the incident** (which
project, which Ticket, what gap, what would have gone differently with the
fix); **propose the specific fix** (which file, what change, why this
scope) and get the human's sign-off *before* editing `core/`; then **log
it in [`CHANGELOG.md`](CHANGELOG.md)** — date, triggering project/Ticket,
what changed, which files.

If the same category of weakness recurs after a logged fix, that's a new
entry referencing the old one — the first fix missed the root cause.
Subtraction runs the same way: any rule or recipe not triggered across the
next three projects is a candidate for deletion, and the removal is logged
exactly like an addition.
