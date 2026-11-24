# ceh-python-service design notes

## Why the plugin ships no hooks

The plugin ships no hooks. The skills load from their descriptions alone, so nothing is injected into
a session that does not touch these moments. The cross-cutting rules (logging, metrics, CORS, rate
limiting, secrets, entity IDs) ride on the skills that load on most service work, because their own
moments occur too rarely to load a skill of their own. If one is observed to under-trigger on
implicit mid-turn decisions, sharpen the host skill's description rather than add a hook.

## How the agents call the scripts

Called by the tester agents via `bash "${CLAUDE_PLUGIN_ROOT}/scripts/<name>.sh"`.
