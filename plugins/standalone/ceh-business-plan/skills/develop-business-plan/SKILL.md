---
name: develop-business-plan
description: >-
  Load this skill when anything about a business plan comes up: the single entry point that routes
  to the specialist skill for the moment. Trigger on "write a business plan", "validate my product
  idea", "do the numbers work", "run a premortem", "write a pitch deck".
argument-hint: "[plan-or-idea]"
compatibility: >-
  The HTML rebuild needs Node.js 18+ and network access: npx fetches the marked CLI on first run,
  and the page loads Mermaid from a CDN. Without Node or the network, the plan is still written
  and the HTML is skipped. Checking and rendering BUSINESS_PLAN.yaml needs uv; without it the YAML
  is saved unchecked and its Markdown is not rendered.
disable-model-invocation: false
user-invocable: true
license: Apache-2.0
---

# Develop business plan

Route a business-plan request to the one specialist skill that owns its moment, and keep
`BUSINESS_PLAN.yaml` consistent between specialists. This skill owns only the routing and the rules
below. Every interview, test, and section edit belongs to a specialist. Done is the specialist for
this moment has run and the plan's frontmatter agrees with its content.

## Procedure

1. Find the plan: `.agents_workspace/product/business/BUSINESS_PLAN.yaml`, else
   `BUSINESS_PLAN.md` there, else Glob `**/BUSINESS_PLAN.yaml` and `**/BUSINESS_PLAN.md` (schema,
   and what to do with a plan at the old path, in
   `${CLAUDE_SKILL_DIR}/references/business-plan-schema.md`). When several exist, ask which one.
   Check the YAML as the schema's `business-plan/v3` section says, and stop on its errors. A
   Markdown plan with no YAML beside it is moved to the YAML now, as that section says, before
   any specialist runs.
2. No plan exists → first ask one question: "Is this a business now, something you mean to sell,
   share for money or raise for, or a tool you build for your own use?" When the request already
   says which (a pitch deck, a launch, "for myself"), take that answer and do not ask. Business:
   go on. Own use: offer "wait, and write no plan yet" (recommended, because a plan written before
   the product works makes every number a guess) or "write it as a dormant plan, with no
   deadlines". Wait writes nothing and stops. Dormant passes "dormant" in the brief. Then
   Invoke the Skill tool with skill="ceh-business-plan:find-product-market-fit", whatever was
   asked. It drafts from app plans or supplied material before asking anything. When
   the user asked for a different specialist, say in one line that it needs a plan first. The one
   exception: a request to review a plan, deck, or memo the user supplied goes straight to the
   review row.
3. A plan exists → match the request to a row of the routing table and invoke that skill, passing
   the plan's path. When the request names no moment ("continue", "work on my plan"), read the
   frontmatter: `status: draft` or `dormant` routes to the first row, `status: validated` to the
   review row. On a dormant plan, a request routed to `set-operating-plan` or
   `write-investor-materials` stops with one line: the plan is dormant and that skill needs a
   business, so ask whether it is one now.
4. When the specialist returns, re-read the YAML. If `pmf_gate` is below `8` and `status`
   is not `dormant`, set `status: draft`. Set `updated` to today.
5. Render: `uv run --script ${CLAUDE_SKILL_DIR}/scripts/artifact.py render <plan>.yaml`, which
   writes every heading number and the `**Contents**` list, and fix the YAML for each error it
   lists. Without uv, say the Markdown was not rendered.
6. Rebuild the HTML: `node ${CLAUDE_SKILL_DIR}/scripts/build-plan-html.cjs <plan>.md`, which
   writes `BUSINESS_PLAN.html` next to the plan. When Node is missing or the run fails, say so in
   one line and go on: the YAML is the source.
7. Report in one or two lines what changed, the HTML's path, and which specialist the result
   points to next. Invoke it only when the user agrees.

## Routing

| The moment                                                                   | Call                                                                            |
| ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| No plan yet, the gate is below 8/8, or the customer or problem is in doubt   | Invoke the Skill tool with skill="ceh-business-plan:find-product-market-fit"    |
| A verdict is wanted before time or money goes in                             | Invoke the Skill tool with skill="ceh-business-plan:review-business-plan"       |
| The plan cannot say why it wins, what it refuses, or what stops a copy       | Invoke the Skill tool with skill="ceh-business-plan:sharpen-strategy"           |
| The numbers must be believed: price, unit economics, runway, break-even      | Invoke the Skill tool with skill="ceh-business-plan:stress-test-unit-economics" |
| The first customers must be won: channel, launch, acquisition                | Invoke the Skill tool with skill="ceh-business-plan:plan-go-to-market"          |
| A hard-to-undo commitment is near, or the question is what could go wrong    | Invoke the Skill tool with skill="ceh-business-plan:run-premortem"              |
| The plan is agreed and work must start: objectives, owners, the next 90 days | Invoke the Skill tool with skill="ceh-business-plan:set-operating-plan"         |
| Money must be raised: a pitch deck, investor outreach, a fundraising email   | Invoke the Skill tool with skill="ceh-business-plan:write-investor-materials"   |
| The project is not a business yet: make the plan dormant                     | Set `status: dormant` here, and keep every written line                         |
| A dormant project is now a business                                          | Set `status: draft` here, then name the owners of undated tests, one at a time  |

The last two rows change only `status`, so the router runs them itself. After "A dormant project
is now a business", it names as next steps, one at a time, each specialist that owns an undated
test or kill criterion in the plan (`find-product-market-fit`, `run-premortem`,
`plan-go-to-market`, `sharpen-strategy`), because each dates only its own lines.

## Rules

- One specialist per request. Chaining them unasked runs interviews the user did not ask for.
- Do not do a specialist's work here. If this skill starts scoring, interviewing, or editing a
  section, the request was routed wrong. The edits it makes are `status` and `updated` (step 4
  and the two status rows) and step 5's numbers and contents list, which span every
  specialist's subsections, so only the router can keep them in step.
- When a specialist stops on a missing input (no price, no ranked risks, no named customer), it
  names the skill that supplies it. Offer that skill as the next step.
- The status rule in step 4 runs after every specialist, because several of them re-score
  `pmf_gate` and only `find-product-market-fit` sets `status`, to `validated` when the gate
  passes, apart from the router's status rows.
- **No human to answer** (a headless run, or called by another agent): when several plans exist,
  take the most recently updated and say which. The specialist drafts and revises from what exists,
  asks nothing, and ends with the questions it would have asked, in order, each with the assumption
  it used instead. Report the next specialist without invoking it.
- With no human to answer, when no plan exists and the request does not say whether the project
  is a business, draft a `draft` plan, as before, and end with that question.

## Stop conditions

- The request is for the app's technical plan or architecture → say this plugin owns the business
  plan only and name `ceh-build-plan`.
