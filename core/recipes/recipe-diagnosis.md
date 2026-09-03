# Recipe: Diagnosis

Owner: Planner, as a pre-Ticket investigation when a request is a
bug or performance regression with no known cause — or the Implementer, if
a bug turns out mid-Implement to be somewhere other than where the Ticket
said it was. Adapted from the `diagnosing-bugs` skill in
[mattpocock/skills](https://github.com/mattpocock/skills) — reworked into
Docket's own words and split across the workflow rather than reproduced
verbatim.

## The idea

A bug with an unknown cause can't be ticketed. You can't write Files
Touched, an Approach, or a rollback plan for a defect you haven't located
yet — so trying to skip straight to a Ticket produces a fictional one that
the Implement stage then can't follow. Diagnosis is the work that turns
"X is broken" into "X is broken *here*, for *this* reason, and *this*
command proves it," which is what a real Ticket needs.

The whole discipline is one move: **build a tight, red-capable feedback
loop before theorising about the cause.** A loop that goes red on *this*
bug and green when it's fixed does 90% of the work — bisection,
hypothesis-testing, and instrumentation all just consume it. Reading code
to build a theory before that loop exists is the exact failure this recipe
prevents.

## When to use this

Any Ticket whose Problem is "something is broken / throwing / failing /
slow" and the cause isn't already known. If the cause *is* already
understood (a typo, an obvious off-by-one, a missing null check the
stack trace points straight at), skip this — write the Ticket directly.
This is for the bugs where you'd otherwise start guessing.

## Where this sits in the workflow

- **Phases 1–4 run before Stage 1 (Ticket).** The Planner (or a
  context it delegates to) does them; the output — confirmed root cause
  plus the minimal repro — becomes the Ticket's Problem statement, and
  the repro becomes its first acceptance criterion (it goes green when
  the fix lands).
- **Phases 5–6 fold into Implement and Self-review.** The Implementer
  writes the regression test, applies the fix, and does cleanup as normal
  Ticket work.
- If diagnosis during Implement shows the Ticket's Files Touched or
  Approach was aimed at the wrong place, that's an escalate-to-Planner per
  [`WORKFLOW.md`](../WORKFLOW.md) Stage 4 — not something the Implementer
  re-plans silently.

## Steps

1. **Build the feedback loop.** One command you have already run at least
   once that drives the actual bug code path and asserts the user's exact
   symptom — a failing test, a curl against a dev server, a CLI call
   diffed against known-good output, a replayed captured request, a
   throwaway harness around one function. It must be *red-capable*
   (catches this specific bug, not just "runs without erroring"),
   *deterministic* (same verdict every run — for a flaky bug, loop the
   trigger until the reproduction rate is high enough to debug against),
   and *fast* (seconds). Spend disproportionate effort here.
2. **Reproduce and minimise.** Run the loop, watch it go red, confirm
   it's the symptom the user described and not a nearby one. Then shrink
   the scenario one element at a time, re-running after each cut, until
   every remaining element is load-bearing — removing any one makes it go
   green. The minimal repro is the regression test later.
3. **Hypothesise.** Write 3–5 ranked, falsifiable hypotheses *before*
   testing any — each stating its prediction ("if X is the cause, then
   changing Y makes the bug disappear"). A hypothesis with no prediction
   is a vibe; sharpen or drop it. Show the list to the human if they're
   around — domain knowledge re-ranks it instantly.
4. **Instrument.** One probe per hypothesis, one variable changed at a
   time. Prefer a debugger or REPL breakpoint over logs; if logging, tag
   every line with a unique prefix (`[DEBUG-a4f2]`) so cleanup is one
   grep. For performance regressions, measure against a baseline and
   bisect — don't log.
5. **Regression test, then fix** (Implementer, during Implement). Turn the
   minimal repro into a test at a seam that exercises the real bug
   pattern as it occurs at the call site. Watch it fail, apply the fix,
   watch it pass, then re-run the Phase 1 loop against the original
   un-minimised scenario. If no honest seam exists for the test, say so
   in the handoff notes — that's a finding about the codebase, not a step
   to skip.
6. **Cleanup** (Implementer, at Self-review). Original repro no longer
   reproduces; all `[DEBUG-...]` instrumentation removed; throwaway
   harnesses deleted; the hypothesis that turned out correct is stated in
   the commit or PR message so the next debugger learns from it.

## Redaction

This recipe has you show commands and their output. Redact every secret
before showing it — write `<REDACTED>` in its place, build loops against
environment variables so credentials stay in the environment, and quote
only the signal-carrying lines of any captured trace. See
[`RULES.md`](../RULES.md) §5.

## When you genuinely cannot build a loop

Stop and say so — don't proceed to guessing. List what you tried and ask
the human for one of: access to an environment that reproduces it, a
redacted captured artifact (HAR, log dump, core dump), or permission to
add temporary instrumentation. No loop, no Ticket.
