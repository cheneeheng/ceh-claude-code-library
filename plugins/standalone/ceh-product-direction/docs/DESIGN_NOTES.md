# ceh-product-direction design notes

## The reader rule

The reason is in `.claude/rules/decision-business-plan-readers.md` in this
library's repo: a business plan turns guesses into dated tests, and a skill that reads it copies
those tests into committed files later sessions treat as binding.

## Schemas

`write-product-requirements` writes `.agents_workspace/product/PRD.yaml` (`prd/v1`) with `PRD.md`
rendered beside it.

A single living `BUSINESS_PLAN.yaml` (`business-plan/v3`, 13 sections: problem, target customer,
value prop, solution, competition, market math, business model, go-to-market, traction,
financials, risks, milestones), revised in place across the loop, with a `pmf_gate` score out of 8. Every skill checks it against its model through `uv` before reading it, and `BUSINESS_PLAN.md`
is rendered from it: Mermaid diagrams sit beside the text they show, every heading carries a
nested number (`§12.01.02`), and a linked contents list opens it, all written by the renderer. The HTML needs Node.js 18+ and
network access (npx fetches `marked`, the page loads Mermaid from a CDN); without them the
markdown is still written and the HTML is skipped. The schema and
the 8-point gate live in `references/business-plan-schema.md`, copied into each of the nine skills.

## Specialist invocation

The other eight are business plan specialists and model-only, with no
slash command and a one-line description: they do not trigger on their own, and
`develop-business-plan` calls the right one.

## Hook wiring

After every write to `BUSINESS_PLAN.yaml`, `VISION.yaml`, `STRATEGY.yaml` or `PRD.yaml`,
`artifact-render-hook.py` (`PostToolUse`) checks it against its model through `uv` and renders its
Markdown, or reports each error back to the agent and leaves the Markdown as it was. An adopted
vision, strategy or PRD that still holds `[assumed]` is one such error. A `PRD.yaml` is found by
its `schema:` line only, so one that has lost that line is not reported. `find-product-market-fit` also carries the architecture
model, to check `.agents_workspace/product/ARCHITECTURE.yaml` before reading it, so the hook acts on a write to that
file too. It also checks and renders `review-business-plan`'s saved review
(`business-plan-review/v3`, one file whose rounds and lens findings later reviews update in place) and `write-investor-materials`' `INVESTOR_DECK.yaml`
(`investor-deck/v2`) and `INVESTOR_OUTREACH.yaml` (`investor-outreach/v2`). `generated-md-guard.py` (`PreToolUse`) denies a direct
edit to a generated Markdown file and names its YAML. Both need `uv`: without it the agent is told
once per session that the file went unchecked. `CEH_ARTIFACT_CHECK=off`, or `CEH_DISABLED_HOOKS`
with `artifact-render-hook` or `generated-md-guard`, switches them off.

## Location history

Since 2026-11-14 this plugin saves and reads product files in `.agents_workspace/product/`.
