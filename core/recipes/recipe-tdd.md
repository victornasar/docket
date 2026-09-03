# Recipe: Test-Driven Development

Owner: Implementer, during Implement. Adapted from the `tdd` skill in
[mattpocock/skills](https://github.com/mattpocock/skills) — reworked into
Tabouleh's own words and tied into the Ticket/workflow structure rather
than reproduced verbatim.

Use this when a Ticket's approach involves new behavior with a test suite
to write against (see the Project Audit's Test setup section — if a
project has no test framework, step 7 below applies instead of the rest).

## Steps

1. **Agree on the seam before writing a test.** A seam is the public
   boundary you test at — a function signature, an API response, an
   exported behavior — not a private method or internal data structure.
   If the Ticket's acceptance criteria are already checkable statements
   (per [recipe-ticket-writing.md](recipe-ticket-writing.md)), the seam is
   usually just "the thing that criterion describes." If it isn't obvious,
   that's worth a quick check back against the Ticket before writing code,
   not a guess.

2. **Write one failing test for one vertical slice.** Not "all the tests,
   then all the code" (horizontal slicing) — one slice of real behavior,
   tested, then built, then the next slice. Run it and confirm it fails
   for the reason you expect (red), not for an unrelated compile error.

3. **Write the minimum implementation to pass that test** (green). Resist
   building ahead of the current slice — the next slice gets its own
   red-green cycle, not a preemptive implementation now.

4. **Repeat per slice.** Each vertical slice of the Ticket's acceptance
   criteria gets its own red→green cycle rather than batching several
   together.

5. **Don't refactor mid-cycle.** Refactoring belongs in Self-review
   ([recipe-self-review.md](recipe-self-review.md)) or in the Standards
   pass of [recipe-code-review.md](recipe-code-review.md) — interleaving
   it into red/green makes it unclear whether a test failure is a real
   regression or fallout from an in-progress refactor.

6. **Watch for two specific failure patterns:**
   - **Tautological assertions** — a test that recomputes the same logic
     the implementation uses, so it can never catch a real bug. (`assert
     result == price * 0.9` when the implementation is also just `price *
     0.9` proves the arithmetic works, not that the behavior is correct.)
   - **Testing through a private seam** — asserting against an internal
     method or data shape that changes whenever the implementation is
     refactored, even when the actual observable behavior hasn't changed.
     A test that breaks on every refactor isn't testing behavior, it's
     testing implementation.

7. **No test framework in the project yet?** Don't add one unprompted.
   Per [`RULES.md`](../RULES.md) §3, adding a dependency is a
   CONFIRM-gated action — flag it back to the Planner as a decision for
   the human, not something to fold into the current Ticket silently.
