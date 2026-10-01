# ceh-architecture

Stack-agnostic architectural standards: maintaining a living architecture document (Mermaid diagrams
plus a Key Decisions log) and domain modeling (identifier formats, status enums, state transitions,
layer boundaries).

REST API design, PostgreSQL schema design, and directory layout are not covered here.

## Skills

| Skill                   | Invoke                       | Triggers when                                                                                                                                                                    |
| ----------------------- | ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `document-architecture` | Model-only, no slash command | Writing or updating the living `ARCHITECTURE.md` — a 3-second Overview, Mermaid diagrams, plus a Key Decisions log — including when a version re-plan changes the system's shape |
| `domain-modeling`       | Model-only, no slash command | Designing entities, identifier formats, status enums, state transitions, or layer boundaries                                                                                     |

## Hooks

This plugin ships a `SessionStart` hook (`hooks/hooks.json` → `scripts/load-invariants.sh`) that
injects the **architecture invariants** as always-on context. It fires on the `startup`, `clear`,
and `compact` events and activates automatically when the plugin is enabled — no global
`settings.json` change required. The script is plain `bash` with a static payload and needs no other
runtime.

**Why a hook and not just skills:** the load-bearing rules here (prefixed IDs, closed status enums,
immutable identifiers, layer boundaries) are _invariants_ — they must hold for every relevant change.
But skill auto-loading is evaluated against the user's prompt at the start of a turn, so a skill that
triggers on an implicit mid-turn decision ("deciding where a file belongs", "defining an entity ID")
reliably under-fires. The hook injects a compact version of these invariants every session so they
always apply; the skills remain the on-demand reference for the full patterns and code. Each line in
the injected block is tagged with the skill (e.g. `[domain-modeling]`) that documents it in depth.

The layer-boundary invariants assume a route handler, service, and database layering. In a project
without that shape (a CLI, a library) they are noise: install this plugin per project rather than
at user scope there.
