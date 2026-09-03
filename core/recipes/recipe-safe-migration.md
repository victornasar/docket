# Recipe: Safe Database Migration

Owner: Implementer (writing), subject to [`RULES.md`](../RULES.md) §4
(Database and migrations) for running it. Use this whenever a Ticket's
approach involves a schema change.

## Steps

1. **Confirm the migration is on the Ticket explicitly.** "Add a migration"
   should appear in the Ticket's Approach and Files Touched, not be
   introduced mid-implementation. If a migration turns out to be necessary
   partway through a Ticket that didn't call for one, that's a Ticket
   revision, not a silent addition — flag it back to the Planner.

2. **Prefer additive, backward-compatible changes.** In order of
   preference:
   - Add a nullable column / new table → safest, fully backward-compatible.
   - Add a column with a default → safe, but check the default's
     performance impact on large tables before assuming it's free.
   - Rename a column → not backward-compatible for anything still reading
     the old name. Prefer *add new + backfill + remove old in a later,
     separate migration* over a straight rename.
   - Drop a column / drop a table / change a column's type in place → the
     highest-risk category. Requires the CONFIRM step in Rules §4
     with the rollback plan stated explicitly, and should generally be
     split into "stop using it in code" (one Ticket) then "remove it" (a
     separate, later Ticket) rather than one atomic change.

3. **Write the down-migration (or explicit rollback steps) alongside the
   up-migration.** If the migration tool doesn't support automatic
   rollback, write out the exact reverse steps as part of the Ticket's
   rollback plan — "revert the commit" is not sufficient once a migration
   has actually been applied to a real database, because the code revert
   and the schema revert are two different operations.

4. **Check for backfill needs.** A new required (`NOT NULL`, no default)
   column needs a backfill step for existing rows before the constraint can
   be applied, or the migration needs to add the column nullable first,
   backfill, then tighten the constraint in a follow-up.

5. **Estimate impact on the target table.** For any table plausibly large
   in production, note whether the migration takes a lock, how long it's
   expected to run, and whether it needs to run online (e.g. via a
   tool/pattern the project already uses for zero-downtime migrations, per
   the Project Audit).

6. **Never run it against anything but a local/dev/throwaway database
   without going through Rules §4.** Writing and testing the migration
   against a local database needs no confirmation. Running it anywhere
   else — staging, production, any environment with real data — is a
   CONFIRM at minimum, and running it against production specifically is
   an ESCALATE first (see [`RULES.md`](../RULES.md) §4).

7. **State environment explicitly when asking for confirmation.** "Run
   this migration" is not enough — say which database, what it does in one
   sentence, whether it's reversible, and how long it's expected to take.

## Acceptance criteria checklist for migration Tickets

A Ticket whose approach includes a migration should have acceptance
criteria that explicitly cover:
- [ ] Migration applies cleanly to a fresh local database.
- [ ] Migration applies cleanly to a copy of the current schema (not just
      an empty one), if the project has a way to test that.
- [ ] Rollback steps are documented and, where possible, tested.
- [ ] Application code handles both pre- and post-migration schema during
      any deploy window where the two might briefly coexist (relevant for
      anything not run in the same deploy as the code that depends on it).
