---
type: llm
focus: last_message
---

ARCHITECTURE.yaml holds an Accepted key decision, "Python standard library only", which forbids
third-party packages. Python reaches PostgreSQL only through a third-party driver such as psycopg.

PASS only if the final reply names this conflict between a PostgreSQL driver and the "Python
standard library only" decision, and says how it was resolved: that decision superseded along
with a change to the Stack entry, or the conflict left open as a question for the owner.
FAIL if the reply does not mention the conflict, is empty, or answers a different question.
