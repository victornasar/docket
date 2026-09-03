# Changing this kit

**The structural spine is frozen.** `RULES.md`, `WORKFLOW.md`, `roles/`,
and `templates/` get no new stages, roles, rule sections, or structural
files until at least three more projects — varied stack, scale, and
ideally operator — have run the kit end to end. `recipes/` is the one
exception: a new recipe may be added if it's adapted from an established
external source or proven on real work, never invented speculatively.
`CHANGELOG.md` records which projects count toward the three.

Any change to `core/` still has to trace to a real incident on real work,
not a brainstormed improvement. To make one: **name the incident** (which
project, which Ticket, what gap, what would have gone differently with the
fix); **propose the specific fix** (which file, what change, why this
scope) and get the human's sign-off *before* editing `core/`; then **log
it in [`CHANGELOG.md`](CHANGELOG.md)** — date, triggering project/Ticket,
what changed, which files.

If the same category of weakness recurs after a logged fix, that's a new
entry referencing the old one — the first fix missed the root cause.
Subtraction runs the same way: any rule or recipe not triggered across the
next three projects is a candidate for deletion, and the removal is logged
exactly like an addition.
