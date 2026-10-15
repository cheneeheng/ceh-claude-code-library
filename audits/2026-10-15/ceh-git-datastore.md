# Model audit: ceh-git-datastore

- Date: 2026-10-15
- claude-code 2.1.301
- Edits applied: no
- WARNING: 1 tool call(s) were denied, so the report may be incomplete.

## Unpinned audit against fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5

Audit model: sonnet-5-5, effort: medium. Raw output: [ceh-git-datastore.doctor.md](ceh-git-datastore.doctor.md).

## Kept changes

### skills/build-git-datastore/SKILL.md:19

**Rule:** 4, a missing statement of when the task is done, added to the file's opening.

**Backing:** Rule 4 itself. The Opus 5.5 guide also says "You can also state the completion condition up front" (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5). The report's empty diff did not look for this gap.

**Before:**
```
A bare git repo as the data layer for an app that does not have a database yet.
One repo per deployed instance; one **orphan branch per project**; JSON records
in trees under that branch.
```

**After:**
```
A bare git repo as the data layer for an app that does not have a database yet.
One repo per deployed instance; one **orphan branch per project**; JSON records
in trees under that branch.

The task is done when the gate verdict is stated. If the gate passes, it is also done when the
store sits behind the store interface, backup is wired, and the migration trigger is in the README.
```

### skills/migrate-git-datastore/SKILL.md:19

**Rule:** 4, a missing statement of when the task is done, added to the file's opening.

**Backing:** Rule 4 itself. The Opus 5.5 guide also says "You can also state the completion condition up front" (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5).

**Before:**
```
The git store was a deliberate stage. This is how to leave it without downtime,
without losing writes, and without discovering the data was messier than
expected halfway through a backfill.
```

**After:**
```
The git store was a deliberate stage. This is how to leave it without downtime,
without losing writes, and without discovering the data was messier than
expected halfway through a backfill.

The task is done when the "is it time" verdict is stated. If a trigger has fired, it is also done
when `verify.py` passes for every project, each project is cut over, and the archive bundle exists.
```

### skills/migrate-git-datastore/SKILL.md:190

**Rule:** 4, a negative instruction rewritten as the positive one it implies.

**Backing:** "Positive examples showing how Claude can communicate with the appropriate level of concision tend to be more effective than negative examples or instructions that tell the model what not to do." (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5). The next sentence already gives the positive behavior, so dropping "Not a batch job that ends with 'migrated'" changes nothing the model does.

**Before:**
```
Not a batch job that ends with "migrated". Report at each phase what was found,
what it implies, and what needs a decision — ...
```

**After:**
```
Work in phases. Report at each phase what was found,
what it implies, and what needs a decision — ...
```

---

I checked two things in the report and kept neither.

- **Unverifiable claims:** The report flagged "Tested for concurrency, atomicity, and lost updates" and "observed on a realistic test store". I left both alone. They are provenance claims that no guide asks to remove, and the report says removing them "gains nothing".
- **Stop conditions:** I left the "Do not build it anyway…" and "Do not plan the migration" lines alone. Rewriting them positively could weaken the stop.
