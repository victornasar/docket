# Recipe: Program Design

Owner: Planner, as part of writing a Ticket's Approach — or the
Implementer, if the exact shape only becomes clear once the relevant code
is actually open, in which case this happens right before Implement, not
during it. Adapted from the "program design" phase in Dex Horthy's
[Why Software Factories Fail](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/wsff.md) —
reworked into Docket's own words and tied to the Ticket structure, not
reproduced verbatim.

## The idea

Architecture ("add an export feature," "replace the tab bar with native
`TabView`") is one level above the actual shape of the change: the
fields, the types, the call flow. Skipping straight from architecture to
implementation is where a specific, avoidable class of rework comes
from — not bugs in logic, but a shape that was wrong from the start
because nobody wrote it down before code existed to check it against.

**This has already cost a real rework cycle in this repo.** vitals'
Ticket 19 shipped an export DTO built from a skim of "the current
fields" on `GymEntry`, not a deliberate field-by-field check against the
actual model — and silently dropped two real legacy fields as a result.
Independent review caught it, but a few minutes of this recipe before
Implement would have caught it for free, before any code needed reviewing
at all.

## When to use this

Only for Tickets that introduce **a new type, a new data-transformation
boundary (DTOs, serializers, adapters), a new interface, or a call-flow
change** — not every Ticket. A copy tweak or a one-line style fix doesn't
need this; matches the Planner's existing "size the work" judgment and
Dex's own observation that most tasks don't need the full treatment. If a
Ticket's Approach doesn't involve a new shape, skip this recipe entirely.

## Steps

1. **For a new type or data-transformation boundary:** write out the
   actual field-by-field (or parameter-by-parameter) mapping against the
   real source it derives from — by re-reading the current source file,
   not from memory or a skim. If the source has a field, the mapping
   states explicitly whether it's included and why, or excluded and why
   — "excluded, superseded by X" is a fine answer; "forgot it existed" is
   the failure mode this step exists to catch.
2. **For a call-flow or control-flow change:** sketch the call stack —
   even a few lines of indented text — before implementing. Doesn't need
   a diagram; needs to exist before the code does.
3. **For a change touching more than a couple of files:** extend the
   Ticket's Files Touched entries with a one-line "what changes here"
   per file, not just the filename. Files Touched already answers
   *which* files; this answers *what shape* the change takes in each one.
4. **This becomes part of the Ticket's Approach**, reviewed by the human
   at Ticket-approval time — catching a wrong shape before Implement,
   which is cheaper than catching it at Review, which is cheaper than
   catching it after Done.
5. **This doesn't replace Self-review or Review.** It's an earlier,
   cheaper layer — [recipe-self-review.md](recipe-self-review.md)'s live
   verification and [`reviewer.md`](../roles/reviewer.md)'s independent
   check still both happen. Program design catches wrong *shape* before
   code exists; Self-review and Review catch wrong *behavior* once it
   does.
