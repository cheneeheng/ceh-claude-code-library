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

| Copy                                                                      | Section     | Diverges                                                                                                                                                                                   |
| ------------------------------------------------------------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `plugins/ceh-python-library/skills/configure-python-library-env/SKILL.md` | entire file | drops `fastapi`/`uvicorn[standard]`/`asyncpg` from the deps example and the uvicorn dev-server command; `dependencies = []`; `known-first-party` is the library; library docstring example |

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
external boundaries, `unittest.mock` or `pytest-mock`), and the Coverage targets block — two rows,
word for word: `Python application package | 80%` and `Core business logic / domain services | 95%`.
The service copy adds the `--cov=app` command, the library copy `--cov=your_library`.

## Choosing what to test (hand-off to design-test-cases)

**Canonical:** `plugins/ceh-python-service/skills/write-pytest-service-tests/SKILL.md` — § Choosing what to test

| Copy                                                                     | Section                 | Diverges |
| ------------------------------------------------------------------------ | ----------------------- | -------- |
| `plugins/ceh-python-library/skills/write-pytest-library-tests/SKILL.md`  | § Choosing what to test | none     |
| `plugins/ceh-web-frontend/skills/write-vitest-playwright-tests/SKILL.md` | § Choosing what to test | none     |

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

## Layer boundaries (route → service → db)

**Canonical:** `plugins/ceh-python-service/skills/model-domain/SKILL.md` — § Layer boundaries

| Copy                                   | Section | Diverges |
| -------------------------------------- | ------- | -------- |
| none yet in this repo — see note below |         |          |

**Shared:** route handlers contain no business logic (they call services), services contain no SQL
(they call the db layer), the db layer contains no business logic, and each aggregate has one
mutation path. In agent-skills `ceh-scaffolding:scaffold-python-service` restates the rules next to
the initial backend directory tree. Add it here as a copy when `ceh-scaffolding` migrates.
`write-fastapi-endpoints` § Route handlers are thin states the first rule in its own words.

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
