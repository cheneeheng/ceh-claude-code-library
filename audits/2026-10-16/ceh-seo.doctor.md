| # | Topic | Outcome | Status |
| --- | --- | --- | --- |
| 1 | Scope and target model | I audited all 5 files in `plugins/standalone/ceh-seo` (3 `SKILL.md` files, `README.md`, `plugin.json`) against Sonnet 5.5, the model running this audit. | assumed |
| 2 | Findings | No finding reaches medium or high confidence. All four groups come back zero or not applicable. | inferred |
| 3 | Flagged items | Two low-confidence items are flagged with no edit proposed. | unverified |
| 4 | Proposed diff | The diff is empty, so nothing changes. | done |
| 5 | Provenance | I did not run `git blame`, so I could not date any line to a model era. | couldn't do it |

**Scope and target model**

- I audited only the plugin directory, so no user-level configuration files were in scope or skipped.
- I did not read `plugins/CLAUDE.md`, the repo's skill-authoring rules. The audit therefore did not check these files against those conventions.

**Findings**

- Group 1 (dated prompt text) has zero matches. The all-caps emphasis words (`MUST`, `NEVER`, `CRITICAL`) and the "think step by step" idioms I scanned for are absent. The `Rules` sections give a reason beside most prohibitions. I read all of them, and the only two bare ones, "no keyword stuffing" and "no different pitches", still earn their place.
- Group 2 (brittle files) has zero findings. Every cross-plugin reference resolves. `ceh-blog`, `ceh-documentation`, and the `ceh-git-workflow:update-readme` skill listed in this session all exist, as does `ceh-seo:write-llms-txt`. I confirmed `product/BUSINESS_PLAN.md` and `product/EVIDENCE.md` against `docs/STRATEGY.md:46-61`. I checked them by `ls` and `grep`.
- Groups 3 and 4 do not apply. There are no tool definitions or request code. The numbered procedures are fine to keep, since order matters in them. The GEO block copied between two skills is registered in `docs/CROSS_REFERENCES.md:192-206`, and it agrees in both places, so it stays.

**Flagged items**

- `make-page-crawlable/SKILL.md:104-105` says "Most AI crawlers do not execute JavaScript". This is a time-sensitive claim with no verification date, so it is low confidence. I did not verify it and made no web search. If you want the audit to settle it, re-check which crawlers render JavaScript today. Otherwise date the claim, or phrase it as "do not assume a crawler runs JavaScript".
- `make-page-crawlable/SKILL.md:67-74` gives title ≤ 60, description ≤ 155, and a 1200×630 image. These are folk limits, not model-dependent text, so they are not a prompt-audit finding. Search engines actually truncate by pixel width, so treat them as heuristics.

**Provenance**

- The `git blame` call was blocked because it needed a `cd` into the repo. Run `git blame plugins/standalone/ceh-seo/skills/*/SKILL.md` if you want the provenance pass. It could only raise findings, and no line in these files currently looks like a fossil.

---

I made no edits. The checks I ran were reads, plus an `ls` of `plugins/standalone/` and a `grep` of `docs/STRATEGY.md` and `docs/CROSS_REFERENCES.md`.
