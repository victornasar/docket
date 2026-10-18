# Ticket: Keep test output and session baseline out of the model's context

**Status:** implemented 2026-10-17, awaiting independent Review (owner: "okay do it", approving the Ticket and the `core/` CONFIRM)
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

<!-- Filled during Self-review. -->

## Notes for the Reviewer

- Done outside this Ticket, as local config with no repo change: `.claude/settings.local.json` in guibrief and in docket turns off the Vercel and Swift LSP plugins. The file is excluded with `.git/info/exclude`.
- Self-review: `tooling/.venv/bin/pytest -q -p no:cacheprovider tooling` → 49 passed. That includes the three new digest tests (`-k digest` → 3 passed). `docket pre-review` and the Evidence blocks aren't filled yet.
- The digest's line budget: the tail (up to 10 lines) and two header lines come first, and matching lines fill the rest, so the total never exceeds `--digest-lines`.
- The new attach step is Step 6, at the end of `setup/attach.md`.
- Implemented on branch `cheap-verify`.

