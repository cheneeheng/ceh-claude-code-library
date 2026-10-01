# Evaluation Rubric & Method

Two things this file holds: the **content-quality rubric** (the portable authoring principles the
content dimension judges against) and the **method detail** for the trigger-battery and
behavioral-simulation runs. Both are tool-agnostic so the skill works in any repo.

> **Provenance.** The principles and the simulation method below are distilled _from_ the Anthropic
> `skill-creator` and `plugin-dev` plugins as reference material. They are restated here so this
> plugin is self-contained — those plugins are **optional cross-checks**, not dependencies, and are
> not authoritative over these criteria.

---

## Part 1 — Content-quality rubric

Judge the target's body and description against these. Each judgment needs a **cited line** as
evidence; a judgment with no quote is an opinion and does not count.

### Description (the triggering mechanism)

- **States what AND when.** The description is the only thing the model sees when deciding to fire a
  skill. It must say what the skill does _and_ the concrete contexts/phrases that should invoke it.
- **Frames a moment, not a topic.** Good descriptions trigger on a verb/situation ("I'm opening a
  PR", "I just wrote a migration"), not a noun/subject ("PostgreSQL", "testing"). Topic-named skills
  either never auto-fire or restate what the model already knows.
- **Slightly pushy.** Models tend to _under_-trigger skills. A description that lists explicit
  "use this whenever…" contexts fires more reliably than a terse one. Pushiness is a feature here,
  within honesty.
- **Names what it is NOT for.** A pointer to the right alternative skill reduces false-positives.

### Body

- **It's the delta.** The body should carry only what the model doesn't already know or wouldn't
  already do — the repo/tool-opinionated specifics. A body that restates general best practice is
  dead weight: it bloats context and adds nothing. This is the single most common failure.
- **Progressive disclosure.** SKILL.md stays lean (aim under ~500 lines); push schemas, templates,
  and long detail into `references/` with a clear pointer to when to read them.
- **Explains the why.** Prefer reasoning the model can generalize from over heavy-handed ALL-CAPS
  MUSTs. Rigid rules without rationale make the model brittle; "X because Y" makes it capable.
- **Least surprise / safety.** Nothing deceptive, no malware or exfiltration, no behavior a user
  reading the description wouldn't expect.

### Content red flags (each is a finding)

- Body restates general knowledge the model already has → cut it.
- Description is a topic/noun → will under-trigger; reframe as a moment.
- Walls of ALL-CAPS MUST/NEVER with no rationale → reframe with the why.
- SKILL.md is huge with no references split → apply progressive disclosure.
- `references/` holds prose the body should own, or vice versa → misplaced content.

---

## Part 2 — Trigger-battery method

The triggering dimension measures whether the description fires when it should and stays quiet when
it shouldn't.

### Building the battery

- **8–10 positives**: different phrasings of the real intent — some formal, some casual; include
  cases where the user does NOT name the skill or file type but clearly needs it; include a couple of
  uncommon-but-valid uses and a case where this skill competes with another but should win.
- **8–10 near-miss negatives**: the valuable ones share keywords or concepts with the skill but
  actually need something else (adjacent domain, ambiguous phrasing a naive keyword match would
  catch, a context where another tool is the right answer). Avoid obvious irrelevant negatives —
  they test nothing.
- **Realistic and specific**: file paths, real-sounding context, company/column names, typos,
  lowercase, a little backstory. Not "Format this data" but "ok my boss dropped a 'Q4 final FINAL
  v2.xlsx' in my downloads and wants a profit-margin column, revenue's in C, cost in D i think".
- **Substantive enough to matter**: the model only consults a skill for tasks it can't trivially do
  alone. A one-step request won't fire any skill regardless of description quality — don't put such
  prompts in the positive set or you'll measure the harness, not the description.

### Running it

- Each prompt runs through a **fresh (cold) subagent** that has the skill available. Cold matters:
  the subagent has none of your context, so the trigger decision reflects what a real user gets.
- **Hand the subagent only the user's prompt — never ask it which skills it would load** (or to
  "report skills used"). Naming the skill library primes skill-consideration and inflates the
  positive rate; observe whether the skill fires while the agent simply handles the task.
- Run each prompt **N = 3 times** (triggering is probabilistic). Count a prompt as "fires" if it
  triggers in ≥ 2 of 3 runs.
- Report positive trigger rate and near-miss false-positive rate **separately** — a skill can score
  well on one and badly on the other, and the fixes differ (broaden phrasing vs add "not for…").

### Fixing triggering

- Under-triggering → make the description more explicit about when to use it; add the missed
  phrasings/contexts; make it pushier.
- Over-triggering → name the adjacent domains it is NOT for and point to the right alternative;
  tighten the moment so it's specific.

---

## Part 3 — Behavioral-simulation method

Measures whether following the skill produces a better outcome than not having it.

### Setup

- For each behavioral task, spawn **two subagents in the same turn**: one **with-skill**, one
  **baseline** (no skill at all). Launch both together so they finish around the same time and share
  conditions. Save each to `<workspace>/iteration-<N>/<task>/with_skill/` and `/baseline/`.
- For evaluating a _changed_ skill rather than a new one, the baseline is the **previous version**:
  snapshot it before editing and point the baseline subagent at the snapshot.

### Grading

- Grade each output against the task's **assertions** — objectively verifiable statements that are
  true only if the skill genuinely worked. Each gets pass/fail with a **cited quote** from the
  transcript or output as evidence.
- **No surface credit.** A file with the right name but empty/wrong content fails. The burden of
  proof to pass is on the assertion.
- Also note any important outcome no assertion covers, and any assertion that would pass even for a
  clearly wrong output — weak assertions create false confidence and should be sharpened.

### Reading the result

- The signal is the **difference**: assertions the with-skill run clears that the baseline misses
  (or, for a guardrail skill, a standard with-skill holds that baseline violates).
- Run each task **N times** and report the spread. A single run is noise. "Helps in 3 of 4 runs, no
  regression in the 4th" is the honest result — report it as such; do not average it into a single
  misleading number.
- A skill that makes **no measurable difference** is a real, important finding: the value may be
  zero, or the task may not exercise what the skill improves. Say which.
