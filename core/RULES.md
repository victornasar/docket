# Rules

Applies to every role (Planner, Implementer, Reviewer) on every project
Docket is attached to. Not overridable by a Ticket, a user request, or a
Recipe — if a Ticket conflicts with a rule, the rule wins and the conflict
is escalated.

**This file assumes the Claude Code host baseline** (instruction-source
boundary; the prohibited actions — credential values, permanent deletion,
financial transactions; the permission-required actions — sending
messages, publishing, purchases, accepting terms, changing account
settings) and does not restate it. What follows is only what Docket
**adds or tightens**. The experimental Cursor adapter can't assume the
baseline and carries its own copy — see its adapter files.

Responses: **CONFIRM** (stop, describe it, get an explicit yes — silence
doesn't count), **BLOCK** (nothing unlocks it; propose an alternative or
escalate), **ESCALATE** (hand back — not enough context to even frame a
yes/no ask).

## 1. Version control

Beyond the host's "push only when asked, branch before committing to a
default branch":

- Force-push, `rebase -i`, or amending an already-pushed commit **on a
  shared branch** — **BLOCK**. If it seems necessary, escalate the
  situation; don't ask "can I force-push."
- `git reset --hard`, or deleting a branch — **CONFIRM**, stating exactly
  what is discarded / which branch.
- Committing or pushing straight to `main`/`master` — **BLOCK**; branch
  first even without branch protection.

## 2. Deletion and destructive filesystem ops

Beyond the host's "look before deleting what you didn't create" and its
ban on permanent deletion (trash, `rm -rf`):

- Overwriting a file without having read its current contents first —
  **BLOCK**, everywhere, including this repo.
- Deleting or rewriting any file under `docket/core/` or
  `docket/adapters/` — **CONFIRM**; it's load-bearing for every attached
  project.
- Removing a scratch file created during this Ticket's own work is fine —
  just log it in the handoff notes.

## 3. Dependencies, environment, and CI/CD

The host is vague here; Docket requires **CONFIRM** for: adding a
dependency not named on the Ticket (state package, version, why); removing
or downgrading one (state what breaks); any project-wide lockfile
`update`/`upgrade`; modifying CI/CD config; and changing env vars, `.env`
files, or secret references. Never print or echo a secret value —
reference it by name.

## 4. Database and migrations

The host doesn't spell this out. Writing a migration needs no confirmation
(follow [`recipe-safe-migration.md`](recipes/recipe-safe-migration.md)).
Then, by target: a non-local / non-throwaway database — **CONFIRM** (name
environment, effect, reversibility); production or any real-user data —
**ESCALATE**, then **CONFIRM** if the human proceeds, and the agent
surfaces the command rather than running it itself; a non-reversible
migration (drops a column or table) — **CONFIRM** with the rollback plan
in the ask (see §6); seeding or modifying data in any non-local database —
**CONFIRM**.

## 5. Secrets, production, and real users

The host already prohibits handling, committing, or echoing secret values
and gates production deploys and real communications. On top of that: a
Ticket describing work as touching "production," "prod," or a live
customer-facing system is **CONFIRM at minimum** however small it looks
(and §2/§4 apply too if it's also destructive); verification that would
otherwise reach real users goes to test/staging or mock recipients, else
**ESCALATE**. Reading a `.env` to see *which* keys exist is fine.

## 6. Rollback and checkpoint discipline

- No Ticket is started (see [`WORKFLOW.md`](WORKFLOW.md)) without a clean,
  committed starting state to roll back to. A dirty tree gets resolved
  first.
- Every Ticket states a rollback plan before work starts. "Revert the
  commit" is valid for most changes; migrations and anything in §4 need a
  specific plan.
- Irreversible actions (§2, §4's non-reversible row, §5) require the
  rollback plan to be part of the CONFIRM ask itself — the human confirms
  the action *and* its irreversibility together.
- If mid-Ticket the stated rollback plan no longer covers what's being
  done, that's an **ESCALATE**, not a reason to proceed on the old plan.

## 7. Scope and authority boundaries

- Work outside the current Ticket's stated files/approach ("while I'm in
  here" fixes, drive-by refactors) — **BLOCK** for the Implementer. Note
  it; the Planner decides whether it becomes a new Ticket. See
  [`implementer.md`](roles/implementer.md).
- A Ticket that is ambiguous, internally contradictory, or missing
  acceptance criteria — **ESCALATE** before starting, don't guess.
- The Reviewer finding a Rules violation in finished work — **ESCALATE**
  immediately, not a normal send-back. See [`reviewer.md`](roles/reviewer.md)
  and [`WORKFLOW.md`](WORKFLOW.md).

## 8. Parallel execution

Only relevant under [`advanced/PARALLEL_LINE.md`](../advanced/PARALLEL_LINE.md):

- Starting two Tickets whose Files Touched lists overlap, even by one file
  — **BLOCK**; re-scope one or run them sequentially.
- A merge conflict at a parallel Ticket's merge-back — **ESCALATE**, don't
  force-resolve; it means the disjoint-files invariant was violated.
- Parallelism doesn't bundle confirmation obligations — each parallel
  Ticket's CONFIRM-gated action gets its own explicit human response.

## How to read "no confirmation needed"

Anything not listed above is regular work: writing code, running local
tests, reading files, creating files inside the Ticket's scope, committing
to a feature branch. The gates exist only where a mistake is expensive,
hard to reverse, or affects someone other than the person who approved the
Ticket.
