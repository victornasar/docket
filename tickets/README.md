# Tickets

Work on Tabouleh itself goes through Tabouleh's own workflow: a Ticket,
approved before code, then implemented one at a time.

## Docs release (`v-next.0.0` — structural: rename, cut, move, reposition)

Run in order. 001 must be Served before the rest (everything points at the
filenames it changes). 002–005 touch mostly disjoint files and can be
fired in any order after 001, but 005 is last because it repoints the
README at what the others produced.

| # | Ticket | Touches | Depends on |
|---|---|---|---|
| 001 | [Rename kitchen vocabulary in `core/`](001-rename-vocabulary-in-core.md) | all of `core/**` | — |
| 002 | [Cut `RULES.md` to Tabouleh-specific deltas](002-cut-rules-to-deltas.md) | `core/RULES.md` + cross-refs | 001 |
| 003 | [Move `PARALLEL_LINE.md` to `advanced/`](003-move-parallel-line-to-advanced.md) | `core/PARALLEL_LINE.md`, `core/WORKFLOW.md` | 001 |
| 004 | [Compress the Line Meeting, declare the freeze](004-compress-line-meeting-declare-freeze.md) | `core/LINE_MEETING.md` | 001 |
| 005 | [Reposition README, rename `adapters/` + `setup/`](005-reposition-readme-and-adapters.md) | `README.md`, `adapters/**`, `setup/` | 001 (003, 004) |

## Deferred — not in this batch

- **Behavioural workflow changes** (grill Q6, Q7): the real checkpoint at
  Ticket-approval with a trivial-ticket fast path, and the tiered
  independent Review pass (by risk / size / rules-category). These change
  how the workflow *behaves*, not its vocabulary — a separate docs change
  right after this batch so "we renamed everything" and "we changed the
  process" stay in different diffs.
- **Tooling release** (grill Q8, Q12, Q14): vendored-copy distribution,
  `tabouleh sync`, the `attach` script, semver + `RELEASES.md`. Code, not
  Markdown; needs its own design pass once these templates are in their
  final shape.
- **Re-attach `vitals`** (grill Q19): happens when the tooling lands,
  since re-attach is a tooling flow. `vitals` stays the canary project.
