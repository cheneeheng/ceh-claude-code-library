# Model audit: ceh-testing

- Date: 2026-10-16
- claude-code 2.1.301
- Edits applied: no
- WARNING: 1 tool call(s) were denied, so the report may be incomplete.

## Unpinned audit against fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5

Audit model: sonnet-5-5, effort: medium. Raw output: [ceh-testing.doctor.md](ceh-testing.doctor.md).

## Kept changes

### plugins/standalone/ceh-testing/skills/audit-test-suite/SKILL.md:225
Rule 2 (Opus 5, Opus 5.5), and the `/doctor` report's finding F1.
- Backing, [Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5): "Match the length of written documents to what the task needs: cover the substance, but do not pad with filler sections, redundant summaries, or boilerplate."
- Opus 5.5 builds on the Opus 5 patterns. The other guides say nothing about numeric caps on report length, so those models are unaffected.
- The Sonnet 5 guide says "be concrete about where the bar is rather than using qualitative terms like 'important'". The report's wording ("findings that change a decision") is qualitative, so I made the bar concrete.
```diff
-- Cap the list at about 15 findings and cut the tail rather than listing everything, because a
-  long tail buries the few fixes that matter.
+- Keep the list to findings that let a suite pass on broken code or let a real failure go
+  unnoticed, ranked worst-first, because a long tail buries the few fixes that matter.
```

### plugins/standalone/ceh-testing/skills/audit-test-suite/SKILL.md:124
Rule 3. Two instructions contradict each other.
- Line 22 says "Run the checks in order". Line 124 says mutation (check 3) runs "last", before checks 4 to 6.
- Backing: none needed, since this is an internal contradiction.
```diff
-Cap the run, for example `timeout 900 mutmut run ...`. Run it last so a timeout still leaves the
-cheap findings intact, and if it does not finish, report partial results and say the run was
-truncated.
+Cap the run, for example `timeout 900 mutmut run ...`. Run it after checks 1 and 2 so a timeout
+still leaves the cheap findings intact, and if it does not finish, report partial results and say
+the run was truncated.
```

### plugins/standalone/ceh-testing/skills/audit-test-suite/SKILL.md:20
Rule 4 (missing statement of when the task is done, added to the opening).
- Backing, [general page](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices): "Provide clear success criteria: Define what constitutes a successful answer to your research question."
```diff
 a hurry or by a model — reliably contains tests that pass on broken code. This skill finds them.
+
+The task is done when checks 1 and 2 have run, every later check has run or is named as unrun with
+its command, and each finding in the report quotes the code it is about.
 
 Run the checks in order: each is cheaper than the one after it, and the cheap ones find most of it.
```

### plugins/standalone/ceh-testing/skills/close-test-risk-gaps/SKILL.md:26
Rule 4 (missing done statement). Backing: the same success-criteria quote and URL as above.
```diff
 called done. **For each class: does the trigger fire? If no, skip it and say so.** Adding tests
 whose trigger did not fire is ritual, and it is how a suite becomes slow and ignored.
+
+The task is done when all five classes have a verdict and every class that fires has its tests
+written and passing.
```

### plugins/standalone/ceh-testing/skills/design-test-cases/SKILL.md:17
Rule 4 (missing done statement). The only done criterion sits at line 211 under Rules. Backing: the same success-criteria quote and URL as above.
```diff
 and which scenarios.**
+
+The task is done when every rung has its tests or a stated skip, and no test lacks a nameable
+`fails_when`.
 
 ## Two failure modes, not one
```

### plugins/standalone/ceh-testing/skills/design-test-cases/SKILL.md:126
Rule 4 (a negative instruction rewritten as the positive one it implies). Rule 2 also applies to Sonnet 5 and 5.5.
- Backing, [Sonnet 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5): "Positive examples showing how Claude can communicate with the appropriate level of concision tend to be more effective than negative examples or instructions that tell the model what not to do."
- Sonnet 5.5 builds on Sonnet 5. No other guide says positive phrasing hurts, so the other models are unaffected.
```diff
-boundary cases from rung 2. Do **not** write an oracle by re-implementing the function in the test
-file unless a genuinely independent reference already exists: a re-implementation shares your
-misreading of the spec and doubles what has to change when the spec moves.
+boundary cases from rung 2. Write an oracle only against a genuinely independent reference that
+already exists, because a re-implementation in the test file shares your misreading of the spec and
+doubles what has to change when the spec moves.
```

### plugins/standalone/ceh-testing/skills/test-a-bug-fix/SKILL.md:20
Rule 4 (missing done statement). Backing: the same success-criteria quote and URL as above.
```diff
 code, not against the bug, and routinely passes on the broken version too.
+
+The task is done when the reproducer failed with the bug's symptom before the fix, passes with it,
+fails again with the fix removed, and ships in the same commit as the fix.
 
 ## What waits for a request
```

### plugins/standalone/ceh-testing/skills/test-a-bug-fix/SKILL.md:60
Rule 4 (negative rewritten as the positive it implies). Backing: the same Sonnet 5 quote as above.
```diff
-Minimal change that turns the test green. Resist fixing anything the reproducer does not cover.
+Minimal change that turns the test green. Fix only what the reproducer covers.
```

### plugins/standalone/ceh-testing/skills/test-a-bug-fix/SKILL.md:106
Rule 3. The bisect command names a test that does not exist: step 1 and the naming table define `test_parse_duration_rejects_bare_number`.
```diff
-git bisect run pytest tests/unit/test_parse_duration.py::test_rejects_bare_number
+git bisect run pytest tests/unit/test_parse_duration.py::test_parse_duration_rejects_bare_number
```

### plugins/standalone/ceh-testing/skills/verify-behavior-preserved/SKILL.md:23
Rule 4 (missing done statement). Backing: the same success-criteria quote and URL as above.
```diff
 Green on a suite that never covered the region proves nothing.
+
+The task is done when the pins were committed before the change, the suite is green with no test
+edits, and the differential run shows no divergence or each divergence is declared.
 
 ## What waits for a request
```

I left these out:
- **F2** (the `mutmut --paths-to-mutate` flag) and **F3** (`/tmp/before`). The report itself marks both low confidence and unverified, so neither is a confirmed defect.
- **Verification steps.** The Opus 5 advice to drop verification instructions would hurt Sonnet 5.5, whose guide wants a real check run before a change is reported done. It also conflicts with this plugin's purpose.
- **Report-only items on the `/doctor` page.** The `# MUST fail` comment and "try to break it" trigger phrase are not pressure language, and the report says so.
