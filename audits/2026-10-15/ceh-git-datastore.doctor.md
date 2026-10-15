| # | Topic | Outcome | Status |
|---|-------|---------|--------|
| 1 | Scope and target model | Scope is `plugins/standalone/ceh-git-datastore`: 2 SKILL.md files, README, plugin.json, 8 reference files, `docs/git-datastore.md`, 4 scripts. Target model is Claude Opus 5.5, the model I'm running as a coding agent. | assumed |
| 2 | Dated prompt text (Group 1) | No pressure language, no scaffolds replaced by API features, no step-by-step choreography, no retired-model workarounds. The prohibitions in the Anti-patterns lists each carry a reason. | inferred |
| 3 | Brittle skill files (Group 2) | No high or medium findings. Every cross-plugin name and script subcommand I checked still resolves. Two low-confidence flags: the unversioned benchmark numbers and the "observed on a realistic test store" claim. | verified for references, inferred otherwise |
| 4 | Tool descriptions and request config (Groups 3 and 4) | Not applicable. The plugin defines no tools and no request-building code. | done |
| 5 | Proposed diff | Empty. | done |

**Scope and target model**

- This is non-interactive, so I assumed the whole plugin directory is in scope. I skipped files outside it, such as `plugins/CLAUDE.md` and the root `CLAUDE.md`, except where I read them to check for conflicts.
- Cruft is relative to a model. I used Opus 5.5 because the plugin names no target model and its files are read by the coding agent.

**Dated prompt text**

- A grep for `MUST|NEVER|ALWAYS|CRITICAL|IMPORTANT|try to|if possible|think step|scratchpad|STEP \d|Remember,|no longer` and for retired model names found nothing that steers behavior. The only hits were the word "no longer" in two prose sentences.
- The gate table, the five rules and the anti-patterns state their reasons next to each constraint, so they are context. "Bare repo, never a working tree" and "pin the base commit before the CAS" are fragile operations where exact wording belongs.

**Brittle skill files**

- The first flag is low confidence, action `flag`, at `skills/build-git-datastore/SKILL.md:105-115` and `skills/migrate-git-datastore/SKILL.md:56`. The text is "From `scripts/gitstore.py` on an ordinary container ... ~17 ms" and "~220 ms". These numbers carry no date, hardware or git version, so they will rot. They also feed the gate thresholds ("under ~10/sec"). I left them out of the diff because they are context the reader needs, not a dated instruction. Adding a measured-on line would be the fix.
- The second flag is also low confidence, `flag`. `skills/migrate-git-datastore/SKILL.md:162` ("Each of these was observed on a realistic test store") and `skills/build-git-datastore/SKILL.md:151` ("Tested for concurrency, atomicity, and lost updates") are claims no file in the plugin backs up. I did not look for a test file, so I can't say whether they hold. They are provenance claims, not instructions, so removing them gains nothing.
- The README repeats the skills' trigger phrases and a gate summary. The copies agree with the skills, so this is working redundancy and I left it alone.

**Proposed diff**

- No hunks. A surface with no high or medium findings should change nothing.

---

I did not read `references/*.md`, `docs/git-datastore.md` or the script bodies in full. I only grepped them for the signals and checked the CLI subcommands and flags in `scripts/*.py`, so a reference-file finding is possible. I checked these cross-plugin names and CLI subcommands and flags and they all resolve:
- `ceh-python-service:write-postgresql-code`
- `ceh-codebase-explanation:document-architecture`
- `gitexport.py inventory|infer|export|changed` with `--dialect`
- `verify.py --unnest`
- `sync.py setup|bundle|push|status|daemon|restore`
- `gitstore.py init`

I ran no behavioral probes, because there is nothing to remove.
