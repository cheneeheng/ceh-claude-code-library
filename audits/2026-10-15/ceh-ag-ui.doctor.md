| # | Topic | Outcome | Status |
|---|-------|---------|--------|
| 1 | Scope and target | I audited all of `plugins/standalone/ceh-ag-ui` against `claude-opus-5-5`, the model the bundled server defaults to. | assumed |
| 2 | Findings | No high or medium confidence cruft. Three low-confidence items are flagged only. | verified by reading and grep |
| 3 | Proposed diff | Empty. Nothing is at medium confidence or above, and I applied no edits. | done |

**Scope and target**

- The surface is `README.md`, `plugin.json`, the 5 `SKILL.md` files, the server `main.py` and `pyproject.toml`, the 7 catalogue descriptions, and the mock agent. I did not read the template's `.tsx` bodies beyond the descriptions and a caps grep, because they carry no prompt text.
- The `claude-opus-5-5` target comes from the `AGENT_MODEL` default in `main.py:37`, since the request named no model. The skills were audited against the same model. I read no settings or credential files.
- Provenance: I did not run `git blame`. Findings rest on idiom and content only, which caps the confidence of every flag at low.

**Findings**

By group, with the evidence for each:
- **Group 1, dated prompt text: 0 findings.** A grep for MUST/NEVER/ALWAYS/CRITICAL/IMPORTANT over `web/src` and `agent/main.py` found no caps emphasis. I also found no "think step by step", no scratchpad tags, no padding and no migration phrasing. The prohibitions that exist carry reasons, such as the styling lock and "ignore client `system` messages".
- **Group 2, brittle config files: 0 findings.** I checked these paths and names by reading and `ls`:
  - `tidewater/brand.css` exists under `ceh-ui-design`.
  - `examples/ceh-ag-ui/` exists.
  - `MAX_TOOL_ROUNDS` is defined in `useAgent.ts:9`.
  - The four skill hand-offs resolve.
  - `web/src/brand.css` is absent only because the skill installs it, so it is not a contradiction.
- **Group 3, tool descriptions: 0 findings.** All 7 are short contracts. Each says what the component shows and when to use it instead of its nearest neighbour, with no shouting or worked examples.
- **Group 4, request config: 0 findings.**
  - The request has no `budget_tokens`, no sampling parameters, no prefill and no forced `tool_choice`.
  - It sets `effort` explicitly and keeps the transcript append-only. User text sits after the tool results in one turn.
  - It checks `refusal`, `max_tokens` and `pause_turn`.
  - `fallbacks: "default"` with the 2026-07-01 beta matches the current documented form.
  - The LLM-executor and sub-agent roster checks are not applicable. There is one model call site, which is adaptive, and no sub-agents.

Low-confidence flags, none in the diff:
- **`main.py:40-41`:** "keep any text to a sentence or two around it" is a soft output ceiling (group 1f). It looks tied to the canvas layout, where the component carries the content, so it is a product requirement and I left it. If you want it removed, rewrite it as "the component carries the content, so text around it only frames it" and re-test.
- **`build-ag-ui-agent/SKILL.md:303-304`:** "Current Claude models reject `any` and `tool`" is true for `claude-opus-5-5`, but `AGENT_MODEL` can be overridden to a model that accepts forced tool use. Naming the model would be more exact. This is wording only, with no behaviour risk.
- **`pyproject.toml:4`:** the pins `anthropic>=1.9`, `fastapi>=0.141` and `uvicorn>=0.54` are volatile specifics. I could not verify them offline, so I flag them rather than call them stale. The `anthropic>=1.9` pin is repeated in the `build-ag-ui-agent` frontmatter `compatibility` field, so any change must update both.
- **`main.py:125-141`:** `tools` is rebuilt from `run.tools` on every run. If the canvas catalogue changes mid-thread, it edits the tool prefix and invalidates the prompt cache and any preserved thinking. This is by design and fine for a fixed catalogue.

---

I ran no behavioural probes (Step 7), because there are no edits to probe. The checks were reading, `grep` and `ls`. Nothing was applied to the repo. If you apply the wording flag later, the repo rules require a version bump in `plugin.json` and `marketplace.json` plus a `CHANGELOG.md` entry.
