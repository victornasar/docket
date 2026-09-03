# Recipe: Domain Modeling (a living glossary)

Owner: Planner, ongoing across many Tickets — not a single-Ticket
procedure. Adapted from the `domain-modeling` skill in
[mattpocock/skills](https://github.com/mattpocock/skills) — reworked into
Tabouleh's own words, not reproduced verbatim.

## The idea

The Project Audit captures a project once, at attach time. Vocabulary
drifts after that — a term gets used two different ways across Tickets
written months apart, and nobody notices until it causes a real mistake.
This recipe is a small, optional habit for catching that drift as it
happens, not a document to produce up front.

## Steps

1. **Don't create `CONTEXT.md` preemptively.** Create it the first time a
   real terminology question actually comes up while writing a Ticket —
   not as part of the initial Project Audit. An example of "real": Vitals'
   Ticket 10 had to settle whether "service" meant only a scheduled,
   due-tracked maintenance item, or also covered a one-off logged repair
   with no schedule — that's exactly the kind of question worth capturing
   once it's resolved, not before.

2. **When the human's words and the codebase's existing naming diverge,
   say so.** This is a specific, concrete version of the Planner's
   existing duty to ask clarifying questions
   ([`planner.md`](../roles/planner.md)) — worth naming on its own because
   terminology drift is a recurring, easy-to-miss flavor of ambiguity.
   "Your request says X, the code calls this Y — same thing?" is a
   one-line question, not a research project.

3. **Record resolved terms immediately**, as a short glossary entry (term
   → one-line definition) in `CONTEXT.md`, right when they're settled —
   not batched up at the end of a Ticket where half of them get
   forgotten.

4. **Write an ADR (Architecture Decision Record) separately, and only
   when all three are true:** the decision is costly to reverse later, it
   would be non-obvious to a future reader why it was made this way, and
   it involved a genuine trade-off between real alternatives. Most
   decisions don't clear this bar. Concrete example from this project:
   deciding *not* to unify `VitalsFont` with native Dynamic Type styles
   (Ticket 3) was ADR-worthy — costly-ish to revisit, not obvious from the
   code alone why Forms and cards diverge, and a real trade-off between
   visual consistency and accessibility. Renaming a magic number to a
   named token (Ticket 2) was not — trivially reversible, one obviously
   correct answer, nothing to explain to a future reader.

5. **Multiple genuinely separate domains** (a project tracking two
   unrelated things with vocabularies that don't overlap) can use a
   `CONTEXT-MAP.md` pointing to one `CONTEXT.md` per domain instead of a
   single shared glossary. Most single-purpose projects don't need this —
   don't reach for it by default.

6. **`CONTEXT.md` stays a glossary, nothing else.** Terms and their
   meanings only. Specs belong in Tickets. Reasoned decisions belong in
   ADRs. Implementation notes belong in code comments. If it starts
   accumulating any of those, that content has drifted into the wrong
   file — move it, don't let `CONTEXT.md` become a second Project Audit.
