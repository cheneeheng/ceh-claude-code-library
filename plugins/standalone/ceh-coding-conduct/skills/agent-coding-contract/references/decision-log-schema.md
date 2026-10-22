# Decision log schema

The append-only log `agent-coding-contract` keeps at `.agents_workspace/DECISION_LOG.md`, unless the
project `CLAUDE.md` names another path. A new log is a copy of `../assets/decision-log.template.md`,
relative to this file. The `schema: decision-log/v1` line stays as written.

## Entries

Each entry goes below the last, and no entry is edited or removed.

- **Heading:** `### Entry <ID>`, IDs counting up from 1: the last entry's ID plus one.
- **Type:** `Decision`.
- **Mode:** `Autonomous`.
- **Timestamp:** ISO-8601.
- **Task:** a brief description of the task.
- **Context:** what was ambiguous, or why a choice was needed.
- **Decision:** what was chosen and why.
- **Impact / Risk:** potential side effects.
- **Outcome:** the observed result, if there is one yet.
