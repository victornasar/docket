# Ticket: Cut token cost per Ticket without weakening the gates

**Status:** done
**Owner (Implementer):** Claude
**Retry count:** 0
**Related project audit:** N/A — this repo
**Baseline:** 8fcf685198f57ff412caf2a7bea2ebade075fa28
**Worktree:** (blank)

## Problem

These figures come from a real run on Guibrief, Program v3, Tickets 093–101, all in one Claude Code session:

- 822 model calls re-sent **211M cached input tokens**. That's about 99% of the input. Output was only 1.05M tokens.
- The median call carried a 233k-token conversation.
- A Ticket cost 25–29M tokens late in the session. The Ticket right after an automatic summary cost 7.8M for the same kind of work.
- Reviewer subagents cost 55–80k tokens per pass, about 0.5% of the total, and they caught real bugs.

So the cost comes from long sessions, not from the gates. WORKFLOW.md already says Done is a session boundary (lines 207–214), but nothing makes that happen, and the agent didn't follow it.

Three smaller costs added round-trips:
- **Hand-written Evidence:** 8–10KB per Ticket that the tooling never checks. "See verify log" is taken on trust.
- **Late format errors:** these surface only at `pre-review`. Examples: `method: test + read` is rejected, and comma-separated Files touched breaks the parser.
- **An incomplete `review-packet`:** it omits untracked new files, so every reviewer prompt needs a hand-written list.

## Approach

1. **`docket done <ticket>`**:
   - It checks the Ticket says `done`, the tree is clean, and the last commit touches the Ticket.
   - It prints a short handoff: the Ticket path, its status, the next Ticket if a program file lists one, and the line *"Start a fresh session (/clear) before the next Ticket."*
   - It changes no files.
2. **`docket resume [<ticket>]`**:
   - It prints a compact brief (under 40 lines) for a fresh session: the Ticket title, status and baseline; the AC ids with their pass/blank state; the last attestation and whether it's stale; and the files changed since the baseline, with untracked files included.
   - A new session reads this instead of the old transcript.
3. **Evidence by test reference.** An AC may give `tests:`, one test title per line, in place of a prose `evidence:`.
   - `check-evidence` then passes only if every listed title appears as passed in the attestation's log.
   - It fails if a title is missing, or appears as failed or skipped.
   - Matching is plain substring on the log line, with a per-runner adapter starting with Playwright's `✓  N [project] › file:line:col › … › <title>` format, and pytest's `PASSED`.
   - Prose `evidence:` stays valid, so this changes nothing for existing Tickets.
4. **`docket lint-ticket <ticket>`**: structural checks that need no diff or verify.
   - Required headers are present.
   - Each AC's method is one of the valid methods.
   - Files touched has one path per line, with no commas or globs.
   - Baseline is a commit hash or the "(set when …)" placeholder.
   - `pre-review` runs it first.
5. **`review-packet`** adds an `untracked:` list (`git status --porcelain`, `??` entries filtered to paths under Files touched) and a `diff_stat:` line.
6. **Docs.**
   - WORKFLOW.md "Reaching Done" gains the two commands, as the default ending of every Ticket.
   - `core/roles/implementer.md` gets one line: end the session at Done; begin the next with `docket resume`.
   - `core/templates/ticket.template.md` shows the `tests:` form.
   - CHANGELOG entry.

## Files touched

- tooling/docket/cli.py
- tooling/docket/done_cmd.py
- tooling/docket/resume_cmd.py
- tooling/docket/lint_ticket.py
- tooling/docket/check_evidence.py
- tooling/docket/parse.py
- tooling/docket/pre_review.py
- tooling/docket/review_packet.py
- tooling/tests/test_done_resume.py
- tooling/tests/test_lint_ticket.py
- tooling/tests/test_check_evidence.py
- tooling/tests/test_review_packet.py
- tooling/README.md
- core/WORKFLOW.md
- core/roles/implementer.md
- core/templates/ticket.template.md
- core/CHANGELOG.md

## Acceptance criteria

- [ ] AC-1: `docket done` refuses a Ticket that isn't done or a dirty tree, and otherwise prints the handoff with the fresh-session line. (test)
- [ ] AC-2: `docket resume` prints under 40 lines covering the title, status, baseline, AC states, attestation freshness and changed files, untracked included. (test)
- [ ] AC-3: `tests:` evidence passes only when every title is a passed line in the attested log. Missing, failed or skipped titles fail with the title named. Prose evidence still passes as before. (test, with Playwright and pytest log fixtures)
- [ ] AC-4: `lint-ticket` catches an invalid method, comma-separated Files touched, and missing headers, and `pre-review` runs it first. (test)
- [ ] AC-5: `review-packet` lists untracked files under Files touched and a diff stat. (test)
- [ ] AC-6: WORKFLOW.md, implementer.md, the ticket template, the tooling README and the CHANGELOG describe the new flow. The existing test suite passes. (test + read)

## Rollback plan

Revert the commit. The new commands are additive, and prose Evidence remains valid.

## Rules check

No dependencies, secrets or deploys. This repo has no CI. The tests run locally with `tooling/.venv`.

## Evidence

### Project verify

```text
command: tooling/.venv/bin/pytest -v -p no:cacheprovider tooling
exit: 0
log: .docket/verify/009-token-efficiency-20261015T202317Z.log
ran_at: 2026-10-15T20:23:17Z
git_head: 8fcf685198f57ff412caf2a7bea2ebade075fa28
tree_fingerprint: f021ccc5d429ab8927fb61918fb56806ae243986906440185b2aa2b4cb1df1a0
attestation: .docket/verify/009-token-efficiency-20261015T202317Z.json
```

### Acceptance criteria

```text
id: AC-1
criterion: docket done refuses a non-done Ticket or dirty tree, otherwise prints the handoff with the fresh-session line
method: test
how: tooling/.venv/bin/pytest -v tooling (via docket verify)
result: pass
tests:
- tooling/tests/test_done_resume.py::test_done_refuses_ticket_not_done
- tooling/tests/test_done_resume.py::test_done_refuses_dirty_tree
- tooling/tests/test_done_resume.py::test_done_refuses_when_last_commit_skips_ticket
- tooling/tests/test_done_resume.py::test_done_prints_handoff_with_next_ticket
- tooling/tests/test_done_resume.py::test_done_without_program_file
notes: .docket/ is ignored for the clean-tree check (verify scratch)

id: AC-2
criterion: docket resume prints under 40 lines covering title, status, baseline, AC states, attestation freshness and changed files, untracked included
method: test
how: tooling/.venv/bin/pytest -v tooling (via docket verify)
result: pass
tests:
- tooling/tests/test_done_resume.py::test_resume_brief_covers_state
- tooling/tests/test_done_resume.py::test_resume_caps_length_and_finds_open_ticket
- tooling/tests/test_done_resume.py::test_resume_without_open_ticket
notes:

id: AC-3
criterion: tests: evidence passes only when every title is a passed line in the attested log; missing/failed/skipped fail naming the title; prose still passes
method: test
how: tooling/.venv/bin/pytest -v tooling (via docket verify)
result: pass
tests:
- tooling/tests/test_check_evidence.py::test_title_problems_playwright
- tooling/tests/test_check_evidence.py::test_title_problems_pytest
- tooling/tests/test_check_evidence.py::test_tests_evidence_passes_without_prose
- tooling/tests/test_check_evidence.py::test_tests_evidence_fails_naming_title
- tooling/tests/test_check_evidence.py::test_tests_evidence_missing_title_fails
- tooling/tests/test_check_evidence.py::test_complete_evidence_pass
notes: this Ticket's own Evidence uses tests: and passes check-evidence

id: AC-4
criterion: lint-ticket catches invalid method, comma-separated Files touched, missing headers; pre-review runs it first
method: test
how: tooling/.venv/bin/pytest -v tooling (via docket verify)
result: pass
tests:
- tooling/tests/test_lint_ticket.py::test_invalid_method_fails
- tooling/tests/test_lint_ticket.py::test_comma_separated_files_touched_fails
- tooling/tests/test_lint_ticket.py::test_missing_headers_fail
- tooling/tests/test_lint_ticket.py::test_bad_or_missing_baseline_fails
- tooling/tests/test_lint_ticket.py::test_pre_review_runs_lint_before_verify
notes:

id: AC-5
criterion: review-packet lists untracked files under Files touched and a diff stat
method: test
how: tooling/.venv/bin/pytest -v tooling (via docket verify)
result: pass
tests:
- tooling/tests/test_review_packet.py::test_packet_lists_untracked_in_scope_and_diff_stat
- tooling/tests/test_review_packet.py::test_packet_without_untracked
notes:

id: AC-6
criterion: WORKFLOW.md, implementer.md, ticket template, tooling README and CHANGELOG describe the new flow; existing suite passes
method: test
how: full suite via docket verify (exit 0, 46 passed); docs read in the diff
result: pass
evidence: .docket/verify/009-token-efficiency-20261015T202109Z.log; git diff 8fcf685198f57ff412caf2a7bea2ebade075fa28 -- core/WORKFLOW.md core/roles/implementer.md core/templates/ticket.template.md tooling/README.md core/CHANGELOG.md
notes: the read half is for the Reviewer to judge
```

### Scope review

```text
diff_vs_files_touched: match
extras: none
justified: n/a
notes: .DS_Store added to .git/info/exclude locally (not committed) so check-scope ignores Finder files
```

## Notes for the Reviewer

- `core/recipes/recipe-self-review.md` is the Evidence schema source of truth and does not yet mention `tests:`. It wasn't on Files touched, so it's left for a follow-up.
- Review (independent, Sonnet): PASS with six non-blocking findings. Fixed after Review, then re-verified: lint no longer treats `[ ]` as a glob (Next.js `app/[slug]/` paths), `done` reads merge commits (`-m --first-parent`), and the README tells you to give full, unique test titles. Left as is: older Tickets 001–008 fail lint (it is for current-format Tickets), the classifier fails safe when a title contains "ERROR", and quoted porcelain paths with spaces are not unquoted.
