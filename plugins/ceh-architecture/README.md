# ceh-architecture

Stack-agnostic architectural standards: maintaining a living architecture document (Mermaid diagrams
plus a Key Decisions log) and domain modeling (identifier formats, status enums, state transitions,
layer boundaries).

REST API design, PostgreSQL schema design, and directory layout are not covered here.

## Skills

| Skill                   | Invoke                                    | Triggers when                                                                                                                                                                    |
| ----------------------- | ----------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `document-architecture` | `/ceh-architecture:document-architecture` | Writing or updating the living `ARCHITECTURE.md` — a 3-second Overview, Mermaid diagrams, plus a Key Decisions log — including when a version re-plan changes the system's shape |
| `domain-modeling`       | `/ceh-architecture:domain-modeling`       | Designing entities, identifier formats, status enums, state transitions, or layer boundaries                                                                                     |

The plugin ships no hooks. Both skills load from their descriptions alone, so nothing is injected
into a session that does not touch these moments.
