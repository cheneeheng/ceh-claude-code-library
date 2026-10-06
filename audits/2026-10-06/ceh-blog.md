# Model audit: ceh-blog

- Date: 2026-10-06
- claude-code 2.1.291
- Edits applied: yes

## Unpinned audit against fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5

Audit model: sonnet-5-5, effort: medium. Raw output: [ceh-blog.doctor.md](ceh-blog.doctor.md).

## Kept changes

### plugins/standalone/ceh-blog/skills/draft-post/SKILL.md:192

- **Rule:** 3, two instructions that contradict each other.
- **Backing:** No guide quote applies. The Launch template says to open with a product line, while the Opening rule (`:137`) says "not background, not a product pitch" and Voice (`:245-246`) says "never a product pitch". Nothing says which one wins.
- **Change:**
  - Before: `Hook: What it does and who it's for (one sentence)`
  - After: `Hook: The moment that led to building it (a scene or a thought), with what it does and who it's for inside the first paragraph`

### plugins/standalone/ceh-blog/skills/edit-post/SKILL.md:114

- **Rule:** 3. This is the mirror of the same contradiction, against `edit-post:55` and the Voice rules.
- **Backing:** Same as above. `docs/CROSS_REFERENCES.md:123-132` registers this template, so `draft-post` was edited first and the same text mirrored here.
- **Change:**
  - Before: `Hook: What it does and who it's for (one sentence)`
  - After: `Hook: The moment that led to building it (a scene or a thought), with what it does and who it's for inside the first paragraph`

### plugins/standalone/ceh-blog/skills/edit-post/SKILL.md:151, 157, 158

- **Rule:** 2.
- **Backing:** "Skills developed for prior models are often too prescriptive for Claude Fable 5 and can degrade output quality. Review and consider removing older instructions if default performance is better." (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5)
- **Models:**
  - Fable 5 benefits.
  - The Fable 5.1, Opus 5, Opus 5.5, Sonnet 5 and Sonnet 5.5 guides are silent on these bullets, so I treat them as unaffected.
  - Nothing is lost: Step 2 (`:40-43`) and Output (`:166`) cover "Diagnose before editing", Step 4 (`:143`) covers "One question after", and `:155` covers "Draft is already good".
- **Change (three bullets removed):**
  - Before:
    - `- **Diagnose before editing**: a brief diagnosis always precedes the revised draft. The author needs the reasoning, not just a new version.`
    - `- **One question after**: after sharing the edit, ask one focused question. It is a dialogue, not a checklist.`
    - `- **Draft is already good**: say so clearly and make only minor polish edits.`
  - After: removed.

### plugins/standalone/ceh-blog/skills/draft-post/SKILL.md:278

- **Rule:** 2.
- **Backing:** The same Fable 5 quote and URL as above.
- **Models:**
  - Fable 5 benefits.
  - The Opus 5 guide wants padding guarded ("Match the length of written documents to what the task needs… do not pad with filler sections"), so removing a padding rule could have hurt it. The line `:140` ("Length: what the content needs — don't pad, don't cut substance") stays and still carries that guard, so Opus 5 is unaffected.
  - The other guides are silent.
- **Change (one bullet removed):**
  - Before: `- **No fluff drafts**: specific, well-structured, worth publishing — not a padded word count mirroring the input length.`
  - After: removed.

## Dropped from the report

- **F4 (`draft-post:141-143`, word ranges to relative wording):** I dropped it. The Opus 5 guide says its written files run long and recommends "explicit length calibration", so removing the numeric ranges would hurt Opus 5 and nothing in the guides backs the change.

I edited only the two `SKILL.md` files. I did not run `validate.py`. The report's follow-up chores are still open: a PATCH bump of `ceh-blog` in `plugin.json` and `marketplace.json`, the `CHANGELOG.md` entry, the `docs/PLUGIN_VERSIONS.md` row, and a check that the `CROSS_REFERENCES.md:129` "Diverges" note still matches.
