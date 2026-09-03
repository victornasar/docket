# Ticket: Rename kitchen vocabulary to plain terms across `core/`

**Status:** done
**Owner (Implementer):** Claude (this session)
**Retry count:** 0
**Related project Mise en Place:** N/A — Tabouleh's own repo, no project-level audit
**Worktree:** (leave blank — one ticket at a time)

## Problem

Tabouleh's documents are written in a kitchen-brigade metaphor (Executive
Chef, Line Cook, Expediter, "Fire it", "Plate", "The Pass", "Mise en
Place", "Walk-in"). A grilling session established that the metaphor is a
net cost now that the kit is single-operator: it adds an indirection layer,
the README spends three paragraphs plus a decode table apologising for it,
and it is the biggest reason the kit reads as idiosyncratic rather than
adoptable. The decision (grill Q4, Q16) is to demote the metaphor to a
one-line analogy and use plain terms everywhere. This ticket does the
rename inside `core/` only; `README.md`, `adapters/`, and `setup/` are a
separate ticket (005) so the "we renamed everything" diff and the
"we repositioned the project" diff stay reviewable apart.

The project name "Tabouleh" stays — it is branding, not vocabulary, and
carries no comprehension tax.

## Approach

1. **Apply this term mapping** (agreed at grill; Implementer applies it
   verbatim, does not invent alternatives):

   | Current | New |
   |---|---|
   | Executive Chef | Planner |
   | Line Cook | Implementer |
   | Expediter | Reviewer |
   | Kitchen Brigade | the roles |
   | Kitchen Rules / `KITCHEN_RULES.md` | Rules / `RULES.md` |
   | The Pass / `THE_PASS.md` | the workflow / `WORKFLOW.md` |
   | Stage "Ticket" | Ticket (unchanged — already plain) |
   | Stage "Fire" / "Fire it" | Implement / "start implementation" |
   | Stage "Plate" | Self-review |
   | Stage "Expedite" | Review |
   | Stage "Serve" / "served" | Done / "done" |
   | Mise en Place / `mise-en-place.template.md` | Project Audit / `project-audit.template.md` |
   | Walk-in | Project Context |
   | "harness" (as a category noun) | "workflow kit" / "kit" |
   | Recipe / `recipe-*.md` | Recipe (kept — common software usage, not brigade jargon) |
   | Ticket | Ticket (kept) |

2. **Rename files with `git mv`** (preserve history):
   - `core/KITCHEN_RULES.md` → `core/RULES.md`
   - `core/THE_PASS.md` → `core/WORKFLOW.md`
   - `core/roles/executive-chef.md` → `core/roles/planner.md`
   - `core/roles/line-cook.md` → `core/roles/implementer.md`
   - `core/roles/expediter.md` → `core/roles/reviewer.md`
   - `core/templates/mise-en-place.template.md` → `core/templates/project-audit.template.md`
   - `core/PARALLEL_LINE.md`, `core/LINE_MEETING.md`, `core/recipes/*` keep
     their filenames; only their contents get the term mapping.

3. **Update every in-file reference** in all `core/**` files (links,
   section headings, prose) to the new names and terms per the mapping.
   Includes the recently-added `core/recipes/recipe-diagnosis.md`.

4. **`core/CHANGELOG.md` is not rewritten.** Its entries are a historical
   log of what happened, in the words used at the time. Add one line at
   the top of the file: "Entries dated before this rename use the earlier
   kitchen-brigade vocabulary — Executive Chef = Planner, Line Cook =
   Implementer, Expediter = Reviewer, The Pass = the workflow, Mise en
   Place = Project Audit." Leave the historical entries untouched.

5. **Do not change structure, rules content, or workflow behaviour.** This
   is a rename only. `RULES.md` still has the same rules (ticket 002 cuts
   them); `WORKFLOW.md` still has the same five stages and exit criteria
   (ticket 006 adjusts behaviour). If a sentence only makes sense because
   of the metaphor ("a cook checking a dish before it goes to the pass"),
   rewrite it to plain phrasing with the same meaning — flag any such
   rewrites in the handoff notes so the Reviewer checks meaning was
   preserved.

## Files touched

- `core/KITCHEN_RULES.md` → `core/RULES.md` (rename + term update)
- `core/THE_PASS.md` → `core/WORKFLOW.md` (rename + term update)
- `core/roles/executive-chef.md` → `core/roles/planner.md` (rename + term update)
- `core/roles/line-cook.md` → `core/roles/implementer.md` (rename + term update)
- `core/roles/expediter.md` → `core/roles/reviewer.md` (rename + term update)
- `core/templates/mise-en-place.template.md` → `core/templates/project-audit.template.md` (rename + term update)
- `core/templates/ticket.template.md` (term update)
- `core/PARALLEL_LINE.md` (term update only)
- `core/LINE_MEETING.md` (term update only)
- `core/CHANGELOG.md` (add one vocabulary-note line at top; entries untouched)
- `core/recipes/recipe-code-review.md` (term update)
- `core/recipes/recipe-diagnosis.md` (term update)
- `core/recipes/recipe-domain-modeling.md` (term update)
- `core/recipes/recipe-program-design.md` (term update)
- `core/recipes/recipe-safe-migration.md` (term update)
- `core/recipes/recipe-self-review.md` (term update; title drops "(Plate)")
- `core/recipes/recipe-tdd.md` (term update)
- `core/recipes/recipe-ticket-writing.md` (term update)

## Acceptance criteria

- [ ] `grep -rIn -e "Executive Chef" -e "Line Cook" -e "Expediter" -e "Kitchen Rules" -e "KITCHEN_RULES" -e "THE_PASS" -e "The Pass" -e "Mise en Place" -e "mise-en-place" -e "Walk-in" -e "Fire it" -e "Kitchen Brigade" core/` returns no matches **except** inside the dated historical entries of `core/CHANGELOG.md`.
- [ ] The six file renames listed above are present in `git status` as renames (`R`), not delete+add.
- [ ] Every intra-`core/` markdown link resolves (no link points at an old filename). Verify by checking each `](...)` target in `core/**` exists.
- [ ] `core/WORKFLOW.md` still documents exactly five stages with the same exit criteria as before — diff shows term substitutions and metaphor-sentence rephrasings only, no criterion added, removed, or reworded in substance.
- [ ] `core/RULES.md` still contains the same rule rows as the old `KITCHEN_RULES.md` — no rule content changed (that is ticket 002).
- [ ] `core/CHANGELOG.md` has the vocabulary-note line at the top and its historical entries are byte-identical to before otherwise.
- [ ] Handoff notes list every sentence that was rephrased (not just term-substituted) so the Reviewer can confirm meaning was preserved.

## Rollback plan

Single commit. `git revert <sha>` (or `git reset --hard` to the prior sha
if not yet pushed) restores the previous filenames and vocabulary
wholesale. No data migration, no external dependency.

## Rules check

- No action in the BLOCK table. Editing/renaming files under `core/` is
  CONFIRM-gated (Rules §2) — this ticket's approval is that confirmation
  for the enumerated files. `git mv` is a tracked rename, not a delete.
  No overwriting a file without reading it (§2): Implementer reads each
  file before editing.
- CONFIRM step expected during work: none beyond the ticket approval
  itself, provided the Implementer stays within Files Touched.

## Notes for the Reviewer

<Filled during Self-review, not now.>
