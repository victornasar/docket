# Docket

Docket makes one unit of agent work **trustworthy**.

```
Skills  = capability   how to perform a type of work
Docket  = trust        one Ticket specified, proven, independently reviewed
pstack  = scale        many trustworthy units (outside this repo — not built here)
```

**Skills make agents capable. Docket makes their work trustworthy. pstack
makes trustworthy work scalable.**

Docket does not try to make the agent more trustworthy. It makes the
**system less dependent on trusting the agent**: specify the work, bind
proof to the worktree, and require independent review before Done.

---

## What problem it solves

AI agents can implement changes quickly and still fail quietly: forged
“tests passed,” scope creep, self-review that remembers writing the code,
and Done that means “the agent said so.”

Docket is a vendored planning-and-review kit for that failure mode:

- a human-approved **Ticket** before code
- **Evidence** recorded at Self-review (not narrative claims)
- mechanical **pre-review** gates (verify → scope → evidence)
- independent **Review** that audits Evidence + diff
- **Done** as an evidence-backed state — not an agent declaration

It is mostly Markdown and role definitions, plus a small Python CLI
(`bin/docket` / `tooling/`). Attach it to a project (symlink or submodule
today); generate a thin adapter (`CLAUDE.md` or Cursor rules) that points
back at it.

**On “works anywhere”:** `core/` is plain Markdown. In practice the Claude
Code adapter is the reference. Cursor exists but is experimental — it
approximates independent Review with a fresh chat, not a true subagent.

---

## Skills vs Docket vs pstack

| Layer | Answers | Lives |
|---|---|---|
| **Skills** | “How do I perform this kind of work?” | Thin, optional; host skill paths; point into Docket recipes |
| **Docket** | “How do we know this work stayed inside the agreed contract?” | This repo — Ticket, Evidence, gates, Review, Done |
| **pstack** | “How do many trustworthy units scale?” | Outside this repo — not built here |

Do not blur these boundaries. Docket is the trust layer. Skills are
capability / procedural knowledge. pstack is outer-loop orchestration.

Skills should stay thin. Expand them only when real Tickets show a
**recurring** procedural need — not by inventing a Skills framework up
front. Today Docket ships one: [`skills/verify-with-evidence`](skills/verify-with-evidence/SKILL.md).

---

## Current status

**Stage 1–3: implemented and stabilized** (experimental baseline).

Milestone commit: `d683b73` —
*Docket Stage 1-3: evidence, verification, and review gates*.

| Stage | What landed |
|---|---|
| **1 — Evidence** | Ticket Evidence contract; Done as an evidence state; Project Audit Verification; Reviewer audits evidence (does not invent it) |
| **2 — Gates** | `verify`, `check-scope`, `check-evidence`; attestation; worktree fingerprint / stale detection |
| **3 — Habit** | Fail-closed `pre-review` (ordered handoff); `review-packet` for fresh-context Review discovery |

Kit tests: **23** pytest cases. Isolated CLI smoke: **32/32** (stabilization).
Stage 4 has **not** been implemented.

### Current phase: real-project validation

The next step is **not** more Docket infrastructure.

Use Docket on a real (preferably non-production) codebase and run complete
Tickets through the workflow. Empirically learn:

- where agents struggle
- what information they repeatedly need
- whether Evidence is useful proof or bureaucracy
- whether Review catches meaningful problems
- where friction appears
- what recurring procedures deserve a Skill

Those questions are open until real use answers them.

---

## How it works

```
TICKET → IMPLEMENT → SELF-REVIEW → PRE-REVIEW → REVIEW → DONE
```

Self-review fills Evidence; **PRE-REVIEW** is the mechanical gate before
handoff (`docket pre-review`):

1. **Canonical project verification** (`verify`) — Audit command runs; exit, log, HEAD, fingerprint recorded
2. **Scope** (`check-scope`) — changes since Ticket **Baseline** ⊆ Files Touched
3. **Evidence** (`check-evidence`) — structure valid; Markdown matches attestation; not stale

Non-zero from any step **blocks** Review. Green gates establish
execution / scope / evidence integrity. They do **not** mean the change
is semantically correct — that remains independent Reviewer judgment.

| Stage | Owner | What happens | Exit gate |
|---|---|---|---|
| **Ticket** | Planner | Problem, Approach, Files Touched, ACs, Rollback; Evidence blank; Project Audit if needed; **Baseline:** at start | Human approval. No code before this. |
| **Implement** | Implementer | Execute the Ticket within Files Touched | Approach done; no silent scope creep |
| **Self-review** | Implementer | Fill Evidence for every AC | Ready to run pre-review |
| **Pre-review** | Implementer (CLI) | `docket pre-review` → verify → check-scope → check-evidence | Exit 0 on the **final** worktree |
| **Review** | Reviewer | Independent audit of Evidence + diff (`review-packet` for discovery). Missing/inadequate Evidence → send-back | Pass / Send-back / Escalate |
| **Done** | — | Evidence-backed Done | See below |

**Roles.** Planner writes Tickets (no self-approval). Implementer is scoped
to Files Touched. Reviewer is read-only and, where the host allows,
genuinely separate context (Claude Code subagent; Cursor: fresh chat
approximation).

**Send-back:** itemized feedback → Implement → re-verify → pre-review →
Review. After two send-backs, escalate to the human.

**Rules.** [`core/RULES.md`](core/RULES.md) — CONFIRM / BLOCK / ESCALATE on
top of the host’s baseline safety.

Tooling details: [`tooling/README.md`](tooling/README.md).

---

## What Done means

Done is an **evidence-backed state**, not “the agent says it works,” and
not merge/deploy.

At minimum Done requires:

- Evidence structurally complete for every AC
- Canonical project verification recorded as passing (`docket verify`)
- Verification / Evidence bound to the current relevant worktree (not stale)
- Scope accounted for (`check-scope`)
- Independent Reviewer **Pass** (adequacy of evidence vs ACs)
- No unresolved CONFIRM / ESCALATE

Deployment and production actions remain separate human CONFIRM after Done.

### What Docket does **not** prove

Mechanical green does not establish:

- that an AC is well-written
- that a test actually proves the AC
- that a suite is non-vacuous
- that manual evidence is truthful
- that the Reviewer exercised good judgment
- that the project architecture is correct
- that the human approved the right Ticket
- that production deployment is safe

Those remain Reviewer, human, and project judgment — by design.

---

## What you can do with it

- **Attach.** [`setup/attach.md`](setup/attach.md) (or `attach-docket`):
  symlink/submodule, Project Audit, adapter files, confirm Ticket-before-code.
- **Run one Ticket.** Approve → Implement → Self-review → `pre-review` →
  independent Review → Done → you merge.
- **Parallel (experimental).** [`advanced/PARALLEL_LINE.md`](advanced/PARALLEL_LINE.md)
  — unproven on a single-operator project.
- **Evolve from incidents.** Real gaps → human-approved `core/` change →
  [`CHANGELOG.md`](core/CHANGELOG.md). Spine is frozen; see
  [`LINE_MEETING.md`](core/LINE_MEETING.md).

**Intentionally later (not next):** Stage 4 machinery, attach/sync CLIs,
kit CI, pstack fleets, autonomous merge, semantic “test quality” oracles.

---

## Repo map

```
docket/
  core/                 Rules, workflow, roles, recipes, templates, changelog
  skills/               Thin host skills (verify-with-evidence today)
  tooling/docket/       CLI: verify, check-scope, check-evidence,
                        pre-review, review-packet
  bin/docket            Wrapper → python3 -m docket
  advanced/             Experimental parallel Line (unproven solo)
  adapters/             claude-code (reference), cursor (experimental)
  setup/attach.md       How to wire Docket into a project
```

## Reading order

1. This README
2. [`core/RULES.md`](core/RULES.md)
3. [`core/WORKFLOW.md`](core/WORKFLOW.md)
4. [`core/roles/`](core/roles/)
5. [`tooling/README.md`](tooling/README.md)
6. [`adapters/claude-code/`](adapters/claude-code/) (or Cursor, experimental)

## Scope of this repo

Docket is a template kit, not an application. `core/` is load-bearing for
every attached project. Changes follow [`RULES.md`](core/RULES.md) and the
freeze in [`LINE_MEETING.md`](core/LINE_MEETING.md) — grounded in real
incidents, not speculative Stage 4.
