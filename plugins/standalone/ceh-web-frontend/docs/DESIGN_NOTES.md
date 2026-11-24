# ceh-web-frontend design notes

Maintainer detail moved out of the plugin README, word for word.

## Bundled files

`visualize-graph-cytoscape` bundles a working `assets/template.html`, a `scripts/to-elements.js`
data converter, and six reference files.

## No hooks

The plugin ships no hooks. The skills load from their descriptions alone, so nothing is injected into
a session that does not touch these moments. If `make-ui-accessible` is observed to under-trigger on
implicit mid-turn decisions, sharpen its description rather than add a hook.

## Scripts

Called by the tester agents via `bash "${CLAUDE_PLUGIN_ROOT}/scripts/<name>.sh"`.

| Script                                         | Purpose                                              |
| ---------------------------------------------- | ---------------------------------------------------- |
| `detect-test-framework.sh [root]`              | Detects Jest / Vitest / Mocha + Playwright / Cypress |
| `run-unit-tests.sh [file]`                     | Runs unit tests with the detected runner             |
| `check-coverage.sh <file>`                     | Prints the coverage line for a specific source file  |
| `run-integration-tests.sh [pattern]`           | Runs integration tests with `NODE_ENV=test`          |
| `run-e2e.sh {up\|down\|test\|smoke} [pattern]` | Manages the E2E stack and runs Playwright / Cypress  |

Below the coverage floor, run `check-coverage.sh` and look for the untested regions.

## Dependencies

The tester agents preload `ceh-testing:design-test-cases` and `write-vitest-playwright-tests` invokes
it on every run, so the plugin declares `ceh-testing` as a dependency and Claude Code installs it
automatically.

`ceh-ui-design` is a dependency by deliberate exception: no skill here invokes it on every run.
`design-ui` lived in this plugin until 1.1.0, and the dependency keeps it installed for everyone
who installs the web stack.
