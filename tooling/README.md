# Docket tooling (Stage 2 + 3)

Deterministic trust gates. Python 3.10+ stdlib for the CLI; pytest (dev) for tests.

**Stage 3:** the normal Self-review → Review handoff is `docket pre-review`.
Mechanical gates establish execution/scope/evidence integrity. They do **not**
establish that an acceptance criterion is adequate or that Evidence proves it.

## Commands

```bash
# Normal Self-review → Review path (runs verify first):
./bin/docket pre-review path/to/ticket.md --audit PROJECT_AUDIT.md
# After copying the Project verify block from that run into the Ticket,
# re-check scope + evidence without re-executing the Audit command:
./bin/docket pre-review path/to/ticket.md --audit PROJECT_AUDIT.md --skip-verify

# Individual gates
./bin/docket verify --audit PROJECT_AUDIT.md --ticket path/to/ticket.md
./bin/docket check-scope path/to/ticket.md
./bin/docket check-evidence path/to/ticket.md

# Fresh-context Reviewer discovery (no chat history)
./bin/docket review-packet path/to/ticket.md

# Structure only, no diff or verify (pre-review runs this first)
./bin/docket lint-ticket path/to/ticket.md

# Session boundary: after the Done commit, then in the fresh session
./bin/docket done path/to/ticket.md [--program tickets/README.md]
./bin/docket resume [path/to/ticket.md]
```

Or: `PYTHONPATH=/path/to/docket/tooling python3 -m docket …`

Order matters: **`verify` before `check-evidence`** (attestation must exist).

Non-zero from `pre-review` **blocks** Review handoff — fix the cause.

## Evidence by test reference

An AC may list test titles under `tests:` in place of prose `evidence:`:

```text
id: AC-3
criterion: rejects a bad password
method: test
how: npx playwright test tests/login.spec.ts
result: pass
tests:
- auth › rejects bad password
- auth › locks after five tries
```

`check-evidence` reads the attested verify log and fails, naming the
title, if any title is missing or appears on a failed or skipped line.
Matching is a plain substring on the line, so give full, unique titles
(for pytest, the `path::name` node id): `test_foo` also matches `test_foo_bar`. Recognized formats: Playwright
list reporter (`✓` / `✘` / `-`) and pytest (`PASSED` / `FAILED` /
`ERROR` / `SKIPPED` / `XFAIL`). Titles must appear in the verify output,
so a summary-only reporter needs a per-test reporter for these ACs.
Prose `evidence:` remains valid.

## Session boundary

`docket done <ticket>` checks that the Ticket says `done`, the tree is clean
(ignoring `.docket/`), and the last commit touches the Ticket. It then
prints the next Ticket from a program file (`--program`, or any non-Ticket
`.md` beside the Ticket that lists it, such as `tickets/README.md`) and
the fresh-session line. It writes nothing.

`docket resume [<ticket>]` prints a brief of under 40 lines: title, status,
Baseline, AC states, attestation freshness, and changed files with
untracked ones marked. Without a Ticket argument, it picks the most
recently modified open Ticket under `tickets/`.

## Escape hatches (not the normal path)

These flags exist for iteration / debugging. They are **not** equivalent to
a full trustworthy handoff:

| Flag | Where | Intent |
|---|---|---|
| `--skip-verify` | `pre-review` | Skip re-running the Audit command **after** a real `verify` attestation was copied into the Ticket. Still runs check-scope + check-evidence. |
| `--allow-stale` | `check-evidence` only | Do not fail on fingerprint mismatch. **Not** wired into `pre-review`. |
| `--skip-attestation` | `check-evidence` only | Structural Evidence fields only. **Not** for Done; **not** wired into `pre-review`. |

Normal `pre-review` (without `--skip-verify`) always runs `verify` first and
is fail-closed on non-zero verify, scope, or evidence.

## Generated files and scope

`check-scope` sees untracked files the same way git does (respecting
`.gitignore`). If a verify command creates local artifacts such as
`__pycache__/` and those paths are not ignored, they can fail scope until
cleaned or gitignored. That is project hygiene, not a Docket special case.

## What each command proves

| Command | Proves | Does not prove |
|---|---|---|
| `verify` | Audit command actually ran; exit/log/HEAD/fingerprint captured | Tests prove each AC |
| `check-scope` | diff since Baseline ⊆ Files Touched (+ `tickets/`, `.docket/`, `PROJECT_AUDIT.md`) | In-scope edits are correct |
| `check-evidence` | Evidence structure; Markdown matches attestation; not stale; `tests:` titles passed in the log | AC adequacy |
| `lint-ticket` | Required headers, valid methods, one path per Files touched line, Baseline shape | Anything about the diff |
| `pre-review` | lint-ticket, then the three above, in order | AC adequacy |
| `review-packet` | Lists repo paths, untracked in-scope files, diff stat for a fresh Reviewer | Anything about correctness |
| `done` | Ticket is `done`, committed, tree clean | That Review happened |
| `resume` | Nothing; it is a summary for a fresh session | Anything |

## Attestation / stale binding

`docket verify` writes `.docket/verify/*.log` and `*.json`, plus `latest.json`.

On a non-zero exit, `verify` and `pre-review` also print a **failure digest**
of at most 40 lines: log lines matching a failure marker (`✘`, `✖`, `FAIL`,
`Error:`, `error TS`, `failed`, `ERR!`), each prefixed with its log line
number, then the log's last 10 lines. `--digest-lines N` changes the cap;
`0` turns it off. The digest is output only; the log and attestation are
unchanged.

Fingerprint = HEAD + dirty worktree, excluding `.docket/` and the Ticket file.
Implementation edits invalidate attestation → re-verify.

## CI

**Not added in this kit.** Docket is a Markdown template repo with no CI
workflow, no PR type that means “Ticket PR,” and no attached application
suite. Requiring `check-scope` / `check-evidence` in *this* repository’s CI
would not see real Tickets from consumer projects.

When you attach Docket to an application repo, optionally add a CI job that
runs `docket pre-review` (or check-scope + check-evidence) on PRs that
touch `tickets/**` **and** provide Baseline + Evidence — only if that
matches your branching model. False failures are easy if Tickets are drafts
or Baseline is unset; prefer enforcing gates in the agent Self-review loop
first (Stage 3).

## Security note

`verify` executes the Project Audit command as **trusted project configuration**
at the repository root. Prefer simple argv commands. Shell metacharacters
force `shell=True`. No sandbox.

## Tests

```bash
cd tooling
python3 -m venv .venv
.venv/bin/pip install pytest
.venv/bin/pytest -q
```
