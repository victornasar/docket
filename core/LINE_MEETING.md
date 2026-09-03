# The Line Meeting

A line meeting is the real restaurant term for the pre/post-shift huddle
where a kitchen reviews what happened and adjusts before the next
service. This is that, for Tabouleh itself: the procedure for turning a
real weakness found while doing real work on an attached project into an
actual change to `core/`, instead of the weakness just being noticed once
and then forgotten the next time it bites.

This formalizes what already happened twice in this repo's own history —
finding that the Reviewer was reviewing its own work in the same
context, and building the Parallel Line — into a repeatable procedure,
so future findings go through the same discipline instead of depending on
someone happening to ask the right question.

## When this applies

A Line Meeting candidate is a weakness **in the process itself**, found
**while doing real work**, not a hypothetical improvement invented by
sitting down and brainstorming. Two tests, both must pass:

1. **It's about the process, not the output.** "This Ticket's code has a
   bug" is the Review stage's job on that Ticket, not a Line Meeting.
   "The process that was supposed to catch this kind of bug has a
   structural gap" is a Line Meeting.
2. **It's grounded in something that actually happened**, not a vague
   feeling that something could be better. "The Reviewer missed X
   because it reviewed its own reasoning" is grounded. "Maybe reviews
   should be stricter" is not — that's not specific enough to fix
   anything, and isn't a Line Meeting finding until it's tied to a real
   incident.

Deliberate, planned additions to the kit (a new feature someone
decided to build, like the Parallel Line) are **not** Line Meeting
findings — they don't need an incident, they need the same design
rigor as anything else in `core/`, but they're proposed directly, not
through this recipe. Line Meeting is specifically for closing gaps that
real use exposed.

## Steps

1. **Capture the incident concretely before proposing anything.** What
   Ticket, what specific action or gap, what would have gone differently
   with the fix in place. This is the same discipline as a postmortem —
   describe what happened and why the gap exists, not just that something
   felt off.
2. **State the fix with Ticket-Approach-level specificity.** Which
   `core/` file(s) change, what the change is, and why this fix rather
   than a narrower or broader one. A finding without a specific proposed
   fix isn't ready to bring to the human yet — go back to step 1.
3. **Present the finding and the proposed fix before touching any core
   file.** Not optional, and not weaker because it's "only markdown" —
   `core/` is load-bearing for every attached project (see the main
   [`README.md`](../README.md)'s Scope section), so this is where that
   stated discipline actually happens, not just a policy line that gets
   skipped in practice.
4. **On approval, apply the fix and log it in
   [`CHANGELOG.md`](CHANGELOG.md).** One entry: date, the triggering
   project/Ticket, what changed, which files. This is what makes the
   kit's evolution auditable — every rule in `core/` should be
   traceable to either the original scaffold or a specific logged
   incident, not silent drift.
5. **If the same category of weakness resurfaces after a logged fix**,
   that's a new finding on its own — the original fix didn't reach the
   actual root cause. Log it as a new entry that references the earlier
   one, rather than patching over the same spot again.

## Who can raise a finding

Any role can surface one — an Implementer running into a
scope-creep-adjacent situation the rules didn't quite cover, a Reviewer
noticing its own checklist has a gap, a Planner finding the Project Audit
structurally insufficient for a new kind of project. Whoever notices it
writes up steps 1–2. Only the human approves step 3 — same authority
boundary as every other core-file change in Tabouleh, nothing new here.

## What this is not

- Not a way around the Rules' confirmation discipline for `core/` —
  it's the concrete procedure for how that discipline gets exercised.
- Not proactive "let's brainstorm kit improvements" — see the two
  tests above. Speculative ideas are fine to raise, but they're a
  conversation, not a Line Meeting finding, until grounded in something
  that actually happened.
- Not a replacement for git history — `CHANGELOG.md` is a curated,
  human-readable index on top of it, answering "why does this rule
  exist," which a raw commit log doesn't make easy to scan quickly.
