# Ticket: Compress the Line Meeting and declare the `core/` freeze

**Status:** done
**Owner (Implementer):** Claude (this session)
**Retry count:** 0
**Related project Mise en Place:** N/A — Tabouleh's own repo
**Worktree:** (blank)

**Depends on:** 001 (needs post-rename vocab in `LINE_MEETING.md`).

## Problem

Two connected decisions from the grill:

- **Q18:** `LINE_MEETING.md` is an 87-line formal governance procedure
  (postmortem capture, Ticket-level fix specificity, human-approval gate,
  changelog logging, recurrence handling) for amending the kit from
  incidents. For a one-person project at ~1 attached codebase that is
  heavier than the thing it governs. Compress it to a short "Changing
  this kit" section — keep the ideas (changes trace to real incidents not
  vibes; there is a subtraction rule), drop the ceremony. It can grow
  back into its own file if a second operator ever joins.
- **Q3 / Q9:** `core/`'s structural spine is frozen — no new layers until
  at least three more structurally different projects (different stack,
  scale, ideally a different operator) have run the kit end to end.
  Recipes are the one sanctioned growth surface, and unused recipes/rules
  are pruning candidates. This freeze needs to be written down somewhere
  or it is not real.

## Approach

1. **Rewrite `core/LINE_MEETING.md`** as a ~15–20 line section titled
   "Changing this kit". Content:
   - Changes to `core/` trace to a real incident on real work, not a
     brainstormed improvement. Name the incident, propose the specific
     fix (which file, what change, why this scope), get the human's
     sign-off before editing `core/`, log it in `CHANGELOG.md` (date,
     triggering project/Ticket, what changed, files).
   - If the same category of weakness recurs after a logged fix, that is
     a new entry referencing the old one — the first fix missed the root
     cause.
   - **Subtraction rule:** any rule or recipe not triggered across the
     next three projects is a candidate for deletion. Removals are logged
     the same way as additions.
   - Keep the file at `core/LINE_MEETING.md` (rename the *title* inside,
     not the filename — filename churn for no gain; a later ticket can
     rename the file if desired).
2. **Add the freeze declaration.** Put it at the top of the "Changing
   this kit" file as its own short paragraph:
   - The structural spine — `RULES.md`, `WORKFLOW.md`, `roles/`,
     `templates/` — is frozen. No new stages, roles, rules-sections, or
     structural files until ≥3 more projects (varied stack / scale /
     operator) have completed end-to-end runs.
   - `recipes/` is the exception: new recipes may be added if adapted
     from an established external source or proven on real work — not
     invented speculatively.
   - `CHANGELOG.md` records which projects count toward the three.
3. **Update references** to `LINE_MEETING.md` across `core/**` and check
   `CHANGELOG.md`'s header line that points at it still reads correctly
   after the retitle. (`README.md` references are ticket 005.)
4. `CHANGELOG.md` entries themselves are not touched (same principle as
   001 — historical log).

## Files touched

- `core/LINE_MEETING.md` (full rewrite of body; filename kept)
- `core/CHANGELOG.md` (only if its top-of-file description references the
  Line Meeting in a way the retitle breaks — otherwise untouched)
- Any `core/**` file linking to `LINE_MEETING.md` (grep; update link text
  if it said "The Line Meeting")

## Acceptance criteria

- [ ] `core/LINE_MEETING.md` is ≤25 lines, titled "Changing this kit",
      and still contains: incident-grounded changes, human sign-off before
      editing `core/`, changelog logging, recurrence-as-new-entry, and the
      subtraction rule.
- [ ] The freeze declaration is present, names the frozen spine files
      explicitly, states the ≥3-projects condition, and carves out
      `recipes/` with its "external source or proven" condition.
- [ ] `grep -rn "LINE_MEETING\|Line Meeting" core/` — every hit resolves
      and reads correctly with the new title.
- [ ] `CHANGELOG.md`'s historical entries are unchanged.
- [ ] The old procedure's five numbered steps are gone as *ceremony* but
      their intent is traceable in the compressed version — handoff notes
      map old-step → where-it-landed (or "dropped, because…").

## Rollback plan

Single commit. `git revert <sha>` restores the full 87-line
`LINE_MEETING.md` and removes the freeze paragraph.

## Rules check

- No BLOCK action. Rewriting a `core/` file is CONFIRM-gated (§2); ticket
  approval covers it. Read-before-write observed (the Implementer reads
  the current `LINE_MEETING.md` fully before replacing it).
- Note: this ticket *shrinks* a governance doc. That is deliberate and
  agreed at the grill — it is not scope creep, and the compressed version
  keeps the enforceable parts.

## Notes for the Reviewer

Reviewed in isolated context — PASS on all 5 acceptance criteria. Filename/heading mismatch (LINE_MEETING.md vs "Changing this kit") is ticket-sanctioned; README refs are ticket 005.
