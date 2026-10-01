# Cross-Reference Map

Tracks content duplicated word-for-word across multiple skills. When editing any entry,
update **all listed files**. Each block is intentionally inlined (zero file reads at runtime);
this map exists so edits don't get lost.

Add an entry when a migrated or new skill duplicates content from another, using the shape at the
bottom of this file.

## Hotfix workflow

**Canonical:** `plugins/ceh-git-workflow/skills/release/SKILL.md` — § Hotfix

| Copy                                   | Section | Diverges |
| -------------------------------------- | ------- | -------- |
| none yet in this repo — see note below |         |          |

**Shared:** the hotfix process: branch `fix/critical-<description>` from `main`, minimal scope,
1-approval review, CI must pass, merge commit to `main`, bump PATCH + tag, staging → production.
In agent-skills `ceh-ops:incidents` carries the same steps without commands. Add it here as a copy
when `ceh-ops` migrates.

## Semver bump mapping

**Canonical:** `plugins/ceh-git-workflow/skills/release/SKILL.md` — § Versioning

| Copy                                                        | Section                                          | Diverges                                                               |
| ----------------------------------------------------------- | ------------------------------------------------ | ---------------------------------------------------------------------- |
| `plugins/ceh-git-workflow/skills/update-changelog/SKILL.md` | § Procedure, 2. Determine version and categorize | Keyed off commit prefixes, adds the Keep a Changelog section per level |

**Shared:** breaking change → MAJOR, new backward-compatible feature → MINOR,
fixes/chores/docs/refactors → PATCH, and "when in doubt, PATCH".

## Write-less-code ladder (skill + per-turn digest)

**Canonical:** `plugins/ceh-coding-agent/skills/write-less-code/SKILL.md` — § Procedure + § When not to be lazy

| Copy                                                    | Section                  | Diverges                                                                                                                       |
| ------------------------------------------------------- | ------------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| `plugins/ceh-coding-agent/scripts/less-code-payload.sh` | `additionalContext` text | compact digest of the ladder and the never-simplify list, injected per turn by the hook, plus a pointer to load the full skill |

**Shared:** the six-rung ladder (YAGNI → stdlib → native platform feature → already-installed
dependency → one line → minimum that works) and the never-simplify-away list (trust-boundary
validation, data-loss handling, security, accessibility, anything explicitly requested). The
retroactive ladder below re-frames the same six rungs, so a rung change propagates there too.

## Retroactive ladder + behavior preservation

**Canonical:** `plugins/ceh-coding-agent/skills/shrink-diff/SKILL.md` — § The retroactive ladder + § Behavior preservation

| Copy                                                     | Section                                            | Diverges                                                                          |
| -------------------------------------------------------- | -------------------------------------------------- | --------------------------------------------------------------------------------- |
| `plugins/ceh-coding-agent/skills/refactor-repo/SKILL.md` | § The retroactive ladder + § Behavior preservation | none in the text; applied per approved cluster rather than to the branch seed set |

**Shared:** both blocks word for word — the six retroactive rungs, and the behavior-preservation
bullets (no behavior change in a refactor, tests before and after, mechanical transforms only
without coverage, pin behavior with `ceh-testing:verify-behavior-preserved`, `refactor:` commits).

## Explanation honesty rules

**Canonical:** `plugins/ceh-coding-agent/skills/explain-codebase/SKILL.md` — § Rules

| Copy                                                                | Section | Diverges                                                                                 |
| ------------------------------------------------------------------- | ------- | ---------------------------------------------------------------------------------------- |
| `plugins/ceh-coding-agent/skills/explain-until-understood/SKILL.md` | § Rules | carries only the three rules that hold for a spoken explanation, not the file-bound ones |

**Shared:** three bullets word for word — "Evidence over inference", "Don't paste code" (with the
verbatim-literal exception), and "Describe what exists today".

## Bulk-read guard exemption list (`ALWAYS_ALLOW`)

**Canonical:** `plugins/ceh-core/scripts/bulk-read-guard.py` — `ALWAYS_ALLOW` tuple

| Copy                                               | Section              | Diverges |
| -------------------------------------------------- | -------------------- | -------- |
| `plugins/ceh-core/scripts/bulk-read-bash-guard.py` | `ALWAYS_ALLOW` tuple | none     |

**Shared:** the glob tuple, verbatim. The two guards cover the same files by two routes (`Read` and
`cat`/`head`), so a pattern in one and not the other denies a file on one route and allows it on
the other. Each hook is a standalone script with no shared module, so the list is duplicated.

## Bulk-reader answer format (Answer / Not found / Coverage)

**Canonical:** `plugins/ceh-core/agents/bulk-reader.md` — § Output to parent session

| Copy                                                   | Section                            | Diverges                                                                            |
| ------------------------------------------------------ | ---------------------------------- | ----------------------------------------------------------------------------------- |
| `plugins/ceh-core/skills/delegate-bulk-reads/SKILL.md` | § Trust the anchors, not the prose | names the sections only and carries the caller-side verification rules, no template |

**Shared:** the three fixed sections and their order — `## Answer` (every claim anchored
`path:line`), `## Not found / uncertain` (never omitted, `- Nothing outstanding.` when clean),
`## Coverage` (lines read per file, then the sum).

## Blog voice (Voice block)

**Canonical:** `plugins/ceh-blog/skills/draft-post/SKILL.md` — § Rules, Voice

| Copy                                              | Section        | Diverges                                                                         |
| ------------------------------------------------- | -------------- | -------------------------------------------------------------------------------- |
| `plugins/ceh-blog/skills/edit-post/SKILL.md`      | § Rules        | restated as diagnose-and-quiet rules: banned tells are flagged, never introduced |
| `plugins/ceh-blog/skills/repurpose-post/SKILL.md` | § Rules, Voice | applied to channel formats; adds "never invent" and the plain-link ending        |

**Shared:** the personal-voice rule (first person, reflective, no influencer style), the banned-tells
list (punchy one-liner paragraphs, aphoristic closers, imperative lessons, "If you're building X"
prescriptions, bold pseudo-headers, tidy meta-takeaway sign-offs, CTA endings), the open-thread
ending, and "the target repo's `CLAUDE.md` blog voice overrides".

## Blog post-type structures

**Canonical:** `plugins/ceh-blog/skills/draft-post/SKILL.md` — § Procedure, 4. Draft the post

| Copy                                         | Section                           | Diverges                                                                        |
| -------------------------------------------- | --------------------------------- | ------------------------------------------------------------------------------- |
| `plugins/ceh-blog/skills/edit-post/SKILL.md` | § Procedure, 3. Edit (structures) | shorter Project/Launch Origin and Thought Leadership lines, used for reordering |

**Shared:** the six post-type templates (Lessons Learned, How-To, Opinion / Take, Project / Launch,
Thought Leadership, Personal Story), each ending on **The Open Thread**.

## GEO writing rules

**Canonical:** `plugins/ceh-seo/skills/make-page-crawlable/SKILL.md` — § Procedure, 5. Write the page text for citation

| Copy                                            | Section                             | Diverges                                                                 |
| ----------------------------------------------- | ----------------------------------- | ------------------------------------------------------------------------ |
| `plugins/ceh-seo/skills/pitch-project/SKILL.md` | § Procedure, 4. Apply the GEO rules | adds "state scope facts explicitly"; drops the answer-first-section rule |

**Shared:** extractable standalone claims with numbers over adjectives, and question-shaped headings.

## Python environment foundation (uv / ruff / mypy + style)

**Canonical:** `plugins/ceh-python-service/skills/configure-python-service-env/SKILL.md` — entire file

| Copy                                                                      | Section     | Diverges                                                                                                                                                                                                                                |
| ------------------------------------------------------------------------- | ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `plugins/ceh-python-library/skills/configure-python-library-env/SKILL.md` | entire file | drops `fastapi`/`uvicorn[standard]`/`asyncpg` from the deps example and the uvicorn dev-server command; `dependencies = []`; `known-first-party` is the library; library docstring example; omits the service-only § Secrets management |

**Shared:** Python 3.12 + uv + `pyproject.toml`/`uv.lock` workflow, the uv command table, the ruff
(line-length 88, `select = [E,F,I,UP,N,B]`) + mypy (`strict = true`) + pytest
(`asyncio_mode = "auto"`) config, the coding-style rules (type hints, built-in generics, no `Any`
without a comment), the naming table, three-group imports, and the "ruff only, no `# type: ignore`
without a comment" linting rules.

## Python testing foundation (pytest core)

**Canonical:** `plugins/ceh-python-service/skills/write-pytest-service-tests/SKILL.md` — entire file

| Copy                                                                    | Section     | Diverges                                                                                                                                  |
| ----------------------------------------------------------------------- | ----------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `plugins/ceh-python-library/skills/write-pytest-library-tests/SKILL.md` | entire file | replaces the real-database integration tier and the system tier with an `api/` tier that imports the package as a consumer; no DB or HTTP |

**Shared:** pytest + pytest-asyncio (`asyncio_mode = "auto"`), `tests/unit/` structure,
`test_<what>_<expected_behavior>.py` naming, the one-behavior-per-test rule, the mocking rules (mock
external boundaries, `unittest.mock` or `pytest-mock`), and the Coverage floor block — the
two-sentence floor-not-goal intro and two rows, word for word: `Python application package | 80%`
and `Core business logic / domain services | 95%`.
The service copy adds the `--cov=app` command, the library copy `--cov=your_library`.

## Tests not requested (write and run nothing)

**Canonical:** `plugins/ceh-testing/skills/test-a-bug-fix/SKILL.md` — § When tests were not requested

| Copy                                                            | Section                              | Diverges                                                                                                         |
| --------------------------------------------------------------- | ------------------------------------ | ---------------------------------------------------------------------------------------------------------------- |
| `plugins/ceh-testing/skills/verify-behavior-preserved/SKILL.md` | § When tests were not requested      | the request is "only the refactor"; adds no separate commit of the pins; names "the tests" and "the steps below" |
| `plugins/ceh-testing/skills/close-test-risk-gaps/SKILL.md`      | § When tests were not requested      | the request is "only a readiness check"; still triages all five classes and names a test per class that fires    |
| `plugins/ceh-testing/skills/audit-test-suite/SKILL.md`          | § When a suite run was not requested | the unrequested action is running the suite, not writing tests; check 1 only reads files and still applies       |

**Shared:** the rule, stated in prose with no reference to `ceh-coding-agent:agent-coding-contract`
so `ceh-testing` keeps no dependency: writing tests and running a suite happen only when asked,
otherwise write and run nothing, name the test or check (what it asserts or reveals, where it would
live), state what stays unverified so the user can ask for it, and apply the skill in full when tests
were requested.

## Choosing what to test (hand-off to design-test-cases)

**Canonical:** `plugins/ceh-python-service/skills/write-pytest-service-tests/SKILL.md` — § Hands off to

| Copy                                                                     | Section        | Diverges |
| ------------------------------------------------------------------------ | -------------- | -------- |
| `plugins/ceh-python-library/skills/write-pytest-library-tests/SKILL.md`  | § Hands off to | none     |
| `plugins/ceh-web-frontend/skills/write-vitest-playwright-tests/SKILL.md` | § Hands off to | none     |

**Shared:** the section word for word — the tooling-versus-inputs boundary, the
`Invoke the Skill tool with skill="ceh-testing:design-test-cases"` call, and the list of what it
supplies. The call is why all three stack plugins declare `ceh-testing` as a dependency.

## asyncpg connection pool and transaction code

**Canonical:** `plugins/ceh-python-service/skills/write-postgresql-code/SKILL.md` — § Atomic transactions + § Connection pool

| Copy                                                                 | Section                             | Diverges                                              |
| -------------------------------------------------------------------- | ----------------------------------- | ----------------------------------------------------- |
| `plugins/ceh-python-service/skills/write-fastapi-endpoints/SKILL.md` | § Lifespan for startup and shutdown | the same `create_pool(...)` call, no transaction code |

**Shared:** `asyncpg.create_pool(min_size=5, max_size=20, command_timeout=30)` and the pool-in-lifespan
rule.

## Frontend API client and ApiRequestError

**Canonical:** `plugins/ceh-web-frontend/skills/write-sveltekit-code/SKILL.md` — § Centralized API client + § Error handling

| Copy                                                             | Section                                     | Diverges                                                                                                                                                                                                                                         |
| ---------------------------------------------------------------- | ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `plugins/ceh-web-frontend/skills/write-react-vite-code/SKILL.md` | § Centralized API client + § Error handling | env access is `import.meta.env.VITE_API_BASE_URL` instead of `PUBLIC_API_BASE_URL` from `$env/static/public`; "components and hooks" instead of "components and shared-state modules"; no Svelte component pattern; adds the error-boundary rule |

**Shared:** the `src/lib/api/client.ts` rule (all `fetch` calls go through it), the `apiClient`
method shape (`response.ok` check, then `throw new ApiRequestError(response.status, err.error)`), the
`ApiRequestError` class, and the three error rules: never expose internal codes or stack traces, map
`error.code` to friendly messages in one central map, and always surface the `correlation_id`.

## Layer boundaries (route → service → db)

**Canonical:** `plugins/ceh-python-service/skills/write-fastapi-endpoints/SKILL.md` — § Layer boundaries

| Copy                                   | Section | Diverges |
| -------------------------------------- | ------- | -------- |
| none yet in this repo — see note below |         |          |

**Shared:** route handlers contain no business logic (they call services), services contain no SQL
(they call the db layer), the db layer contains no business logic, and each aggregate has one
mutation path. In agent-skills `ceh-scaffolding:scaffold-python-service` restates the rules next to
the initial backend directory tree. Add it here as a copy when `ceh-scaffolding` migrates.

## Patch ITER frontmatter

**Canonical:** `plugins/ceh-plan-build-review/references/plan-schema.md` — § Frontmatter (the `patch` field rules)

| Copy                                                                | Section                              | Diverges                                                           |
| ------------------------------------------------------------------- | ------------------------------------ | ------------------------------------------------------------------ |
| `plugins/ceh-plan-build-review/skills/patch-built-version/SKILL.md` | § Procedure, 3. Write the patch ITER | the patch ITER frontmatter block only, with per-field placeholders |

**Shared:** the ITER frontmatter keys with `patch: true`, no `mvp`, `depends_on` the terminator or the
prior patch, and `sections_changed` within §04/§05. The rest of the plan schema (file naming, version
families, SKELETON and ITER frontmatter, terminator, pointers, resolution order) lives once in
`plan-schema.md` at the plugin root, read through `${CLAUDE_PLUGIN_ROOT}` by all five skills. In
agent-skills `ceh-business-plan:develop-business-plan` carries a separate `plan-schema.md`. Add it
here as a copy when `ceh-business-plan` migrates.

## Section contents (§01-§06 specs and the schema's Sections table)

**Canonical:** `plugins/ceh-plan-build-review/references/section-specs.md` — all sections

| Copy                                                      | Section             | Diverges                                                                   |
| --------------------------------------------------------- | ------------------- | -------------------------------------------------------------------------- |
| `plugins/ceh-plan-build-review/references/plan-schema.md` | § Sections, a table | condensed into table cells for the three consumer skills that read only it |

**Shared:** what each of §01-§06 holds at skeleton and iteration level, including the
`implementation-gotchas.md` note on §04 and §05 (the specs tell the planners to apply it, the table
tells the build skills to). A change to one goes to the other.

## §02 Architecture diagram requirement (Mermaid, iterations visualize the change)

**Canonical:** `plugins/ceh-plan-build-review/references/section-specs.md` — § §02 · Architecture

| Copy                                                                | Section                                           | Diverges                         |
| ------------------------------------------------------------------- | ------------------------------------------------- | -------------------------------- |
| `plugins/ceh-plan-build-review/references/plan-schema.md`           | § Sections, §02 row                               | condensed table-cell form        |
| `plugins/ceh-plan-build-review/references/audit-checklist.md`       | Architecture (§02)                                | one checklist bullet             |
| `plugins/ceh-plan-build-review/skills/review-against-plan/SKILL.md` | § Procedure, 2. Audit section by section, §02 row | post-implementation review check |

**Shared:** the component diagram is Mermaid, not ASCII art. At skeleton level it shows what exists
and how the pieces connect. At iteration level it also visualizes what changed, with new or
modified pieces marked distinctly.

## Planner "Plan families and versions" prose

**Canonical:** `plugins/ceh-plan-build-review/skills/plan-fullstack-app-to-mvp/SKILL.md` — § Plan families and versions

| Copy                                                                           | Section                      | Diverges                                                                                                       |
| ------------------------------------------------------------------------------ | ---------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `plugins/ceh-plan-build-review/skills/plan-fullstack-app-iteratively/SKILL.md` | § Plan families and versions | different words for the same rules, no `mvp: true` terminator, and no section on continuing an existing family |

**Shared:** the family and `depends_on` rules: the default family is untagged, a new major version
is a fresh family with the `NN` counter restarting at 01, a version with its own skeleton is
self-contained, an iterations-only version depends on the prior family's terminal artifacts, and
`depends_on` names artifacts by stem and points only backward. The shared rules also live in
`plan-schema.md`, so a change goes to both planners and to that file.

## Usability persona set and severity scale

**Canonical:** `plugins/ceh-usability-audit/references/personas-and-severity.md` — § The personas, § Severity

| Copy                                                  | Section                                                             | Diverges                                                                                       |
| ----------------------------------------------------- | ------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `plugins/ceh-usability-audit/README.md`               | § The personas, § Severity — assigned by outcome, not by appearance | condensed for the reader: column wording differs, the five personas and four severities do not |
| `plugins/ceh-usability-audit/agents/novice-walker.md` | § Holding the persona                                               | the same five personas as second-person instructions to the walker, not a table                |

**Shared:** the five personas (Blank Slate, Cautious Returner, Interrupted, Wrong Turn, Small
Screen) with their constraints and the failure class each catches, the four severities (Blocker,
Detour, Friction, Polish) with their assignment conditions, and the rule that severity comes from
an observed walker outcome, with anything unobserved demoted to an unranked `Hypotheses` list. The
two audit skills read the canonical file, so they are not copies. The README and the agent keep
their own form because a reader and a walker each need a different one.

## AG-UI styling lock and canvas extensions

**Canonical:** `plugins/ceh-ag-ui/skills/build-ag-ui/assets/canvas-template/web/src/catalogue/define.ts` and `web/src/useAgent.ts` — `STYLE_KEY`, `defineComponent`, `render` (the enforced code)

| Copy                                                     | Section                                         | Diverges                                   |
| -------------------------------------------------------- | ----------------------------------------------- | ------------------------------------------ |
| `plugins/ceh-ag-ui/skills/build-ag-ui/SKILL.md`          | § The styling lock                              | the three layers, described                |
| `plugins/ceh-ag-ui/skills/add-canvas-component/SKILL.md` | § Schema, content only, § Component, theme only | the same rules at authoring time           |
| `plugins/ceh-ag-ui/skills/add-live-state-panel/SKILL.md` | § 3. Canvas side, § Rules                       | state is validated and styled the same way |
| `plugins/ceh-ag-ui/skills/add-human-approval/SKILL.md`   | § 2. Canvas side, § The approval card           | the approval card's fixed look             |

**Shared:** schemas carry content only (no `style`/`className`/`color`/`size`/`variant`…), a needed
visual choice is a semantic enum mapped to a theme class, agent output is rendered only after
`safeParse`, and components use theme tokens and classes only.

---

Entry shape:

```markdown
## <Shared block name>

**Canonical:** `plugins/ceh-<plugin>/skills/<skill>/SKILL.md` — § <section>

| Copy                                           | Section     | Diverges                               |
| ---------------------------------------------- | ----------- | -------------------------------------- |
| `plugins/ceh-<plugin>/skills/<skill>/SKILL.md` | § <section> | <what deliberately differs, or "none"> |

**Shared:** <what must stay identical across every copy>.
```
