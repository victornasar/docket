# Ticket: Document `tests:` Evidence in the self-review recipe

**Status:** in-review
**Owner (Implementer):** Claude
**Retry count:** 0
**Related project audit:** N/A — this repo
**Baseline:** 811822c2578264f92c787494cf3515057609a0cf
**Worktree:**

## Problem

Ticket 009 added `tests:` as an alternative to prose `evidence:`. The ticket template, WORKFLOW.md and the tooling README describe it. `core/recipes/recipe-self-review.md`, which the template names as the "Schema source of truth", does not. Its step 3 still lists only `method`, `how`, `result`, `evidence`.

## Approach

1. In step 3 of `recipe-self-review.md`, add `tests:` as the alternative to `evidence:` for `method: test`. Use one test title per line, copied as it appears in the verify log.
2. Copy over the matching rules the tooling README already states: plain substring match, a passed line must exist, and missing, failed or skipped titles fail. Also copy the advice to use full, unique titles (for pytest, the `path::name` ID). Link to the README instead of repeating it if the passage gets long.
3. Add one short worked AC block that uses `tests:`.
4. In the checklist near the end, note that `check-evidence` also checks `tests:` titles against the attested log.

## Files touched

- core/recipes/recipe-self-review.md

## Acceptance criteria

- [ ] AC-1: The recipe names `tests:` as a valid alternative to `evidence:` and gives the passed/missing/failed/skipped rule. (read)
- [ ] AC-2: The recipe includes an example AC block using `tests:` that matches the ticket template's form. (read)
- [ ] AC-3: Nothing in the recipe contradicts `tooling/README.md` or `core/templates/ticket.template.md` on `tests:`. (read)

## Rollback plan

Revert the commit.

## Rules check

Docs only. Nothing here triggers BLOCK or CONFIRM.

## Evidence

### Project verify

```text
command: tooling/.venv/bin/pytest -v -p no:cacheprovider tooling
exit: 0
log: .docket/verify/012-document-tests-evidence-in-recipe-20261015T203102Z.log
ran_at: 2026-10-15T20:31:02Z
git_head: 811822c2578264f92c787494cf3515057609a0cf
tree_fingerprint: 481edd694dc07061f67c5e03822c6aa973d678b91aee7ef1a8e7dd50f3af2ab3
attestation: .docket/verify/012-document-tests-evidence-in-recipe-20261015T203102Z.json
```

### Acceptance criteria

```text
id: AC-1
criterion: The recipe names tests: as a valid alternative to evidence: and gives the passed/missing/failed/skipped rule
method: manual
how: read core/recipes/recipe-self-review.md step 3 and "Evidence by test reference"
result: pass
evidence: step 3 points to the new section; section states pass only on a passed line, fail naming the title when missing/failed/skipped
notes:

id: AC-2
criterion: The recipe has an example AC block using tests: matching the ticket template's form
method: manual
how: compare the recipe example against core/templates/ticket.template.md AC-2
result: pass
evidence: same fields in the same order (id, criterion, method, how, result, tests: with "- " lines)
notes:

id: AC-3
criterion: Nothing in the recipe contradicts tooling/README.md or the ticket template on tests:
method: manual
how: read the three side by side
result: pass
evidence: wording and example follow tooling/README.md "Evidence by test reference"; runner formats are linked, not restated, so they can't drift
notes:
```

### Scope review

```text
diff_vs_files_touched: match
extras: none
justified: n/a
notes:
```

## Notes for the Reviewer
