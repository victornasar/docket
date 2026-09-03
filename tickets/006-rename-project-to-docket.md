# Ticket: Rename the project from Tabouleh to Docket

**Status:** draft
**Owner (Implementer):**
**Retry count:** 0
**Related project audit:** N/A — this repo
**Worktree:** (blank)

**Depends on:** 001–005 (the whole docs release — this renames on top of
the repositioned README, plain-term `core/`, and `advanced/` layout).

## Problem

The grill kept the name "Tabouleh" as a no-cost codename (Q4, Q16). On
reflection the food word reads as arbitrary now that the kitchen-brigade
vocabulary is gone, and a name that *means* something related to the work
is worth more. Decision: rename to **Docket** — a docket is the agenda of
matters to be handled plus the record of what was decided on each, which
is exactly what this kit is (a Ticket is a docket entry; `CHANGELOG.md` is
the record). Same reasoning as the Q10 vocab rename applies to timing:
cheaper now than after the vendored-copy tooling bakes the name into the
directory convention and the `attach` script.

## Approach

1. **Prose:** every "Tabouleh" → "Docket" across `README.md`, `core/`,
   `adapters/`, `setup/` — titles, sentences, the recipe attribution lines
   ("reworked into Tabouleh's own words" → "Docket's own words", ×5).
2. **Path convention:** the vendored/symlinked directory is referred to as
   `tabouleh/` in several places — `core/RULES.md` §2 ("any file under
   `tabouleh/core/` or `tabouleh/adapters/`"), the `README.md` repo-map
   tree root, both adapter READMEs, `CLAUDE.md.template`, `setup/attach.md`.
   All → `docket/`.
3. **Placeholder:** `<TABOULEH_PATH>` → `<DOCKET_PATH>` in
   `adapters/claude-code/CLAUDE.md.template` and
   `adapters/cursor/cursorrules.template` (11 occurrences).
4. **Cursor frontmatter:** `description: Tabouleh workflow and safety
   rules` → `description: Docket workflow and safety rules`.
5. **`core/CHANGELOG.md`:** dated historical entries are **not** edited
   (they name "Tabouleh" as the project was then called — still
   recognizable). Add one line to the existing "Vocabulary note" block:
   "The project was renamed from Tabouleh to Docket on <date>." The intro
   description paragraph (not a dated entry) gets "Tabouleh" → "Docket".
6. **Out of repo — human steps, do NOT attempt from here, list them in the
   handoff:**
   - GitHub repo rename `victornasar/tabouleh` → `victornasar/docket`, then
     `git remote set-url origin …/docket.git`.
   - Rename the local working-tree folder `…/Active/tabouleh` → `…/Active/docket`.
   - The `~/.claude/skills/attach-tabouleh/` skill (separate artifact,
     not in this repo) needs renaming to `attach-docket` with its
     `SKILL.md` updated.

## Files touched

- `README.md`
- `core/RULES.md`
- `core/CHANGELOG.md` (intro paragraph + one line in the Vocabulary note; dated entries untouched)
- `core/templates/project-audit.template.md`
- `core/recipes/recipe-code-review.md`
- `core/recipes/recipe-diagnosis.md`
- `core/recipes/recipe-domain-modeling.md`
- `core/recipes/recipe-program-design.md`
- `core/recipes/recipe-tdd.md`
- `adapters/claude-code/README.md`
- `adapters/claude-code/CLAUDE.md.template`
- `adapters/cursor/README.md`
- `adapters/cursor/cursorrules.template`
- `setup/attach.md`

## Acceptance criteria

- [ ] `README.md`'s H1 is `# Docket`.
- [ ] `grep -rIn -e "Tabouleh" -e "TABOULEH" -e "tabouleh" .` (excluding
      `tickets/` and `.git/`) returns matches **only** inside
      `core/CHANGELOG.md`'s dated historical entries.
- [ ] `<TABOULEH_PATH>` appears nowhere; `<DOCKET_PATH>` appears in both
      templates and every reference resolves the same way it did before.
- [ ] The `tabouleh/` path convention is `docket/` everywhere it appears
      (`core/RULES.md` §2, `README.md` repo map, both adapter READMEs,
      `CLAUDE.md.template`, `setup/attach.md`).
- [ ] Every markdown link across `README.md`, `core/**`, `advanced/**`,
      `adapters/**`, `setup/**` still resolves.
- [ ] `core/CHANGELOG.md` dated entries are byte-identical to before; the
      only changes are the intro paragraph and one added line in the
      Vocabulary note.
- [ ] Handoff notes list the four out-of-repo human steps from Approach §6.

## Rollback plan

Single commit. `git revert <sha>` restores every "Tabouleh" and the
`<TABOULEH_PATH>` placeholder. The out-of-repo steps (GitHub repo name,
remote URL, local folder, the attach skill) are done by the human and
reverted by the human — this Ticket's commit does not touch them.

## Rules check

- No BLOCK action. Editing files under `core/` and `adapters/` is
  CONFIRM-gated (RULES.md §2) — Ticket approval covers the enumerated
  files. `README.md` / `setup/` edited under the same approval.
  Read-before-write observed. The repo/remote rename is explicitly a human
  step, not performed here.

## Notes for the Reviewer

<Filled during Self-review.>
