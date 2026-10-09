---
name: stress-test-plan
description: >-
  Load this skill when a plan, design, strategy, or roadmap should be questioned before anyone acts
  on it: ask every open question in rounds, only once its prerequisites are settled, each with a
  recommended answer a plain "yes" accepts, and fetch facts with a subagent instead of asking.
  Trigger on "grill me on this plan", "stress-test this", "poke holes in this", "what am I
  missing", "challenge this design". Not for questions to someone outside the session (use
  ceh-every-session:write-questionnaire).
argument-hint: "[plan-file]"
disable-model-invocation: false
user-invocable: true
license: Apache-2.0
---

# Stress-test a plan

Question a plan until every decision it rests on is either settled or named as open, and write the
answers back into the plan. Works on any plan: a code change, a product roadmap, a business
strategy, a document outline. Done means no question remains whose prerequisites are settled, or
the user ends the session, and the plan records the outcome.

## Procedure

1. **Read the plan**: the file given, otherwise the plan in the conversation. If there is no plan,
   stop and say so: this skill tests a plan, it does not write one.
2. **List the questions.** Every decision the plan makes without a stated reason, every assumption
   it does not test, every choice it leaves open, and the riskiest one: "what would make this
   fail?". For each, note which other questions must be settled first.
3. **Split facts from decisions.** A question the files, the code, or the web can answer is a
   fact. Send facts to a subagent (Agent tool, `Explore` for local files, `general-purpose` for the
   web), several in parallel, and fold the answers in. The user is asked only what only the user
   can decide.
4. **Ask a round.** Take the decision questions whose prerequisites are all settled, at most four,
   most consequential first, and ask them with `AskUserQuestion`. Each question carries a
   recommended option, listed first and marked "(Recommended)", with its reason in the
   description. "Yes", "go with your recommendations", or no objection accepts every recommendation
   in the round.
5. **Update and repeat.** Record each answer, cross off what it settles, add the questions it
   unlocks, and ask the next round. Stop when no question is ready, or when the user says enough.
6. **Write the outcome back.** Add or update a `## Decisions` section in the plan file: each
   settled question with its answer and one-line reason, then `## Open` for what is left. With no
   plan file, put the same two sections in your reply.

## Rules

- One decision per question. "Should we use X, and how should Y work?" is two.
- Every question earns its place by changing the plan. Drop a question whose every answer leads
  to the same next step.
- Recommend, do not survey. Give the option you would pick and why, not a neutral list.
- Ask nothing already settled in the plan, the conversation, or a recorded decision, unless a
  fact found in step 3 contradicts it. Then that contradiction is the question.
- With no human to answer (a subagent, a headless run), take every recommendation, record each as
  assumed rather than decided, and list them first under `## Open`.

## Output

```markdown
## Decisions

- <Question> — <answer>. <One-line reason.>

## Open

- <Question> — assumed <recommendation>, not confirmed | blocked on <prerequisite>
```
