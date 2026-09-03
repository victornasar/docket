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
yes/no answer once checked.>

- [ ]
- [ ]
- [ ]

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

## Notes for the Reviewer

<Filled in during Self-review, not now — left blank at Ticket-approval time.>
