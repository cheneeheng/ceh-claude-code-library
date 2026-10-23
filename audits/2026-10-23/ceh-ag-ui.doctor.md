1. **Scope and target** · _assumed_
   All of `plugins/standalone/ceh-ag-ui`: 5 `SKILL.md` files, `README.md`, `plugin.json`, `tuning.json`, and the prompt text and request code in `agent-server/main.py`. The target model is Claude Sonnet 5.5, since no file pins a model and `tuning.json` has `"pinned": {}`.
2. **Findings** · _inferred_
   Nothing at high or medium confidence. One low-confidence flag, and Group 4 request config is clean.
3. **Proposed diff** · _done_
   Empty. The surface is clean, so the audit proposes no change.
4. **Stale-fact check** · _verified_
   Every path, symbol and command I checked in the skills resolves in the repository.
5. **Not checked** · _unverified_
   No behavioural probes were run, and `git blame` provenance was not pulled.

---

**Findings**

- **Group 1, dated prompt text:** zero matches.
  - The skills use no pressure language, no "think step by step" scaffolds, no step-by-step scripts for judgment work and no grader vocabulary. I read all five `SKILL.md` files in full.
  - The prohibitions each carry a reason or encode a contract. Examples are "never run them" (the canvas owns frontend tools), the styling lock, and "answer every tool call in one user turn" (the API rejects splits). The keep list protects these.
- **Group 2, brittle configuration:** zero matches.
  - No two instruction files disagree. Step-count references match (the "five checks in step 3" and "three checks in step 5" claims line up with the bodies).
  - Version pins in the `compatibility` fields (`anthropic 1.9+`, `ag-ui-protocol 1.0`, `zod 4`) are real requirements. `pyproject.toml` matches the `anthropic>=1.9` pin.
- **Group 3, tool descriptions:** zero matches. The example description in `add-canvas-component` ("use show_table for records without an order") names the nearest neighbour, which is the form the rubric asks for.
- **Group 4, request config:** `main.py` is current for Sonnet 5.5, and the target-model reading is consistent with `tuning.json` (`audit-model: sonnet-5-5`, last audited 2026-10-15).
  - It sets `claude-opus-5-5`, streaming, `max_tokens=64000`, explicit `effort: "medium"`, `fallbacks="default"` with the `server-side-fallback-2026-07-01` beta, and no `thinking` field, `budget_tokens`, sampling parameters, prefill or forced `tool_choice`.
  - It appends to a per-thread transcript and never rewrites history, which suits the preserved-thinking check.
  - The system prompt is a static string with no timestamps, so cache ordering is fine. The server makes one model call per loop turn and has no deterministic step to move into code.
- **Low-confidence flag, no edit:** `agent-server/main.py:39-41` says "keep any text to a sentence or two around it".
  - Pattern: Group 1f, a numeric-style output ceiling. Confidence: low.
  - It is qualitative, and it serves a real layout constraint (text sits beside a placed component). I left it alone. If replies read too clipped on a real run, re-express it as "text only frames the component".

**Stale-fact check**

- **Resolved:** `web/src/brand.css` (created at step 2, so its absence from the template is expected), `tidewater/brand.css` and `meridian/brand.css` in `ceh-ui-design`, the `typecheck` script, and the `AGENT_ORIGIN` proxy on `/agent`.
- **Also resolved:** `MAX_TOOL_ROUNDS = 5`, `abortRun`, `useMemo` and `safeParse` in `useAgent.ts`, and `Thread`, `held`, `awaiting`, `THREADS` and `eager_input_streaming` in `main.py`.
- **Not confirmed on its own:** `echoable()` in `main.py`. My grep counted 15 matches across several terms but did not isolate it.

---

I did not run the template or the mock agent, so nothing here shows the skills' runtime behaviour. Nothing was edited, and I did not touch the working tree.
