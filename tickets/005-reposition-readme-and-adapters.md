# Ticket: Reposition the README and rename vocabulary in `adapters/` + `setup/`

**Status:** done
**Owner (Implementer):** Claude (this session)
**Retry count:** 0
**Related project Mise en Place:** N/A — Tabouleh's own repo
**Worktree:** (blank)

**Depends on:** 001, 003, 004 (so the README/adapters point at final
`core/` filenames, the `advanced/` location, and the compressed Line
Meeting). Can run after 001 alone if 003/004 slip, but then re-check the
links.

## Problem

The README leads with "a portable, model-agnostic AI coding harness." The
grill gutted that claim: single-operator first (Q1), one real adapter with
Cursor demoted to experimental (Q5), rules that assume the Claude Code
host baseline (Q11), and the category is "workflow kit" not "harness"
(Q16). Continuing to lead with "portable, model-agnostic harness" is
marketing ahead of reality. This ticket repositions the README honestly
and carries the 001 vocabulary rename into `adapters/` and `setup/`, which
001 deliberately left out of scope to keep diffs reviewable.

Out of scope (explicitly deferred): the `tabouleh sync` / `attach` scripts
and semver/`RELEASES.md` wiring — that is the separate tooling release.
This ticket only updates prose to match decisions already made.

## Approach

1. **README repositioning:**
   - Replace the opening definition with: *"Tabouleh is an opinionated
     planning-and-review workflow you vendor into a Claude Code project:
     a Ticket you approve before any code, an independent review pass
     before anything is called done, and a procedure for improving the
     workflow itself from real incidents."*
   - Move the kitchen metaphor to **one paragraph** ("We borrowed the
     structure of a kitchen brigade as a mental model — a planner, an
     implementer, an independent checker, and a checkpoint before
     anything ships") and **delete the decode table** and the multi-
     paragraph justification. The plain terms now stand on their own.
   - Reframe model-agnosticism as an **aspiration** ("the core is plain
     Markdown with no Claude-specific syntax, so porting it to another
     tool is possible") and tool-portability as **unproven beyond Claude
     Code** (the Cursor adapter is experimental and cannot do the
     independent review pass).
   - Update the repo map and reading-order sections to the new filenames
     (`RULES.md`, `WORKFLOW.md`, `roles/planner.md` etc.,
     `advanced/PARALLEL_LINE.md`) and the "Changing this kit" retitle.
   - Update the Scope section: `core/` is frozen (point at the freeze
     declaration from ticket 004).
2. **`adapters/` vocabulary rename** — apply the 001 term mapping to:
   - `adapters/claude-code/README.md`
   - `adapters/claude-code/CLAUDE.md.template` (including the generated
     `.claude/agents/` filenames it tells projects to create:
     `executive-chef.md`→`planner.md`, `line-cook.md`→`implementer.md`,
     `expediter.md`→`reviewer.md`; and the `@`/path references to
     `KITCHEN_RULES.md`→`RULES.md`, `THE_PASS.md`→`WORKFLOW.md`)
   - `adapters/cursor/README.md`
   - `adapters/cursor/cursorrules.template`
   - Add a one-line "experimental — no true independent review pass;
     approximates it with a separate chat" banner to both Cursor adapter
     files (Q5), if not already stated that plainly.
3. **`setup/attach.md` vocabulary rename** — apply the term mapping.
   Do **not** rewrite the symlink/submodule steps into the vendored-copy
   model here — that is the tooling release. Add a single note at the top:
   "The distribution model is moving to a vendored copy pinned to a
   release tag; until the `attach` script lands, the symlink/submodule
   steps below still apply." Keep the steps otherwise as-is.
4. Grep the whole repo for any remaining kitchen terms and old filenames
   after all edits; the only permitted survivors are the dated historical
   entries in `core/CHANGELOG.md`.

## Files touched

- `README.md`
- `adapters/claude-code/README.md`
- `adapters/claude-code/CLAUDE.md.template`
- `adapters/cursor/README.md`
- `adapters/cursor/cursorrules.template`
- `setup/attach.md`

## Acceptance criteria

- [ ] `README.md`'s first sentence is the new "opinionated
      planning-and-review workflow you vendor into a Claude Code project"
      definition; the words "portable" and "model-agnostic" do not appear
      as headline claims (they may appear once, in the
      aspiration/unproven framing).
- [ ] The kitchen-metaphor decode table is gone; the metaphor survives as
      exactly one paragraph.
- [ ] README repo map and reading order list only files that exist after
      tickets 001/003/004 (`RULES.md`, `WORKFLOW.md`, `roles/planner.md`,
      `roles/implementer.md`, `roles/reviewer.md`,
      `templates/project-audit.template.md`,
      `advanced/PARALLEL_LINE.md`), and every link resolves.
- [ ] README Scope section references the `core/` freeze.
- [ ] Both Cursor adapter files carry the "experimental, no independent
      review pass" banner.
- [ ] `CLAUDE.md.template` tells projects to create
      `.claude/agents/planner.md`, `implementer.md`, `reviewer.md` and
      references `RULES.md` / `WORKFLOW.md`.
- [ ] `setup/attach.md` uses the new vocabulary and carries the
      "distribution model is moving" note, with the symlink/submodule
      steps otherwise intact.
- [ ] `grep -rIn -e "Executive Chef" -e "Line Cook" -e "Expediter" -e "Kitchen Rules" -e "KITCHEN_RULES" -e "THE_PASS" -e "The Pass" -e "Mise en Place" -e "Walk-in" -e "harness" .` across the whole repo returns matches only inside `core/CHANGELOG.md` historical entries and the single README metaphor paragraph.

## Rollback plan

Single commit. `git revert <sha>` restores the previous README positioning
and the old vocabulary in `adapters/` and `setup/`.

## Rules check

- No BLOCK action. Editing files under `adapters/` is CONFIRM-gated
  (§2) — ticket approval covers the enumerated files. `README.md` and
  `setup/` are not under `core/`/`adapters/` but are edited here under the
  same approval. Read-before-write observed.

## Notes for the Reviewer

Reviewed in isolated context — PASS on all 8 acceptance criteria. tickets/** still quote old terms (working docs, not shipped kit).
