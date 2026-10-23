# Model audit: ceh-blog

- Date: 2026-10-23
- claude-code 2.1.309
- Edits applied: no

## Unpinned audit against fable-5, fable-5-1, haiku-5-5, opus-5, opus-5-5, sonnet-5, sonnet-5-5

Audit model: sonnet-5-5, effort: medium. Raw output: [ceh-blog.doctor.md](ceh-blog.doctor.md).

## Kept changes

### plugins/standalone/ceh-blog/skills/draft-post/SKILL.md:297

Rule 4: this cuts prose that changes no behavior. The report backs it as finding 1, and I also checked it against the file.

Backing, from the Fable 5 guide (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5): "Skills developed for prior models are often too prescriptive for Claude Fable 5 and can degrade output quality. Review and consider removing older instructions if default performance is better." The same guide says "Instruction-following is improved enough that you can steer most behaviors with a brief instruction rather than enumerating each behavior by name."

Five of the six Working principles bullets restate rules the same file already gives:

- "Infer first, ask second" repeats step 2's "Infer without asking" and `ask-the-author.md` rule 5.
- "All questions at once" repeats interview rule 1 and `ask-the-author.md` rule 1.
- "Read everything before writing anything" repeats the first line of step 2.
- "Concrete over abstract" repeats step 3's "specific raw material" and the Voice rules.
- "Use the user's words" repeats the step 4 Body bullet.

Before:

```
### Working principles

- **Infer first, ask second**: extract everything the user has already said, and only ask what you genuinely can't infer.
- **All questions at once**: never ask turn by turn. Send every question in one numbered batch, each atomic and ending in options, and ask the author to answer all of them. Put the question that unlocks the post first. Notes with a workable angle get zero questions.
- **Read everything before writing anything**: full material first, identify the angle, then one complete draft.
- **Pick the strongest thread**: if the material sprawls, choose the sharpest angle rather than covering everything, and tell the user which thread you picked and why.
- **Concrete over abstract**: push for specifics — real numbers, actual events, named people, exact moments.
- **Use the user's words**: pull real phrases, specifics, and examples from the material and the interview. A usable line ("first impression is a lot cleaner and smooth") goes into the draft nearly word-for-word.
```

After:

```
### Working principles

- **Pick the strongest thread**: if the material sprawls, choose the sharpest angle rather than covering everything, and tell the user which thread you picked and why.
```

### plugins/standalone/ceh-blog/skills/draft-post/SKILL.md:143

Rule 4: this keeps the one clause from the cut bullets that nothing else states. It is part of the previous change, so without it that change drops a behavior.

Backing: the report's own note. "'Put the question that unlocks the post first' is not stated elsewhere, so move that clause into step 3's interview rule 1." The Fable 5 quote above covers the cut. "Notes with a workable angle get zero questions" is already covered by step 3's opening, "Skip this step when the material is rich or the route was notes."

Before:

```
1. **One batch, answered together.** Send all the questions at once and wait for the author's
   answers to all of them. Never ask turn by turn.
```

After:

```
1. **One batch, answered together.** Send all the questions at once, the one that unlocks the post
   first, and wait for the author's answers to all of them. Never ask turn by turn.
```
