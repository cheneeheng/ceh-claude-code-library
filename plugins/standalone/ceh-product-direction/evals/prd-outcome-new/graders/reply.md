---
type: llm
focus: last_message
---

PASS only if the final reply does all of these:

1. Gives the path of PRD.yaml and says its status is draft.
2. Shows the features with each one's id, name, status and dependencies.
3. Gives a result for each of the six tests: Observable, Checkable, One plan, Traces, Refuses,
   Clean.
4. Lists questions for the owner, each with a recommended or assumed answer.

FAIL if any is missing, if it says the file is adopted, if the reply is empty, or if it answers a
different question.
