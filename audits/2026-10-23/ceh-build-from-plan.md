# Model audit: ceh-build-from-plan

- Date: 2026-10-23
- claude-code 2.1.309
- Edits applied: no

## Unpinned audit against fable-5, fable-5-1, haiku-5-5, opus-5, opus-5-5, sonnet-5, sonnet-5-5

Audit model: sonnet-5-5, effort: medium. Raw output: [ceh-build-from-plan.doctor.md](ceh-build-from-plan.doctor.md).

## Kept changes

### plugins/standalone/ceh-build-from-plan/skills/implement-from-plan/references/plan-schema.md:85

**Rule 3.** Two instructions contradict each other. This is the report's one finding.

Backing: the two files disagree on when decisions are copied to `ARCHITECTURE.md`. No guide page backs this change.

- `SKILL.md:46-49`: "When `ceh-check-build-against-plan` is installed, run `ceh-check-build-against-plan:check-build-against-plan` first". The check is conditional, so without that plugin the skill still copies the decisions.
- `plan-schema.md:85`: "Once any check of the build against it has run, each Design decision a later reader still needs is copied". Here the copy waits for a check.
- `architecture-schema.md:5` says `implement-from-plan` "appends Key Decisions" with no condition. That agrees with the skill, so the schema line is the outlier.

The report left the choice to the user and recommended its option 1. I follow that option because it needs one wording change and no behavior change. `plan-schema.md` is copied word for word into three plugins (`ceh-build-planning`, `ceh-build-from-plan`, `ceh-check-build-against-plan`). The edit must be mirrored in every copy per `docs/CROSS_REFERENCES.md`.

Before:

```
- A `built` plan is kept. Once any check of the build against it has run, each Design decision a
  later reader still needs is copied to the Key Decisions log in `product/ARCHITECTURE.md`, and the
  change gets a changelog entry when the repo keeps one. New work gets a new plan file.
```

After:

```
- A `built` plan is kept. Once every phase is done, each Design decision a later reader still
  needs is copied to the Key Decisions log in `product/ARCHITECTURE.md`, after the check of the
  build against the plan when that check is installed, and the change gets a changelog entry when
  the repo keeps one. New work gets a new plan file.
```

The remaining model-guide patterns were left out because they do not pass the rules:

- **Verification and keep-working paragraphs (Haiku 5.5, Sonnet 5.5).** The skill already requires a passing Check and a stop-and-report rule. `prompting-claude-opus-5` also says: "If your prompt contains explicit verification instructions … remove them: instructions like these cause over-verification on Claude Opus 5". So adding verification text would hurt Opus 5, and rule 2 fails.
- **Scope-limiting and early-stopping text.** The skill already carries it in "Build only what the phase names" and the Stop conditions.
- **Parallel tool calls.** The skill makes no independent tool calls that need a rule.
- **Duplicate stop rules (step 3.4, Rules, Stop conditions).** The report reads them as working redundancy, so I follow it.
