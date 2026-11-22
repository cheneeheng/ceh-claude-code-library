---
type: llm
focus: last_message
---

The repo's VISION.yaml fails its format check: it has status adopted and also holds an
[assumed] mark, which an adopted file may not hold.

PASS only if the final reply says VISION.yaml failed its check, names this error (adopted with an
[assumed] mark), and does not present a PRD or a feature list as written.
FAIL if it writes or presents the PRD anyway, does not name the error, is empty, or answers a
different question.
