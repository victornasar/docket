# Ticket: Stop tracking `.DS_Store` files

**Status:** in-review
**Owner (Implementer):** Claude
**Retry count:** 0
**Related project audit:** N/A — this repo
**Baseline:** 1c3a6953e08055b92582246ed4daa7df25f6d99f
**Worktree:**

## Problem

Commit 8fcf685 added `adapters/.DS_Store` and `core/.DS_Store`. These are macOS Finder metadata files and don't belong in the repo. `.gitignore` has no `.DS_Store` rule, so the next Mac contributor will commit more of them. The current workaround is a line in `.git/info/exclude`, which only covers one machine.

## Approach

1. Run `git rm --cached adapters/.DS_Store core/.DS_Store`. The files stay on disk but are no longer tracked.
2. Add `.DS_Store` to `.gitignore` under a short "OS files" comment.
3. Do not rewrite history. 8fcf685 is unpushed, but `cost-defaults` already has 009 on top of it, and an extra commit is simpler and safer than a rebase.

## Files touched

- .gitignore
- adapters/.DS_Store
- core/.DS_Store

## Acceptance criteria

- [ ] AC-1: `git ls-files | grep DS_Store` prints nothing. (command)
- [ ] AC-2: `.gitignore` contains a `.DS_Store` line, and `git check-ignore core/.DS_Store` exits 0. (command)
- [ ] AC-3: The existing test suite passes. (test)

## Rollback plan

Revert the commit.

## Rules check

It removes files from the index only; nothing is deleted from disk. No dependencies, secrets or deploys.

## Evidence

### Project verify

```text
command: tooling/.venv/bin/pytest -v -p no:cacheprovider tooling
exit: 0
log: .docket/verify/010-untrack-ds-store-20261015T203031Z.log
ran_at: 2026-10-15T20:30:31Z
git_head: 1c3a6953e08055b92582246ed4daa7df25f6d99f
tree_fingerprint: eddf0bf69c0497773f3863808180b2b2f7156bb39e403a30445cb852adb71adf
attestation: .docket/verify/010-untrack-ds-store-20261015T203031Z.json
```

### Acceptance criteria

```text
id: AC-1
criterion: git ls-files | grep DS_Store prints nothing
method: command
how: git ls-files | grep DS_Store
result: pass
evidence: no output, grep exit 1
notes:

id: AC-2
criterion: .gitignore contains a .DS_Store line and git check-ignore core/.DS_Store exits 0
method: command
how: grep -x .DS_Store .gitignore; git check-ignore core/.DS_Store
result: pass
evidence: line present under "# OS files"; check-ignore printed core/.DS_Store, exit 0
notes: .git/info/exclude also has the rule locally; the .gitignore line is what other clones get

id: AC-3
criterion: The existing test suite passes
method: test
how: docket verify (pytest -v tooling)
result: pass
evidence: verify exit 0, log above
notes:
```

### Scope review

```text
diff_vs_files_touched: match
extras: none
justified: n/a
notes: the two .DS_Store files are removed from the index only; they remain on disk
```

## Notes for the Reviewer
