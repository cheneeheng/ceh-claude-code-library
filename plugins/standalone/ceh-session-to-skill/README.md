# ceh-session-to-skill

Turn the task you just finished into a skill, built from what actually ran in the session instead
of from an interview.

The session already holds the commands and flags that worked, their order, and every correction
you made along the way. This plugin writes those into one `SKILL.md` in the target repo's
`.claude/skills/`, so the next session repeats the task without being told again.

## Skills

| Skill                     | When it loads                                           | What it does                                                                                                                                                                                                                                                                              |
| ------------------------- | ------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `turn-session-into-skill` | Right after a task is done, when you want it repeatable | Recovers the steps that worked (from the transcript file when context was compacted), turns your corrections into rules and per-run values into arguments, writes one `SKILL.md`, and maps each step back to the session. Irreversible steps get a confirmation and user-only invocation. |

**Manual trigger:** `/ceh-session-to-skill:turn-session-into-skill [skill-name]`, or say
`"turn what we just did into a skill"` / `"save this as a skill"`.

## Not this plugin

- A task you have not done yet, or one that needs approvals, resumption, or fan-out: use
  `ceh-workflow-builder`, which interviews the task and can emit a gated workflow. When the
  recovered steps need that shape and the builder is installed, this skill hands them over.
- Adding a skill to the ceh plugin repo itself.
