# Tickets

Work on Docket itself goes through Docket's own workflow: a Ticket,
approved before code, then implemented one at a time.

## Docs release (`v-next.0.0` — structural: rename, cut, move, reposition)

Run in order. 001 must be Served before the rest (everything points at the
filenames it changes). 002–005 touch mostly disjoint files and can be
fired in any order after 001, but 005 is last because it repoints the
README at what the others produced.

| # | Ticket | Touches | Depends on |
|---|---|---|---|
| 001 | [Rename kitchen vocabulary in `core/`](001-rename-vocabulary-in-core.md) | all of `core/**` | — |
| 002 | [Cut `RULES.md` to Docket-specific deltas](002-cut-rules-to-deltas.md) | `core/RULES.md` + cross-refs | 001 |
| 003 | [Move `PARALLEL_LINE.md` to `advanced/`](003-move-parallel-line-to-advanced.md) | `core/PARALLEL_LINE.md`, `core/WORKFLOW.md` | 001 |
| 004 | [Compress the Line Meeting, declare the freeze](004-compress-line-meeting-declare-freeze.md) | `core/LINE_MEETING.md` | 001 |
| 005 | [Reposition README, rename `adapters/` + `setup/`](005-reposition-readme-and-adapters.md) | `README.md`, `adapters/**`, `setup/` | 001 (003, 004) |

## Project rename (follow-on, before the tooling release)

| # | Ticket | Touches | Depends on |
|---|---|---|---|
| 006 | [Rename the project to Docket](006-rename-project-to-docket.md) | `README.md`, `core/**`, `adapters/**`, `setup/` | 001–005 |

## Guide and tooling (after the rename)

The Stage 1–3 gate tooling (`tooling/`, `bin/docket`) landed in d683b73
without a Ticket. These Tickets came after it.

| # | Ticket | Touches | Depends on |
|---|---|---|---|
| 007 | [Expand the README into a usage guide](007-expand-readme-into-a-guide.md) | `README.md` | 006 |
| 008 | [Lead the README attach bullet with the entry point](008-readme-attach-entrypoint.md) | `README.md` | 007 |
| 009 | [Cut token cost per Ticket without weakening the gates](009-token-efficiency.md) | `tooling/**`, `core/WORKFLOW.md`, `core/roles/implementer.md`, `core/templates/ticket.template.md`, `core/CHANGELOG.md` | — |

## Housekeeping after 009

| # | Ticket | Touches | Depends on |
|---|---|---|---|
| 010 | [Stop tracking `.DS_Store` files](010-untrack-ds-store.md) | `.gitignore`, `adapters/.DS_Store`, `core/.DS_Store` | — |
| 011 | [Bring this index up to date](011-refresh-tickets-index.md) | `tickets/README.md` | — |
| 012 | [Document `tests:` Evidence in the self-review recipe](012-document-tests-evidence-in-recipe.md) | `core/recipes/recipe-self-review.md` | 009 |

## Deferred — still open

- **Behavioural workflow changes** (grill Q6, Q7): the real checkpoint at
  Ticket-approval with a trivial-ticket fast path, and the tiered
  independent Review pass (by risk / size / rules-category). Neither is in
  `core/WORKFLOW.md` or `core/roles/reviewer.md` yet.
- **Distribution tooling** (grill Q8, Q12, Q14): vendored-copy
  distribution, `docket sync`, the `attach` script, semver +
  `RELEASES.md`. The gate CLI shipped, but none of these did;
  `setup/attach.md` still uses the symlink/submodule steps.
- **Re-attach `vitals`** (grill Q19): waits on the distribution tooling,
  since re-attach is a tooling flow. `vitals` stays the canary project.
