# Recipe: Writing a Ticket

Owner: Planner. Use this when turning a raw request into a Ticket via
[`ticket.template.md`](../templates/ticket.template.md).

## Steps

1. **Restate the problem, not the request.** A request is what the human
   typed; the problem is what's actually wrong or missing. "Add a retry to
   the payment webhook handler" (request) might really be "webhook
   failures are silently dropping payment confirmations" (problem). Write
   the problem down first — it disciplines the rest of the Ticket and
   surfaces when the requested approach isn't actually the right fix.

2. **Ask before assuming, on anything that changes the approach.** If two
   reasonable interpretations of the request would lead to meaningfully
   different implementations, ask which one — don't pick silently and
   don't hedge by trying to satisfy both. Ambiguity that only affects
   wording or minor details doesn't need a question.

3. **Check the Project Audit.** If the project doesn't have a
   [Project Audit](../templates/project-audit.template.md) on file, or the
   request touches a part of the stack it doesn't cover, do that first
   (including Verification commands). The Ticket's Approach section should
   be able to say "follows existing convention in X" rather than inventing
   a new pattern, when an existing one applies.

4. **Write Approach as steps, not a paragraph.** An Implementer should be
   able to follow it without re-deriving the design. Name the specific
   functions/modules/endpoints involved where known.

5. **Files Touched is a real list.** Not "the payment module" — the actual
   file paths, to the extent they're known before implementation starts.
   It's fine to be slightly approximate (an Implementer may discover one
   more file needs a one-line change), but it shouldn't be a guess at the
   level of an entire directory when the change is small.

6. **Acceptance criteria are checkable, not descriptive.** Write them so
   each has a clear yes/no once verified. Number them `AC-1`, `AC-2`, …
   Prefer observable, specific, scoped, outcome-oriented statements.
   Testable where possible; manual criteria remain valid when human
   judgment is genuinely required.
   - Bad: "Make CSV export better." / "Retries work correctly."
   - Good: "CSV export produces a valid CSV file containing all selected
     records." / "A webhook that fails with a 5xx is retried up to 3 times
     with exponential backoff; a 4xx is not retried; after 3 failed
     retries the event is written to the dead-letter table."
   - When a verify method is obvious, you may note it in parentheses on
     the criterion (e.g. "… (pnpm test export)"). The Implementer still
     owns recording actual Evidence at Self-review — **do not fabricate
     Evidence as Planner.** Leave the Evidence section blank at approval.

7. **Rollback plan matches the risk.** For most code changes, "revert the
   commit" is sufficient — say so explicitly rather than leaving it blank.
   For anything touching Rules categories (migrations, production,
   dependencies), the rollback plan needs to be specific — see
   [`recipe-safe-migration.md`](recipe-safe-migration.md) for the
   migration case.

8. **Run the approach past the Rules before presenting the Ticket.** If
   the approach as written would require a BLOCKed action, redesign the
   approach — don't write a Ticket that will hit a wall mid-implementation.

9. **Present for approval.** The Ticket isn't final until the human
   approves it. Don't hand off to the Implementer on an assumed yes.

## Worked example

> **Request:** "Users should be able to export their data as CSV."

**Problem:** There's currently no way for a user to get their data out of
the product; support has to run manual DB queries on request.

**Approach:**
1. Add `GET /api/account/export` that streams the requesting user's rows
   from `orders`, `line_items`, and `profile` as a single CSV, joined on
   `user_id`.
2. Reuse the existing `requireAuth` middleware; scope the query strictly to
   `req.user.id`.
3. Add a "Download my data" button in `AccountSettings` that hits the
   endpoint and triggers a browser download.

**Files touched:** `src/routes/account/export.ts` (new),
`src/routes/account/index.ts` (register route),
`src/components/AccountSettings.tsx`, `test/routes/export.test.ts` (new)

**Acceptance criteria:**
- [ ] AC-1: `GET /api/account/export` returns `401` when unauthenticated.
- [ ] AC-2: For an authenticated user, response is `text/csv` containing
      only that user's rows across all three tables (`pnpm test export`).
- [ ] AC-3: A user with zero orders gets a CSV with headers only, not an
      error.
- [ ] AC-4: "Download my data" in Account Settings triggers the download
      in a browser check (manual or browser test).

**Evidence:** blank at approval — filled at Self-review.

**Rollback plan:** Revert the commit; no schema or data changes involved.
