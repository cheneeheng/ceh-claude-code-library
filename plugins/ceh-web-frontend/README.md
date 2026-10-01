# ceh-web-frontend

Engineering standards for the **Bun + Vite** web stack, **SvelteKit and React** in one plugin.
Framework skills trigger on file type (`write-sveltekit-code` on `.svelte`, `write-react-vite-code`
on `.tsx`), so they coexist without mis-firing, while shared standards (TypeScript style,
accessibility, testing, tooling) stay single-sourced.

## Skills

| Skill                           | Invoke                                            | Triggers when                                                                                                                                                                                                                                                                              |
| ------------------------------- | ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `configure-bun-vite-env`        | `/ceh-web-frontend:configure-bun-vite-env`        | Bun/Vite setup, scripts, deps, TypeScript style, ESLint/Prettier, type config                                                                                                                                                                                                              |
| `write-sveltekit-code`          | `/ceh-web-frontend:write-sveltekit-code`          | Editing Svelte routes, shared `.svelte.ts` state, components, or the API client                                                                                                                                                                                                            |
| `write-react-vite-code`         | `/ceh-web-frontend:write-react-vite-code`         | Editing React components, hooks, routing, or `vite.config.ts`                                                                                                                                                                                                                              |
| `write-vitest-playwright-tests` | `/ceh-web-frontend:write-vitest-playwright-tests` | Writing `.test.ts`, `.test.tsx`, or `.spec.ts` files, or MSW handlers                                                                                                                                                                                                                      |
| `make-ui-accessible`            | `/ceh-web-frontend:make-ui-accessible`            | Writing component markup (Svelte or React)                                                                                                                                                                                                                                                 |
| `design-ui`                     | `/ceh-web-frontend:design-ui`                     | Any frontend UI visual design decision: layout archetypes, hierarchy, navigation placement, empty/loading/error states, density, finishing recipes (command dock, humanized tables, lifecycle steppers), plus theming from bundled token-driven templates (Meridian, Tidewater)            |
| `visualize-graph-cytoscape`     | `/ceh-web-frontend:visualize-graph-cytoscape`     | Building a network, dependency map, org chart, knowledge graph, or any clickable node-link diagram with Cytoscape.js: layout by graph shape, converting real data into elements JSON, stylesheet, tap-to-highlight, readable zoom defaults, and when a node-link diagram is the wrong tool |

`design-ui` bundles two themes under `references/` (`meridian/` and `tidewater/`, each a
`brand.css` plus a `brand-guide.html`). `visualize-graph-cytoscape` bundles a working
`assets/template.html`, a `scripts/to-elements.js` data converter, and eight reference files.

The plugin ships no hooks. The skills load from their descriptions alone, so nothing is injected into
a session that does not touch these moments. If `make-ui-accessible` is observed to under-trigger on
implicit mid-turn decisions, sharpen its description rather than add a hook.

## Agents

| Agent                       | Use when                                                                 |
| --------------------------- | ------------------------------------------------------------------------ |
| `vitest-unit-tester`        | Writing isolated unit tests for TypeScript functions or modules          |
| `vitest-integration-tester` | Testing components wired with real shared state and MSW network handlers |
| `playwright-system-tester`  | Writing Playwright E2E tests or smoke tests against a running stack      |

All three preload `ceh-web-frontend:write-vitest-playwright-tests` and
`ceh-testing:design-test-cases`.

## Scripts

Called by the tester agents via `bash "${CLAUDE_PLUGIN_ROOT}/scripts/<name>.sh"`.

| Script                                         | Purpose                                              |
| ---------------------------------------------- | ---------------------------------------------------- |
| `detect-test-framework.sh [root]`              | Detects Jest / Vitest / Mocha + Playwright / Cypress |
| `run-unit-tests.sh [file]`                     | Runs unit tests with the detected runner             |
| `check-coverage.sh <file>`                     | Prints the coverage line for a specific source file  |
| `run-integration-tests.sh [pattern]`           | Runs integration tests with `NODE_ENV=test`          |
| `run-e2e.sh {up\|down\|test\|smoke} [pattern]` | Manages the E2E stack and runs Playwright / Cypress  |

## Coverage floor

70% for `src/lib/`, a floor for finding blind spots rather than a goal. Below it, run
`check-coverage.sh` and look for the untested regions.

## Dependencies

The tester agents preload `ceh-testing:design-test-cases` and `write-vitest-playwright-tests` invokes
it on every run, so the plugin declares `ceh-testing` as a dependency and Claude Code installs it
automatically.
