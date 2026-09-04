# Ticket: Lead the README "Attach it to a project" bullet with the entry point

**Status:** done
**Owner (Implementer):** Claude (this session)
**Retry count:** 0
**Related project audit:** N/A — this repo
**Worktree:** (blank)

**Depends on:** 007 (edits the section 007 added).

## Problem

The README's "What you can do with it" → "Attach it to a project" bullet
describes the attach procedure but never names how to start it. A reader
has to open `setup/attach.md` to find out the first move is either the
`attach-docket` skill or that file's numbered steps. One-line fix: lead
with the entry point, keep the summary, link the detail. No new section,
no duplicated procedure (that stays in `setup/attach.md`).

## Approach

In `README.md`, replace the "Attach it to a project" bullet:

Current:
> - **Attach it to a project.** `setup/attach.md` walks it: symlink the
>   repo, run a Project Audit of the codebase, generate `CLAUDE.md` and the
>   three `.claude/agents/` role files, verify the agent produces a Ticket
>   before writing code.

New:
> - **Attach it to a project.** Run the `attach-docket` skill ("attach
>   docket here"), or follow [`setup/attach.md`](setup/attach.md) by hand:
>   symlink the repo, run a Project Audit of the codebase, generate
>   `CLAUDE.md` and the three `.claude/agents/` role files, then verify the
>   agent produces a Ticket before writing code.

## Files touched

- `README.md`

## Acceptance criteria

- [ ] The "Attach it to a project" bullet leads with the `attach-docket`
      skill and links `setup/attach.md`; the rest of the bullet's summary
      wording is unchanged in substance.
- [ ] No other line of `README.md` changes.
- [ ] `setup/attach.md`'s link resolves.
- [ ] No procedure steps were copied into the README (still just a
      summary + link).

## Rollback plan

Single commit. `git revert <sha>`.

## Rules check

- No BLOCK action. `README.md` is not under `core/` or `adapters/`.
  Not a `core/` change — the freeze doesn't apply.

## Notes for the Reviewer

Reviewed in isolated context — PASS. One hunk, inside the target bullet only; "verify" -> "then verify" the only trailing-summary change.
