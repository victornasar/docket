# Ticket: <short title>

<!--
Filled out by the Planner before any code is written. See
core/recipes/recipe-ticket-writing.md for guidance and a worked example.
Do not remove sections; write "N/A" with a one-line reason if genuinely
not applicable.
-->

**Status:** draft | approved | in-progress | in-review | send-back | done
**Owner (Implementer):**
**Retry count:** 0
**Related project audit:** <link, if applicable>
**Baseline:** <git commit SHA at Ticket start — required for `docket check-scope`>
**Worktree:** <branch name, only if started under advanced/PARALLEL_LINE.md — leave blank otherwise>

## Problem

<What's actually wrong or missing — not a restatement of the request. One
or two sentences a reader unfamiliar with the request would understand.
For a bug or performance Ticket, this states the confirmed root cause and
names the repro command from core/recipes/recipe-diagnosis.md — not just
the symptom. If the cause is still unknown, the Ticket isn't ready.>

## Approach

<Numbered steps, concrete enough that an Implementer can follow them
without re-deriving the design. Name specific functions/modules/endpoints
where known. If this introduces a new type, a new data-transformation
boundary, or a call-flow change, include the field/type mapping or
call-stack sketch from core/recipes/recipe-program-design.md here — not
every Ticket needs this, only ones with a new shape to get wrong.>

1.
2.
3.

## Files touched

<Real file paths, not directory-level guesses.>

-

## Acceptance criteria

<Checkable statements, not descriptions. Each one should have a clear
yes/no answer once checked. Number them AC-1, AC-2, … so Evidence can
refer to them. Optionally note an intended verify method in parentheses
when obvious — the Implementer records actual execution in Evidence.>

- [ ] AC-1:
- [ ] AC-2:
- [ ] AC-3:

## Rollback plan

<How this gets undone if it needs to be. "Revert the commit" is sufficient
for most simple code changes — say so explicitly. Anything touching Rules
categories (migrations, dependencies, production, deletions) needs a
specific plan — see core/recipes/recipe-safe-migration.md for the
migration case.>

## Rules check

<Confirm the approach above doesn't require anything RULES.md marks BLOCK.
Note anything that will need a CONFIRM step during implementation, so it
isn't a surprise mid-Ticket.>

## Evidence

<!--
Filled during Self-review by the Implementer. Leave blank at Ticket
approval. Schema source of truth: core/recipes/recipe-self-review.md.
An agent's claim is not evidence. Evidence is what allows the system to
trust the claim.
-->

### Project verify

```text
command: <from `docket verify` — not typed by hand>
exit: <from `docket verify` attestation>
log: <path written by `docket verify`>
ran_at: <ISO timestamp from attestation>
git_head: <from attestation>
tree_fingerprint: <from attestation>
attestation: <.docket/verify/….json from `docket verify`>
```

### Acceptance criteria

```text
id: AC-1
criterion: <copy of the criterion>
method: test | command | manual | artifact
how: <exact command or steps>
result: pass | fail | n/a
evidence: <path, output excerpt, or artifact>
notes: <optional>

id: AC-2
criterion:
method:
how:
result:
evidence:
notes:
```

### Scope review

```text
diff_vs_files_touched: match | extras | missing
extras: <paths not on Files Touched, or none>
justified: yes | no | n/a
notes: <if extras, why — or revert before Review>
```

<!--
Stage 2: run `docket check-scope <ticket>` (uses Baseline + Files Touched).
tickets/ and .docket/ are auto-allowed. Scope review fields above remain for
the handoff; the CLI is the mechanical gate.
-->

## Notes for the Reviewer

<Optional extras beyond Evidence — deviations from Approach with
justification, CONFIRM log, open questions. Evidence above is required;
this section is for anything else the Reviewer should know.>
