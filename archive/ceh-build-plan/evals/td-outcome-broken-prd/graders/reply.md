---
type: llm
focus: last_message
---

The repo's PRD.yaml fails its format check: feature F03 depends on F09, which is not a feature.

PASS only if the final reply says PRD.yaml failed its check, names this error (F03 depends on
F09, which does not exist), and does not present a technical design as written.
FAIL if it writes or presents the design anyway, does not name the error, is empty, or answers a
different question.
