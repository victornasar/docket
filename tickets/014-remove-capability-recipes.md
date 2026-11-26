# Ticket: Remove the capability recipes from `core/`

**Status:** approved
**Owner (Implementer):** Claude
**Retry count:** 0
**Related project audit:** N/A — this repo
**Baseline:** (set when the Ticket starts)
**Worktree:**

## Problem

Docket owns trust: whether work stayed inside an approved Ticket and has current evidence. Six of its eight recipes teach how to do the engineering instead: code review, diagnosis, domain modeling, program design, TDD, and ticket writing. The owner reports they are no longer used. They still load into every attached project, because the roles, the workflow, and the Ticket template link to them. That puts a second, drifting source of coding guidance into the same context as whatever capability layer the project uses (for example Hechent).

The other two recipes are not capability. `recipe-self-review.md` defines the Evidence contract that `check-evidence` enforces, is named "Schema source of truth" by the Ticket template, and is printed by `review-packet`. `recipe-safe-migration.md` is what `RULES.md` §4 points to for migrations. Both stay.

No incident triggered this. It is a subtraction backed by the owner's report that the recipes are unused, logged in the changelog as `LINE_MEETING.md` requires for removals.

## Approach

1. Delete the six capability recipes:
   - `core/recipes/recipe-code-review.md`
   - `core/recipes/recipe-diagnosis.md`
   - `core/recipes/recipe-domain-modeling.md`
   - `core/recipes/recipe-program-design.md`
   - `core/recipes/recipe-tdd.md`
   - `core/recipes/recipe-ticket-writing.md`
2. Keep `recipe-self-review.md` and `recipe-safe-migration.md` where they are. Moving them would add structural files to the frozen spine, and would break `review-packet` and external tools that reference the self-review path.
3. Remove every link to a deleted recipe, keeping the rule the link supported:
   - `core/WORKFLOW.md` Stage 1: drop the parenthetical link; the criterion already says what a checkable AC is.
   - `core/roles/planner.md`: for bugs with no known cause, still require a confirmed root cause and a repro command before writing the Ticket, without the link. Keep "ask about terminology drift", drop the glossary pointer. Keep "go one level below architecture" for new types and flows, drop the link. Drop the "worked example" line.
   - `core/roles/implementer.md`: drop the TDD sentence. Bug-fix Tickets: the repro named in the Ticket's Problem becomes a regression test before the fix.
   - `core/roles/reviewer.md` step 7: keep the separate Standards pass and the rule that a Standards finding alone sends back only when severe; drop the link.
   - `core/templates/ticket.template.md`: point the header comment at `core/roles/planner.md` instead of the ticket-writing recipe; reword the Problem and Approach comments so they don't name deleted recipes.
4. `core/LINE_MEETING.md`: replace the "`recipes/` is the one exception" sentence. `recipes/` now holds only the trust procedures (self-review, safe migration) and follows the same freeze as the rest of the spine. Capability guidance does not belong in Docket.
5. `skills/README.md`: "point into Docket recipes" becomes "point into Docket's core documents".
6. Add a `core/CHANGELOG.md` entry: date, "no triggering incident; removal per owner report that the recipes are unused", what was removed and kept, files changed.
7. Add Ticket 014 to `tickets/README.md`.

Out of scope: tooling changes, the Evidence schema, the two kept recipes' contents, `README.md` (its tree line "recipes" stays accurate), past Tickets and past changelog entries that mention deleted recipes (they are history).

## Files touched

- core/recipes/recipe-code-review.md
- core/recipes/recipe-diagnosis.md
- core/recipes/recipe-domain-modeling.md
- core/recipes/recipe-program-design.md
- core/recipes/recipe-tdd.md
- core/recipes/recipe-ticket-writing.md
- core/WORKFLOW.md
- core/roles/planner.md
- core/roles/implementer.md
- core/roles/reviewer.md
- core/templates/ticket.template.md
- core/LINE_MEETING.md
- core/CHANGELOG.md
- skills/README.md
- tickets/README.md

## Acceptance criteria

- [ ] AC-1: The six capability recipe files no longer exist; `recipe-self-review.md` and `recipe-safe-migration.md` exist unchanged. (command: `ls core/recipes` and `git diff --stat <Baseline> -- core/recipes/recipe-self-review.md core/recipes/recipe-safe-migration.md`)
- [ ] AC-2: No file outside `tickets/` and `core/CHANGELOG.md` mentions a deleted recipe. (command: `grep -rnE "recipe-(code-review|diagnosis|domain-modeling|program-design|tdd|ticket-writing)" --exclude-dir=tickets --exclude-dir=.git . | grep -v core/CHANGELOG.md` prints nothing)
- [ ] AC-3: The rules those links supported are still stated: Planner requires a confirmed root cause and repro before a bug Ticket; Implementer turns that repro into a regression test before the fix; Reviewer keeps a separate Standards pass that sends back alone only when severe. (manual: read the three role files)
- [ ] AC-4: `LINE_MEETING.md` no longer allows adding capability recipes, and `CHANGELOG.md` has an entry for this removal naming the removed and kept files. (manual)
- [ ] AC-5: The tooling test suite passes unchanged. (test: Project verify)

## Rollback plan

Revert the commit. The deleted files come back with it; nothing outside the repo changes.

## Rules check

- Deleting files under `core/` is **CONFIRM** (RULES §2). Approving this Ticket names the six files, but the Implementer still asks for an explicit yes immediately before deleting them.
- Editing `core/` is gated by `LINE_MEETING.md`: the owner's sign-off before editing, and a changelog entry. Approval of this Ticket is that sign-off; step 6 is the entry.
- Work goes on a branch, not `main` (RULES §1).
- Nothing BLOCK.

## Evidence

### Project verify

```text
command:
exit:
log:
ran_at:
git_head:
tree_fingerprint:
attestation:
```

### Acceptance criteria

```text
id: AC-1
criterion:
method:
how:
result:
evidence:
notes:
```

### Scope review

```text
diff_vs_files_touched:
extras:
justified:
notes:
```

## Notes for the Reviewer

External dependency to check after Done, not part of this Ticket: Hechent's `DOCKET-INTEGRATION.md` references `core/recipes/recipe-self-review.md` (kept, so unaffected) and lists the recipe overlap as open question 1 (resolved by this Ticket). Hechent updates its side separately.
