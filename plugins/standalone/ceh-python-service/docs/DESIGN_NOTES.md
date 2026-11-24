# ceh-python-service design notes

Maintainer detail moved out of the plugin README on 2026-11-24, when the README was rewritten for
the person installing the plugin. The site does not publish this file.

## Why the plugin ships no hooks

The plugin ships no hooks. The skills load from their descriptions alone, so nothing is injected into
a session that does not touch these moments. The cross-cutting rules (logging, metrics, CORS, rate
limiting, secrets, entity IDs) ride on the skills that load on most service work, because their own
moments occur too rarely to load a skill of their own. If one is observed to under-trigger on
implicit mid-turn decisions, sharpen the host skill's description rather than add a hook.

## How the agents call the scripts

Called by the tester agents via `bash "${CLAUDE_PLUGIN_ROOT}/scripts/<name>.sh"`.

The testers run the suites through the plugin's scripts:

| Script                                     | Usage                                                |
| ------------------------------------------ | ---------------------------------------------------- |
| `run-unit-tests.sh [path]`                 | Run unit tests only (excludes integration/system)    |
| `run-integration-tests.sh [path]`          | Run integration tests (requires `TEST_DATABASE_URL`) |
| `run-system-tests.sh [path] [--no-docker]` | Run system tests with optional Docker orchestration  |
