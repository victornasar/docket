# Ticket: Cut `RULES.md` down to Tabouleh-specific deltas

**Status:** draft
**Owner (Implementer):**
**Retry count:** 0
**Related project Mise en Place:** N/A — Tabouleh's own repo
**Worktree:** (blank)

**Depends on:** 001 (needs `core/RULES.md` at its post-rename name and vocab).

## Problem

`KITCHEN_RULES.md` (now `RULES.md`) restates a large amount of safety
policy the Claude Code host already enforces in its own system prompt —
secrets handling, destructive git operations, production/user-facing
comms. Restating it means two copies that can silently drift (grill Q2,
Q11). The fix is to keep only what is genuinely Tabouleh-specific, replace
the duplicative material with a citation to the host baseline, and rewrite
the borderline cases as explicit "Tabouleh tightens this" deltas.

## Approach

1. **Add a preamble** to `RULES.md`: this file assumes a host that already
   enforces the Claude Code safety baseline (instruction-source boundary,
   prohibited actions, permission-required actions). It lists only what
   Tabouleh adds or tightens on top of that baseline. The experimental
   Cursor adapter, which cannot assume that baseline, carries its own copy
   of what it needs (handled in its own adapter files, not here).

2. **Keep as Tabouleh's own (bucket A) — full rules text stays:**
   - §2: "Deleting or rewriting any file under `tabouleh/core/` or
     `tabouleh/adapters/`" → CONFIRM. Tabouleh-specific.
   - §2: "Overwriting a file without having read its current contents
     first" → BLOCK. Keep (it is a workflow discipline, stated more
     absolutely than the host does).
   - §7: rollback-plan discipline (whichever section number it is) — the
     requirement that a Ticket states a rollback plan and it stays
     accurate. Tabouleh-specific.
   - §8: scope-creep / Files-Touched discipline. Tabouleh-specific.
   - The "Ticket conflicts with a rule → rules win, escalate to human"
     framing. Tabouleh-specific.

3. **Cut to a citation (bucket B) — delete the rows, replace with one
   line pointing at the host baseline:**
   - §5 secrets/credentials (all rows) — host already covers this.
   - §1 destructive git (`push --force`, history rewriting, committing to
     `main`) — host + normal git norms cover this; keep only if a row is
     stricter than the host, and if so move it to bucket C.
   - §6 production deploys and real-user comms — host covers "sending
     communications" and "purchases/irreversible actions"; keep only a
     pointer plus any Tabouleh-specific note about Ticket wording.

4. **Rewrite as explicit deltas (bucket C) — "Tabouleh tightens the host
   baseline here, specifically:":**
   - §3 dependencies: host is vague on adding/removing deps; Tabouleh
     requires the package + version + reason be named on the Ticket
     first.
   - §4 migrations: keep the migration-specific gradation (write freely /
     CONFIRM against non-local / ESCALATE against prod / CONFIRM with
     rollback for non-reversible) — the host does not spell this out.
   - §3 CI/CD config changes → CONFIRM. Keep as a delta.

5. **Renumber** the sections after the cut so references stay sensible,
   then **update every `RULES.md §N` cross-reference** in `core/**` to the
   new numbers. Grep for `RULES.md §` and `Rules §` and fix each.

6. Judgement calls on individual rows (is this row stricter than the host,
   bucket B or C?) get listed in the handoff notes with the Implementer's
   reasoning, for the Reviewer to check — this ticket names the buckets,
   the Implementer places the ambiguous rows and shows their work.

## Files touched

- `core/RULES.md` (the cut, preamble, renumber)
- `core/WORKFLOW.md` (update `§N` cross-references)
- `core/roles/planner.md` (update `§N` cross-references)
- `core/roles/implementer.md` (update `§N` cross-references)
- `core/roles/reviewer.md` (update `§N` cross-references)
- `core/recipes/recipe-safe-migration.md` (update `§N` cross-references)
- `core/recipes/recipe-self-review.md` (update `§N` cross-references)
- `core/recipes/recipe-diagnosis.md` (update `§N` cross-references)
- `core/templates/ticket.template.md` (update `§N` cross-references)
- Any other `core/**` file a `grep -rn "RULES.md §\|Rules §" core/` turns up

## Acceptance criteria

- [ ] `RULES.md` opens with the "assumes the Claude Code host baseline"
      preamble.
- [ ] The bucket-A rules (core/adapters edit protection, read-before-write,
      rollback discipline, scope-creep, rules-win-over-Ticket) are still
      present in full.
- [ ] The bucket-B material (secrets §5, generic destructive git,
      generic prod/comms) is replaced by a citation line, not restated
      rule-by-rule.
- [ ] The bucket-C deltas (dependencies, migrations gradation, CI/CD)
      each read as "Tabouleh requires X on top of the baseline," not as
      standalone restatements.
- [ ] `RULES.md` is meaningfully shorter than before (rough target: ~⅓ to
      ½ the line count) — attach `wc -l` before/after in the notes.
- [ ] `grep -rn "RULES.md §\|Rules §" core/` — every hit points at a
      section number that exists in the renumbered file.
- [ ] No bucket-A rule was cut and no new rule was invented. The diff is
      deletions, the preamble, renumbering, and bucket-C rephrasings only.
- [ ] Handoff notes list every row whose bucket placement was a judgement
      call, with reasoning.

## Rollback plan

Single commit. `git revert <sha>` restores the full rules file and old
section numbers. No external impact — no attached project reads this file
at runtime; they vendor or regenerate against a tagged release.

## Rules check

- No BLOCK action. Editing `core/RULES.md` is CONFIRM-gated (§2, current
  numbering) — ticket approval is that confirmation. Read-before-write
  observed.
- This ticket *removes* rule text. That is a content change to a
  load-bearing file, which is exactly why it is its own ticket with its
  own approval rather than folded into 001.

## Notes for the Reviewer

<Filled during Self-review.>
