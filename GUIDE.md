# Guide: building with Docket

A hands-on walkthrough you can come back to. It takes two sample issues through Docket from request to Done: one trivial, one real. The [README](README.md) explains what Docket is; this shows what using it looks like.

## The idea in one paragraph

You agree on the work before any code exists (the Ticket). The agent builds only that, then proves each acceptance criterion with evidence. A small tool checks the evidence is real, current, and in scope. A separate reviewer, who never saw the agent's reasoning, decides whether the evidence is enough. You approve the plan at the start and merge at the end. Nobody has to take the agent's word for anything.

## Who does what

| Role | Who | Does | Never does |
|---|---|---|---|
| Planner | Agent | Turns your request into a draft Ticket | Writes code, approves its own Ticket |
| You | Human | Approve Tickets, answer CONFIRM asks, merge and deploy | Nothing is assumed from your silence |
| Implementer | Agent | Builds what the Ticket says, records evidence, runs `docket pre-review` | Touches files outside the Ticket, decides it's Done |
| Reviewer | Separate agent, read-only | Checks evidence and diff against the Ticket: Pass, Send-back, or Escalate | Edits anything, fills in missing evidence itself |
| `docket` tool | Deterministic | Runs the test command, checks scope and evidence | Judges whether the work is correct |

## Set up once per project

Follow [setup/attach.md](setup/attach.md). The parts you should check yourself:

- **`PROJECT_AUDIT.md`, Verification section.** This is the one test command every Ticket is checked with. If it's wrong, every gate is wrong.
- **The fresh-session test.** Ask for a small change in a new session. You should get a draft Ticket, not code. If you get code, the adapter file isn't loading.

## The sample project

**Shelf** is a small Python web app a neighborhood library uses to lend books. `PROJECT_AUDIT.md` names `pytest -v` as the Verification command.

> **Issue #12: README has a typo in the run command**
>
> The Quick start says `pyhton -m shelf`. Should be `python -m shelf`.

> **Issue #15: Popular books never come back**
>
> Members can renew a loan as many times as they want. We need a limit on renewals.

## Walkthrough 1: the knockout (#12)

Even a typo goes through a Ticket. That's deliberate: the process doesn't depend on the agent judging what's "too small to check". It's also why Docket is attached per project, not everywhere.

1. **Ticket.** You ask for the fix. The Planner drafts `tickets/012-fix-readme-typo.md`:
   - Files touched: `README.md`
   - AC-1: The Quick start command reads `python -m shelf` and starts the app. (command)
   - Rollback plan: Revert the commit.
2. **Approve.** You read it and say yes.
3. **Implement.** The Implementer records `Baseline:` (the current commit), sets Status `in-progress`, and fixes the word.
4. **Self-review.** It runs `python -m shelf` and records that as AC-1's evidence (`method: command`), then runs `docket pre-review`. The project's test suite runs too, even for a docs change. Pre-review passes.
5. **Review.** The Reviewer reads the Ticket and the one-line diff: Pass.
6. **Done.** The Implementer commits with Status `done` and runs `docket done`.

## Walkthrough 2: the real problem (#15)

### 1. Ticket

You ask for a renewal limit. The Planner reads `shelf/loans.py` and `shelf/holds.py` first, and finds that `Loan.renewals` is already counted but never checked.

The request leaves policy open: how many renewals, whether a hold blocks renewal, what happens to loans already over the limit. Those are your decisions, so the Planner asks before writing the Ticket. Say you answer: 2 renewals, holds block renewal, loans already over the limit are refused.

The draft:

```markdown
# Ticket: Limit loan renewals to 2, and refuse renewals when a hold exists

**Status:** draft
**Baseline:**

## Problem
renew() increments Loan.renewals but never checks it, so loans can be renewed
forever and books with holds never return.

## Approach
1. In renew(), refuse when loan.renewals >= 2 (applies to existing loans too).
2. In renew(), refuse when another member holds the book (holds.has_waiting).
3. Refusals raise LoanError with a message saying why; the due date is unchanged.

## Files touched
- shelf/loans.py
- tests/test_loans.py

## Acceptance criteria
- [ ] AC-1: Renewing a loan with 2 renewals raises LoanError and leaves the due date unchanged. (test)
- [ ] AC-2: Renewing a loan whose book has another member's hold raises LoanError. (test)
- [ ] AC-3: Renewing with 0 or 1 renewals and no hold still adds 14 days. (test)

## Rollback plan
Revert the commit. No data changes.

## Rules check
Nothing BLOCK or CONFIRM.

## Evidence
(blank until Self-review)
```

`docket lint-ticket tickets/015-renewal-limit.md` checks the structure.

### 2. Approve

What to check before you say yes:

- **Do the ACs say what you meant?** Each should be a yes/no fact. "Renewals work correctly" is not an AC.
- **Is Files touched complete?** Every changed file must be listed. A missing file means the scope check will stop the work later.
- **Would the reviewer understand this without your conversation?** They only see the Ticket and the diff.

### 3. Implement

The Implementer starts from a clean, committed tree, records `Baseline: <commit>`, sets Status `in-progress`, and builds only the Approach. If it finds that `holds.py` needs a change too, it stops and tells you. That's a Ticket amendment or a new Ticket, not a quiet extra edit.

### 4. Self-review: record evidence

For each AC it records what it ran and what happened. For tested ACs it lists the test IDs, which the tool checks against the actual run:

```text
id: AC-2
criterion: Renewing a loan whose book has another member's hold raises LoanError
method: test
how: pytest -v tests/test_loans.py
result: pass
tests:
- tests/test_loans.py::test_renew_refused_when_other_member_holds
```

Then the handoff check:

```bash
docket pre-review tickets/015-renewal-limit.md --audit PROJECT_AUDIT.md
```

It runs three gates in order. Here is what each one catches:

| Gate | Fails when | Example |
|---|---|---|
| `verify` | The Project Audit's test command fails | A refactor broke an unrelated test. The output is a short digest, not the whole log |
| `check-scope` | A file changed that isn't in Files touched | The agent "tidied up" `shelf/holds.py` |
| `check-evidence` | Evidence is missing, a listed test didn't pass in the recorded run, or the code changed after the run | The agent fixed a typo in the test after running the suite, so the recorded run is stale |

The Project verify block in the Ticket is copied from the tool's output, never typed. Any failure blocks the handoff, and the fix is to change what the gate points at, never the record. Once it exits 0, Status becomes `in-review`.

### 5. Review

The main session spawns the reviewer agent and hands it the Ticket. It runs `docket review-packet tickets/015-renewal-limit.md` to find everything it needs and reads the diff from Baseline. It has no write access.

Possible outcomes:

- **Pass.** Every AC has adequate evidence.
- **Send-back**, with itemized findings. For example: "AC-2: the test uses a hold placed by the borrower themselves, so it never tests another member's hold." The Implementer fixes it, re-runs what changed, updates the evidence, and runs pre-review again.
- **Escalate** to you: a Rules violation, a Ticket that's wrong rather than badly implemented, or a third attempt after two send-backs.

### 6. Done

On Pass, the Implementer commits the work with Status `done` and runs:

```bash
docket done tickets/015-renewal-limit.md
```

It refuses unless the Ticket says `done`, the tree is clean, and the last commit includes the Ticket. Then it prints the next Ticket, if `tickets/README.md` lists one, and tells you to start a fresh session.

Done means the evidence held up and review passed. It doesn't mean merged or deployed. **You** merge.

### 7. Next Ticket

Start a fresh session (`/clear`) and run `docket resume`. It prints a brief of under 40 lines (status, Baseline, AC states, whether the last test run is still current, changed files), so the new session doesn't need the old transcript.

## Things that always need your explicit yes

However small the Ticket, the agent stops and asks before: deleting things, touching production or real user data, adding or removing dependencies, changing CI, changing env vars or secrets, and anything irreversible. The full list is in [core/RULES.md](core/RULES.md).

## Command cheat sheet

| Command | When |
|---|---|
| `docket lint-ticket <ticket>` | Check a draft Ticket's structure |
| `docket pre-review <ticket> --audit PROJECT_AUDIT.md` | End of Self-review. Must exit 0 before Review |
| `docket review-packet <ticket>` | What a fresh reviewer needs |
| `docket done <ticket>` | After the Done commit |
| `docket resume [<ticket>]` | First thing in a new session |

Details and escape-hatch flags: [tooling/README.md](tooling/README.md).

## Pairing with Hechent

Docket checks whether work can be trusted. It doesn't teach the agent how to do the engineering. [Hechent](https://github.com/victornasar/hechent) does that: it sizes each change, asks only the questions that are yours, and verifies before claiming anything. When Docket is attached, Hechent works inside the Ticket flow above and never approves or marks anything done itself. Its [guide](https://github.com/victornasar/hechent/blob/main/docs/guide.md) walks through the same two issues with both tools.
