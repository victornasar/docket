# Ticket: Bring `tickets/README.md` up to date

**Status:** done
**Owner (Implementer):** Claude
**Retry count:** 0
**Related project audit:** N/A — this repo
**Baseline:** d1bbc5f51ba9b890f6aa8c6fb321404204ed882a
**Worktree:**

## Problem

`tickets/README.md` lists only 001–006 and still calls the project "Tabouleh". Tickets 007–009 are missing, so `docket done` prints "next: (none listed)" even when a next Ticket exists. Its "Deferred" section also describes work that has since partly landed, such as the tooling.

## Approach

1. Replace "Tabouleh" with "Docket" throughout the file.
2. Add a table for 007–009 (README guide, attach entrypoint, token efficiency) with the same columns as the existing tables. Use each Ticket's own title and Files touched.
3. Add a table for 010–012 so `docket done` can name the next Ticket.
4. Trim the "Deferred" list to the items that are still open. Check each one against the repo (`tooling/`, `bin/`, `setup/`) rather than guessing, and drop or mark done whatever has shipped.
5. Check that `docket done` on Ticket 009 now prints `next: 010`, and adjust the table format if it doesn't parse.

## Files touched

- tickets/README.md

## Acceptance criteria

- [ ] AC-1: `grep -i tabouleh tickets/README.md` prints nothing. (command)
- [ ] AC-2: Every Ticket file 001–012 in `tickets/` has a row in the index. (read)
- [ ] AC-3: `docket done tickets/009-token-efficiency.md` reports `next:` as Ticket 010. (command)
- [ ] AC-4: Every remaining "Deferred" item is checked against the repo and is actually still open. (read)

## Rollback plan

Revert the commit.

## Rules check

Docs only. Nothing here triggers BLOCK or CONFIRM.

## Evidence

### Project verify

```text
command: tooling/.venv/bin/pytest -v -p no:cacheprovider tooling
exit: 0
log: .docket/verify/011-refresh-tickets-index-20261015T203047Z.log
ran_at: 2026-10-15T20:30:47Z
git_head: d1bbc5f51ba9b890f6aa8c6fb321404204ed882a
tree_fingerprint: 7c7b46aaf2e15b0247315e215035f7b3af42e45946c478663b3c4a6565cd1008
attestation: .docket/verify/011-refresh-tickets-index-20261015T203047Z.json
```

### Acceptance criteria

```text
id: AC-1
criterion: grep -i tabouleh tickets/README.md prints nothing
method: command
how: grep -ci tabouleh tickets/README.md
result: pass
evidence: 0
notes:

id: AC-2
criterion: Every Ticket file 001-012 has a row in the index
method: manual
how: read tickets/README.md tables against ls tickets/
result: pass
evidence: 001-006 in the existing tables; 007-009 in "Guide and tooling"; 010-012 in "Housekeeping after 009"
notes:

id: AC-3
criterion: docket done tickets/009-token-efficiency.md reports next as Ticket 010
method: command
how: tooling/.venv/bin/python -c "from docket.done_cmd import next_ticket; print(next_ticket(Path('../tickets/009-token-efficiency.md')))"
result: pass
evidence: ../tickets/010-untrack-ds-store.md
notes: docket done itself refuses until this batch is committed (dirty tree), so the same next_ticket() it calls was run directly. After commit, docket done on 009 refuses because the last commit no longer touches 009, which is expected; Review re-ran next_ticket() and got 010.

id: AC-4
criterion: Every remaining Deferred item is checked against the repo and still open
method: manual
how: grep WORKFLOW.md/reviewer.md for tiered or trivial-ticket review; ls bin/ setup/ for sync/attach script/RELEASES.md
result: pass
evidence: no tiered review or fast path in core/; bin/ has only docket (no sync); no RELEASES.md; setup/attach.md still says "Until the attach script lands"
notes: reworded "Tooling release" to "Distribution tooling", since the gate CLI did ship
```

### Scope review

```text
diff_vs_files_touched: match
extras: none
justified: n/a
notes:
```

## Notes for the Reviewer

Review (independent, Sonnet): Pass, no blocking findings.
