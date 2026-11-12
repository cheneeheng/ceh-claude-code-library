# Cross-Reference Map

Tracks content duplicated word-for-word across multiple skills. When editing any entry,
update **all listed files**. Each block is intentionally inlined (zero file reads at runtime);
this map exists so edits don't get lost. A whole bundled-file copy is also checked byte for byte
by the `copies` check in `validate.py`.

Add an entry when a migrated or new skill duplicates content from another, using the shape at the
bottom of this file.

## Hotfix workflow

**Canonical:** `plugins/standalone/ceh-git-workflow/skills/release/SKILL.md` — § Hotfix

| Copy                                   | Section | Diverges |
| -------------------------------------- | ------- | -------- |
| none yet in this repo — see note below |         |          |

**Shared:** the hotfix process: branch `fix/critical-<description>` from `main`, minimal scope,
1-approval review, CI must pass, merge commit to `main`, bump PATCH + tag, staging → production.
In agent-skills `ceh-ops:incidents` carries the same steps without commands. Add it here as a copy
if `ceh-ops` is ever migrated.

## Semver bump mapping

**Canonical:** `plugins/standalone/ceh-git-workflow/skills/release/SKILL.md` — § Versioning

| Copy                                                                   | Section                                          | Diverges                                                               |
| ---------------------------------------------------------------------- | ------------------------------------------------ | ---------------------------------------------------------------------- |
| `plugins/standalone/ceh-git-workflow/skills/update-changelog/SKILL.md` | § Procedure, 2. Determine version and categorize | Keyed off commit prefixes, adds the Keep a Changelog section per level |

**Shared:** breaking change → MAJOR, new backward-compatible feature → MINOR,
fixes/chores/docs/refactors → PATCH, and "when in doubt, PATCH".

## Auto-merge probe and remote-branch check (`gh pr merge --auto`)

**Canonical:** `plugins/standalone/ceh-git-workflow/skills/pull-request/SKILL.md` — § Merge, step 2 (the probe with the direct-merge fallback)

| Copy                                                               | Section                       | Diverges                                                                                       |
| ------------------------------------------------------------------ | ----------------------------- | ---------------------------------------------------------------------------------------------- |
| `plugins/standalone/ceh-git-workflow/skills/pull-request/SKILL.md` | § Open, step 2                | probe-and-enable half only, right after `gh pr create`, with no fallback and no `--subject`    |
| `plugins/standalone/ceh-git-workflow/skills/pull-request/SKILL.md` | § Reporting the remote branch | the `delete_branch_on_merge` check that § Open also runs, here with the wording for the report |

**Shared:** the `allow_auto_merge` probe (`gh api repos/{owner}/{repo} --jq .allow_auto_merge`)
guarding `gh pr merge --merge --auto`, and the `delete_branch_on_merge` check that tells the user
whether the remote branch survives the merge. All three sites are in one file, so a change to the
probe means editing it twice. `ceh-git-workflow:release` reaches the same behavior through the
`pull-request` procedure and carries no copy.

## Write-less-code ladder (skill + per-turn digest)

**Canonical:** `plugins/standalone/ceh-coding-conduct/skills/write-less-code/SKILL.md` — § Procedure + § When not to be lazy

| Copy                                                                         | Section                  | Diverges                                                                                |
| ---------------------------------------------------------------------------- | ------------------------ | --------------------------------------------------------------------------------------- |
| `plugins/standalone/ceh-coding-conduct/scripts/inject-less-code-reminder.sh` | `additionalContext` text | compact digest of the ladder and the never-simplify list, injected per turn by the hook |

**Shared:** the six-rung ladder (YAGNI → stdlib → native platform feature → already-installed
dependency → one line → minimum that works) and the never-simplify-away list (trust-boundary
validation, data-loss handling, security, accessibility, anything explicitly requested). The
retroactive ladder below re-frames the same six rungs, so a rung change propagates there too.

## Retroactive ladder + behavior preservation

**Canonical:** `plugins/standalone/ceh-coding-conduct/skills/shrink-diff/SKILL.md` — § The retroactive ladder + § Behavior preservation

| Copy                                                                  | Section                                            | Diverges                                                                          |
| --------------------------------------------------------------------- | -------------------------------------------------- | --------------------------------------------------------------------------------- |
| `plugins/standalone/ceh-coding-conduct/skills/refactor-repo/SKILL.md` | § The retroactive ladder + § Behavior preservation | none in the text; applied per approved cluster rather than to the branch seed set |

**Shared:** both blocks word for word — the six retroactive rungs, and the behavior-preservation
bullets (no behavior change in a refactor, tests before and after, mechanical transforms only
without coverage, pin behavior with `ceh-testing:verify-behavior-preserved`, `refactor:` commits).

## Explanation honesty rules

**Canonical:** `plugins/standalone/ceh-coding-conduct/skills/explain-codebase/SKILL.md` — § Rules

| Copy                                                                             | Section | Diverges                                                                                 |
| -------------------------------------------------------------------------------- | ------- | ---------------------------------------------------------------------------------------- |
| `plugins/standalone/ceh-coding-conduct/skills/explain-until-understood/SKILL.md` | § Rules | carries only the three rules that hold for a spoken explanation, not the file-bound ones |

**Shared:** three bullets word for word — "Evidence over inference", "Don't paste code" (with the
verbatim-literal exception), and "Describe what exists today".

## Bulk-read guard exemption list (`ALWAYS_ALLOW`)

**Canonical:** `plugins/standalone/ceh-every-session/scripts/bulk-read-guard.py` — `ALWAYS_ALLOW` tuple

| Copy                                                                   | Section              | Diverges |
| ---------------------------------------------------------------------- | -------------------- | -------- |
| `plugins/standalone/ceh-every-session/scripts/bulk-read-bash-guard.py` | `ALWAYS_ALLOW` tuple | none     |

**Shared:** the glob tuple, verbatim. The two guards cover the same files by two routes (`Read` and
`cat`/`head`), so a pattern in one and not the other denies a file on one route and allows it on
the other. Each hook is a standalone script with no shared module, so the list is duplicated.

## Hook kill switch (`CEH_DISABLED_HOOKS`)

**Canonical:** `plugins/standalone/ceh-git-workflow/scripts/branch-guard.py` — the `CEH_DISABLED_HOOKS` check at the top of `main()`

| Copy                                                                         | Section                | Diverges                               |
| ---------------------------------------------------------------------------- | ---------------------- | -------------------------------------- |
| `plugins/standalone/ceh-every-session/scripts/bulk-read-guard.py`            | top of `main()`        | `sys.exit(0)` instead of `return`      |
| `plugins/standalone/ceh-every-session/scripts/bulk-read-bash-guard.py`       | top of `main()`        | `sys.exit(0)` instead of `return`      |
| `plugins/standalone/ceh-every-session/scripts/usage-limit-watch.py`          | top of `main()`        | `sys.exit(0)` instead of `return`      |
| `plugins/standalone/ceh-every-session/scripts/ask-user-question-guard.py`    | top of `main()`        | `sys.exit(0)` instead of `return`      |
| `plugins/standalone/ceh-build-plan/scripts/build-record-guard.py`            | top of `main()`        | none                                   |
| `plugins/standalone/ceh-git-workflow/scripts/sync-agents-workspace.py`       | top of `main()`        | none                                   |
| `plugins/standalone/ceh-testing/scripts/skill-started-guard.py`              | top of `main()`        | none                                   |
| `plugins/standalone/ceh-git-workflow/scripts/skill-started-guard.py`         | top of `main()`        | none                                   |
| `plugins/standalone/ceh-coding-conduct/scripts/load-contract.sh`             | the `case` line on top | bash: `case` on `$(basename "$0" .sh)` |
| `plugins/standalone/ceh-coding-conduct/scripts/inject-less-code-reminder.sh` | the `case` line on top | bash: `case` on `$(basename "$0" .sh)` |

**Shared:** `CEH_DISABLED_HOOKS` is a comma-separated list of hook script names without the
extension, spaces ignored, and a listed script exits 0 with no output before reading its input.
Every hook script carries the check, and `checks/hooks.py` in `tools/validate-plugins/` has a fixture proving it for each.

## Denial dampening (`denial_number`)

**Canonical:** `plugins/standalone/ceh-git-workflow/scripts/branch-guard.py` — `denial_number()` and its use in `main()`

| Copy                                                                   | Section                                | Diverges                                       |
| ---------------------------------------------------------------------- | -------------------------------------- | ---------------------------------------------- |
| `plugins/standalone/ceh-every-session/scripts/bulk-read-guard.py`      | `denial_number()`, its use in `main()` | the short line points at offset/limit reads    |
| `plugins/standalone/ceh-every-session/scripts/bulk-read-bash-guard.py` | `denial_number()`, its use in `main()` | the short line points at narrowing the command |

**Shared:** `denial_number()` verbatim (a per-hook, per-session counter file in the temp
directory), the full deny text for denials 1 to 3, then one line carrying "denial N this session",
and every deny, full or short, naming the setting that switches the guard off.

## Bulk-reader answer format (Answer / Not found / Coverage)

**Canonical:** `plugins/standalone/ceh-every-session/agents/bulk-reader.md` — § Output to parent session

| Copy                                                                       | Section                            | Diverges                                                                            |
| -------------------------------------------------------------------------- | ---------------------------------- | ----------------------------------------------------------------------------------- |
| `plugins/standalone/ceh-every-session/skills/delegate-bulk-reads/SKILL.md` | § Trust the anchors, not the prose | names the sections only and carries the caller-side verification rules, no template |

**Shared:** the three fixed sections and their order — `## Answer` (every claim anchored
`path:line`), `## Not found / uncertain` (never omitted, `- Nothing outstanding.` when clean),
`## Coverage` (lines read per file, then the sum).

## Blog voice (Voice block)

**Canonical:** `plugins/standalone/ceh-blog-and-seo/skills/draft-post/SKILL.md` — § Rules, Voice

| Copy                                                                 | Section        | Diverges                                                                         |
| -------------------------------------------------------------------- | -------------- | -------------------------------------------------------------------------------- |
| `plugins/standalone/ceh-blog-and-seo/skills/edit-post/SKILL.md`      | § Rules        | restated as diagnose-and-quiet rules: banned tells are flagged, never introduced |
| `plugins/standalone/ceh-blog-and-seo/skills/repurpose-post/SKILL.md` | § Rules, Voice | applied to channel formats; adds "never invent" and the plain-link ending        |

**Shared:** the personal-voice rule (first person, reflective, no influencer style), the banned-tells
list (punchy one-liner paragraphs, aphoristic closers, imperative lessons, "If you're building X"
prescriptions, bold pseudo-headers, tidy meta-takeaway sign-offs, CTA endings), the open-thread
ending, and "the target repo's `CLAUDE.md` blog voice overrides".

## Blog post-type structures

**Canonical:** `plugins/standalone/ceh-blog-and-seo/skills/draft-post/SKILL.md` — § Procedure, 4. Draft the post

| Copy                                                            | Section                           | Diverges                                                                        |
| --------------------------------------------------------------- | --------------------------------- | ------------------------------------------------------------------------------- |
| `plugins/standalone/ceh-blog-and-seo/skills/edit-post/SKILL.md` | § Procedure, 3. Edit (structures) | shorter Project/Launch Origin and Thought Leadership lines, used for reordering |

**Shared:** the six post-type templates (Lessons Learned, How-To, Opinion / Take, Project / Launch,
Thought Leadership, Personal Story), each ending on **The Open Thread**.

## Blog location and draft destination ("Finding the blog", "Where it goes")

**Canonical:** `plugins/standalone/ceh-blog-and-seo/skills/draft-post/SKILL.md` — § Procedure, 1. Read the blog first ("Finding the blog") + § Output ("Where it goes")

| Copy                                                            | Section                                                                 | Diverges                                                                                                                                                                                                    |
| --------------------------------------------------------------- | ----------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `plugins/standalone/ceh-blog-and-seo/skills/edit-post/SKILL.md` | § Procedure, 3. Edit ("Series continuity") + § Output ("Where it goes") | looks for earlier posts in the draft's own directory first, and writes the revision back to the draft's file instead of a new one, or to `<slug>-edited.md` for a pasted draft; the diagnosis stays in chat |

**Shared:** the lookup order for the blog (a path or URL the user gave, then a posts directory in the
current repo: `content/`, `posts/`, `_posts/`, `src/content/`, `blog/`), and the destination rule:
inside a blog repo the post is a file matching the existing posts' filename pattern and front matter,
with the title and meta description in the front matter, and otherwise a file in
`.agents_workspace/product/blog/` named `<YYYY-MM-DD>-<slug>`, filling the plugin's
`assets/blog-draft.template.md`, shown in chat too.

## Blog repurpose handoff line

**Canonical:** `plugins/standalone/ceh-blog-and-seo/skills/draft-post/SKILL.md` — § Hands off to

| Copy                                                            | Section        | Diverges |
| --------------------------------------------------------------- | -------------- | -------- |
| `plugins/standalone/ceh-blog-and-seo/skills/edit-post/SKILL.md` | § Hands off to | none     |

**Shared:** the single sentence pointing a satisfied user at `/ceh-blog-and-seo:repurpose-post` (Twitter/X
thread, LinkedIn post, TL;DR, newsletter blurb). Renaming the skill or adding a channel means
editing both.

## GEO writing rules

**Canonical:** `plugins/standalone/ceh-blog-and-seo/skills/make-page-crawlable/SKILL.md` — § Procedure, 5. Write the page text for citation

| Copy                                                                             | Section                             | Diverges                                                                 |
| -------------------------------------------------------------------------------- | ----------------------------------- | ------------------------------------------------------------------------ |
| `plugins/standalone/ceh-blog-and-seo/skills/write-project-listing-text/SKILL.md` | § Procedure, 5. Apply the GEO rules | adds "state scope facts explicitly"; drops the answer-first-section rule |

**Shared:** extractable standalone claims with numbers over adjectives, and question-shaped headings.

## Tell reads the product handoff files

**Canonical:** `plugins/standalone/ceh-blog-and-seo/skills/draft-post/SKILL.md` — § Procedure, 2. Read the material, "Product handoff files"

| Copy                                                                             | Section                                        | Diverges                                         |
| -------------------------------------------------------------------------------- | ---------------------------------------------- | ------------------------------------------------ |
| `plugins/standalone/ceh-blog-and-seo/skills/write-project-listing-text/SKILL.md` | § Procedure, 1. Read the product handoff files | a numbered step, not a paragraph; same sentences |

**Shared:** what Tell takes from `.agents_workspace/product/business/BUSINESS_PLAN.md` (user, problem, differentiator), that
`product/EVIDENCE.md` bounds every product claim to the Claims of its newest section with nothing said about a
`stale`, `not run`, or `open issues` area, and the missing-file fallback. The file names and
statuses must match `ceh-testing:write-evidence-report` and `docs/STRATEGY.md`.

## Python environment foundation (uv / ruff / mypy + style)

**Canonical:** `plugins/standalone/ceh-python-service/skills/configure-python-service-env/SKILL.md` — entire file

| Copy                                                                                 | Section     | Diverges                                                                                                                                                                                                                                                                                                                  |
| ------------------------------------------------------------------------------------ | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `plugins/standalone/ceh-python-library/skills/configure-python-library-env/SKILL.md` | entire file | drops `fastapi`/`uvicorn[standard]`/`asyncpg` from the deps example and the uvicorn dev-server command; `dependencies = []`; `known-first-party` is the library; library docstring example; omits the service-only § Secrets management; drops the naming table, the three-group imports block, and the `time.sleep` rule |

**Shared:** Python 3.12 + uv + `pyproject.toml`/`uv.lock` workflow, the uv command table, the ruff
(line-length 88, `select = [E,F,I,UP,N,B]`) + mypy (`strict = true`) + pytest
(`asyncio_mode = "auto"`) config, the coding-style rules (88 columns as the ruff default, type
hints, `Any` only with a comment), and the "ruff only, every `# type: ignore` gets a comment"
linting rules. The § Pre-commit hooks block has its own entry below.

## Python testing foundation (pytest core)

**Canonical:** `plugins/standalone/ceh-python-service/skills/write-pytest-service-tests/SKILL.md` — entire file

| Copy                                                                               | Section     | Diverges                                                                                                                                                                                                         |
| ---------------------------------------------------------------------------------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `plugins/standalone/ceh-python-library/skills/write-pytest-library-tests/SKILL.md` | entire file | replaces the real-database integration tier and the system tier with an `api/` tier that imports the package as a consumer; no DB or HTTP; coverage rows named `Library package` and `Public API and core logic` |

**Shared:** pytest + pytest-asyncio (`asyncio_mode = "auto"`), `tests/unit/` structure,
`test_<what>_<expected_behavior>.py` naming, the one-behavior-per-test rule, the mocking rules (mock
external boundaries, `unittest.mock` or `pytest-mock`), and the Coverage floor block — the
two-sentence floor-not-goal intro and two rows at 80% and 95%. The service copy names them
`Python application package` and `Core business logic / domain services`.
The service copy adds the `--cov=app` command, the library copy `--cov=your_library`.

## What waits for a request (proof by default)

**Canonical:** `plugins/standalone/ceh-testing/skills/test-a-bug-fix/SKILL.md` — § What waits for a request

| Copy                                                                       | Section                    | Diverges                                                                                                                                                          |
| -------------------------------------------------------------------------- | -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `plugins/standalone/ceh-testing/skills/verify-behavior-preserved/SKILL.md` | § What waits for a request | proves the refactor; lists the region coverage check, the separate commit of the pins, and the differential run; adds coverage beyond the region to the slow list |
| `plugins/standalone/ceh-testing/skills/close-test-risk-gaps/SKILL.md`      | § What waits for a request | proof is per class that fires; adds a benchmark harness run and a migration against a production-sized copy to the slow list                                      |
| `plugins/standalone/ceh-testing/skills/audit-test-suite/SKILL.md`          | § What waits for a request | judges existing tests rather than proving a change: checks 1 and 2 run unasked, checks 3 to 6 are the slow list                                                   |
| `plugins/standalone/ceh-testing/skills/write-test-first/SKILL.md`          | § What waits for a request | applies on every task that adds behavior, not only when asked                                                                                                     |

**Shared:** the rule, stated in prose with no reference to `ceh-coding-conduct:agent-coding-contract`
so `ceh-testing` keeps no dependency, and matching `docs/VISION.md` principle 3: writing and running
the tests that prove the change is part of the task and happens unasked; only a slow or paid run (the
full suite, coverage, mutation testing, repeated passes over the whole suite) waits for a request;
when one would help and was not requested, name the command and what it would reveal, and state what
stays unverified. The contract's Validation policy states the same split.

## Choosing what to test (hand-off to design-test-cases)

**Canonical:** `plugins/standalone/ceh-python-service/skills/write-pytest-service-tests/SKILL.md` — § Hands off to

| Copy                                                                                | Section        | Diverges |
| ----------------------------------------------------------------------------------- | -------------- | -------- |
| `plugins/standalone/ceh-python-library/skills/write-pytest-library-tests/SKILL.md`  | § Hands off to | none     |
| `plugins/standalone/ceh-web-frontend/skills/write-vitest-playwright-tests/SKILL.md` | § Hands off to | none     |

**Shared:** the section word for word — the tooling-versus-inputs boundary, the
`Invoke the Skill tool with skill="ceh-testing:design-test-cases"` call, and the list of what it
supplies. The call is why all three stack plugins declare `ceh-testing` as a dependency.

## asyncpg connection pool and transaction code

**Canonical:** `plugins/standalone/ceh-python-service/skills/write-postgresql-code/SKILL.md` — § Atomic transactions + § Connection pool

| Copy                                                                            | Section                             | Diverges                                              |
| ------------------------------------------------------------------------------- | ----------------------------------- | ----------------------------------------------------- |
| `plugins/standalone/ceh-python-service/skills/write-fastapi-endpoints/SKILL.md` | § Lifespan for startup and shutdown | the same `create_pool(...)` call, no transaction code |

**Shared:** `asyncpg.create_pool(min_size=5, max_size=20, command_timeout=30)` and the pool-in-lifespan
rule.

## Frontend API client and ApiRequestError

**Canonical:** `plugins/standalone/ceh-web-frontend/skills/write-sveltekit-code/SKILL.md` — § Centralized API client + § Error handling

| Copy                                                                        | Section                                     | Diverges                                                                                                                                                                                                                                         |
| --------------------------------------------------------------------------- | ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `plugins/standalone/ceh-web-frontend/skills/write-react-vite-code/SKILL.md` | § Centralized API client + § Error handling | env access is `import.meta.env.VITE_API_BASE_URL` instead of `PUBLIC_API_BASE_URL` from `$env/static/public`; "components and hooks" instead of "components and shared-state modules"; no Svelte component pattern; adds the error-boundary rule |

**Shared:** the `src/lib/api/client.ts` rule (all `fetch` calls go through it), the `apiClient`
method shape (`response.ok` check, then `throw new ApiRequestError(response.status, err.error)`), the
`ApiRequestError` class, the three error rules: never expose internal codes or stack traces, map
`error.code` to friendly messages in one central map, and always surface the `correlation_id`, and
the three client traps under the client code: `credentials: "include"` for cross-origin cookie
auth, one shared in-flight token refresh, and `fetch` with a `ReadableStream` reader instead of
`EventSource` for a POST or authenticated stream.

## Layer boundaries (route → service → db)

**Canonical:** `plugins/standalone/ceh-python-service/skills/write-fastapi-endpoints/SKILL.md` — § Layer boundaries

| Copy                                   | Section | Diverges |
| -------------------------------------- | ------- | -------- |
| none yet in this repo — see note below |         |          |

**Shared:** route handlers contain no business logic (they call services), services contain no SQL
(they call the db layer), the db layer contains no business logic, and each aggregate has one
mutation path. In agent-skills `ceh-scaffolding:scaffold-python-service` restates the rules next to
the initial backend directory tree. Add it here as a copy if `ceh-scaffolding` is ever migrated.

## Build plan format

**Canonical:** whole files, `plugins/standalone/ceh-build-plan/skills/write-build-plan/references/plan-schema.md`, `plugins/standalone/ceh-build-plan/skills/write-build-plan/references/plan-model.py`, `plugins/standalone/ceh-build-plan/skills/write-build-plan/assets/plan.template.md`, `plugins/standalone/ceh-build-plan/skills/write-build-plan/assets/plan.template.yaml`, `plugins/standalone/ceh-build-plan/skills/write-build-plan/scripts/artifact.py`, `plugins/standalone/ceh-build-plan/scripts/artifact-render-hook.py`, `plugins/standalone/ceh-build-plan/scripts/generated-md-guard.py`

| Copy                                                                                                                              | Section                                                     | Diverges                                                                         |
| --------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- | -------------------------------------------------------------------------------- |
| `plugins/standalone/ceh-build-plan/skills/review-build-plan/references/plan-schema.md`                                            | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-build-plan/skills/review-build-plan/references/plan-model.py`                                             | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-build-plan/skills/review-build-plan/assets/plan.template.md`                                              | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-build-plan/skills/review-build-plan/assets/plan.template.yaml`                                            | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-build-plan/skills/review-build-plan/scripts/artifact.py`                                                  | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-build-plan/skills/implement-from-plan/references/plan-schema.md`                                          | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-build-plan/skills/implement-from-plan/references/plan-model.py`                                           | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-build-plan/skills/implement-from-plan/assets/plan.template.md`                                            | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-build-plan/skills/implement-from-plan/assets/plan.template.yaml`                                          | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-build-plan/skills/implement-from-plan/scripts/artifact.py`                                                | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-check-build-against-plan/skills/check-build-against-plan/references/plan-schema.md`                       | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-check-build-against-plan/skills/check-build-against-plan/references/plan-model.py`                        | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-check-build-against-plan/skills/check-build-against-plan/assets/plan.template.md`                         | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-check-build-against-plan/skills/check-build-against-plan/assets/plan.template.yaml`                       | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-check-build-against-plan/skills/check-build-against-plan/scripts/artifact.py`                             | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-build-plan/scripts/artifact.py`                                                                           | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-build-plan/scripts/artifact.py`                                                                           | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-build-plan/scripts/artifact-render-hook.py`                                                               | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-build-plan/scripts/generated-md-guard.py`                                                                 | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-check-build-against-plan/scripts/artifact.py`                                                             | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-check-build-against-plan/scripts/artifact-render-hook.py`                                                 | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-check-build-against-plan/scripts/generated-md-guard.py`                                                   | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-testing/skills/write-evidence-report/scripts/artifact.py`                                                 | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-testing/skills/explore-app-for-bugs/scripts/artifact.py`                                                  | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-testing/skills/measure-performance/scripts/artifact.py`                                                   | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-security-audit/skills/audit-codebase-security/scripts/artifact.py`                                        | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-security-audit/scripts/artifact.py`                                                                       | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-security-audit/scripts/artifact-render-hook.py`                                                           | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-security-audit/scripts/generated-md-guard.py`                                                             | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-coding-conduct/skills/find-root-cause/scripts/artifact.py`                                                | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-testing/skills/test-a-bug-fix/scripts/artifact.py`                                                        | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-coding-conduct/scripts/artifact.py`                                                                       | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-coding-conduct/scripts/artifact-render-hook.py`                                                           | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-coding-conduct/scripts/generated-md-guard.py`                                                             | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-every-session/skills/hand-off-session/scripts/artifact.py`                                                | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-every-session/scripts/artifact.py`                                                                        | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-every-session/scripts/artifact-render-hook.py`                                                            | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-every-session/scripts/generated-md-guard.py`                                                              | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-workflow-builder/skills/interview-workflow-task/scripts/artifact.py`                                      | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-workflow-builder/skills/build-agentic-workflow/scripts/artifact.py`                                       | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-workflow-builder/scripts/artifact.py`                                                                     | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-workflow-builder/scripts/artifact-render-hook.py`                                                         | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-workflow-builder/scripts/generated-md-guard.py`                                                           | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-workflow-runner/skills/run-agentic-workflow/scripts/artifact.py`                                          | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-workflow-runner/scripts/artifact.py`                                                                      | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-workflow-runner/scripts/artifact-render-hook.py`                                                          | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-workflow-runner/scripts/generated-md-guard.py`                                                            | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-competitor-analysis/skills/analyze-competitor/scripts/artifact.py`                                        | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-competitor-analysis/skills/compare-competitors/scripts/artifact.py`                                       | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-competitor-analysis/scripts/artifact.py`                                                                  | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-competitor-analysis/scripts/artifact-render-hook.py`                                                      | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-competitor-analysis/scripts/generated-md-guard.py`                                                        | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-usability-audit/skills/simulate-newcomer-first-run/scripts/artifact.py`                                   | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-usability-audit/skills/audit-interface/scripts/artifact.py`                                               | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-usability-audit/skills/audit-error-messages/scripts/artifact.py`                                          | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-usability-audit/scripts/artifact.py`                                                                      | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-usability-audit/scripts/artifact-render-hook.py`                                                          | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-usability-audit/scripts/generated-md-guard.py`                                                            | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-testing/scripts/artifact.py`                                                                              | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-testing/scripts/artifact-render-hook.py`                                                                  | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-testing/scripts/generated-md-guard.py`                                                                    | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-codebase-explanation/skills/document-architecture/scripts/artifact.py`                                    | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-codebase-explanation/skills/maintain-glossary/scripts/artifact.py`                                        | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-codebase-explanation/scripts/artifact.py`                                                                 | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-codebase-explanation/scripts/artifact-render-hook.py`                                                     | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-codebase-explanation/scripts/generated-md-guard.py`                                                       | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-product-direction/skills/write-vision-and-strategy/scripts/artifact.py`                                   | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-product-direction/scripts/artifact.py`                                                                    | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-product-direction/scripts/artifact-render-hook.py`                                                        | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-product-direction/scripts/generated-md-guard.py`                                                          | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-product-direction/skills/develop-business-plan/scripts/artifact.py`                                       | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-product-direction/skills/find-product-market-fit/scripts/artifact.py`                                     | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-product-direction/skills/plan-go-to-market/scripts/artifact.py`                                           | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-product-direction/skills/review-business-plan/scripts/artifact.py`                                        | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-product-direction/skills/run-premortem/scripts/artifact.py`                                               | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-product-direction/skills/set-operating-plan/scripts/artifact.py`                                          | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-product-direction/skills/sharpen-strategy/scripts/artifact.py`                                            | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-product-direction/skills/stress-test-unit-economics/scripts/artifact.py`                                  | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-product-direction/skills/write-investor-materials/scripts/artifact.py`                                    | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-product-direction/scripts/artifact.py`                                                                    | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-product-direction/scripts/artifact-render-hook.py`                                                        | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-product-direction/scripts/generated-md-guard.py`                                                          | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-every-session/skills/whats-next/references/plan-schema.md`                                                | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-every-session/skills/whats-next/references/plan-model.py`                                                 | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-every-session/skills/whats-next/assets/plan.template.md`                                                  | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-every-session/skills/whats-next/assets/plan.template.yaml`                                                | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-every-session/skills/record-project-decisions/references/plan-schema.md`                                  | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-every-session/skills/record-project-decisions/references/plan-model.py`                                   | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-every-session/skills/record-project-decisions/assets/plan.template.md`                                    | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-every-session/skills/record-project-decisions/assets/plan.template.yaml`                                  | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-every-session/skills/whats-next/scripts/artifact.py`                                                      | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-every-session/skills/record-project-decisions/scripts/artifact.py`                                        | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-every-session/skills/prevent-repeat-mistake/scripts/artifact.py`                                          | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-blog-and-seo/skills/draft-post/scripts/artifact.py`                                                       | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-blog-and-seo/skills/edit-post/scripts/artifact.py`                                                        | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-blog-and-seo/scripts/artifact.py`                                                                         | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-blog-and-seo/scripts/artifact-render-hook.py`                                                             | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-blog-and-seo/scripts/generated-md-guard.py`                                                               | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-blog-and-seo/skills/write-project-listing-text/scripts/artifact.py`                                       | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-documentation/skills/write-concept-docs/scripts/artifact.py`                                              | whole file                                                  | none                                                                             |
| `plugins/standalone/ceh-python-service/skills/write-fastapi-endpoints/scripts/artifact.py`                                        | whole file                                                  | none                                                                             |
| `ceh-build-plan:review-build-plan`, `ceh-build-plan:implement-from-plan`, `ceh-check-build-against-plan:check-build-against-plan` | the "A `plan/v2` plan is checked first" paragraph in step 1 | `implement-from-plan` adds where a Status note and a Record entry go in the YAML |

**Shared:** the whole plan format, byte for byte: the `product/plans/<slug>.md` location, the
frontmatter and its four statuses, the Goal, Scope, Design, Phases, and Open sections, the phase
rules (a runnable Check, `todo` / `unplanned` / `done` with evidence), and the rules for changing
a plan, and the `plan/v2` YAML template `plan.template.yaml` with its keys and rules. Every skill
that reads a plan carries the format, the model and `scripts/artifact.py` in its own folder, so the
skill folder works on its own. Each plugin also keeps `scripts/artifact.py` and the two artifact
hooks at its root, for its hooks. `validate.py` fails when a copy differs (the `copies` check). The
read-time check paragraph is kept in step by hand. `ceh-product-direction:find-product-market-fit`
reads plans too, but carries no copy: it reads only the plans folder and the Goal, Scope, and
Design sections.

## Architecture template and schema

**Canonical:** whole files, `plugins/standalone/ceh-codebase-explanation/skills/document-architecture/references/architecture-schema.md`, `plugins/standalone/ceh-codebase-explanation/skills/document-architecture/assets/architecture.template.md`, `plugins/standalone/ceh-codebase-explanation/skills/document-architecture/references/architecture-model.py`, `plugins/standalone/ceh-codebase-explanation/skills/document-architecture/assets/architecture.template.yaml`

| Copy                                                                                                        | Section    | Diverges |
| ----------------------------------------------------------------------------------------------------------- | ---------- | -------- |
| `plugins/standalone/ceh-build-plan/skills/implement-from-plan/references/architecture-schema.md`            | whole file | none     |
| `plugins/standalone/ceh-build-plan/skills/implement-from-plan/assets/architecture.template.md`              | whole file | none     |
| `plugins/standalone/ceh-build-plan/skills/implement-from-plan/references/architecture-model.py`             | whole file | none     |
| `plugins/standalone/ceh-build-plan/skills/implement-from-plan/assets/architecture.template.yaml`            | whole file | none     |
| `plugins/standalone/ceh-product-direction/skills/find-product-market-fit/references/architecture-schema.md` | whole file | none     |
| `plugins/standalone/ceh-product-direction/skills/find-product-market-fit/assets/architecture.template.md`   | whole file | none     |
| `plugins/standalone/ceh-product-direction/skills/find-product-market-fit/references/architecture-model.py`  | whole file | none     |
| `plugins/standalone/ceh-product-direction/skills/find-product-market-fit/assets/architecture.template.yaml` | whole file | none     |
| `plugins/standalone/ceh-every-session/skills/record-project-decisions/references/architecture-schema.md`    | whole file | none     |
| `plugins/standalone/ceh-every-session/skills/record-project-decisions/references/architecture-model.py`     | whole file | none     |
| `plugins/standalone/ceh-every-session/skills/record-project-decisions/assets/architecture.template.md`      | whole file | none     |
| `plugins/standalone/ceh-every-session/skills/record-project-decisions/assets/architecture.template.yaml`    | whole file | none     |
| `plugins/standalone/ceh-documentation/skills/write-concept-docs/references/architecture-schema.md`          | whole file | none     |
| `plugins/standalone/ceh-documentation/skills/write-concept-docs/references/architecture-model.py`           | whole file | none     |
| `plugins/standalone/ceh-documentation/skills/write-concept-docs/assets/architecture.template.md`            | whole file | none     |
| `plugins/standalone/ceh-documentation/skills/write-concept-docs/assets/architecture.template.yaml`          | whole file | none     |
| `plugins/standalone/ceh-python-service/skills/write-fastapi-endpoints/references/architecture-schema.md`    | whole file | none     |
| `plugins/standalone/ceh-python-service/skills/write-fastapi-endpoints/references/architecture-model.py`     | whole file | none     |
| `plugins/standalone/ceh-python-service/skills/write-fastapi-endpoints/assets/architecture.template.md`      | whole file | none     |
| `plugins/standalone/ceh-python-service/skills/write-fastapi-endpoints/assets/architecture.template.yaml`    | whole file | none     |

**Shared:** the `product/ARCHITECTURE.md` layout: its `schema:` line, the Overview, the diagram
sections, and the Key Decisions entry shape. `document-architecture` owns the file and
`implement-from-plan` appends Key Decisions entries to it, so each plugin carries a copy to work
installed alone. `find-product-market-fit` only reads the file, and carries a copy to check
`ARCHITECTURE.yaml` before its intake reads it. `validate.py` fails when a copy differs from the
canonical file.

## Evidence format

**Canonical:** whole files, `plugins/standalone/ceh-testing/skills/write-evidence-report/references/evidence-schema.md`, `plugins/standalone/ceh-testing/skills/write-evidence-report/references/evidence-model.py`, `plugins/standalone/ceh-testing/skills/write-evidence-report/assets/evidence.template.md`, `plugins/standalone/ceh-testing/skills/write-evidence-report/assets/evidence.template.yaml`

| Copy                                                                                                  | Section    | Diverges |
| ----------------------------------------------------------------------------------------------------- | ---------- | -------- |
| `plugins/standalone/ceh-blog-and-seo/skills/draft-post/references/evidence-schema.md`                 | whole file | none     |
| `plugins/standalone/ceh-blog-and-seo/skills/draft-post/references/evidence-model.py`                  | whole file | none     |
| `plugins/standalone/ceh-blog-and-seo/skills/draft-post/assets/evidence.template.md`                   | whole file | none     |
| `plugins/standalone/ceh-blog-and-seo/skills/draft-post/assets/evidence.template.yaml`                 | whole file | none     |
| `plugins/standalone/ceh-blog-and-seo/skills/write-project-listing-text/references/evidence-schema.md` | whole file | none     |
| `plugins/standalone/ceh-blog-and-seo/skills/write-project-listing-text/references/evidence-model.py`  | whole file | none     |
| `plugins/standalone/ceh-blog-and-seo/skills/write-project-listing-text/assets/evidence.template.md`   | whole file | none     |
| `plugins/standalone/ceh-blog-and-seo/skills/write-project-listing-text/assets/evidence.template.yaml` | whole file | none     |

**Shared:** the `evidence/v2` format with its template. `write-evidence-report` owns
`product/EVIDENCE.yaml`, and `draft-post` and `write-project-listing-text` read its newest run's
claims and area statuses, so each carries a copy to check the file before reading it.
`validate.py` fails when a copy differs from the canonical file.

## QA report format

**Canonical:** whole files, `plugins/standalone/ceh-testing/skills/explore-app-for-bugs/references/qa-report-schema.md`, `plugins/standalone/ceh-testing/skills/explore-app-for-bugs/references/qa-report-model.py`, `plugins/standalone/ceh-testing/skills/explore-app-for-bugs/assets/qa-report.template.md`, `plugins/standalone/ceh-testing/skills/explore-app-for-bugs/assets/qa-report.template.yaml`

| Copy                                                                                         | Section    | Diverges |
| -------------------------------------------------------------------------------------------- | ---------- | -------- |
| `plugins/standalone/ceh-testing/skills/write-evidence-report/references/qa-report-schema.md` | whole file | none     |
| `plugins/standalone/ceh-testing/skills/write-evidence-report/references/qa-report-model.py`  | whole file | none     |
| `plugins/standalone/ceh-testing/skills/write-evidence-report/assets/qa-report.template.md`   | whole file | none     |
| `plugins/standalone/ceh-testing/skills/write-evidence-report/assets/qa-report.template.yaml` | whole file | none     |

**Shared:** the `qa-report/v2` format with its templates. `explore-app-for-bugs` writes
`QA_REPORT.yaml`, and `write-evidence-report` reads its `commit` and `bugs` by key, so it carries a
copy to check the file first. `validate.py` fails when a copy differs from the canonical file.

## Performance report format

**Canonical:** whole files, `plugins/standalone/ceh-testing/skills/measure-performance/references/perf-report-schema.md`, `plugins/standalone/ceh-testing/skills/measure-performance/references/perf-report-model.py`, `plugins/standalone/ceh-testing/skills/measure-performance/assets/perf-report.template.md`, `plugins/standalone/ceh-testing/skills/measure-performance/assets/perf-report.template.yaml`

| Copy                                                                                           | Section    | Diverges |
| ---------------------------------------------------------------------------------------------- | ---------- | -------- |
| `plugins/standalone/ceh-testing/skills/write-evidence-report/references/perf-report-schema.md` | whole file | none     |
| `plugins/standalone/ceh-testing/skills/write-evidence-report/references/perf-report-model.py`  | whole file | none     |
| `plugins/standalone/ceh-testing/skills/write-evidence-report/assets/perf-report.template.md`   | whole file | none     |
| `plugins/standalone/ceh-testing/skills/write-evidence-report/assets/perf-report.template.yaml` | whole file | none     |

**Shared:** the `perf-report/v2` format with its templates. `measure-performance` keeps
`<metric>.yaml`, and `write-evidence-report` reads its `commit` and `attempts` by key, so it
carries a copy to check the file first. `validate.py` fails when a copy differs from the canonical
file.

## Security audit format

**Canonical:** whole files, `plugins/standalone/ceh-security-audit/skills/audit-codebase-security/references/security-audit-schema.md`, `plugins/standalone/ceh-security-audit/skills/audit-codebase-security/references/security-audit-model.py`, `plugins/standalone/ceh-security-audit/skills/audit-codebase-security/assets/security-audit.template.md`, `plugins/standalone/ceh-security-audit/skills/audit-codebase-security/assets/security-audit.template.yaml`

| Copy                                                                                              | Section    | Diverges |
| ------------------------------------------------------------------------------------------------- | ---------- | -------- |
| `plugins/standalone/ceh-testing/skills/write-evidence-report/references/security-audit-schema.md` | whole file | none     |
| `plugins/standalone/ceh-testing/skills/write-evidence-report/references/security-audit-model.py`  | whole file | none     |
| `plugins/standalone/ceh-testing/skills/write-evidence-report/assets/security-audit.template.md`   | whole file | none     |
| `plugins/standalone/ceh-testing/skills/write-evidence-report/assets/security-audit.template.yaml` | whole file | none     |

**Shared:** the `security-audit/v2` format with its templates. `audit-codebase-security` writes
`SECURITY_AUDIT-<YYYYMMDD-HHMM>.yaml`, and `write-evidence-report` reads its `commit` and `findings` by key,
so it carries a copy to check the file first, and `ceh-testing`'s hook checks the file too. With
both plugins installed an error is reported twice, from the same model. `validate.py` fails when a
copy differs from the canonical file.

## Usability audit formats

**Canonical:** whole files, `plugins/standalone/ceh-usability-audit/skills/simulate-newcomer-first-run/references/first-run-audit-schema.md`, `plugins/standalone/ceh-usability-audit/skills/simulate-newcomer-first-run/references/first-run-audit-model.py`, `plugins/standalone/ceh-usability-audit/skills/simulate-newcomer-first-run/assets/first-run-audit.template.md`, `plugins/standalone/ceh-usability-audit/skills/simulate-newcomer-first-run/assets/first-run-audit.template.yaml`, `plugins/standalone/ceh-usability-audit/skills/audit-interface/references/interface-audit-schema.md`, `plugins/standalone/ceh-usability-audit/skills/audit-interface/references/interface-audit-model.py`, `plugins/standalone/ceh-usability-audit/skills/audit-interface/assets/interface-audit.template.md`, `plugins/standalone/ceh-usability-audit/skills/audit-interface/assets/interface-audit.template.yaml`, `plugins/standalone/ceh-usability-audit/skills/audit-error-messages/references/error-messages-audit-schema.md`, `plugins/standalone/ceh-usability-audit/skills/audit-error-messages/references/error-messages-audit-model.py`, `plugins/standalone/ceh-usability-audit/skills/audit-error-messages/assets/error-messages-audit.template.md`, `plugins/standalone/ceh-usability-audit/skills/audit-error-messages/assets/error-messages-audit.template.yaml`

| Copy                                                                                                    | Section    | Diverges |
| ------------------------------------------------------------------------------------------------------- | ---------- | -------- |
| `plugins/standalone/ceh-testing/skills/write-evidence-report/references/first-run-audit-schema.md`      | whole file | none     |
| `plugins/standalone/ceh-testing/skills/write-evidence-report/references/first-run-audit-model.py`       | whole file | none     |
| `plugins/standalone/ceh-testing/skills/write-evidence-report/assets/first-run-audit.template.md`        | whole file | none     |
| `plugins/standalone/ceh-testing/skills/write-evidence-report/assets/first-run-audit.template.yaml`      | whole file | none     |
| `plugins/standalone/ceh-testing/skills/write-evidence-report/references/interface-audit-schema.md`      | whole file | none     |
| `plugins/standalone/ceh-testing/skills/write-evidence-report/references/interface-audit-model.py`       | whole file | none     |
| `plugins/standalone/ceh-testing/skills/write-evidence-report/assets/interface-audit.template.md`        | whole file | none     |
| `plugins/standalone/ceh-testing/skills/write-evidence-report/assets/interface-audit.template.yaml`      | whole file | none     |
| `plugins/standalone/ceh-testing/skills/write-evidence-report/references/error-messages-audit-schema.md` | whole file | none     |
| `plugins/standalone/ceh-testing/skills/write-evidence-report/references/error-messages-audit-model.py`  | whole file | none     |
| `plugins/standalone/ceh-testing/skills/write-evidence-report/assets/error-messages-audit.template.md`   | whole file | none     |
| `plugins/standalone/ceh-testing/skills/write-evidence-report/assets/error-messages-audit.template.yaml` | whole file | none     |

**Shared:** the `first-run-audit/v2`, `interface-audit/v2` and `error-messages-audit/v2` formats
with their templates. Each audit skill writes its own report with a required `commit`, and
`write-evidence-report` reads their `commit`, `findings`, `gate` and `rows` by key, so it carries a
copy of each to check the file first, and `ceh-testing`'s hook checks the files too. The first-run
and interface audits share a finding and gate shape, written into each model rather than shared,
so each model file stands alone. `validate.py` fails when a copy differs from the canonical file.

## Vision and strategy format

**Canonical:** whole files, `plugins/standalone/ceh-product-direction/skills/write-vision-and-strategy/references/vision-schema.md`, `plugins/standalone/ceh-product-direction/skills/write-vision-and-strategy/references/vision-model.py`, `plugins/standalone/ceh-product-direction/skills/write-vision-and-strategy/assets/vision.template.md`, `plugins/standalone/ceh-product-direction/skills/write-vision-and-strategy/assets/vision.template.yaml`, `plugins/standalone/ceh-product-direction/skills/write-vision-and-strategy/references/strategy-schema.md`, `plugins/standalone/ceh-product-direction/skills/write-vision-and-strategy/references/strategy-model.py`, `plugins/standalone/ceh-product-direction/skills/write-vision-and-strategy/assets/strategy.template.md`, `plugins/standalone/ceh-product-direction/skills/write-vision-and-strategy/assets/strategy.template.yaml`

| Copy                                                                                       | Section    | Diverges |
| ------------------------------------------------------------------------------------------ | ---------- | -------- |
| `plugins/standalone/ceh-build-plan/skills/write-build-plan/references/vision-schema.md`    | whole file | none     |
| `plugins/standalone/ceh-build-plan/skills/write-build-plan/references/vision-model.py`     | whole file | none     |
| `plugins/standalone/ceh-build-plan/skills/write-build-plan/assets/vision.template.md`      | whole file | none     |
| `plugins/standalone/ceh-build-plan/skills/write-build-plan/assets/vision.template.yaml`    | whole file | none     |
| `plugins/standalone/ceh-build-plan/skills/write-build-plan/references/strategy-schema.md`  | whole file | none     |
| `plugins/standalone/ceh-build-plan/skills/write-build-plan/references/strategy-model.py`   | whole file | none     |
| `plugins/standalone/ceh-build-plan/skills/write-build-plan/assets/strategy.template.md`    | whole file | none     |
| `plugins/standalone/ceh-build-plan/skills/write-build-plan/assets/strategy.template.yaml`  | whole file | none     |
| `plugins/standalone/ceh-build-plan/skills/review-build-plan/references/vision-schema.md`   | whole file | none     |
| `plugins/standalone/ceh-build-plan/skills/review-build-plan/references/vision-model.py`    | whole file | none     |
| `plugins/standalone/ceh-build-plan/skills/review-build-plan/assets/vision.template.md`     | whole file | none     |
| `plugins/standalone/ceh-build-plan/skills/review-build-plan/assets/vision.template.yaml`   | whole file | none     |
| `plugins/standalone/ceh-build-plan/skills/review-build-plan/references/strategy-schema.md` | whole file | none     |
| `plugins/standalone/ceh-build-plan/skills/review-build-plan/references/strategy-model.py`  | whole file | none     |
| `plugins/standalone/ceh-build-plan/skills/review-build-plan/assets/strategy.template.md`   | whole file | none     |
| `plugins/standalone/ceh-build-plan/skills/review-build-plan/assets/strategy.template.yaml` | whole file | none     |

**Shared:** the `vision/v2` and `strategy/v2` formats with their templates.
`write-vision-and-strategy` owns both files, and `write-build-plan` and `review-build-plan` read
them, so each carries a copy to check `VISION.yaml` and `STRATEGY.yaml` before reading them.
`validate.py` fails when a copy differs from the canonical file.

## Fix record format

**Canonical:** whole files, `plugins/standalone/ceh-coding-conduct/skills/find-root-cause/references/fix-record-schema.md`, `plugins/standalone/ceh-coding-conduct/skills/find-root-cause/references/fix-record-model.py`, `plugins/standalone/ceh-coding-conduct/skills/find-root-cause/assets/fix-record.template.md`, `plugins/standalone/ceh-coding-conduct/skills/find-root-cause/assets/fix-record.template.yaml`

| Copy                                                                                   | Section    | Diverges |
| -------------------------------------------------------------------------------------- | ---------- | -------- |
| `plugins/standalone/ceh-testing/skills/test-a-bug-fix/references/fix-record-schema.md` | whole file | none     |
| `plugins/standalone/ceh-testing/skills/test-a-bug-fix/references/fix-record-model.py`  | whole file | none     |
| `plugins/standalone/ceh-testing/skills/test-a-bug-fix/assets/fix-record.template.md`   | whole file | none     |
| `plugins/standalone/ceh-testing/skills/test-a-bug-fix/assets/fix-record.template.yaml` | whole file | none     |

**Shared:** the whole fix record format, `fix-record/v1` and the `fix-record/v2` YAML with its
model, which renders the `v1` layout of `fix-record.template.md`, and the templates (canonical in
`find-root-cause/assets/`, beside the canonical schema's `references/`), byte for byte: the `product/fixes/<slug>.md` location and
slug rule, the write-only-for-repo-causes rule, the frontmatter with its three statuses and the
`plan:` and `previous:` rules, the sections each status keeps, and the same-commit and
committed-alone rules. `find-root-cause` writes the record and `test-a-bug-fix` completes or creates
it, and each plugin carries a copy so it works installed alone. `validate.py` fails when a copy
differs from the canonical file.

## Handoff format

**Canonical:** whole files, `plugins/standalone/ceh-every-session/skills/hand-off-session/references/handoff-schema.md`, `plugins/standalone/ceh-every-session/skills/hand-off-session/references/handoff-model.py`, `plugins/standalone/ceh-every-session/skills/hand-off-session/assets/handoff.template.md`, `plugins/standalone/ceh-every-session/skills/hand-off-session/assets/handoff.template.yaml`

| Copy                                                                                  | Section    | Diverges |
| ------------------------------------------------------------------------------------- | ---------- | -------- |
| `plugins/standalone/ceh-every-session/skills/whats-next/references/handoff-schema.md` | whole file | none     |
| `plugins/standalone/ceh-every-session/skills/whats-next/references/handoff-model.py`  | whole file | none     |
| `plugins/standalone/ceh-every-session/skills/whats-next/assets/handoff.template.md`   | whole file | none     |
| `plugins/standalone/ceh-every-session/skills/whats-next/assets/handoff.template.yaml` | whole file | none     |

**Shared:** the `handoff/v1` layout and the `handoff/v2` YAML with its model. `hand-off-session`
saves and loads the handoff, and `whats-next` reads the newest one, checking a `v2` file with its
own copy of the model first. `validate.py` fails when a copy differs from the canonical file.

## Workflow spec format

**Canonical:** whole files, `plugins/standalone/ceh-workflow-builder/skills/interview-workflow-task/references/workflow-spec-schema.md`, `plugins/standalone/ceh-workflow-builder/skills/interview-workflow-task/references/workflow-spec-model.py`, `plugins/standalone/ceh-workflow-builder/skills/interview-workflow-task/assets/workflow-spec.template.md`, `plugins/standalone/ceh-workflow-builder/skills/interview-workflow-task/assets/workflow-spec.template.yaml`

| Copy                                                                                                       | Section    | Diverges |
| ---------------------------------------------------------------------------------------------------------- | ---------- | -------- |
| `plugins/standalone/ceh-workflow-builder/skills/build-agentic-workflow/references/workflow-spec-schema.md` | whole file | none     |
| `plugins/standalone/ceh-workflow-builder/skills/build-agentic-workflow/references/workflow-spec-model.py`  | whole file | none     |
| `plugins/standalone/ceh-workflow-builder/skills/build-agentic-workflow/assets/workflow-spec.template.md`   | whole file | none     |
| `plugins/standalone/ceh-workflow-builder/skills/build-agentic-workflow/assets/workflow-spec.template.yaml` | whole file | none     |

**Shared:** the `workflow-spec/v1` layout and the `workflow-spec/v2` YAML with its model.
`interview-workflow-task` writes the spec, and `build-agentic-workflow` checks it with its own copy
of the model, reads it by key, and writes conversation answers and the row 8 or 9 assumption into
it. `validate.py` fails when a copy differs from the canonical file.

## Competitor report format

**Canonical:** whole files, `plugins/standalone/ceh-competitor-analysis/skills/analyze-competitor/references/competitor-report-schema.md`, `plugins/standalone/ceh-competitor-analysis/skills/analyze-competitor/references/competitor-report-model.py`, `plugins/standalone/ceh-competitor-analysis/skills/analyze-competitor/assets/competitor-report.template.md`, `plugins/standalone/ceh-competitor-analysis/skills/analyze-competitor/assets/competitor-report.template.yaml`

| Copy                                                                                                           | Section    | Diverges |
| -------------------------------------------------------------------------------------------------------------- | ---------- | -------- |
| `plugins/standalone/ceh-competitor-analysis/skills/compare-competitors/references/competitor-report-schema.md` | whole file | none     |
| `plugins/standalone/ceh-competitor-analysis/skills/compare-competitors/references/competitor-report-model.py`  | whole file | none     |
| `plugins/standalone/ceh-competitor-analysis/skills/compare-competitors/assets/competitor-report.template.md`   | whole file | none     |
| `plugins/standalone/ceh-competitor-analysis/skills/compare-competitors/assets/competitor-report.template.yaml` | whole file | none     |

**Shared:** the `competitor-report/v1` layout and the `competitor-report/v2` YAML with its model.
`analyze-competitor` writes the report, and `compare-competitors` checks each one with its own copy
of the model and reads it by key. `validate.py` fails when a copy differs from the canonical file.

## Glossary format

**Canonical:** whole files, `plugins/standalone/ceh-codebase-explanation/skills/maintain-glossary/references/glossary-schema.md`, `plugins/standalone/ceh-codebase-explanation/skills/maintain-glossary/references/glossary-model.py`, `plugins/standalone/ceh-codebase-explanation/skills/maintain-glossary/assets/glossary.template.md`, `plugins/standalone/ceh-codebase-explanation/skills/maintain-glossary/assets/glossary.template.yaml`

| Copy                                                                                                 | Section    | Diverges |
| ---------------------------------------------------------------------------------------------------- | ---------- | -------- |
| `plugins/standalone/ceh-every-session/skills/record-project-decisions/references/glossary-schema.md` | whole file | none     |
| `plugins/standalone/ceh-every-session/skills/record-project-decisions/references/glossary-model.py`  | whole file | none     |
| `plugins/standalone/ceh-every-session/skills/record-project-decisions/assets/glossary.template.md`   | whole file | none     |
| `plugins/standalone/ceh-every-session/skills/record-project-decisions/assets/glossary.template.yaml` | whole file | none     |

**Shared:** the `glossary/v1` layout and the `glossary/v2` YAML with its model. `maintain-glossary`
writes `GLOSSARY.yaml`, and `record-project-decisions` checks it with its own copy of the model
during Seed and reads its entries by key. `validate.py` fails when a copy differs from the
canonical file.

## Blog voice format

**Canonical:** whole files, `plugins/standalone/ceh-blog-and-seo/skills/draft-post/references/blog-voice-schema.md`, `plugins/standalone/ceh-blog-and-seo/skills/draft-post/references/blog-voice-model.py`, `plugins/standalone/ceh-blog-and-seo/skills/draft-post/assets/blog-voice.template.md`, `plugins/standalone/ceh-blog-and-seo/skills/draft-post/assets/blog-voice.template.yaml`

| Copy                                                                                   | Section    | Diverges |
| -------------------------------------------------------------------------------------- | ---------- | -------- |
| `plugins/standalone/ceh-blog-and-seo/skills/edit-post/references/blog-voice-schema.md` | whole file | none     |
| `plugins/standalone/ceh-blog-and-seo/skills/edit-post/references/blog-voice-model.py`  | whole file | none     |
| `plugins/standalone/ceh-blog-and-seo/skills/edit-post/assets/blog-voice.template.md`   | whole file | none     |
| `plugins/standalone/ceh-blog-and-seo/skills/edit-post/assets/blog-voice.template.yaml` | whole file | none     |

**Shared:** the `blog-voice/v1` layout and the `blog-voice/v2` YAML with its model. `draft-post`
captures the profile once and reads it on later runs, and `edit-post` checks it with its own copy
of the model and reads its sections by key. `validate.py` fails when a copy differs from the
canonical file.

## Business-plan "No human to answer" clause

**Canonical:** `plugins/standalone/ceh-product-direction/skills/develop-business-plan/SKILL.md` — § Rules, "No human to answer"

| Copy                                                                                  | Section                            | Diverges                                                   |
| ------------------------------------------------------------------------------------- | ---------------------------------- | ---------------------------------------------------------- |
| `plugins/standalone/ceh-product-direction/skills/sharpen-strategy/SKILL.md`           | § Stop conditions, last bullet     | adds: remove nothing in step 8, list the conflicts instead |
| `plugins/standalone/ceh-product-direction/skills/stress-test-unit-economics/SKILL.md` | § Stop conditions, last bullet     | none                                                       |
| `plugins/standalone/ceh-product-direction/skills/plan-go-to-market/SKILL.md`          | § Stop conditions, last bullet     | none                                                       |
| `plugins/standalone/ceh-product-direction/skills/run-premortem/SKILL.md`              | § Stop conditions, last bullet     | none                                                       |
| `plugins/standalone/ceh-product-direction/skills/set-operating-plan/SKILL.md`         | § Stop conditions, last bullet     | none                                                       |
| `plugins/standalone/ceh-product-direction/skills/find-product-market-fit/SKILL.md`    | § Edge Cases, "No human to answer" | takes its own "no questions" path and scores the PMF gate  |

**Shared:** with no human to answer, the skill asks nothing, drafts from what the plan holds, and
ends with the questions it would have asked, in order, each with the assumption it used instead.

## Usability persona set and severity scale

**Canonical:** `plugins/standalone/ceh-usability-audit/skills/audit-interface/references/personas-and-severity.md` — § The personas, § Severity

| Copy                                                                                                            | Section                                                             | Diverges                                                                                       |
| --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `plugins/standalone/ceh-usability-audit/skills/simulate-newcomer-first-run/references/personas-and-severity.md` | whole file                                                          | none                                                                                           |
| `plugins/standalone/ceh-usability-audit/README.md`                                                              | § The personas, § Severity — assigned by outcome, not by appearance | condensed for the reader: column wording differs, the five personas and four severities do not |
| `plugins/standalone/ceh-usability-audit/agents/newcomer-simulator.md`                                           | § Holding the persona                                               | the same five personas as second-person instructions to the walker, not a table                |

**Shared:** the five personas (Blank Slate, Cautious Returner, Interrupted, Wrong Turn, Small
Screen) with their constraints and the failure class each catches, the four severities (Blocker,
Detour, Friction, Polish) with their assignment conditions, and the rule that severity comes from
an observed walker outcome, with anything unobserved demoted to an unranked `Hypotheses` list. Each
audit skill carries its own copy of the file. The README and the agent keep
their own form because a reader and a walker each need a different one.

## AG-UI styling lock and canvas extensions

**Canonical:** `plugins/standalone/ceh-ag-ui/skills/build-ag-ui/assets/canvas-template/web/src/catalogue/define.ts` and `web/src/useAgent.ts` — `STYLE_KEY`, `defineComponent`, `render` (the enforced code)

| Copy                                                                | Section                                         | Diverges                                   |
| ------------------------------------------------------------------- | ----------------------------------------------- | ------------------------------------------ |
| `plugins/standalone/ceh-ag-ui/skills/build-ag-ui/SKILL.md`          | § The styling lock                              | the three layers, described                |
| `plugins/standalone/ceh-ag-ui/skills/add-canvas-component/SKILL.md` | § Schema, content only, § Component, theme only | the same rules at authoring time           |
| `plugins/standalone/ceh-ag-ui/skills/add-live-state-panel/SKILL.md` | § 3. Canvas side, § Rules                       | state is validated and styled the same way |
| `plugins/standalone/ceh-ag-ui/skills/add-human-approval/SKILL.md`   | § 2. Canvas side, § The approval card           | the approval card's fixed look             |

**Shared:** schemas carry content only (no `style`/`className`/`color`/`size`/`variant`…), a needed
visual choice is a semantic enum mapped to a theme class, agent output is rendered only after
`safeParse`, and components use theme tokens and classes only. `add-live-state-panel` and
`add-human-approval` also inline code that edits the template's `useAgent.ts` and the mock's
`respond`, so a change to the shape of the template's hook or mock goes to both skills' snippets.

## flow.yaml schema

**Canonical:** whole files, `plugins/standalone/ceh-workflow-builder/skills/build-agentic-workflow/references/flow-config-schema.md`, `plugins/standalone/ceh-workflow-builder/skills/build-agentic-workflow/references/run-state-schema.md`, `plugins/standalone/ceh-workflow-builder/skills/build-agentic-workflow/references/approval-schema.md`, `plugins/standalone/ceh-workflow-builder/skills/build-agentic-workflow/assets/run-state.template.md`, `plugins/standalone/ceh-workflow-builder/skills/build-agentic-workflow/assets/approval.template.md`, `plugins/standalone/ceh-workflow-builder/skills/build-agentic-workflow/references/run-state-model.py`, `plugins/standalone/ceh-workflow-builder/skills/build-agentic-workflow/assets/run-state.template.yaml`

| Copy                                                                                                  | Section    | Diverges |
| ----------------------------------------------------------------------------------------------------- | ---------- | -------- |
| `plugins/standalone/ceh-workflow-runner/skills/run-agentic-workflow/references/flow-config-schema.md` | whole file | none     |
| `plugins/standalone/ceh-workflow-runner/skills/run-agentic-workflow/references/run-state-schema.md`   | whole file | none     |
| `plugins/standalone/ceh-workflow-runner/skills/run-agentic-workflow/references/approval-schema.md`    | whole file | none     |
| `plugins/standalone/ceh-workflow-runner/skills/run-agentic-workflow/assets/run-state.template.md`     | whole file | none     |
| `plugins/standalone/ceh-workflow-runner/skills/run-agentic-workflow/assets/approval.template.md`      | whole file | none     |
| `plugins/standalone/ceh-workflow-runner/skills/run-agentic-workflow/references/run-state-model.py`    | whole file | none     |
| `plugins/standalone/ceh-workflow-runner/skills/run-agentic-workflow/assets/run-state.template.yaml`   | whole file | none     |

**Shared:** the entire `flow.yaml` contract: keys, stage kinds, validation rules, the run state
(`run-state-schema.md`): its `v1` layout and template, and `run-state/v2` with its model and YAML
template, the approval file (`approval-schema.md`) and its
template, and the `FLOW STATUS:` line. The canonical schemas sit beside `flow-config-schema.md` in
`build-agentic-workflow/references/`, and the canonical templates in its `assets/`.
The `copies` check fails when a template or schema differs from its copy. The builder writes and checks a config against it, the runner
checks it again before running, so a rule present in only one copy lets the builder emit a config
the runner rejects, or the reverse. Keep the two files byte-identical.

## Workflow spec: the nine questions

**Canonical:** `plugins/standalone/ceh-workflow-builder/skills/interview-workflow-task/SKILL.md` — § The nine questions, § How to ask, § The spec file

| Copy                                                                                                        | Section                                 | Diverges                                                                                                                                                           |
| ----------------------------------------------------------------------------------------------------------- | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `plugins/standalone/ceh-workflow-builder/skills/build-agentic-workflow/SKILL.md`                            | § Phase 1 — Intake                      | compact gate: one label per question plus what does not satisfy it, because it checks answers rather than eliciting them                                           |
| `plugins/standalone/ceh-workflow-builder/skills/interview-workflow-task/references/workflow-spec-schema.md` | § Sections, § Rules, § workflow-spec/v2 | what each of the nine headings holds, one line each, the step-numbering and `Declined` rules, and the nine `v2` keys with their states: the format, not how to ask |

**Shared:** the nine questions, their numbering, and that numbering carrying through to the nine
`v2` keys and the rendered `## 1.` to `## 9.` headings. Later sections of `build-agentic-workflow` cite them as "spec question
6/7/8/9", so renumbering means editing both files plus those citations. Five more things must change
in both files together:

- **Never answer for the user.** The interview must not record an obvious answer as the user's, and
  the builder must not turn an unanswered row into an assumption. Both wordings cover all nine rows
  and name the quiet row-4 case next to the loud 8/9 one.
- **The human go/no-go gate** is the one proof question 3 accepts that no command can settle. The
  interview records it and the builder's intake row 3 exempts it. Tightening one alone deadlocks a
  task with a real judgement step, because question 3 has no `Declined` escape.
- **The `Declined` marker.** The interview writes `state: declined` on a row the user refuses to
  answer and stops asking. The builder reads it as "take the conservative reading and stop delegating". The
  pair loops forever if only one of them knows the convention.
- **The closed heading set and `$CEH_WORKFLOW_BUILD_DIR`.** Neither skill may add a heading to the
  spec, and both name the variable and its `.agents_workspace/workflow/` default, because the interview has
  to work without the builder loaded.
- **The no-human path.** The interview leaves an unanswerable row recorded as unanswered with its
  question, and the builder's Headless build carries that row into the draft as `OPEN: spec row
<n>` and its closing questions. Neither fills it, and the builder never gives it the declined-row
  reading. If one skill starts filling open rows headless, the other's gate stops catching them.

## Quote or suppress (review findings)

**Canonical:** `plugins/standalone/ceh-git-workflow/skills/code-review/SKILL.md` — § Rules

| Copy                                                                                       | Section      | Diverges                                                                            |
| ------------------------------------------------------------------------------------------ | ------------ | ----------------------------------------------------------------------------------- |
| `plugins/standalone/ceh-check-build-against-plan/skills/check-build-against-plan/SKILL.md` | § Rules      | a Gap quotes the plan line it is missing; an unquoted finding goes under Unverified |
| `plugins/standalone/ceh-testing/skills/audit-test-suite/SKILL.md`                          | § Output     | an unquoted finding goes below the findings list                                    |
| `plugins/standalone/ceh-python-service/agents/python-service-reviewer.md`                  | § Hard rules | quotes the line from the head version; an unquoted finding goes under Dismissed     |
| `plugins/standalone/ceh-web-frontend/agents/web-frontend-reviewer.md`                      | § Hard rules | same as `python-service-reviewer`                                                   |

**Shared:** every finding quotes the code it is about, as `path:line` plus the line itself, and a
finding you cannot anchor to quoted code is reported as unverified, outside the findings.

## Judge from the code, not the brief

**Canonical:** `plugins/standalone/ceh-git-workflow/skills/code-review/SKILL.md` — § Rules + § Output (Cannot verify)

| Copy                                                                                       | Section                      | Diverges                                                                                                                                          |
| ------------------------------------------------------------------------------------------ | ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| `plugins/standalone/ceh-check-build-against-plan/skills/check-build-against-plan/SKILL.md` | § Rules + § Procedure step 3 | example brief names a part of the app; Cannot verify is a per-item status, not a verdict                                                          |
| `plugins/standalone/ceh-python-service/agents/python-service-reviewer.md`                  | § Hard rules + § Output      | Cannot verify is a list in the agent's report; the calling `code-review` gives the verdict; the brief cannot change whether a finding is reported |
| `plugins/standalone/ceh-web-frontend/agents/web-frontend-reviewer.md`                      | § Hard rules + § Output      | Cannot verify is a list in the agent's report; the calling `code-review` gives the verdict                                                        |

**Shared:** a brief that says "don't flag X" or "minor issues only" narrows where to look, never
how severe a finding is; every finding at its real severity; and a **Cannot verify** outcome that
names what would settle it.

## Pre-commit hooks (stack env skills)

**Canonical:** `plugins/standalone/ceh-python-service/skills/configure-python-service-env/SKILL.md` — § Pre-commit hooks + Procedure step 5

| Copy                                                                                 | Section                                                | Diverges                                                                                          |
| ------------------------------------------------------------------------------------ | ------------------------------------------------------ | ------------------------------------------------------------------------------------------------- |
| `plugins/standalone/ceh-python-library/skills/configure-python-library-env/SKILL.md` | § Pre-commit hooks + Procedure step 5                  | none                                                                                              |
| `plugins/standalone/ceh-web-frontend/skills/configure-bun-vite-env/SKILL.md`         | § Linting and quality checks, Pre-commit hook + step 5 | a committed `.githooks/pre-commit` via `core.hooksPath`, no package; runs `lint` + `format:check` |

**Shared:** lint and format run on every commit, installed once per clone; the whole-program check
(mypy, or `typecheck` + `check`) stays out of the hook and runs before the PR; never commit with
`--no-verify`.

## AI-writing tells

**Canonical:** `plugins/standalone/ceh-blog-and-seo/skills/edit-post/SKILL.md` — § 3. Edit, AI-writing tells

| Copy                                                                                                                 | Section    | Diverges                                |
| -------------------------------------------------------------------------------------------------------------------- | ---------- | --------------------------------------- |
| `plugins/standalone/ceh-documentation/skills/write-api-reference/references/docs-standard.md` (and its three copies) | § 8. Voice | drops "even when the author wrote them" |

**Shared:** the tells list word for word (stock words, stock frames, reflexive triplets,
signposting, the default em dash, the restating closer) and "replace with the specific thing, or
delete".

## Retro routing and report location

**Canonical:** `plugins/standalone/ceh-git-workflow/skills/review-recent-work/SKILL.md` — § Procedure step 6 + § Output, first paragraph

| Copy                                                                          | Section                                        | Diverges                                                                                                                                                                                                                                  |
| ----------------------------------------------------------------------------- | ---------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `plugins/standalone/ceh-session-learning/skills/diagnose-session/SKILL.md`    | § Procedure step 6 + § Output, first paragraph | routes root causes, not issues; a Claude Code cause is always out of scope; the committed file is scrubbed; file kind `session-<id-prefix>`                                                                                               |
| `plugins/standalone/ceh-every-session/skills/prevent-repeat-mistake/SKILL.md` | § Output, first paragraph                      | split save only, no route table; splits by where the fix lands; the committed file masks secrets; file kind `repeat-mistake`, saved as `.yaml` (`repeat-mistake/v2`) with the `.md` rendered beside it; `other_file` names the other YAML |

**Shared:** the route table word for word (bug to `find-root-cause`, feature or design to
`write-build-plan`, agent mistake to `prevent-repeat-mistake`, working rule to
`record-project-decisions`, anything else in the repo fixed directly, outside the repo left for the
user), acting on every in-scope route in the same session, an uninstalled route left open, and the
split save: in-scope issues committed to `product/retros/<YYYY-MM-DD>-<kind>.md`, out-of-scope ones
local in `.agents_workspace/product/retros/`, each file linking the other through its `other_file`
frontmatter field. Each skill keeps its own report template (`period-retro`, `session-retro`,
`repeat-mistake`), because the three reports differ.

## Eval case strictness levels

**Canonical:** `.claude/skills/add-plugin-component/SKILL.md` — § 6. Validate, the eval-cases paragraph and its three levels

| Copy                                      | Section                   | Diverges                                                                                                            |
| ----------------------------------------- | ------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `.claude/skills/evaluate-plugin/SKILL.md` | § Procedure steps 4 and 9 | condensed to one sentence per level; the failure reading sits in step 9's table, which adds grader and setup causes |

**Shared:** each positive case written at three strictness levels over the same task (supportive
names the moment, neutral gives the task only, competing adds a pull that tempts and never orders),
and the reading: failing at neutral points at the description, failing even at supportive points at
the body, failing at all three in a visible tool call is a hook candidate.

---

## Meridian theme (`brand.css`)

**Canonical:** `plugins/standalone/ceh-ui-design/skills/design-ui/references/meridian/brand.css` — the whole file

| Copy                                                                                     | Section    | Diverges |
| ---------------------------------------------------------------------------------------- | ---------- | -------- |
| `plugins/standalone/ceh-product-direction/skills/develop-business-plan/assets/brand.css` | whole file | none     |

**Shared:** the file byte for byte. `ceh-product-direction`'s HTML generator inlines its copy, because
a user may install the business plan without `ceh-ui-design`. The `copies` check keeps the two identical.

## Mermaid source rules

**Canonical:** `plugins/standalone/ceh-ui-design/skills/design-ui/SKILL.md` — § Finishing recipes, Diagrams (the four bullets from "Chain subgraphs" to "pass the CLI")

| Copy                                                                                                                                | Section                 | Diverges                                                                             |
| ----------------------------------------------------------------------------------------------------------------------------------- | ----------------------- | ------------------------------------------------------------------------------------ |
| `plugins/standalone/ceh-product-direction/skills/find-product-market-fit/references/business-plan-schema.md` (and its eight copies) | § Diagrams              | the page-only rules live in the page shell's code                                    |
| `plugins/standalone/ceh-documentation/skills/write-api-reference/references/docs-standard.md` (and its three copies)                | § 5, after the list     | none                                                                                 |
| `plugins/standalone/ceh-codebase-explanation/skills/document-architecture/SKILL.md`                                                 | § Rules, after the list | its render rule points to the last bullet and adds "say so when no renderer can run" |

**Shared:** the four rules that hold wherever a Mermaid diagram renders: chain subgraphs with `~~~`
and `direction LR`, gantt `tickInterval`, `xychart-beta` height in front matter, and validate with
the Mermaid CLI then look at the result. The page-only rules below them (`wrappingWidth: 200`,
`document.fonts.ready`, the fit rule, the size budget, the too-wide order, and the scroller rule)
stay in `design-ui` alone, because a Markdown file has no page to configure.

## Skill-started guard (`skill-started-guard.py`)

**Canonical:** `plugins/standalone/ceh-git-workflow/scripts/skill-started-guard.py` — the whole script

| Copy                                                            | Section          | Diverges                             |
| --------------------------------------------------------------- | ---------------- | ------------------------------------ |
| `plugins/standalone/ceh-testing/scripts/skill-started-guard.py` | the whole script | `RULES` holds only the test-file row |

**Shared:** everything outside `RULES`: `started()`, `subject()`, the
kill switches, the deny message, and the fail-open exit. Each copy keeps only its own plugin's rows
in `RULES`, so each plugin works installed alone. Check with
`diff <(sed '/^RULES = \[/,/^\]/d' <a>) <(sed '/^RULES = \[/,/^\]/d' <b>)`.

## Blog bundled files

**Canonical:** whole files, `plugins/standalone/ceh-blog-and-seo/skills/draft-post/references/ask-the-author.md`, `plugins/standalone/ceh-blog-and-seo/skills/draft-post/references/blog-draft-schema.md`, `plugins/standalone/ceh-blog-and-seo/skills/draft-post/assets/blog-draft.template.md`

| Copy                                                                                     | Section    | Diverges |
| ---------------------------------------------------------------------------------------- | ---------- | -------- |
| `plugins/standalone/ceh-blog-and-seo/skills/edit-post/references/ask-the-author.md`      | whole file | none     |
| `plugins/standalone/ceh-blog-and-seo/skills/edit-post/references/blog-draft-schema.md`   | whole file | none     |
| `plugins/standalone/ceh-blog-and-seo/skills/edit-post/assets/blog-draft.template.md`     | whole file | none     |
| `plugins/standalone/ceh-blog-and-seo/skills/repurpose-post/references/ask-the-author.md` | whole file | none     |

**Shared:** the ask-the-author question format and the blog draft format with its template. Each
skill that asks the author or writes a draft carries its own copy.

## Business plan format

**Canonical:** whole files, `plugins/standalone/ceh-product-direction/skills/find-product-market-fit/references/business-plan-schema.md`, `plugins/standalone/ceh-product-direction/skills/find-product-market-fit/assets/business-plan.template.md`, `plugins/standalone/ceh-product-direction/skills/find-product-market-fit/references/business-plan-model.py`, `plugins/standalone/ceh-product-direction/skills/find-product-market-fit/assets/business-plan.template.yaml`

| Copy                                                                                                            | Section    | Diverges |
| --------------------------------------------------------------------------------------------------------------- | ---------- | -------- |
| `plugins/standalone/ceh-product-direction/skills/develop-business-plan/references/business-plan-schema.md`      | whole file | none     |
| `plugins/standalone/ceh-product-direction/skills/develop-business-plan/assets/business-plan.template.md`        | whole file | none     |
| `plugins/standalone/ceh-product-direction/skills/plan-go-to-market/references/business-plan-schema.md`          | whole file | none     |
| `plugins/standalone/ceh-product-direction/skills/plan-go-to-market/assets/business-plan.template.md`            | whole file | none     |
| `plugins/standalone/ceh-product-direction/skills/review-business-plan/references/business-plan-schema.md`       | whole file | none     |
| `plugins/standalone/ceh-product-direction/skills/review-business-plan/assets/business-plan.template.md`         | whole file | none     |
| `plugins/standalone/ceh-product-direction/skills/run-premortem/references/business-plan-schema.md`              | whole file | none     |
| `plugins/standalone/ceh-product-direction/skills/run-premortem/assets/business-plan.template.md`                | whole file | none     |
| `plugins/standalone/ceh-product-direction/skills/set-operating-plan/references/business-plan-schema.md`         | whole file | none     |
| `plugins/standalone/ceh-product-direction/skills/set-operating-plan/assets/business-plan.template.md`           | whole file | none     |
| `plugins/standalone/ceh-product-direction/skills/sharpen-strategy/references/business-plan-schema.md`           | whole file | none     |
| `plugins/standalone/ceh-product-direction/skills/sharpen-strategy/assets/business-plan.template.md`             | whole file | none     |
| `plugins/standalone/ceh-product-direction/skills/stress-test-unit-economics/references/business-plan-schema.md` | whole file | none     |
| `plugins/standalone/ceh-product-direction/skills/stress-test-unit-economics/assets/business-plan.template.md`   | whole file | none     |
| `plugins/standalone/ceh-product-direction/skills/write-investor-materials/references/business-plan-schema.md`   | whole file | none     |
| `plugins/standalone/ceh-product-direction/skills/write-investor-materials/assets/business-plan.template.md`     | whole file | none     |
| `plugins/standalone/ceh-product-direction/skills/develop-business-plan/references/business-plan-model.py`       | whole file | none     |
| `plugins/standalone/ceh-product-direction/skills/develop-business-plan/assets/business-plan.template.yaml`      | whole file | none     |
| `plugins/standalone/ceh-product-direction/skills/plan-go-to-market/references/business-plan-model.py`           | whole file | none     |
| `plugins/standalone/ceh-product-direction/skills/plan-go-to-market/assets/business-plan.template.yaml`          | whole file | none     |
| `plugins/standalone/ceh-product-direction/skills/review-business-plan/references/business-plan-model.py`        | whole file | none     |
| `plugins/standalone/ceh-product-direction/skills/review-business-plan/assets/business-plan.template.yaml`       | whole file | none     |
| `plugins/standalone/ceh-product-direction/skills/run-premortem/references/business-plan-model.py`               | whole file | none     |
| `plugins/standalone/ceh-product-direction/skills/run-premortem/assets/business-plan.template.yaml`              | whole file | none     |
| `plugins/standalone/ceh-product-direction/skills/set-operating-plan/references/business-plan-model.py`          | whole file | none     |
| `plugins/standalone/ceh-product-direction/skills/set-operating-plan/assets/business-plan.template.yaml`         | whole file | none     |
| `plugins/standalone/ceh-product-direction/skills/sharpen-strategy/references/business-plan-model.py`            | whole file | none     |
| `plugins/standalone/ceh-product-direction/skills/sharpen-strategy/assets/business-plan.template.yaml`           | whole file | none     |
| `plugins/standalone/ceh-product-direction/skills/stress-test-unit-economics/references/business-plan-model.py`  | whole file | none     |
| `plugins/standalone/ceh-product-direction/skills/stress-test-unit-economics/assets/business-plan.template.yaml` | whole file | none     |
| `plugins/standalone/ceh-product-direction/skills/write-investor-materials/references/business-plan-model.py`    | whole file | none     |
| `plugins/standalone/ceh-product-direction/skills/write-investor-materials/assets/business-plan.template.yaml`   | whole file | none     |
| `plugins/standalone/ceh-blog-and-seo/skills/draft-post/references/business-plan-schema.md`                      | whole file | none     |
| `plugins/standalone/ceh-blog-and-seo/skills/draft-post/references/business-plan-model.py`                       | whole file | none     |
| `plugins/standalone/ceh-blog-and-seo/skills/draft-post/assets/business-plan.template.md`                        | whole file | none     |
| `plugins/standalone/ceh-blog-and-seo/skills/draft-post/assets/business-plan.template.yaml`                      | whole file | none     |
| `plugins/standalone/ceh-blog-and-seo/skills/write-project-listing-text/references/business-plan-schema.md`      | whole file | none     |
| `plugins/standalone/ceh-blog-and-seo/skills/write-project-listing-text/references/business-plan-model.py`       | whole file | none     |
| `plugins/standalone/ceh-blog-and-seo/skills/write-project-listing-text/assets/business-plan.template.md`        | whole file | none     |
| `plugins/standalone/ceh-blog-and-seo/skills/write-project-listing-text/assets/business-plan.template.yaml`      | whole file | none     |

**Shared:** the business plan format and its template. `find-product-market-fit` drafts the plan,
and every specialist reads it, so each of the nine skills carries a copy. `ceh-blog-and-seo:draft-post`
and `ceh-blog-and-seo:write-project-listing-text` read it for audience and positioning, and carry a copy to
check `BUSINESS_PLAN.yaml` before reading it.

## Competitor report page

**Canonical:** `plugins/standalone/ceh-competitor-analysis/skills/analyze-competitor/references/report-page.html` — whole file

| Copy                                                                                                | Section    | Diverges |
| --------------------------------------------------------------------------------------------------- | ---------- | -------- |
| `plugins/standalone/ceh-competitor-analysis/skills/compare-competitors/references/report-page.html` | whole file | none     |

**Shared:** the HTML page shell both reports fill, including its COMPARISON-ONLY blocks.

## Docs standard

**Canonical:** `plugins/standalone/ceh-documentation/skills/write-api-reference/references/docs-standard.md` — whole file

| Copy                                                                                                | Section    | Diverges |
| --------------------------------------------------------------------------------------------------- | ---------- | -------- |
| `plugins/standalone/ceh-documentation/skills/write-concept-docs/references/docs-standard.md`        | whole file | none     |
| `plugins/standalone/ceh-documentation/skills/write-guides-and-runbooks/references/docs-standard.md` | whole file | none     |
| `plugins/standalone/ceh-documentation/skills/write-project-docs/references/docs-standard.md`        | whole file | none     |

**Shared:** the one docs format every writing skill follows.

## Usability edit boundary

**Canonical:** `plugins/standalone/ceh-usability-audit/skills/audit-error-messages/SKILL.md` — § 5. Apply the rewrites, last two paragraphs

| Copy                                                                          | Section                                   | Diverges |
| ----------------------------------------------------------------------------- | ----------------------------------------- | -------- |
| `plugins/standalone/ceh-usability-audit/skills/audit-interface/SKILL.md`      | § 7. Report and loop, last two paragraphs | none     |
| `plugins/standalone/ceh-usability-audit/skills/write-plain-language/SKILL.md` | § Output, last two paragraphs             | none     |

**Shared:** the two paragraphs "Leave your edits in the working tree" (no branch, commit, push, or
pull request unless asked) and "Report other defects, do not fix them", word for word, in each
skill that edits the target.

## Update protocol

When changing a shared block:

1. Find the canonical file (named at the top of the entry).
2. Edit it first. It is the source of truth for the rule.
3. Propagate the change to every listed copy in the same commit.
4. Update this file if the scope of sharing changes.

Entry shape:

```markdown
## <Shared block name>

**Canonical:** `plugins/standalone/ceh-<plugin>/skills/<skill>/SKILL.md` — § <section>

| Copy                                                      | Section     | Diverges                               |
| --------------------------------------------------------- | ----------- | -------------------------------------- |
| `plugins/standalone/ceh-<plugin>/skills/<skill>/SKILL.md` | § <section> | <what deliberately differs, or "none"> |

**Shared:** <what must stay identical across every copy>.
```

A whole-file entry names every canonical file in full on its Canonical line, and each copy gets
its own row with one full path, Section `whole file` and Diverges `none`. The `copies` check
pairs each row with the canonical file of the same name and fails a row it cannot parse:

```markdown
**Canonical:** whole files, `plugins/standalone/ceh-<plugin>/skills/<skill>/references/<name>-schema.md`

| Copy                                                                               | Section    | Diverges |
| ---------------------------------------------------------------------------------- | ---------- | -------- |
| `plugins/standalone/ceh-<plugin>/skills/<other-skill>/references/<name>-schema.md` | whole file | none     |
```
