# Saved file names

A file or folder a skill saves takes one of three name forms, by how it behaves. The time comes
from one `date +%Y%m%d-%H%M%S` call when the file is first saved and never changes on later edits.

- **Written once** (a handoff, an audit, an eval, an experiment run, a retro):
  `<YYYYMMDD-HHMMSS>-<session-id>-<name>`, with the whole session id (`${CLAUDE_SESSION_ID}` in a
  skill body, the placeholder `<session-id>` everywhere else). A folder with nothing else to say
  stops after the session id.
- **Edited in place** (a plan, a fix record, every saved review, including a stress test saved
  without a plan file): `<YYYYMMDD-HHMMSS>-<name>`, with no session id.
- **Singleton** (a file found by a fixed name, such as `ARCHITECTURE.yaml`, `VISION.yaml`,
  `BACKLOG.md` or `CODEBASE_EXPLAINED.md`, or a per-target file regenerated in place, such as a
  competitor report): no time prefix.

Every other dated file keeps the form it has until a plan moves it. A file already saved under an
older form keeps its name, and every reader and hook accepts both forms. Two names are exempt: a
blog draft, `<YYYY-MM-DD>-<slug>`, because the date is the post's, and the model-audit folder,
`.agents_workspace/product/audit/model/<date>/`, because its script also runs in CI, where there
is no session. A date inside a file (`saved`, `date`, a Record line) keeps its own format.

Why: one form sorts by time in any folder, and a second run never overwrites the first. The
session id traces a file written once to the transcript that wrote it. A file several sessions
edit in place has no one transcript, so its creating session's id would mislead (decided
2026-11-17).
