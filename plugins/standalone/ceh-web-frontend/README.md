# ceh-web-frontend

Engineering standards for the **Bun + Vite** web stack, **SvelteKit and React** in one plugin. The
framework skills load by file type (`write-sveltekit-code` on `.svelte`, `write-react-vite-code`
on `.tsx`), so they live side by side without firing on the wrong project. The shared standards
(TypeScript style, accessibility, testing, tooling) exist once for both. It also covers Cytoscape.js
graph views, screenshot checks that a restyle changed nothing it should not, and agents that write
unit, integration and end-to-end tests.

## Install

See [Getting started](../../../docs/GETTING_STARTED.md). It installs `ceh-testing` and
`ceh-ui-design` with it, because the plugin depends on both. The tester agents and
`write-vitest-playwright-tests` use `ceh-testing:design-test-cases` on every run, and UI visual
design (layout, hierarchy, navigation, theming) comes from `ceh-ui-design:design-ui`.

The tester agents run `bash` scripts, and the end-to-end tests need Playwright's browser, for
example through `bunx playwright install chromium`.

## Skills

| Skill                           | Say or type                                                                                               | What it does                                                                                                                                                                                                                                                                                                                                 |
| ------------------------------- | --------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `configure-bun-vite-env`        | Loads by itself on a bun command, or when `eslint.config.js`, `.prettierrc` or `tsconfig.json` is written | Bun and Vite setup, scripts, dependencies, TypeScript style, ESLint and Prettier, and type config.                                                                                                                                                                                                                                           |
| `write-sveltekit-code`          | Loads by itself when a SvelteKit route, load function, shared `.svelte.ts` state or component is written  | SvelteKit routes, Svelte 5 runes for shared state, components, and the API client.                                                                                                                                                                                                                                                           |
| `write-react-vite-code`         | Loads by itself when a `.tsx` file or `vite.config.ts` is written                                         | React components, hooks, React Router, state, data fetching, and Vite env vars.                                                                                                                                                                                                                                                              |
| `write-vitest-playwright-tests` | Loads by itself when a `.test.ts`, `.test.tsx` or `.spec.ts` file is written                              | Vitest, Testing Library, MSW handlers, and Playwright tests.                                                                                                                                                                                                                                                                                 |
| `make-ui-accessible`            | Loads by itself when component markup is written, in Svelte or React                                      | Accessible markup for interactive elements, images, forms, and navigation.                                                                                                                                                                                                                                                                   |
| `visualize-graph-cytoscape`     | "visualize this graph", "draw a network", `/ceh-web-frontend:visualize-graph-cytoscape`                   | Builds a clickable node-link view with Cytoscape.js (a network, dependency map, org chart or knowledge graph): layout by graph shape, real data turned into elements JSON, stylesheet, tap-to-highlight, readable zoom defaults, and when a node-link diagram is the wrong tool. It comes with a working HTML template and a data converter. |
| `check-visual-parity`           | "make sure it looks the same", "pixel parity", `/ceh-web-frontend:check-visual-parity`                    | For a migration, CSS refactor or restyle that must not change the look outside the intended areas: Playwright screenshots of the old version as the baseline, the new version compared against them, and every difference explained. The report has one row per screen.                                                                      |

## Agents

| Agent                       | What it does                                                                                                                                                                                      |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `vitest-unit-tester`        | Writes and runs isolated unit tests for TypeScript functions or modules. Ask for "add unit tests" or "cover this module".                                                                         |
| `vitest-integration-tester` | Tests components wired with real shared state and MSW network handlers, such as a form or data-loading flow.                                                                                      |
| `playwright-system-tester`  | Writes Playwright end-to-end or smoke tests against a running stack. It runs only when you ask, because it starts real infrastructure. It refuses everything but a smoke test against production. |
| `web-frontend-reviewer`     | Reviews the frontend files of a large diff in parallel, when `ceh-git-workflow:write-code-review` dispatches it. Every finding quotes its `path:line`. It never edits.                            |

The three testers load `ceh-web-frontend:write-vitest-playwright-tests` and
`ceh-testing:design-test-cases` first. `web-frontend-reviewer` loads only the skills whose files
the diff touches.

## Hooks

This plugin has no hooks.

## Settings

Set a variable under `env` in a Claude Code settings file. The
[environment variables page](../../../docs/ENVIRONMENT_VARIABLES.md) shows which file and how to
undo it.

These are variables of the app under test, which the end-to-end script reads. They are not plugin
switches.

| Variable                   | Default | Effect                                                                                                                   |
| -------------------------- | ------- | ------------------------------------------------------------------------------------------------------------------------ |
| `E2E_BASE_URL`, `BASE_URL` | unset   | Target of the end-to-end run (`E2E_BASE_URL` wins). A URL that looks like production is refused for anything but `smoke` |
| `NODE_ENV`                 | unset   | `production` refuses any end-to-end run but `smoke`, the same guard as a production-looking URL                          |

## How it works

### Coverage floor

70% for `src/lib/`, a floor for finding blind spots rather than a goal. Below it, look for the
untested regions.

## Not this plugin

- UI visual design (layout, hierarchy, navigation, theming): `ceh-ui-design:design-ui`.
- A fixed diagram rather than an interactive graph: Mermaid, not `visualize-graph-cytoscape`.
- Choosing which test cases to write: `ceh-testing:design-test-cases`.

## Where its files live

This plugin saves no files of its own. `check-visual-parity` has you commit its baseline
screenshots with the Playwright spec in your project.
