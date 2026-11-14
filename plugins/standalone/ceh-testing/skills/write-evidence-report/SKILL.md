---
name: write-evidence-report
description: >-
  Load before a product is launched or written about: roll the latest test, QA,
  performance, security, and usability results into one evidence report. Trigger on "are we ready
  to launch", "what have we proven", or before a blog post or listing about the product.
argument-hint: "[product or path]"
disable-model-invocation: false
user-invocable: true
compatibility: >-
  Needs git to pin the report to a commit. Running the test suite needs the project's own test
  runner; without it the Tests area is written as not run. Checking and rendering EVIDENCE.yaml,
  and checking the QA, performance, security and usability YAML it reads, needs uv; without it the
  files go unchecked and the Markdown is not rendered.
license: Apache-2.0
---

# Write the evidence report

Roll every Prove result into one file, `.agents_workspace/product/EVIDENCE.yaml`, that a later
stage reads instead of the scattered reports, with its `EVIDENCE.md` rendered beside it. Done
means a dated run for the current commit sits at the top of the file, every area has a status, and
every claim under Claims cites the result behind it.

The checks leave their reports in `.agents_workspace/product/`, dated, one folder each. A blog
post or a listing that needs "is it tested, fast, safe, usable?" cannot use them: none answers for
the product as a whole. This file is the one answer.

## Procedure

1. **Pin the commit.** Run `git rev-parse --short HEAD` and `git status --porcelain`. A dirty tree
   is named in the report, because results then describe code nobody can check out.
2. **Run the test suite once.** Find the command in the repo's `CLAUDE.md`, README, CI workflow, or
   manifest scripts, run it, and record the command and its summary line (passed, failed, skipped).
   This run is the task, so it needs no separate request. When it cannot run (missing service,
   secret, or runner), the Tests area is `not run` with the reason.
3. **Collect the latest result per area.** Read, newest first, and take one per area (per metric
   for performance, per target for usability):

   | Area        | Source                                                                                                                                                                                                                                              |
   | ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
   | QA          | `.agents_workspace/product/qa/<YYYYMMDD-HHMMSS>-<session-id>/QA_REPORT.yaml`, else its `.md`                                                                                                                                                        |
   | Performance | `.agents_workspace/product/perf/<metric>.yaml`, else its `.md`                                                                                                                                                                                      |
   | Security    | `.agents_workspace/product/security-audit/<YYYYMMDD-HHMMSS>-<session-id>-security-audit.yaml`, else its `.md`. A `*-security-audit` name is newer than every older `SECURITY_AUDIT-*` name, and within one form the last by file name is the newest |
   | Usability   | `.agents_workspace/product/ux-audits/<target>/run-<NNN>/UX_AUDIT.yaml` and `ERROR_MESSAGES.yaml`, else their `.md`                                                                                                                                  |
   | Plan        | each plan in `.agents_workspace/product/plans/` with status `building`, plus each `built` plan whose `## Record` has no Evidence line yet: phases `done` with evidence, and any check-against-plan findings                                         |

   With no such plan, the Plan area reads `none in flight`, not `not run`: nothing was skipped.
   Any other area with no source is
   `not run`, and names the skill that produces it: QA
   `ceh-testing:explore-app-for-bugs`, performance `ceh-testing:measure-performance`, security
   `ceh-security-audit:audit-codebase-security`, usability
   `ceh-usability-audit:simulate-newcomer-first-run`.

   When a report's `.yaml` sits beside its `.md`, read the YAML by key, never the Markdown: first
   run `uv run --script ${CLAUDE_SKILL_DIR}/scripts/artifact.py check <file>.yaml` (formats in
   `${CLAUDE_SKILL_DIR}/references/qa-report-schema.md`, `perf-report-schema.md`,
   `security-audit-schema.md`, `first-run-audit-schema.md`, `interface-audit-schema.md` and
   `error-messages-audit-schema.md`). On exit 1,
   the area is `not run`, naming the errors, because a broken report proves nothing. On exit 3,
   read that report's `.md` instead and say so, because its key paths may not hold. On exit 2, or
   without uv, say in the reply that the report went unchecked, and read the YAML anyway. The
   commit each ran against is `commit`. QA's bugs are `bugs`, each with `severity`, `status` and
   `fix`. Performance takes the last attempt in `attempts` whose `kept` is true, else the baseline
   `attempts.0`, with its `median`, `low`, `high`, the file's `unit` and `machine`. Security
   counts `findings` by `severity`, and its open issues are the `critical` and `high` ones, each
   with its `location`. A `UX_AUDIT.yaml` is a first-run or an interface audit, told apart by its
   `schema:` key, and `artifact.py` picks the model by it: keep the newest of each format per
   target. Both give `findings`, each with `severity`, and `gate` (`score`, `out_of`, `na`). The
   error-messages audit gives `rows`, each with `severity` and `applied`, and `harvested` and
   `already_complete`.

4. **Mark staleness.** For each result, find the commit it ran against (the report's `commit`, or
   take the last commit before its date). When `git log --oneline <that>..HEAD` is not empty, the
   area is `stale` with the commit count, because the code moved after the check. A QA report
   whose `bugs` hold any `fix` counts from its fix commits instead: the smallest
   `git rev-list --count <fix.commit>..HEAD` over them, skipping a `fix.commit` that
   `git cat-file -e <fix.commit>^{commit}` rejects, and with none left, from `commit`. The run made
   those commits and re-ran each bug after its fix, so they are not code that moved after the check.
5. **Write the claims.** List only what a reader outside the team may be told, each one sentence
   with the area and figure behind it: "All 212 tests pass at a1b2c3d", "p95 search latency 38 ms
   on <machine>". A `stale`, `not run`, or `open issues` area yields no positive claim about the
   thing it checks.
6. **Add the run at the top of `.agents_workspace/product/EVIDENCE.yaml`**, as the first item of `runs`, in the
   Output format. Never edit an earlier run: each one is what was proven at its commit, and a
   plan's Record cites it by date. With no file, copy the template. With only an `EVIDENCE.md`,
   move it first, as the schema's `evidence/v2` section says (a file in the older single-run
   layout becomes one run dated from its **Written** line). Before the edit, run
   `uv run --script ${CLAUDE_SKILL_DIR}/scripts/artifact.py check .agents_workspace/product/EVIDENCE.yaml`
   and stop on exit 1 with its errors. After the last edit, run it with `render`, which writes the
   `EVIDENCE.md` beside it, and fix the YAML for each error it lists. Never edit the generated
   `.md`. On exit 2 or 3, or without uv, say in the reply that the file went unchecked and
   unrendered.
7. **Record the evidence in each plan.** Append an Evidence line to the `## Record` of each plan in
   the Plan area: the run date, the short SHA, and every area that is not `passed`. A plan
   with a `<slug>.yaml` beside its `.md` is a `plan/v2` plan: read its status and Record from the
   YAML, not the `.md`, which can lag behind it, and append to the YAML's `record` list instead,
   as `date`, `event: Evidence`, and a quoted `details`, never editing the generated `.md`. When
   the `.md` did not change, because the hook that renders it
   (`ceh-build-plan`) is not installed, say so in the reply.

## Rules

- Every figure is copied from a report or this session's test run, never estimated, reworded, or
  softened. A critical security finding stays critical.
- The file stands alone. Copy the numbers in, because a later run replaces the source reports.
  Name the source path only as a pointer for the author.
- Never run the other checks from here. They are their own skills, and some need a running app or
  a person. Report them `not run` and name the skill.
- Open issues are listed, not judged: critical and high security findings, confirmed QA bugs not
  yet fixed, usability blockers, and plan items missing or failing their check.

## Output

`.agents_workspace/product/EVIDENCE.yaml` follows `assets/evidence.template.yaml`, per the
`evidence/v2` section of `references/evidence-schema.md`: a new file is a copy of it, and each run
adds one item at the top of `runs`. Its `EVIDENCE.md` is rendered from it in the layout of
`assets/evidence.template.md`.

## Stop conditions

- The test suite fails → still write the report with Tests `failed`, list the failures under Open
  issues, and make no Tests claim. A failed run is evidence too.
