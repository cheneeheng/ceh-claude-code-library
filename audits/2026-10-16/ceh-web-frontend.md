# Model audit: ceh-web-frontend

- Date: 2026-10-16
- claude-code 2.1.301
- Edits applied: no
- WARNING: 2 tool call(s) were denied, so the report may be incomplete.

## Unpinned audit against fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5

Audit model: sonnet-5-5, effort: medium. Raw output: [ceh-web-frontend.doctor.md](ceh-web-frontend.doctor.md).

## Kept changes

### plugins/standalone/ceh-web-frontend/skills/visualize-graph-cytoscape/SKILL.md:29
- **Rule:** 3, a model-independent defect: two instructions contradict each other.
- **Backing:** The file's own text. Line 30 says "Read the checklist in step 0 before writing any code" and the step 0 heading says "read the checklist". But step 0 holds the ten failure rules, and `references/checklist.md` is loaded only in step 5 ("Run through `references/checklist.md` before declaring done").
- **Change:**

Before:
```
Follow these steps in order. Do not skip step 1 — picking the wrong layout is the difference between
a legible diagram and a hairball. Read the checklist in step 0 before writing any code.

### 0. Rule zero: read the checklist before writing code
```
After:
```
Follow these steps in order. Do not skip step 1: picking the wrong layout is the difference between
a legible diagram and a hairball.

### 0. Rule zero: the ten failures that break most builds
```

### plugins/standalone/ceh-web-frontend/skills/visualize-graph-cytoscape/SKILL.md:23
- **Rule:** 3, a model-independent defect: a reference to content that no longer exists.
- **Backing:** `plugins/CLAUDE.md`: "The Cytoscape API and stylesheet references were cut on 2026-10-08 as material the model already knows." Line 23 ("The API below is based on version v3.34.2") and line 296 ("the API notes above track a specific release") still point at that cut API section. The version pins on lines 211 and 301 stay as example pins.
- **Change:**

Before (line 23):
```
The API below is based on version **v3.34.2**
```
After:
```
The examples pin Cytoscape.js 3.34.2.
```
Before (line 296):
```
Pin the core exactly — the API notes above track a specific release. Pin extensions to a
```
After:
```
Pin the core exactly. Pin extensions to a
```

### plugins/standalone/ceh-web-frontend/skills/visualize-graph-cytoscape/SKILL.md:87
- **Rule:** 4, cuts prose that changes no behavior.
- **Backing:** The file's own text. Rule 9 (lines 87-94) repeats the 116-node, zoom 0.47, 4.6px figures from "Sizing and readable defaults" (lines 348-399). That section also carries the pixel-size gate and the options for when fitting fails (subset, fixed zoom, fewer elements, search). Deleting the copy in rule 9 changes nothing the model does.
- **Change:**

Before:
```
9. **`cy.fit()` on the whole graph stops working past a few dozen nodes.** Fitting
   computes a zoom that makes everything visible, which for a wide or large graph is a
   zoom nobody can read. A 116-node org chart fits at zoom 0.47, which renders a
   `font-size: 10` label at 4.6px — under `min-zoomed-font-size`, so Cytoscape draws no
   labels at all and the user sees grey confetti. The test is `zoom × font-size` in
   pixels, never a zoom constant. Measure it and decide: fit to a _subset_, start at a
   fixed readable zoom and let the user pan, or show fewer elements. See "Sizing and
   readable defaults" below.
```
After:
```
9. **`cy.fit()` on a large graph can leave every label unreadable.** When `zoom × font-size`
   falls under `min-zoomed-font-size`, Cytoscape draws no labels at all. Gate on that pixel
   size, never a zoom constant. See "Sizing and readable defaults" below.
```

### plugins/standalone/ceh-web-frontend/skills/configure-bun-vite-env/SKILL.md:61
- **Rule:** 1, backed by the general page, and also 4.
- **Backing:** https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices: "these models may now overtrigger. The fix is to dial back any aggressive language. Where you might have said "CRITICAL: You MUST use this tool when...", you can use more normal prompting like "Use this tool when..."." The line gives no reason, and the same page says to give context or motivation for an instruction. "Non-negotiable" adds no behavior beyond the imperative.
- **Change:**

Before:
```
- `strict: true` in `tsconfig.json` is non-negotiable. Never use `// @ts-ignore` — fix the type error.
```
After:
```
- Set `strict: true` in `tsconfig.json`. Fix a type error instead of suppressing it with `// @ts-ignore`.
```

## Pinned tuning: `agents/playwright-system-tester.md` for sonnet-5-5

Tuning model: opus-5-5, effort: high. Last tuned for: never.

### Proposed edits

#### Process, step 5 "Run and verify" (lines 62-64)

> "When you change code that can be run, built, or type-checked, run a real check that exercises the change before reporting it done [...] A syntax-only check, or a check command that failed to start, does not count; if all that is missing is the project's declared dependencies, install them with its own package manager and lockfile [...] never via sudo or the system package manager, unless told not to. Only if no real check can run here, say which one you did not run and why instead of reporting the change as done."
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5

Before:

```markdown
5. **Run and verify.** Execute `bash "${CLAUDE_PLUGIN_ROOT}/scripts/run-e2e.sh" test <pattern>`. Iterate
   until green on a clean bring-up. Confirm the suite passes twice in a row — flakes on
   the second run mean state leak.
```

After:

```markdown
5. **Run and verify.** Execute `bash "${CLAUDE_PLUGIN_ROOT}/scripts/run-e2e.sh" test <pattern>`. Iterate
   until green on a clean bring-up. Confirm the suite passes twice in a row — flakes on
   the second run mean state leak. A run counts only when the stack came up and the browser
   launched. A suite that failed to start, or a type-check of the spec files alone, is not a
   pass. If all that is missing is a declared dependency or the browser binary, install it with
   the project's own package manager and lockfile (for example `bunx playwright install chromium`),
   never via sudo or the system package manager. If no real run can happen here, report the
   suite as not run and give the reason.
```

#### Process, step 6 "Report" (line 66)

> "The model tends to add tests, documentation, and small supporting files that fit your repository's conventions, even when you don't ask for them. [...] If you prefer changes limited to what was explicitly requested, add only the second paragraph of that prompt": "When the work the user asked for is done and checked, stop and report. Don't add features, tests, files, docs or refactors that weren't asked for. If you think one would help, mention it at the end instead of doing it."
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5

Before:

```markdown
6. **Report.** Return the output below as your final message.
```

After:

```markdown
6. **Report.** When the requested journeys are written and have passed both runs, stop and return
   the output below as your final message. Write only the specs, fixtures, and config those
   journeys need. If a CI job, a README section, or another journey would help, name it in the
   report instead of adding it.
```

#### Output to parent session, example block (lines 78-83)

> "**Diverse:** Cover edge cases and vary enough that Claude doesn't pick up unintended patterns."
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
>
> "Claude Sonnet 5 interprets prompts literally and explicitly [...] It does not silently generalize an instruction from one item to another."
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5

Before:

````markdown
```
PASS (2 clean runs) — e2e/checkout.spec.ts: add to cart, pay, confirmation email link.
Run: bash "${CLAUDE_PLUGIN_ROOT}/scripts/run-e2e.sh" test checkout
Env: E2E_BASE_URL, docker-compose.test.yml, Chromium via `bunx playwright install chromium`.
Workaround: none.
```
````

After:

````markdown
```
PASS (2 clean runs) — e2e/checkout.spec.ts: add to cart, pay, confirmation email link.
Run: bash "${CLAUDE_PLUGIN_ROOT}/scripts/run-e2e.sh" test checkout
Env: E2E_BASE_URL, docker-compose.test.yml, Chromium via `bunx playwright install chromium`.
Workaround: none.
```

```
FAIL (run 1 of 2) — e2e/signup.spec.ts: step "open confirmation link" gets a 404 after seeding the user via POST /api/users.
Run: bash "${CLAUDE_PLUGIN_ROOT}/scripts/run-e2e.sh" test signup
Env: E2E_BASE_URL, docker-compose.test.yml, Chromium via `bunx playwright install chromium`.
Workaround: none. Not run: @smoke against staging, because no staging URL is set in env.
```
````

#### Hard rules, new rule after "Never reach into the app's internals" (line 90)

> "Tests are there to verify correctness, not to define the solution. [...] If the task is unreasonable or infeasible, or if any of the tests are incorrect, please inform me rather than working around them."
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

Before:

```markdown
- Never reach into the app's internals. No direct DB writes, no importing app modules.
```

After:

```markdown
- Never reach into the app's internals. No direct DB writes, no importing app modules.
- When a test fails because the app behaves wrongly, keep the assertion and report FAIL with the
  failing step. Loosening the assertion, skipping the test, or editing app code to get green hides
  the bug the suite exists to catch.
```

#### Hard rules, "Never hardcode" and "Never silently retry" (lines 91 and 95)

> "Providing context or motivation behind your instructions, such as explaining to Claude why such behavior is important, can help Claude better understand your goals and deliver more targeted responses."
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
>
> "Tell Claude what to do instead of what not to do"
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

Before:

```markdown
- Never hardcode URLs, credentials, or ports. Read from env.
```

```markdown
- Never silently retry failing tests to hide flakes. If a test flakes, diagnose it.
```

After:

```markdown
- Read URLs, credentials, and ports from env, never hardcode them, so the same suite runs against
  local, CI, and staging and no secret lands in the repo.
```

```markdown
- Diagnose a flaky test instead of adding retries. A retry that hides the flake also hides the
  state leak or race behind it, and the parent inherits a suite that fails at random.
```

#### Hard rules, last rule (line 96)

> "If you'd prefer to minimize net new file creation, you can instruct Claude to clean up after itself: If you create any temporary new files, scripts, or helper files for iteration, clean up these files by removing them at the end of the task."
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

Before:

```markdown
- Never leave Docker containers or browser processes running after the suite exits.
```

After:

```markdown
- Never leave Docker containers or browser processes running after the suite exits. Before you
  report, delete the scratch scripts, screenshots, and traces you made while debugging, unless the
  report cites them.
```

## Pinned tuning: `agents/vitest-integration-tester.md` for sonnet-5-5

Tuning model: opus-5-5, effort: high. Last tuned for: never.

### Proposed edits

#### Line 45: Process step 3, "Plan the test boundary"

> "Claude Sonnet 5 interprets prompts literally and explicitly, particularly at lower effort levels. It does not silently generalize an instruction from one item to another [...] If you need Claude to apply an instruction broadly, state the scope explicitly"
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5

Before:

```markdown
3. **Plan the test boundary.** Add a comment at the top of the test file:
```

After:

```markdown
3. **Plan the test boundary.** Add this comment at the top of every test file you write:
```

#### Lines 59-81: Process step 4, code example `afterEach` block

> "Examples are one of the most reliable ways to steer Claude's output format, tone, and structure."
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

The example resets shared state in `afterEach`. Step 4, the hard rules, and the output contract all say `beforeEach`. The example is the strongest signal in the file, so it should match the rule.

Before:

```ts
beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => {
  server.resetHandlers();
  setSession(null);
});
afterAll(() => server.close());
```

After:

```ts
beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
beforeEach(() => {
  server.resetHandlers();
  setSession(null);
});
afterAll(() => server.close());
```

#### Lines 101-102: Process step 5, "Run and verify"

> "When you change code that can be run, built, or type-checked, run a real check that exercises the change before reporting it done [...] A syntax-only check, or a check command that failed to start, does not count; if all that is missing is the project's declared dependencies, install them with its own package manager and lockfile (e.g. npm install, pip install -r requirements.txt), never via sudo or the system package manager, unless told not to."
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5

> "Implement a solution that works correctly for all valid inputs, not just the test cases. [...] If the task is unreasonable or infeasible, or if any of the tests are incorrect, please inform me rather than working around them."
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

Before:

```markdown
5. **Run and verify.** Execute `bash "${CLAUDE_PLUGIN_ROOT}/scripts/run-integration-tests.sh" <pattern>`.
   Iterate until green. Confirm the suite passes twice — flakes on the second run mean state leak.
```

After:

```markdown
5. **Run and verify.** Execute `bash "${CLAUDE_PLUGIN_ROOT}/scripts/run-integration-tests.sh" <pattern>`.
   Only a run that executes the new tests counts. A syntax or type check alone, or a run that
   failed to start, does not. If the run fails only because the project's declared dependencies are
   missing, install them with the project's own package manager and lockfile (for example
   `npm install`), never with sudo or the system package manager.
   Iterate until green by fixing the tests, not by loosening assertions or editing the component.
   If the component itself is wrong, keep the failing test and report it as the result.
   Confirm the suite passes twice — flakes on the second run mean state leak.
```

#### Line 104: Process step 6, "Report"

> "When the work the user asked for is done and checked, stop and report. Don't add features, tests, files, docs or refactors that weren't asked for."
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5

> "The model tends to add tests, documentation, and small supporting files that fit your repository's conventions, even when you don't ask for them. It does this at every effort level"
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5

The guide's "If you think one would help, mention it at the end" clause is left out on purpose, because adding it would change the output contract.

Before:

```markdown
6. **Report.** Return the output below as your final message.
```

After:

```markdown
6. **Report.** When the suite passes twice, stop and return the output below as your final
   message. Keep your changes to the test files and the MSW handlers and state resets they need:
   no docs, helpers, or refactors beyond that.
```

#### Lines 124-125: Hard rules, first bullet (blocked)

> "On agentic coding tasks at `low` and `medium` effort, the model sometimes checks in before the work is done. [...] Keep working until everything the user asked for is done, and only stop to ask when you can't go on without the user or before a risky step."
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5

A subagent that "checks in" ends its run early and hands back a partial suite, so the rule needs a positive keep-going condition next to the blocker rule.

Before:

```markdown
- You cannot ask questions. When blocked, stop and make the blocker your final message: what you
  finished, what stopped you, what the parent should decide.
```

After:

```markdown
- Keep working until the suite is written and passes twice. Stop early only when you cannot go on
  without the parent. You cannot ask questions, so when blocked, make the blocker your final
  message: what you finished, what stopped you, what the parent should decide.
```

#### Lines 127-131: Hard rules, the five "Never" bullets

> "Providing context or motivation behind your instructions, such as explaining to Claude why such behavior is important, can help Claude better understand your goals and deliver more targeted responses. [...] Claude is smart enough to generalize from the explanation."
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

> "Tell Claude what to do instead of what not to do"
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

Before:

```markdown
- Never mock shared state or internal modules — use the real modules and reset them in `beforeEach`.
- Never call `fetch` directly in tests — use MSW to intercept at the network layer.
- Never assert on internal component state — assert on rendered output and shared state values.
- Never leave shared state dirty between tests — reset every state module in `beforeEach`.
- Never import from `../../` paths — use `$lib` alias throughout.
```

After:

```markdown
- Use the real shared state and internal modules, because mocking them turns this into a unit
  test and hides the wiring bugs this suite exists to catch.
- Let the component's own API client make every request, intercepted by MSW, so the test covers
  the real call path. A `fetch` written in the test itself covers nothing the component does.
- Assert on rendered output and exported shared-state values, which is what users and other
  components see, so the tests survive refactors of a component's internals.
- Reset every state module in `beforeEach`, because state left by one test leaks into the next
  and shows up as the second-run flake that step 5 checks for.
- Import through the `$lib` alias rather than `../../` paths, so tests keep resolving when files
  move.
```

## Pinned tuning: `agents/vitest-unit-tester.md` for sonnet-5-5

Tuning model: opus-5-5, effort: high. Last tuned for: never.

### Proposed edits

#### Process, line 36 (new opening sentence under `## Process`)

> "Claude Sonnet 5 interprets prompts literally and explicitly, particularly at lower effort levels. It does not silently generalize an instruction from one item to another, and it does not infer requests you didn't make. [...] If you need Claude to apply an instruction broadly, state the scope explicitly (for example, "Apply this formatting to every section, not just the first one")."
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5

Steps 2 to 5 talk about one "target" and one `<source_file>`, while the description invites "cover this module" requests that can name several files. A literal reader can stop after the first file.

Before:

```markdown
## Process

1. **Detect the framework.**
```

After:

```markdown
## Process

When the parent names several target files, run steps 2 to 5 for every one of them, not just the
first, and cover them all in one report.

1. **Detect the framework.**
```

#### Step 5, lines 61-64 (Run and verify)

> "When you change code that can be run, built, or type-checked, run a real check that exercises the change before reporting it done [...] A syntax-only check, or a check command that failed to start, does not count; if all that is missing is the project's declared dependencies, install them with its own package manager and lockfile (e.g. npm install, pip install -r requirements.txt), never via sudo or the system package manager, unless told not to. Only if no real check can run here, say which one you did not run and why instead of reporting the change as done."
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5

The guide's example of a skipped check is "it might skip the project's tests because the project's dependencies aren't installed". That is the usual way `run-unit-tests.sh` fails in a fresh TypeScript checkout.

Before:

```markdown
5. **Run and verify.** Execute `bash "${CLAUDE_PLUGIN_ROOT}/scripts/run-unit-tests.sh" <test_file>` and iterate
   until green. Then run `bash "${CLAUDE_PLUGIN_ROOT}/scripts/check-coverage.sh" <source_file>` to find
   the lines and branches of the target file that are still untested. The percentage is not a goal:
   never add a test only to raise it.
```

After:

```markdown
5. **Run and verify.** Execute `bash "${CLAUDE_PLUGIN_ROOT}/scripts/run-unit-tests.sh" <test_file>` and iterate
   until green. A run that failed to start does not count as a run. If the only thing missing is the
   project's declared dependencies, install them with the project's own package manager and
   lockfile (`npm ci`, `pnpm install --frozen-lockfile`, `yarn install --frozen-lockfile`), never
   with sudo or a global install, then run the tests again. Then run
   `bash "${CLAUDE_PLUGIN_ROOT}/scripts/check-coverage.sh" <source_file>` to find the lines and
   branches of the target file that are still untested. The percentage is not a goal: never add a
   test only to raise it.
```

#### Hard rules, lines 85-86 (the "You cannot ask questions" bullet)

> "On agentic coding tasks at `low` and `medium` effort, the model sometimes checks in before the work is done. It might pause to confirm a plan, ask a question it could answer itself, or stop after one part of a multipart task to ask whether to continue. [...] Keep working until everything the user asked for is done, and only stop to ask when you can't go on without the user or before a risky step. When the work the user asked for is done and checked, stop and report. Don't add features, tests, files, docs or refactors that weren't asked for. If you think one would help, mention it at the end instead of doing it."
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5

The agent pins `model: sonnet` with no `effort`, so it runs at whatever level the parent session uses, which can be `low` or `medium`. The guide also says the model "tends to add tests, documentation, and small supporting files [...] at every effort level". For this agent, tests are the deliverable, so the scope line is narrowed to tests outside the targets.

Before:

```markdown
- You cannot ask questions. When blocked, stop and make the blocker your final message: what you
  finished, what stopped you, what the parent should decide.
```

After:

```markdown
- You cannot ask questions. Keep working until every target is covered and its tests have run, and
  stop early only when blocked. Then make the blocker your final message: what you finished, what
  stopped you, what the parent should decide.
- When every target's tests have run, stop and report. Do not add tests for units the parent did
  not name, docs, config changes, or refactors. If one would help, name it in the report instead.
```

#### Hard rules, line 88 (the "Never modify source files" bullet)

> "Implement a solution that works correctly for all valid inputs, not just the test cases. [...] Tests are there to verify correctness, not to define the solution. [...] If the task is unreasonable or infeasible, or if any of the tests are incorrect, please inform me rather than working around them."
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

"Iterate until green" plus "never modify source" leaves one way to get green when the source is wrong: change the assertion to match the bug. The page's principle that tests verify correctness rather than define it applies to this case directly.

Before:

```markdown
- Never modify source files to make tests pass — if the code is untestable, flag it and stop.
```

After:

```markdown
- Never modify source files to make tests pass — if the code is untestable, flag it and stop.
- Assert the behavior the code should have, not whatever it happens to return. When a test fails
  because the source looks wrong, leave the assertion as written and report a FAIL that names the
  suspected bug, rather than loosening the test until it passes.
```

#### Hard rules, lines 89-91 (framework, order, and `any` bullets)

> "Providing context or motivation behind your instructions, such as explaining to Claude why such behavior is important, can help Claude better understand your goals and deliver more targeted responses. [...] Claude is smart enough to generalize from the explanation."
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

These three bullets are bare prohibitions. The `toStrictEqual` rule at lines 57-58 already shows the house style of giving a reason.

Before:

```markdown
- Never add a new test framework or runner.
- Never write tests that depend on execution order across `it` blocks.
- Never use `any` in test code unless the source already exposes `any` at that boundary.
```

After:

```markdown
- Never add a new test framework or runner: the project's CI and scripts run only the one it has.
- Never write tests that depend on execution order across `it` blocks: `.only`, filtering, and
  shuffled runs execute tests alone or reordered, so each must pass by itself.
- Never use `any` in test code unless the source already exposes `any` at that boundary: it turns
  off the type checking that catches a mock or fixture with the wrong shape.
```

#### Output to parent session, lines 77-81 (example block)

> "Examples are one of the most reliable ways to steer Claude's output format, tone, and structure. [...] When adding examples, make them: [...] **Diverse:** Cover edge cases and vary enough that Claude doesn't pick up unintended patterns."
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

The only example shows a PASS. That steers toward one shape and leaves the FAIL path and the suspected-bug path without a model. The new block adds no fields to the contract. It shows the existing "lead with the pass/fail result" rule in its failing case.

Before:

````markdown
```
PASS — 11 tests added in src/lib/format.test.ts.
Untested: format.ts:58-61 (locale fallback), left because it needs a second locale fixture.
Untestable: parseRange() reads Date.now() directly. Inject a clock parameter.
```
````

After:

````markdown
```
PASS — 11 tests added in src/lib/format.test.ts.
Untested: format.ts:58-61 (locale fallback), left because it needs a second locale fixture.
Untestable: parseRange() reads Date.now() directly. Inject a clock parameter.
```

```
FAIL — 7 tests added in src/lib/cart.test.ts, 1 failing.
Failing: applyDiscount() on an empty cart returns NaN, expected 0 (cart.ts:42 divides by subtotal).
Suspected source bug, assertion left as written.
Untested: none.
```
````

## Pinned tuning: `agents/web-frontend-reviewer.md` for sonnet-5-5

Tuning model: opus-5-5, effort: high. Last tuned for: never.

### Proposed edits

#### Output to parent session, lines 37–39 (finding cap and prefixes)

> "When a review prompt says things like "only report high-severity issues," "be conservative," or "don't nitpick," Claude Sonnet 5 may follow that instruction more faithfully than earlier models did … If your harness has a separate verification, deduplication, or ranking stage, tell the model explicitly that its job at the finding stage is coverage rather than filtering." (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5)

> "It does not silently generalize an instruction from one item to another, and it does not infer requests you didn't make." (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5)

The caller, `ceh-git-workflow:code-review` step 2, already re-reads every quoted line and applies its cap after the merge. This reviewer is therefore the finding stage, and the fifteen-item cap is a filter it would follow literally, dropping findings without saying so. The prefixes come from code-review, which this agent never loads, so the edit names them.

Before:

```
Lead with the counts. Then each finding, most severe first, at most fifteen, in code-review's
format: a prefix, `path:line`, the quoted line, the problem, and for `[blocking]` what would
resolve it.
```

After:

```
Lead with the counts. Then each finding, most severe first, in code-review's format: a prefix
(`[blocking]`, `[advisory]`, or `[question]`), `path:line`, the quoted line, the problem, and for
`[blocking]` what would resolve it. Your job is coverage, not filtering: the calling review
re-reads every quoted line and applies its own cap after the merge, so a real finding you drop is
lost, while one it filters out costs nothing. Write out up to fifteen findings in full. Past
fifteen, list the rest by prefix and `path:line` under Dismissed as over the cap.
```

#### Output example, line 42 (count line)

> "Examples are one of the most reliable ways to steer Claude's output format, tone, and structure." (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)

> "Claude Sonnet 5 interprets prompts literally and explicitly" (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5)

The example's count line says 2 advisory, but the example shows only one `[advisory]` finding. A model that copies the example literally learns that the counts do not need to match the findings.

Before:

```
web-frontend-reviewer: 1 blocking, 2 advisory, 0 questions, 1 cannot verify.
```

After:

```
web-frontend-reviewer: 1 blocking, 1 advisory, 0 questions, 1 cannot verify.
```

#### Hard rules, line 63 (the reporting bar)

> "If you do want the model to self-filter in a single pass, be concrete about where the bar is rather than using qualitative terms like "important": for example, "report any bugs that could cause incorrect behavior, a test failure, or a misleading result; only omit nits like pure style or naming preferences."" (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5)

> "Tell Claude what to do instead of what not to do" (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)

The current rule only says what to leave out. The new rule states the bar for what to report, and keeps the one exclusion.

Before:

```
- Leave style a linter would catch out entirely.
```

After:

```
- Report anything that could cause incorrect behavior, a security hole, an accessibility failure,
  a type error, or a test failure, including low-severity cases and ones you are unsure of. Omit
  only style a linter would catch.
```

#### Process, step 6 (line 33, stopping point)

> "At these levels the model is especially thorough. After it finishes a task, it can start its own rounds of review and verification … "When the work the user asked for is done and its checks pass, stop and report. Don't start extra rounds of review or hardening on your own … If you think a deeper review is worth doing, say so at the end."" (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5)

The agent's tools (Read, Grep, Glob, Skill) cannot launch subagents, so the edit adapts only the part about extra review rounds.

Before:

```
6. **Report.** Return the output below as your final message.
```

After:

```
6. **Report.** Once every finding has been checked against the file, stop and return the output
   below as your final message. Do not start a second review pass. If part of the diff deserves a
   deeper look than one pass gives, say so in one line after Dismissed.
```
