# Skill Evaluation Report Schema

The artifact this skill produces: one file, `SKILL_EVAL.md`, in the current run's folder —
`.agents_workspace/skill-evals/<target-name>/run-<NNN>/`. Each fresh evaluation gets a new
`run-NNN`, so re-running never overwrites a prior run. Within a run it is a living document, revised
in place each fix/re-run loop.

```
run-<NNN>/
├── SKILL_EVAL.md      # findings only
├── fixtures/          # inputs: test prompts, competing descriptions, task fixtures
└── iteration-<N>/     # raw transcripts, generated artifacts, harnesses
```

## Who you are writing for

**Someone who has never heard of the skill being evaluated, reading the file for the first time, who
wants to know in ten seconds whether it ships.** Not you, three minutes after running the battery.

That reader is the whole design constraint, and everything below follows from it. An evaluation
nobody reads has measured nothing.

### The seven rules

1. **Say what the target does before you say anything about it.** Open with two or three plain
   sentences on what the skill is for. A reader who does not know what is being measured cannot
   read a measurement of it.
2. **Headings are questions, not labels.** _"Does it switch on at the right time?"_ not
   _"Triggering accuracy"_. The question tells the reader what they are about to learn; the label
   assumes they already know.
3. **Every number says what it is out of, in words, the first time.** "3 of 3 attempts", not "3/3".
   "Fired on all 10 prompts that should trigger it", not "29/30".
4. **No bare identifiers.** `P08`, `B41`, `S1-S4`, `D2`, `:37-43` mean nothing to a first reader.
   Name the thing — _"a request about auth checks across five controllers"_ — and drop the code
   entirely unless someone needs it to find a file.
5. **Name test conditions in plain words.** "No skill" / "Skill installed" / "Skill text pasted in",
   never "baseline" / "natural" / "inlined". If a term is not in the target's own vocabulary, either
   define it in the same sentence or replace it.
6. **Four tables, give or take.** A table earns its place by letting the eye compare across a row. A
   21-row checklist is not a comparison — collapse it to one sentence plus the two rows that
   mattered.
7. **Quote the failure.** One verbatim line of an agent getting it wrong teaches more than any pass
   rate. Every claim of a behavioural difference carries the quote that shows it.

## Section order

A first reader goes top to bottom and stops when satisfied, so the order is: the answer, then what
the answer means, then the evidence, then the caveats.

| Order | Section                            | Content                                                                                           | Size                              |
| ----- | ---------------------------------- | ------------------------------------------------------------------------------------------------- | --------------------------------- |
| 1     | _(untitled opening)_               | What the target does, the verdict, the gate table, what to do next.                               | one screen, hard limit            |
| 2     | How it was tested                  | Plain-language description of each measurement, and what each condition means.                    | one short paragraph per dimension |
| 3     | One question-heading per dimension | The result table, then the quote that shows what passing and failing look like.                   | as long as it needs               |
| 4     | Loose ends                         | Everything non-blocking, as a table: what, and why it is not blocking.                            | one row each                      |
| 5     | Fine print                         | Version measured, the target's claim in its own words, every weakened number, raw-material paths. | unbounded                         |

**Method moved up, limits stayed down.** These are different things and the earlier schema conflated
them. A first reader needs to know _what a number means_ before they see it — that is section 2, and
it is short. They only need to know _how far to trust it_ if they are challenging the result — that
is section 5, and it can be long.

### 1 — The opening

Four elements, no headings between them:

```markdown
**What the skill does.** <two or three plain sentences, for someone who has never heard of it.>

**Verdict: ready to ship.** <what it does well, in words. Then the one concrete before/after
that carries the verdict — with the failure named, not just the number.>

**Readiness gate: 6 of 6.**

| #   | Gate                                                 | Answer | How we know                                          | Remark                                                  |
| --- | ---------------------------------------------------- | ------ | ---------------------------------------------------- | ------------------------------------------------------- |
| 1   | **Structurally valid** — well-formed as a file?      | Yes    | All 21 structure checks passed                       | —                                                       |
| 2   | **Triggers on intent** — switched on when it should? | Yes    | Fired on all 10 prompts that should trigger it       | Measured against the installed version, not this branch |
| 3   | **Does not over-trigger** — quiet when it shouldn't? | Yes    | Fired on 0 of 10 prompts designed to fool it         | —                                                       |
| 4   | **Content is delta + moment-framed** — written well? | Yes    | Passes all 7 writing checks                          | One supporting figure inherited from run 2              |
| 5   | **Behavioral lift** — actually changing behaviour?   | Yes    | Caught a hidden gap 3 of 3 times; without it, 1 of 3 | —                                                       |
| 6   | **User confirms** — signed off by the author?        | Yes    | Confirmed 2026-09-08                                 | —                                                       |

**Nothing is blocking.** <or: **Blocked on <the one thing>.** Then the single action that
closes it.>
```

This table is the source of truth for `eval_gate: N/6` in frontmatter. Four fixed columns plus a
remark:

- **Gate** carries **both names**: the formal criterion in bold, then the plain question. The formal
  half is the only jargon the opening is allowed, and it earns its place because it is the
  vocabulary the author works in and the one thing that ties the report to the loop. A reader who
  skips it still gets the question.
- **Answer** is **Yes**, **No**, or **Not measured** — never a number, never an adjective.
- **How we know** carries the measurement in words, with the threshold when one applies.
- **Remark** is `—` unless the criterion is qualified: measured by proxy, inherited from an earlier
  run, waived, or passed against a threshold looser than default. A remark records a _qualified_
  Yes; a criterion that fails outright is a **No**, not a Yes with a remark. Directly under the
  table, say in one sentence whether the remarks are open or merely noted.

### 3 — The dimension sections

One heading per dimension, phrased as the question the reader has:

- _Does it switch on at the right time?_
- _Does it change what the agent does?_
- _Is the file itself well built?_

Each holds a result table, then prose. The prose is where the finding lives — a quoted failure, a
test whose design assumption turned out wrong, a rule that held for a different reason than it
states. Findings are not a separate section; they belong next to the number that produced them.

**A dimension where every condition scores the same is a finding about the test, not a null result
about the skill.** Say so plainly, explain why the test could not discriminate, and retire it in
_Loose ends_.

## Readiness gate

The target ships (`status: passed`) only when all six are met **and** the author confirms.

| #   | Criterion                        | Plain question               | Met when                                                                                                                                                                                                                                        |
| --- | -------------------------------- | ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Structurally valid               | Well-formed as a file?       | Every deterministic check passes — frontmatter, name matches directory, description present, body non-trivial, references discipline. For a plugin, also the manifest and marketplace version match.                                            |
| 2   | Triggers on intent               | Switched on when it should?  | The should-trigger prompts fire at or above threshold across runs.                                                                                                                                                                              |
| 3   | Does not over-trigger            | Quiet when it shouldn't?     | The near-miss prompts fire at or below threshold.                                                                                                                                                                                               |
| 4   | Content is delta + moment-framed | Written well?                | Passes the rubric in `eval-rubric.md` — the body is the opinionated delta, framed as a moment, within size norms, explaining the why.                                                                                                           |
| 5   | Behavioral lift                  | Actually changing behaviour? | With the skill, the agent clears assertions the no-skill run misses (or holds a standard it violates) **and** regresses nothing, with acceptable run-to-run variance. If lift cannot be simulated meaningfully, the answer is **Not measured**. |
| 6   | User confirms                    | Signed off by the author?    | The author agrees it ships.                                                                                                                                                                                                                     |

Both names appear in the report's gate table, formal first. Everywhere else, use the plain question.

Defaults: criterion 2 needs at least 8 of 10 should-trigger prompts firing, where a prompt counts as
firing if it wins in at least 2 of 3 runs; criterion 3 allows at most 1 of 10 near-misses to fire.
Thresholds are defaults, not laws — state the one actually used in the evidence cell so the score is
reproducible.

A criterion is met only when a **measurement** supports it. An honest **Not measured** is not a
**Yes**, and it is far better than a fabricated one. **Never emit a composite score** — no
"Quality: 87/100". `eval_gate: N/6` is the only summary number in the file.

When fewer than six are met, the open ones are the agenda: fix the highest-leverage one, re-run only
that dimension, re-score.

## Frontmatter

```yaml
---
artifact: SKILL_EVAL
status: draft # draft | passed   (passed = 6/6 + author confirmed)
created: YYYY-MM-DD
updated: YYYY-MM-DD
target: <path to the evaluated SKILL.md or plugin dir>
target_kind: <skill | plugin>
eval_gate: 0/6
iterations: 0
---
```
