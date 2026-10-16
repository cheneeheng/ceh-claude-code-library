| # | Topic | Outcome | Status |
|---|---|---|---|
| 1 | Playwright agent base URL | `playwright-system-tester.md` allows a hardcoded `localhost:3000` fallback and forbids hardcoded URLs and ports. Rewrite proposed (high). | inferred |
| 2 | Cytoscape step 0 | `SKILL.md` tells the reader to read the checklist in step 0, but step 0 is the ten rules and the checklist is step 5. Rewrite proposed (high). | inferred |
| 3 | Cytoscape version claim | "The API below is based on version v3.34.2" points at an API section that was cut on 2026-10-08. Rewrite proposed (medium). | inferred |
| 4 | Cytoscape rule 9 | The 116-node org chart numbers appear in rule 9 and again in "Sizing and readable defaults". Trim rule 9 to a pointer (medium). | inferred |
| 5 | Integration tester | The description says "frontend components" but the body is Svelte-only. Generalize the Svelte references (medium). | inferred |
| 6 | Low-confidence items | Flag only, no diff: the ESLint example's flat-config shape, "non-negotiable" in `configure-bun-vite-env`, and repeated baseline rules in `make-ui-accessible`. | unverified |
| 7 | Everything else | No other findings. No pressure language, scaffolds for older models, prefills, or incident narratives turned up. | inferred |

I made two assumptions, which you can correct by re-running with a narrower request. Scope is all of `plugins/standalone/ceh-web-frontend`. Target model is Sonnet 5.5, which is the model running this audit and the one the agents' `model: sonnet` alias resolves to.

By group: Group 1 has 0 findings. Group 2 has 5 (items 1–5 above). Group 3 (tool descriptions) and Group 4 (request config) are not applicable, because the plugin has no tool definitions or request-building code. The roster check for redundant specialist agents is clean: the unit, integration, and system testers have disjoint scopes.

**Playwright agent base URL**

- `agents/playwright-system-tester.md:41` says "Default to `http://localhost:3000` only as a fallback". Line 91 says "Never hardcode URLs, credentials, or ports. Read from env." A model following both has to guess which one wins.
- The newer line can't be determined by `git blame`, so I assumed the hard rule is the intended one. The fix keeps the fallback but sources it from the project's own config.

```diff
--- a/agents/playwright-system-tester.md
+++ b/agents/playwright-system-tester.md
@@ -39,3 +39,3 @@
 2. **Locate the target environment.** Look for a `BASE_URL` / `E2E_BASE_URL` env var,
    a `.env.test`, or a compose file. Tests must read the target URL from env, never hardcoded.
-   Default to `http://localhost:3000` only as a fallback.
+   If none is set, use the `baseURL` in the Playwright config. If that is unset too, stop and report it.
```

**Cytoscape step 0**

- `SKILL.md:29-30` says "Read the checklist in step 0 before writing any code", and the step 0 heading at `:32` says "read the checklist". But step 0 holds the ten failure rules, and `references/checklist.md` is only loaded at step 5. The skill contradicts itself about what to read first.
- The checklist is a pre-delivery check, so the fix removes the pre-coding claim and renames the heading.

```diff
--- a/skills/visualize-graph-cytoscape/SKILL.md
+++ b/skills/visualize-graph-cytoscape/SKILL.md
@@ -29,4 +29,3 @@
-Follow these steps in order. Do not skip step 1 — picking the wrong layout is the difference between
-a legible diagram and a hairball. Read the checklist in step 0 before writing any code.
+Follow these steps in order. Do not skip step 1: picking the wrong layout is the difference between
+a legible diagram and a hairball.
 
-### 0. Rule zero: read the checklist before writing code
+### 0. Rule zero: the ten failures that break most builds
```

**Cytoscape version claim**

- `plugins/CLAUDE.md` records that the Cytoscape API and stylesheet references were cut on 2026-10-08. Line 23 and the "API notes above" phrase at `:296` still describe an API section that no longer exists. The version appears in three pins: `SKILL.md:211`, `SKILL.md:301`, and `assets/template.html:86`. Those pins are examples, so they stay.

```diff
--- a/skills/visualize-graph-cytoscape/SKILL.md
+++ b/skills/visualize-graph-cytoscape/SKILL.md
@@ -23 +23 @@
-The API below is based on version **v3.34.2**
+The examples pin Cytoscape.js 3.34.2.
@@ -296,2 +296,2 @@
-Pin the core exactly — the API notes above track a specific release. Pin extensions to a
+Pin the core exactly. Pin extensions to a
 major range: their patch releases are not tracked here, and a stale exact pin is worse
```

**Cytoscape rule 9**

- Rule 9 (`:87-94`) and "Sizing and readable defaults" (`:348-399`) both carry the 116-node, zoom 0.47, 4.6px figures. The detailed version belongs under Sizing. The duplicate in rule 9 is the kind of scattered repetition that makes a reader reconcile two wordings.
- I kept the `layoutstop` anecdote in rule 7 because it explains a silent failure, which is context rather than history.

```diff
--- a/skills/visualize-graph-cytoscape/SKILL.md
+++ b/skills/visualize-graph-cytoscape/SKILL.md
@@ -87,8 +87,4 @@
-9. **`cy.fit()` on the whole graph stops working past a few dozen nodes.** Fitting
-   computes a zoom that makes everything visible, which for a wide or large graph is a
-   zoom nobody can read. A 116-node org chart fits at zoom 0.47, which renders a
-   `font-size: 10` label at 4.6px — under `min-zoomed-font-size`, so Cytoscape draws no
-   labels at all and the user sees grey confetti. The test is `zoom × font-size` in
-   pixels, never a zoom constant. Measure it and decide: fit to a _subset_, start at a
-   fixed readable zoom and let the user pan, or show fewer elements. See "Sizing and
-   readable defaults" below.
+9. **`cy.fit()` on a large graph can leave every label unreadable.** When `zoom × font-size`
+   falls under `min-zoomed-font-size`, Cytoscape draws no labels at all. Gate on that pixel
+   size, never a zoom constant. See "Sizing and readable defaults" below.
```

**Integration tester**

- The description in `agents/vitest-integration-tester.md` covers "frontend components", and the plugin supports React. The body is Svelte-only: `$state` at `:25`, `@testing-library/svelte` at `:38` and `:53`, "all Svelte modules are real" at `:47-48`, and the `$lib/...svelte` imports at `:64-65`. On a React project the agent would look for the wrong package and write the wrong boundary comment.
- The sibling skill `write-vitest-playwright-tests` already covers both frameworks, so this brings the agent in line with it.

```diff
--- a/agents/vitest-integration-tester.md
+++ b/agents/vitest-integration-tester.md
@@ -25 +25 @@
-- Components that read shared state (a `$state` module) and react to its changes
+- Components that read shared state (a `$state` module in Svelte, a store or context in React) and react to its changes
@@ -37,2 +37,2 @@
-1. **Detect the framework.** Run `bash "${CLAUDE_PLUGIN_ROOT}/scripts/detect-test-framework.sh"` to confirm
-   Vitest is present and check for `@testing-library/svelte` and `msw` in devDependencies.
+1. **Detect the framework.** Run `bash "${CLAUDE_PLUGIN_ROOT}/scripts/detect-test-framework.sh"` to confirm
+   Vitest is present and check for `@testing-library/svelte` or `@testing-library/react`, and `msw`, in devDependencies.
@@ -47,2 +47,2 @@
-   > External boundary: network (MSW). Internal: all Svelte modules are real."
+   > External boundary: network (MSW). Internal: all app modules are real."
@@ -53 +53 @@
-   - Render the root component under test using `@testing-library/svelte`
+   - Render the root component under test with the Testing Library package for the project's framework
@@ -59 +59 @@
    ```ts
+   // Svelte example, illustrative. For React, render(<MessageForm ... />) from @testing-library/react.
```

**Low-confidence items**

- `configure-bun-vite-env/SKILL.md:143-150` spreads `ts.configs["recommended-type-checked"]` from `@typescript-eslint/eslint-plugin` into a flat config. I believe that key is the legacy eslintrc shape, and the flat form is `flat/recommended-type-checked`. That comes from my own knowledge of the package, not from this repo, and I did not run ESLint. Check it before changing anything.
- `configure-bun-vite-env/SKILL.md:61` says "`strict: true` ... is non-negotiable" with no reason. That is mild pressure language. The same file's Prettier rule says "single quotes" at `:55`, while its code blocks use double quotes. Pre-commit Prettier probably reformatted them, but the two disagree on the page.
- `make-ui-accessible/SKILL.md:32-34` and `:40` say keyboard access twice, and the ARIA example block restates what the model already knows. This is working redundancy, so I left it out of the diff.

---

I read every `SKILL.md` and agent file in full. For the Cytoscape references, template and README, I only ran a signal scan (emphasis words, version pins, dated phrasing, bundled file paths) and found nothing. `references/*.md` beyond the top of `checklist.md`, `assets/template.html`, `scripts/to-elements.js`, and the five shell scripts were not read line by line. I confirmed that the files `SKILL.md` names exist on disk. I applied no edits, ran no probes, and did not run `validate.py`. Adopting any hunk is a plugin content change, so it needs a PATCH bump in `plugin.json` and `marketplace.json`, a `CHANGELOG.md` entry, a `docs/PLUGIN_VERSIONS.md` row, and a green `validate.py` run.
