---
type: llm
focus: last_message
---

PASS only if the final reply does all of these:

1. Gives the path of ARCHITECTURE.yaml.
2. Lists each technical design entry by its topic.
3. Lists each diagram drawn.
4. Gives a result for each of the six tests: Shared, Options, Exact, Covers, Qualities,
   Consistent.
5. Lists the answers it assumed for the owner's questions.

FAIL if any is missing, if the reply is empty, or if it answers a different question.
