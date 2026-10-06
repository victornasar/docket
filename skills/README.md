# Skills

Thin host skills that teach **how to perform a type of work**. They point
into Docket recipes and must not redefine Ticket, Review, Rules, or Done.

```
Skills  = capability  (how to do the work)
Docket  = trust       (this repo — one Ticket proven trustworthy)
pstack  = scale       (outside this repo — many trustworthy units)
```

## Available

| Skill | Purpose |
|---|---|
| [`verify-with-evidence`](verify-with-evidence/SKILL.md) | Self-review handoff: mandatory `docket pre-review` (verify → check-scope → check-evidence); `review-packet` for fresh Reviewers |

## Installing on a host

Docket does not ship a skill installer. Copy or symlink a skill directory
into the host's skill path, for example:

- **Cursor (personal):** `~/.cursor/skills/verify-with-evidence/`
- **Cursor (project):** `<project>/.cursor/skills/verify-with-evidence/`
- **Claude Code:** follow that host's skill/plugin convention, pointing at
  the same `SKILL.md`

The skill body should stay thin and keep referencing
`docket/core/recipes/…` rather than inlining Docket's workflow.
