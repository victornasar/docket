# Ticket: Let no-runtime-change Tickets skip approval before code, per project

**Status:** done
**Owner (Implementer):** Claude
**Retry count:** 0
**Related project audit:** N/A — this repo
**Baseline:** c7498a5a882106648a8487f50a00cabbb545b90f
**Worktree:**

## Problem

Stage 1 requires the human to approve every Ticket before any code, however small. For a change with no runtime effect (a README typo, a comment, a doc link), that approval adds a round trip of the human's attention while protecting almost nothing: the Ticket, evidence, the three gates, and the independent Reviewer still run, and the human still decides the merge. The human's attention goes where it buys the least. This has been deferred since grill Q6 ("a real checkpoint at Ticket-approval with a trivial-ticket fast path"; `tickets/README.md`).

No project incident triggered it. The owner grants a narrow freeze exception for it (step 7).

## Approach

1. **Eligibility.** A Ticket may take the fast path only when all four hold:
   - (a) the project has turned the fast path on in `PROJECT_AUDIT.md` (default off);
   - (b) the change has no runtime effect: docs, comments, or content nothing executes or reads at runtime;
   - (c) nothing in the approach is CONFIRM, BLOCK, or ESCALATE under `RULES.md`;
   - (d) the rollback plan is "Revert the commit."
   When any of these is unclear, the Ticket is not eligible.
2. **`core/WORKFLOW.md` Stage 1.** Keep "The human has approved the Ticket. No code is written before this." as the rule, and add the fast path as its one exception: an eligible Ticket goes from `draft` to `in-progress` without `approved`. Everything else is unchanged: the Ticket, Baseline, Evidence, `docket pre-review`, the independent Review, and the human's merge decision. Update the summary table's Ticket row to say "Human approval, or fast path (eligible Tickets only)".
3. **`core/WORKFLOW.md` Stage 4.** The Reviewer checks fast-path eligibility first. A fast-path Ticket that fails any criterion is **Escalate**, not Send-back: the human never approved it, so there is nothing for the Implementer to fix.
4. **`core/roles/planner.md`.** The Planner may declare the fast path only when every criterion holds, by writing in `## Rules check` one line `Fast path: yes` followed by a reason for each criterion (a)–(d). Otherwise it presents the Ticket for approval as today. The Planner tells the human, in the same message, that the Ticket is proceeding on the fast path, so the human can stop it.
5. **`core/roles/reviewer.md`.** Add the eligibility check as the first checklist item, with the Escalate outcome from step 3.
6. **Templates.**
   - `core/templates/project-audit.template.md`: add a `## Workflow options` section with `Fast path (no-runtime-change Tickets skip approval before code): off`.
   - `core/templates/ticket.template.md`: in the `## Rules check` comment, describe the `Fast path: yes` line and its four reasons.
7. **`core/LINE_MEETING.md`.** Add a named freeze exception, dated, in the same form as the Stage 1–3 exceptions. Permitted: the Stage 1 fast-path exception, the Stage 4 eligibility check, the matching role, template, adapter, README, and GUIDE text. Not permitted: skipping Evidence, gates, or Review; any eligibility beyond (a)–(d); tooling changes. The spine is frozen again after.
8. **`core/CHANGELOG.md`.** Entry: date, "no triggering incident; owner exception (LINE_MEETING.md)", what changed, files.
9. **Adapters, README, GUIDE.** Where they say no code before approval without exception (`adapters/claude-code/CLAUDE.md.template`, `adapters/cursor/cursorrules.template`, `README.md` rule 1, `GUIDE.md` Walkthrough 1 and "Who does what"), add the fast-path exception in one clause and point to WORKFLOW.md Stage 1. GUIDE.md Walkthrough 1 shows the typo taking the fast path when the project has it on.
10. **`tickets/README.md`.** Add Ticket 015. Remove the fast-path half of the deferred grill Q6 item; the tiered Review half (Q7) stays deferred.

Out of scope: tooling (`lint-ticket` already accepts a Ticket that never had Status `approved`; AC-7 confirms this), the tiered independent Review (grill Q7), any change to Evidence or gates, and Hechent's side (see Notes).

## Files touched

- core/WORKFLOW.md
- core/roles/planner.md
- core/roles/reviewer.md
- core/templates/project-audit.template.md
- core/templates/ticket.template.md
- core/LINE_MEETING.md
- core/CHANGELOG.md
- adapters/claude-code/CLAUDE.md.template
- adapters/cursor/cursorrules.template
- README.md
- GUIDE.md
- tickets/README.md

## Acceptance criteria

- [ ] AC-1: WORKFLOW.md Stage 1 states the fast path as the only exception to approval before code, lists criteria (a)–(d), says unclear means ineligible, and says Ticket, Baseline, Evidence, pre-review, Review, and the human's merge are unchanged. (manual: read Stage 1)
- [ ] AC-2: WORKFLOW.md Stage 4 and reviewer.md make eligibility the Reviewer's first check, with Escalate for an ineligible fast-path Ticket. (manual)
- [ ] AC-3: planner.md requires the `Fast path: yes` line in Rules check with a reason for each of (a)–(d), and requires telling the human the Ticket is proceeding on the fast path. (manual)
- [ ] AC-4: The Project Audit template has the fast-path option, set to off by default. (manual)
- [ ] AC-5: No adapter template, README.md, or GUIDE.md states approval before code without mentioning the fast-path exception. (command: `grep -n -i "before code\|before a ticket is approved\|before any code" README.md GUIDE.md adapters/*/*.template core/WORKFLOW.md`, each hit read in context)
- [ ] AC-6: LINE_MEETING.md has the named exception with permitted and not-permitted lists, and CHANGELOG.md has the entry. (manual)
- [ ] AC-7: A sample Ticket with Status `in-progress`, a `Fast path: yes` Rules check, and no approval passes `docket lint-ticket`, and the tooling suite passes unchanged. (command + Project verify)

## Rollback plan

Revert the commit. Projects that turned the option on fall back to approval before code, which is today's behavior.

## Rules check

- Editing `core/` is gated by `LINE_MEETING.md`. This Ticket names the freeze exception (step 7); approving it is the owner's sign-off, and step 8 is the changelog entry.
- No deletions, dependencies, CI, or production. Nothing CONFIRM or BLOCK.
- Work goes on a branch, not `main` (RULES §1).
- This Ticket is not itself eligible for the fast path: it changes how the kit behaves, and this repo has no Project Audit opting in.

## Evidence

### Project verify

```text
command: tooling/.venv/bin/pytest -v -p no:cacheprovider tooling
exit: 0
log: .docket/verify/015-fast-path-approval-20261126T004543Z.log
ran_at: 2026-11-26T00:45:43Z
git_head: c7498a5a882106648a8487f50a00cabbb545b90f
tree_fingerprint: 326df9991848365bb67a81ab9178878a56fc8333518f62468e280f493a7f800c
attestation: .docket/verify/015-fast-path-approval-20261126T004543Z.json
```

### Acceptance criteria

```text
id: AC-1
criterion: WORKFLOW.md Stage 1 states the fast path as the only exception to approval before code, lists (a)-(d), says unclear means ineligible, and says everything else is unchanged
method: manual
how: git diff c7498a5 -- core/WORKFLOW.md (Stage 1)
result: pass
evidence: new paragraph "The fast path: the one exception to approval before code" lists (a) Project Audit opt-in, (b) no runtime effect, (c) nothing CONFIRM/BLOCK/ESCALATE, (d) "Revert the commit"; "If any of these is unclear, the Ticket is not eligible"; "Everything else is unchanged: the Ticket, Baseline, Evidence, docket pre-review, the independent Review, and the human's merge decision"
notes:

id: AC-2
criterion: WORKFLOW.md Stage 4 and reviewer.md make eligibility the Reviewer's first check, with Escalate for an ineligible fast-path Ticket
method: manual
how: git diff c7498a5 -- core/WORKFLOW.md core/roles/reviewer.md
result: pass
evidence: WORKFLOW Stage 4 "the Reviewer first checks ... If it did not, the outcome is Escalate", added to the Escalate outcome list; reviewer.md "Fast-path eligibility" section placed before the Spec axis ("Before anything else"), plus a Decision tree bullet "did not meet the fast-path criteria -> Escalate"
notes:

id: AC-3
criterion: planner.md requires the Fast path: yes line in Rules check with a reason for each of (a)-(d), and requires telling the human
method: manual
how: git diff c7498a5 -- core/roles/planner.md
result: pass
evidence: "write `Fast path: yes` in `## Rules check` followed by a reason for each criterion, and tell the human in the same message that the Ticket is proceeding without approval. If any criterion is unclear, ask for approval."
notes:

id: AC-4
criterion: The Project Audit template has the fast-path option, set to off by default
method: manual
how: tail core/templates/project-audit.template.md
result: pass
evidence: "## Workflow options" with "Fast path (no-runtime-change Tickets skip approval before code): off"
notes:

id: AC-5
criterion: No adapter template, README.md, or GUIDE.md states approval before code without mentioning the fast-path exception
method: command
how: grep -n -i "before code\|before a ticket is approved\|before any code" README.md GUIDE.md adapters/*/*.template core/WORKFLOW.md, plus "approve" hits read in context
result: pass
evidence: CLAUDE.md.template:32-35 and cursorrules.template:47-51 carry the exception in the same paragraph; GUIDE.md:7 now says "(unless you've turned on the fast path ...)"; README rule 1 and table row and GUIDE Walkthrough 1 and "Who does what" mention it; WORKFLOW.md:62 is the exception itself
notes: adapters/claude-code/README.md:82 ("the human approves the Ticket regardless") concerns large or ambiguous requests, which can never qualify; left unchanged and outside Files touched

id: AC-6
criterion: LINE_MEETING.md has the named exception with permitted and not-permitted lists, and CHANGELOG.md has the entry
method: manual
how: read core/LINE_MEETING.md "2026-11-25 — Fast path at Ticket approval (Ticket 015)" and core/CHANGELOG.md entry of the same title
result: pass
evidence: exception lists permitted (Stage 1 fast path limited to (a)-(d), Reviewer eligibility check, matching docs) and not permitted (skipping Evidence/gates/Review, wider eligibility, tooling, tiered Review); changelog entry names the trigger as none (owner exception) and lists files
notes:

id: AC-7
criterion: A sample fast-path Ticket (Status in-progress, Fast path: yes, never approved) passes lint-ticket, and the tooling suite passes unchanged
method: command
how: bin/docket lint-ticket <scratchpad>/fast-path-sample.md; docket pre-review (Project verify above); git diff --stat c7498a5 -- tooling
result: pass
evidence: "lint-ticket PASSED (structure only)", exit 0; verify exit 0 with 49 PASSED and no FAILED/ERROR lines; no diff under tooling/
notes: the sample is a scratch file outside the repo
```

### Scope review

```text
diff_vs_files_touched: match
extras: none
justified: n/a
notes: check-scope PASSED, 13 changed paths including tickets/ (auto-allowed)
```

## Notes for the Reviewer

Review (independent, Sonnet): Pass, no blocking findings. Standards notes for a possible follow-up: WORKFLOW.md Stage 2 and implementer.md still say "approved Ticket" loosely; a Ticket that skips approval without declaring the fast path is caught only by the general Rules checks; adapters/claude-code/README.md:82 could mention the fast path.

External follow-up, not part of this Ticket: Hechent's `assess` (Docket approval boundary) and `DOCKET-INTEGRATION.md` step 2 assume every Ticket waits for approval. Hechent will need a matching change to honor the fast path when a project opts in; until then, Hechent keeps asking for approval, which is the stricter behavior.
