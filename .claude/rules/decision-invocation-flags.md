---
schema: decision-rule/v1
paths:
  - "plugins/**"
  - ".claude/skills/**"
---

# Invocation flags

Every skill states `disable-model-invocation`, `user-invocable`, and `license` explicitly, in one
of three cases:

- Model only (`false`, `false`): standards and gates applied at a moment, and skills a hook,
  router, agent, or skill calls. Every skill a hook script names is model only. Its
  `docs/CATALOG.md` Invoke cell reads `Model-only, no slash command`.
- User only (`true`, `true`): runs that are the human's decision to start. Rare, and each gets a
  row in the User-only skills table of `ceh-every-session:whats-next`.
- Model and user (`false`, `true`): everything else, the default.

When a hook names the skill on every firing, its description is one line: what the skill is, with
no trigger phrases and no mention of the hook.

Why: the frontmatter says who invokes the skill, and a hook-delivered skill has no moment for trigger phrases to fire on. Decided 2026-10-06. Source: plugins/CLAUDE.md (1778e9c).
