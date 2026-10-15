# Model audit: ceh-business-plan

- Date: 2026-10-15
- claude-code 2.1.301
- Edits applied: no

## Unpinned audit against fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5

Audit model: sonnet-5-5, effort: medium. Raw output: [ceh-business-plan.doctor.md](ceh-business-plan.doctor.md).

## Kept changes

### skills/develop-business-plan/SKILL.md:57
**Rule 3.** This is a model-independent contradiction. The same file says no specialist touches `status`, but `skills/find-product-market-fit/SKILL.md:166` says "Flip frontmatter `status: validated`". This matches `/doctor` finding 2.

**Backing:** no page is needed. The two quoted lines contradict each other.

```diff
- - The status rule in step 4 runs after every specialist, because several of them re-score
-   `pmf_gate` and none of them touches `status`.
+ - The status rule in step 4 runs after every specialist, because several of them re-score
+   `pmf_gate` and only `find-product-market-fit` sets `status`, to `validated` when the gate
+   passes.
```

### skills/find-product-market-fit/SKILL.md:24
**Rule 1.** The general page backs rewriting a negative instruction as the positive one it implies.

**Backing:** "Tell Claude what to do instead of what not to do" (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices, "Control the format of responses"). The instruction here and its positive form say the same thing, and the next sentence already gives the reason.

```diff
- The core stance: **draft proactively, then interrogate**. Do not interview from a blank page when
- you can infer a v0 from what already exists. A concrete draft gives the user something to react
- to, and correction is faster and sharper than composition.
+ The core stance: **draft proactively, then interrogate**. Infer a v0 from what already exists
+ and interview against it. A concrete draft gives the user something to react
+ to, and correction is faster and sharper than composition.
```

### skills/find-product-market-fit/SKILL.md:41
**Rule 1.** This is the same positive-form rewrite. Both versions say the gate score picks the next question.

**Backing:** "Tell Claude what to do instead of what not to do" (same URL).

```diff
- Each loop closes one gap. Never run the interview as a fixed questionnaire — the gate score
- **chooses the next question**.
+ Each loop closes one gap. The gate score **chooses the next question**, so the interview is
+ never a fixed questionnaire.
```

### skills/run-premortem/SKILL.md:76
**Rule 4.** Deleting "Do not pad." changes nothing the model does. The next sentence ("Three guarded risks are worth more than fifteen listed ones.") already carries the behavior.

**Backing:** this is a cut of prose that changes no behavior, so no page quote applies.

```diff
- - Do not pad. Three guarded risks are worth more than fifteen listed ones.
+ - Three guarded risks are worth more than fifteen listed ones.
```

### Not kept
I dropped `/doctor` finding 3, the 120-word cap on the cold email in `write-investor-materials`.
- No fetched page backs removing a numeric cap on a fixed-format email.
- The Sonnet 5 guide says the model "interprets prompts literally and explicitly", so a precise cap suits it.
- The replacement "readable in one glance on a phone" is vaguer and can't be checked.
