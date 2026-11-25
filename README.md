# Docket

Docket is a lightweight process for checking an AI coding agent's work before anyone calls it done.

AI agents can make changes quickly and still fail quietly. They report "tests passed" when they didn't run, change files nobody asked them to touch, review their own work and see what they meant instead of what they wrote, or call something done because they say so. Docket doesn't try to make the agent more trustworthy. It makes your process **depend less on trusting the agent**.

It does this with five plain rules:

1. **Agree on the work first.** Every change starts as a short written Ticket you approve: the problem, the approach, the files it will touch, how to check it, and how to undo it. No code before approval.
2. **Prove it, don't describe it.** The agent records evidence for each acceptance criterion: the command it ran and what happened, not a summary of what it believes.
3. **Let tools check the evidence.** A small command-line tool runs your project's real test command, records the result tied to the exact state of the code, and confirms the agent stayed within the files it was approved to change.
4. **Have someone else review.** A separate reviewer, with no memory of writing the code, checks the evidence against the Ticket.
5. **Done means proven.** Work is done when the evidence holds up and the review passes, not when the agent says it's finished. Merging and deploying stay your decision.

Docket is mostly Markdown (rules, a workflow, role descriptions, templates) plus a small Python tool. You add it to an existing project; it isn't an application.

## How a change moves through Docket

```
TICKET  →  IMPLEMENT  →  SELF-REVIEW  →  PRE-REVIEW  →  REVIEW  →  DONE
you approve   agent builds   agent records   tool checks     separate      evidence
the plan      within scope   evidence        the evidence    reviewer      holds up
```

| Step | Who | What happens | Moves on when |
|---|---|---|---|
| Ticket | Planner (agent) and you | Problem, approach, files touched, acceptance criteria, rollback plan | You approve it |
| Implement | Implementer (agent) | Builds exactly what the Ticket describes, touching only its listed files | The approach is done, with no unapproved extra changes |
| Self-review | Implementer | Records evidence for every acceptance criterion | Evidence is complete |
| Pre-review | The `docket` tool | Runs three checks in order: the project's test command, the scope check, the evidence check | All three pass on the final code |
| Review | Reviewer (separate, read-only) | Checks the evidence and the diff against the Ticket | Pass, send back with specific feedback, or escalate to you |
| Done | | Evidence holds up and the review passed | |

If the reviewer sends work back twice, the third time goes to you instead: two failed attempts usually mean the Ticket itself needs rethinking.

Some actions always need your explicit yes, however small the change: deleting things, touching production, changing dependencies or CI, and anything that can't be undone. These are listed in [`core/RULES.md`](core/RULES.md).

## The `docket` tool

```bash
docket pre-review tickets/001-example.md --audit PROJECT_AUDIT.md   # the normal handoff check
docket review-packet tickets/001-example.md                         # what a fresh reviewer needs
docket verify --audit PROJECT_AUDIT.md --ticket tickets/001-example.md   # individual checks,
docket check-scope tickets/001-example.md                             # in this order
docket check-evidence tickets/001-example.md
docket lint-ticket tickets/001-example.md                           # Ticket structure only
docket done tickets/001-example.md                                  # confirm a finished Ticket
docket resume                                                       # short brief to start a new session
```

- **`verify`** runs your project's test command (named once, in a Project Audit file) and records the exit code, the commit, and a fingerprint of the working tree.
- **`check-scope`** fails if any file changed that isn't listed in the Ticket.
- **`check-evidence`** fails if evidence is missing, doesn't match the recorded run, or is out of date because the code changed afterwards.
- On a failed run, `verify` and `pre-review` print a short failure digest: the error lines and the end of the log.

Passing checks prove the tests ran, the scope held, and the evidence is current. They don't prove the change is correct. That stays the reviewer's job. Full details: [`tooling/README.md`](tooling/README.md).

## Getting started

1. **Add Docket to your project.** Follow [`setup/attach.md`](setup/attach.md): link Docket into the project, write a short Project Audit (your stack, conventions, and test command), and add the instruction file for your coding tool.
2. **Run one Ticket end to end.** Ask for a change, approve the Ticket, let the agent build and self-review, run `docket pre-review`, have a separate reviewer check it, then merge it yourself.
3. **Start a fresh session for the next Ticket.** `docket resume` prints a short brief so the new session doesn't need the old conversation.

Supported tools: **Claude Code** (the reference setup, with a true separate reviewer) and **Cursor** (experimental: it approximates the separate reviewer with a fresh chat).

The tool needs Python 3.10 or newer and no other dependencies. Run it as `bin/docket`, or as `python3 -m docket` with `tooling/` on `PYTHONPATH`.

## What "done" does and doesn't mean

Done requires evidence for every acceptance criterion, a passing test run tied to the current code, scope accounted for, a passing independent review, and no open safety questions.

Done does **not** prove that the acceptance criteria were the right ones, that a test really exercises what it claims, that manual evidence is truthful, or that deploying is safe. Those stay with the reviewer and with you, by design.

## Status

The core process and the tool are implemented and stable for single-ticket work: the evidence contract, the three checks, the pre-review handoff, and reviewer support. Running several Tickets in parallel is described in [`advanced/PARALLEL_LINE.md`](advanced/PARALLEL_LINE.md) but is experimental and unproven.

The current focus is real-project use, not more machinery: learning where agents struggle, whether the evidence is useful or just paperwork, and whether review catches real problems.

## What's in this repository

```
core/            rules, workflow, roles, recipes, templates, changelog
tooling/         the docket command-line tool and its tests
bin/docket       wrapper that runs the tool
adapters/        instruction files for Claude Code (reference) and Cursor (experimental)
setup/attach.md  how to add Docket to a project
skills/          a small helper skill for the self-review step
advanced/        experimental parallel workflow
tickets/         Docket's own Tickets: it is built with its own process
```

Suggested reading order: this README, [`core/RULES.md`](core/RULES.md), [`core/WORKFLOW.md`](core/WORKFLOW.md), [`core/roles/`](core/roles/), [`tooling/README.md`](tooling/README.md).

## Changing Docket

`core/` is shared by every project that uses Docket, so changes need a real incident behind them, follow [`core/RULES.md`](core/RULES.md), and are recorded in [`core/CHANGELOG.md`](core/CHANGELOG.md).

## License

[MIT](LICENSE)
