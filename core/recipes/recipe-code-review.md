# Recipe: Two-Axis Code Review

Owner: Reviewer, at Review. Also usable by the Implementer as a second
pass during Self-review, after [recipe-self-review.md](recipe-self-review.md)'s
checklist. Adapted from the `code-review` skill in
[mattpocock/skills](https://github.com/mattpocock/skills) — reworked into
Tabouleh's own words, not reproduced verbatim.

## The idea

A diff can satisfy the Ticket's acceptance criteria while still being
badly written, and it can be well-written while still missing what the
Ticket asked for. Checking both at once tends to let one mask the other —
a reviewer who's impressed by clean code can wave through a spec miss, and
a reviewer focused on "does this match the Ticket" can wave through a
messy implementation because it technically works. This recipe keeps them
as two separate passes with two separate verdicts.

## Steps

1. **Pin the fixed point.** The diff being reviewed is everything since
   the Ticket's baseline commit — the same boundary
   [`WORKFLOW.md`](../WORKFLOW.md) already uses for Self-review. Nothing
   new here, just stating it explicitly before starting two passes over
   it.

2. **Spec axis: does it satisfy the Ticket?** This is
   [`reviewer.md`](../roles/reviewer.md)'s existing checklist item
   one — walk the acceptance criteria individually, verify each one
   against actual behavior, not assumption. Nothing in this recipe
   replaces that; it's the first of the two axes.

3. **Standards axis: is it well-crafted, independent of the Ticket?**
   Read the diff a second time, this time ignoring whether it matches the
   Ticket at all. Check it against:
   - The project's own documented conventions (the Project Audit's
     Conventions section) — these always win over the generic baseline
     below when they conflict.
   - Where conventions don't say, the smell baseline below — judgment
     calls, not hard violations, and always overridable by a documented
     project convention.

4. **Report the two axes separately.** Don't blend them into one
   verdict — say which specific items are Spec misses and which are
   Standards findings, under separate headings if writing this up. A
   Ticket can be "Spec: pass, Standards: one finding" — that's a valid,
   useful outcome, not something to average into a single pass/fail.

5. **Standards findings don't automatically send a Ticket back.** Per
   [`WORKFLOW.md`](../WORKFLOW.md), a Spec miss or a Rules violation is
   what triggers a send-back or escalation. A Standards-axis finding that
   isn't a rules violation and doesn't block correctness is usually a
   candidate for its own future Ticket (note it, don't silently fix it
   mid-review — see the Implementer's scope-creep boundary in
   [`implementer.md`](../roles/implementer.md)), unless it's severe enough
   that shipping it as-is would be irresponsible — in which case escalate
   rather than guess.

## Smell baseline

Judgment calls, from Fowler's *Refactoring* — use when the project has no
stronger documented convention:

- **Mysterious name** — a name that doesn't say what the thing does or
  holds
- **Duplicated code** — the same logic appearing in more than one place
- **Long function / large class** — doing enough unrelated things that it
  resists being described in one sentence
- **Feature envy** — a function more interested in another object's data
  than its own
- **Data clumps** — the same group of values passed around together
  instead of modeled as one thing
- **Primitive obsession** — using raw strings/ints where a small type
  would carry more meaning
- **Shotgun surgery** — one conceptual change requires edits scattered
  across many unrelated files
- **Divergent change** — one file keeps changing for many unrelated
  reasons

None of these are violations on their own — they're prompts to ask "is
there a reason this is shaped this way?" before flagging it.
