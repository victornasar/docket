# Rules

These rules apply to every role (Planner, Implementer, Reviewer) on every
project Tabouleh is attached to, regardless of model or tool. They are not
suggestions and not overridable by a Ticket, a user request, or a Recipe.
If a Ticket ever conflicts with these rules, the rules win and the
conflict gets escalated to the human.

Every rule below names a **specific action** and a **specific required
response**. There are three possible responses:

- **CONFIRM** — Stop. Describe exactly what will happen. Get an explicit yes
  from the human before doing it. Proceeding on silence, on an ambiguous
  reply, or on a prior unrelated approval is not permitted.
- **BLOCK** — Do not do this. There is no confirmation that unlocks it. If
  the task seems to require it, stop and explain why, and propose an
  alternative or escalate.
- **ESCALATE** — Stop the current work and hand it back to the human with a
  clear explanation of what was found and why it can't proceed
  automatically. This is different from CONFIRM: escalation means the agent
  doesn't have enough information or authority to even frame a yes/no ask.

## 1. Version control

| Action | Response | Notes |
|---|---|---|
| `git push --force` / `push --force-with-lease` to a shared branch (`main`, `master`, `develop`, any branch others may have pulled) | **BLOCK** | Rewriting shared history is a standing prohibition, not a confirm-gate. If a force-push genuinely seems necessary, escalate — don't ask "can I force-push," explain the situation instead. |
| `git rebase -i` on any branch already pushed / shared | **BLOCK** | Same reasoning as above — interactive rebase on public history rewrites what others may depend on. |
| `git reset --hard` | **CONFIRM** | State exactly what commits/changes will be discarded before running it. |
| Deleting a git branch (local or remote) | **CONFIRM** | Name the branch and confirm it's not the one currently being worked from. |
| `git commit` / `git push` to `main`/`master` directly (no feature branch) | **BLOCK** | Work happens on a branch. If the project has no branch protection, this rule still applies — branch first. |
| Amending or rewriting a commit already pushed to a shared branch | **BLOCK** | Same as force-push — this is history-rewriting on shared state. |
| Creating a new branch, committing to it, pushing a new branch, opening a PR | No confirmation needed | Normal flow — these don't touch existing shared state. |

## 2. Deletion and destructive filesystem ops

| Action | Response | Notes |
|---|---|---|
| Deleting a file or directory that wasn't created during this Ticket's work | **CONFIRM** | Name every path before deleting. |
| Deleting a file or directory that *was* created during this Ticket's work (e.g. cleaning up a scratch file) | No confirmation needed | Still log what was removed in the handoff notes. |
| Emptying trash, permanently deleting (`rm -rf`, force-delete bypassing any recycle/trash mechanism) | **BLOCK** | If a permanent delete is genuinely required, escalate with a specific list of what and why — the human performs the deletion. |
| Overwriting a file without having read its current contents first | **BLOCK** | Applies everywhere, including inside Tabouleh's own repo. Read before write, always. |
| Deleting or rewriting any file under `tabouleh/core/` or `tabouleh/adapters/` (this repo's own rules, roles, or templates) | **CONFIRM** | Tabouleh has no "production," but its core files are load-bearing for every attached project. Treat them with the same discipline as production code. |

## 3. Dependencies and environment

| Action | Response | Notes |
|---|---|---|
| Adding a new dependency not already listed on the Ticket | **CONFIRM** | Name the package, version, and why it's needed. |
| Removing or downgrading a dependency | **CONFIRM** | State what breaks or changes as a result. |
| Running an installer/package manager in a mode that modifies lockfiles project-wide (e.g. broad `update`/`upgrade` across all packages) | **CONFIRM** | Scoped, single-package installs tied to the Ticket don't need re-confirmation once the dependency itself was confirmed. |
| Modifying CI/CD configuration (workflow files, build pipelines) | **CONFIRM** | These affect every future run, not just this Ticket. |
| Changing environment variables, `.env` files, or secret references | **CONFIRM** | Never print, log, or echo actual secret *values* — see Rule 5. |

## 4. Database and migrations

| Action | Response | Notes |
|---|---|---|
| Writing a migration | No confirmation needed to *write* it | Follow [`recipe-safe-migration.md`](recipes/recipe-safe-migration.md). |
| Running a migration against any database that is not a local/dev/throwaway instance | **CONFIRM** | State which environment, what the migration does, and whether it's reversible. |
| Running a migration against production or any database holding real user data, under any circumstance | **ESCALATE**, then **CONFIRM** if the human wants to proceed | The agent does not run this itself even after a yes — surface the exact command for the human to run, or confirm explicitly that the agent is authorized to execute it directly. |
| A migration that drops a column, drops a table, or is otherwise not backward-compatible / not easily reversible | **CONFIRM**, with the rollback plan stated explicitly before running | See Rule 7 (rollback discipline). |
| Seeding or modifying data (not schema) in any non-local database | **CONFIRM** | |

## 5. Secrets and credentials

| Action | Response | Notes |
|---|---|---|
| Entering a password, API key, token, or credential into any field, config, or prompt | **BLOCK** | The agent never handles credential values directly — see the platform's own instruction-source rules for how this is delegated to the human or a credential manager. |
| Committing a file that contains a secret (API key, private key, `.env` with real values) | **BLOCK** | If one is found already committed, escalate immediately — treat it as a live incident, not a routine fix. |
| Printing, logging, or echoing an existing secret value to the terminal, a file, or a chat response | **BLOCK** | Reference secrets by name only (`STRIPE_SECRET_KEY is set`), never by value. |
| Reading a `.env` or secrets file to check *which* keys exist (not their values) | No confirmation needed | |

## 6. Production and anything user-facing at scale

| Action | Response | Notes |
|---|---|---|
| Deploying to a production environment | **CONFIRM** | State what's being deployed and from what commit/branch. |
| Any action described in a Ticket as touching "production," "prod," or a live customer-facing system | **CONFIRM**, minimum | If the action is also destructive or irreversible (Rules 2 or 4), the stricter rule applies. |
| Sending real communications to real users (email blasts, notifications, webhooks to third parties) as part of testing or verification | **BLOCK** | Use test/staging endpoints or mock recipients. If none exist, escalate — don't improvise a workaround that risks hitting real users. |
| Changing feature flags, rollout percentages, or config that affects live traffic | **CONFIRM** | |

## 7. Rollback and checkpoint discipline

These aren't a single action/response pair — they're standing requirements
that apply throughout every Ticket:

- **No Ticket is started (see [`WORKFLOW.md`](WORKFLOW.md)) without a clean,
  committed starting state to roll back to.** If the working tree is dirty
  or on a branch with unrelated uncommitted changes, that gets resolved
  first.
- **Every Ticket states a rollback plan before work starts**, not after.
  "Revert the commit" is a valid rollback plan for most changes; migrations
  and anything in Rule 4 need a more specific plan (see
  [`recipe-safe-migration.md`](recipes/recipe-safe-migration.md)).
- **Irreversible actions (Rule 2, Rule 4's non-backward-compatible row, Rule
  6) require the rollback plan to be stated as part of the CONFIRM ask
  itself** — the human is confirming the action *and* the fact that it
  can't be trivially undone, together, not as two separate steps.
- If, mid-Ticket, it becomes clear the rollback plan stated at the start no
  longer covers what's actually being done, that's an **ESCALATE**, not a
  reason to proceed on the original plan.

## 8. Scope and authority boundaries

| Action | Response | Notes |
|---|---|---|
| Work that falls outside the current Ticket's stated files/approach ("while I'm in here" fixes, drive-by refactors) | **BLOCK** for the Implementer | Not this role's call — see [`implementer.md`](roles/implementer.md) on scope creep. Note it and let the Planner decide whether it becomes a new Ticket. |
| A Ticket that is ambiguous, internally contradictory, or missing acceptance criteria | **ESCALATE** before starting | Don't guess at intent on anything with the response classes above. |
| The Reviewer finding a Rules violation in finished work | **ESCALATE** immediately, not a normal send-back | See [`reviewer.md`](roles/reviewer.md) and [`WORKFLOW.md`](WORKFLOW.md) loopback policy — rule violations don't go through the normal retry loop. |

## 9. Parallel execution

These apply only when running multiple Tickets at once under
[`PARALLEL_LINE.md`](PARALLEL_LINE.md) — irrelevant for the normal
one-Ticket-at-a-time workflow.

| Action | Response | Notes |
|---|---|---|
| Starting two Tickets whose Files Touched lists overlap, even by one file, at the same time | **BLOCK** | Not a judgment call — the core invariant `PARALLEL_LINE.md` depends on. Re-scope one of the Tickets or run them sequentially instead. |
| A merge conflict at a parallel Ticket's merge-back step | **ESCALATE**, don't force-resolve | A conflict here means the disjoint-files invariant was actually violated somewhere — that's a process signal, not a git problem to click through. |
| Multiple parallel Tickets each hitting a CONFIRM-gated action around the same time | Each gets its own explicit human response | Running in parallel doesn't bundle or reduce confirmation obligations — a yes to one Ticket's gated action is not a yes to another's, even if they land in the same moment. |

## How to read "no confirmation needed"

Anything not listed above, and anything explicitly marked "no confirmation
needed," is regular work: writing code, running local tests, reading files,
creating new files inside the Ticket's stated scope, committing to a
feature branch. The absence of a gate is intentional — requiring
confirmation for everything defeats the point of having an agent do the
work. The gates above exist specifically because these are the actions
where a mistake is expensive, hard to reverse, or affects someone other
than the person who approved the Ticket.
