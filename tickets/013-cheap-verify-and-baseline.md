# Ticket: Keep test output and session baseline out of the model's context

**Status:** done
**Owner (Implementer):** Claude
**Retry count:** 0
**Related project audit:** N/A — this repo
**Baseline:** 5ea3d9e
**Worktree:**

## Problem

On guibrief (2026-10-17) the owner asked why launching a test or a Reviewer starts at about 50k tokens. There are two causes:

1. **Fixed baseline.** Every session and subagent loads tool definitions, plugin tool lists and skill lists before doing any work. In guibrief the Vercel plugin alone lists about 300 tool names and a session-start block. A Reviewer pays this again.
2. **Reading test output.** `docket verify` already writes the log to disk and prints only a summary. But when verify fails, the summary says nothing about *what* failed. So the agent opens the log (thousands of Playwright lines) to find out, or it runs `pnpm verify` directly and gets the whole output in context.

Nothing in `core/` tells the agent, or the human, how to keep that cost down.

## Approach

1. **Failure digest (`tooling/`).** When verify exits non-zero, `docket verify` and `docket pre-review` also print a digest of at most 40 lines. The digest is the log lines that match failure markers (`✘`, `FAIL`, `Error:`, `error TS`, `failed`, `✖`, `ERR!`), each with its line number in the log, followed by the log's last 10 lines. It's a new `--digest-lines N` option; `0` turns it off. The log and the attestation stay exactly as they are now.
2. **Workflow guidance (`core/WORKFLOW.md`, `core/recipes/recipe-self-review.md`).** Add a short "Keeping verification cheap" section:
   - Always run the suite through `docket verify` or `docket pre-review`, never through the raw test command, so the output stays in the log.
   - On failure, read the digest, then only the log lines it points to (with `sed -n` or `grep`), never the whole log.
   - The human may run `docket pre-review` in their own terminal and report only the exit code and digest. The attestation on disk is the same either way.
   - Batch Reviewers: give one Reviewer the whole batch of related Tickets, not one each, so the baseline is paid once.
3. **Setup guidance (`setup/attach.md`).** Add one step: turn off plugins the project doesn't use in `.claude/settings.local.json` (`"enabledPlugins": { "<plugin>": false }`), because subagents inherit them.
4. **CHANGELOG entry** for the incident (`core/CHANGELOG.md`).
5. **Tests** in `tooling/tests/test_verify.py`:
   - a failing command prints the digest, it's capped at the limit, and the matched line numbers are right;
   - a passing command prints no digest;
   - `--digest-lines 0` prints none;
   - the attestation JSON is unchanged in shape.

## Files touched

- `tickets/013-cheap-verify-and-baseline.md`
- `tickets/README.md`
- `tooling/docket/verify_cmd.py`
- `tooling/docket/cli.py`
- `tooling/docket/pre_review.py`
- `tooling/README.md`
- `tooling/tests/test_verify.py`
- `core/WORKFLOW.md`
- `core/recipes/recipe-self-review.md`
- `core/CHANGELOG.md`
- `setup/attach.md`

## Acceptance criteria

- [ ] AC-1: A failing verify prints a digest of at most 40 lines (by default) with failure lines and their log line numbers. A passing verify prints none (test).
- [ ] AC-2: `--digest-lines 0` turns the digest off. The log file and the attestation JSON are byte-for-byte the same as without the digest (test).
- [ ] AC-3: `core/WORKFLOW.md` and the self-review recipe say: run through docket, read the digest, not the whole log; the human may run pre-review themselves; one Reviewer per batch (review).
- [ ] AC-4: `setup/attach.md` covers turning off unused plugins per project (review).
- [ ] AC-5: The existing tooling tests pass (command: `cd tooling && python -m pytest -q`).

## Rollback plan

Revert the commit. The digest is output only: no attestation or log format changes, so revert is safe for attached projects.

## Rules check

- Rewrites files under `core/` — **CONFIRM** (Rules §2). Additive sections only; no rule is relaxed.
- No new dependencies. No deletions.

## Evidence

### Project verify

```text
command: tooling/.venv/bin/pytest -v -p no:cacheprovider tooling
exit: 0
log: .docket/verify/013-cheap-verify-and-baseline-20261018T044516Z.log
ran_at: 2026-10-18T04:45:16Z
git_head: 00879c4b69db972e77fce26b27b6aff568ff046a
tree_fingerprint: 87b4c7cab0c4f47ab170c4747c337757db82fc89b93212b85802584c42a89030
attestation: .docket/verify/013-cheap-verify-and-baseline-20261018T044516Z.json
```

### Acceptance criteria

```text
id: AC-1
criterion: A failing verify prints a digest of at most 40 lines (by default) with failure lines and their log line numbers. A passing verify prints none
method: test
how: tooling/.venv/bin/pytest -v -p no:cacheprovider tooling
result: pass
tests:
- test_failing_verify_digest_points_at_failures
- test_cli_digest_only_on_failure_and_switchable

id: AC-2
criterion: --digest-lines 0 turns the digest off; the log file and attestation JSON are unchanged by the digest
method: test
how: tooling/.venv/bin/pytest -v -p no:cacheprovider tooling
result: pass
tests:
- test_digest_is_capped
- test_cli_digest_only_on_failure_and_switchable

id: AC-3
criterion: core/WORKFLOW.md and the self-review recipe say: run through docket, read the digest not the whole log; the human may run pre-review themselves; one Reviewer per batch
method: manual
how: read core/WORKFLOW.md "Keeping verification cheap" and the recipe paragraph before "Evidence schema (Project verify)"
result: pass
evidence: WORKFLOW.md section has all four points (docket not raw command; digest then only named lines; human may run pre-review, attestation counts; one Reviewer per batch + unused plugins); the recipe paragraph points at it
notes: the digest only adds output; failure_digest reads the log and writes nothing (verify_cmd.py)

id: AC-4
criterion: setup/attach.md covers turning off unused plugins per project
method: manual
how: read setup/attach.md Step 6
result: pass
evidence: Step 6 gives the .claude/settings.local.json enabledPlugins form, /plugin to list, and keeping the file out of git
notes:

id: AC-5
criterion: The existing tooling tests pass
method: test
how: tooling/.venv/bin/pytest -v -p no:cacheprovider tooling
result: pass
evidence: 49 passed in the attested log (46 existing + 3 new)
notes:
```

### Scope review

```text
diff_vs_files_touched: match
extras: none
justified: n/a
notes: guibrief's CLAUDE.md line (a8bc10b) is in the guibrief repo, not this one
```

## Notes for the Reviewer

- Done outside this Ticket, as local config with no repo change: `.claude/settings.local.json` in guibrief and in docket turns off the Vercel and Swift LSP plugins. The file is excluded with `.git/info/exclude`.
- The audit used for `docket verify` is a scratch copy of the test fixture with the pytest command, as 010–012 did (this repo has no PROJECT_AUDIT.md).
- The digest's line budget: the tail (up to 10 lines) and two header lines come first, and matching lines fill the rest, so the total never exceeds `--digest-lines`.
- The new attach step is Step 6, at the end of `setup/attach.md`.
- Implemented on branch `cheap-verify`.
- Review (independent, 2026-10-18): PASS, no blocking findings. Re-ran pytest: 49 passed; the diff matches Files touched. Non-blocking, left for a later Ticket:
  1. AC-2 says "byte-for-byte". The test checks only `latest.json`'s keys; the read-only code is what makes the claim true.
  2. `test_digest_is_capped` doesn't check line numbers or structure; the other digest test does.
  3. No test covers the `pre-review` digest path (`pre_review.py`).
  4. When matches exceed the budget, the header gives the total count without "showing N of M".
  5. Substring matching can flag passing tests whose names contain "failed" or "FAIL" (by design).

