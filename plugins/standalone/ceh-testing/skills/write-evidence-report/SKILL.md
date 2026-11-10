---
name: write-evidence-report
description: >-
  Load before a product is launched or written about: roll the latest test, QA,
  performance, security, and usability results into product/EVIDENCE.md. Trigger on "are we ready
  to launch", "what have we proven", or before a blog post or listing about the product.
argument-hint: "[product or path]"
disable-model-invocation: false
user-invocable: true
compatibility: >-
  Needs git to pin the report to a commit. Running the test suite needs the project's own test
  runner; without it the Tests area is written as not run. Checking and rendering EVIDENCE.yaml,
  and checking the QA, performance and security YAML it reads, needs uv; without it the files go unchecked
  and the Markdown is not rendered.
license: Apache-2.0
---

# Write the evidence report

Roll every Prove result into one committed file, `product/EVIDENCE.md`, that a later stage reads
instead of the scattered reports. Done means a dated section for the current commit sits at the top
of the file, every area has a status, and every claim under Claims cites the result behind it.

The checks leave their reports in the git-ignored `.agents_workspace/`, dated, one folder each. A
blog post or a listing that needs "is it tested, fast, safe, usable?" cannot use them: they vanish
on a fresh clone and none answers for the product as a whole. This file is the one answer.

## Procedure

1. **Pin the commit.** Run `git rev-parse --short HEAD` and `git status --porcelain`. A dirty tree
   is named in the report, because results then describe code nobody can check out.
2. **Run the test suite once.** Find the command in the repo's `CLAUDE.md`, README, CI workflow, or
   manifest scripts, run it, and record the command and its summary line (passed, failed, skipped).
   This run is the task, so it needs no separate request. When it cannot run (missing service,
   secret, or runner), the Tests area is `not run` with the reason.
3. **Collect the latest result per area.** Read, newest first, and take one per area (per metric
   for performance, per target for usability):

   | Area        | Source                                                                                                                                                                                    |
   | ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
   | QA          | `.agents_workspace/product/qa/<timestamp>/QA_REPORT.yaml`, else its `.md`                                                                                                                 |
   | Performance | `.agents_workspace/product/perf/<metric>.yaml`, else its `.md`                                                                                                                            |
   | Security    | `.agents_workspace/product/security-audit/SECURITY_AUDIT-<date>.yaml`, else its `.md`                                                                                                     |
   | Usability   | `.agents_workspace/product/ux-audits/<target>/run-<NNN>/UX_AUDIT.md` and `ERROR_MESSAGES.md`                                                                                              |
   | Plan        | each plan in `product/plans/` with status `building`, plus each `built` plan whose `## Record` has no Evidence line yet: phases `done` with evidence, and any check-against-plan findings |

   With no such plan, the Plan area reads `none in flight`, not `not run`: nothing was skipped.
   Any other area with no source is
   `not run`, and names the skill that produces it: QA
   `ceh-testing:explore-app-for-bugs`, performance `ceh-testing:measure-performance`, security
   `ceh-security-audit:audit-codebase-security`, usability
   `ceh-usability-audit:simulate-newcomer-first-run`.

   When a report's `.yaml` sits beside its `.md`, read the YAML by key, never the Markdown: first
   run `uv run --script ${CLAUDE_SKILL_DIR}/scripts/artifact.py check <file>.yaml` (formats in
   `${CLAUDE_SKILL_DIR}/references/qa-report-schema.md`, `perf-report-schema.md` and
   `security-audit-schema.md`). On exit 1,
   the area is `not run`, naming the errors, because a broken report proves nothing. On exit 3,
   read that report's `.md` instead and say so, because its key paths may not hold. On exit 2, or
   without uv, say in the reply that the report went unchecked, and read the YAML anyway. The
   commit each ran against is `commit`. QA's bugs are `bugs`, each with `severity`, `status` and
   `fix`. Performance takes the last attempt in `attempts` whose `kept` is true, else the baseline
   `attempts.0`, with its `median`, `low`, `high`, the file's `unit` and `machine`. Security
   counts `findings` by `severity`, and its open issues are the `critical` and `high` ones, each
   with its `location`.

4. **Mark staleness.** For each result, find the commit it ran against (the report's `commit`, or
   take the last commit before its date). When `git log --oneline <that>..HEAD` is not empty, the
   area is `stale` with the commit count, because the code moved after the check.
5. **Write the claims.** List only what a reader outside the team may be told, each one sentence
   with the area and figure behind it: "All 212 tests pass at a1b2c3d", "p95 search latency 38 ms
   on <machine>". A `stale`, `not run`, or `open issues` area yields no positive claim about the
   thing it checks.
6. **Add the run at the top of `product/EVIDENCE.yaml`**, as the first item of `runs`, in the
   Output format. Never edit an earlier run: each one is what was proven at its commit, and a
   plan's Record cites it by date. With no file, copy the template. With only an `EVIDENCE.md`,
   move it first, as the schema's `evidence/v2` section says (a file in the older single-run
   layout becomes one run dated from its **Written** line). Before the edit, run
   `uv run --script ${CLAUDE_SKILL_DIR}/scripts/artifact.py check product/EVIDENCE.yaml` and stop on
   exit 1 with its errors. After the last edit, run it with `render`, which writes
   `product/EVIDENCE.md`, and fix the YAML for each error it lists. Never edit the generated `.md`.
   On exit 2 or 3, or without uv, say in the reply that the file went unchecked and unrendered.
   Commit both files with the change they describe or on their own.
7. **Record the evidence in each plan.** Append an Evidence line to the `## Record` of each plan in
   the Plan area: the section date, the short SHA, and every area that is not `passed`. A plan
   with a `<slug>.yaml` beside its `.md` is a `plan/v2` plan: read its status and Record from the
   YAML, not the `.md`, which can lag behind it, and append to the YAML's `record` list instead,
   as `date`, `event: Evidence`, and a quoted `details`, never editing the generated `.md`. Commit
   both files. When the `.md` did not change, because the hook that renders it
   (`ceh-build-planning`) is not installed, say so in the reply.

## Rules

- Every figure is copied from a report or this session's test run, never estimated, reworded, or
  softened. A critical security finding stays critical.
- The file stands alone. Copy the numbers in: a link into `.agents_workspace/` breaks on any clone
  but the author's. Name the source path only as a pointer for the author.
- Never run the other checks from here. They are their own skills, and some need a running app or
  a person. Report them `not run` and name the skill.
- Open issues are listed, not judged: critical and high security findings, confirmed QA bugs not
  yet fixed, usability blockers, and plan items missing or failing their check.

## Output

`product/EVIDENCE.yaml` follows `assets/evidence.template.yaml`, per the `evidence/v2` section of
`references/evidence-schema.md`: a new file is a copy of it, and each run adds one item at the top
of `runs`. `product/EVIDENCE.md` is rendered from it in the layout of `assets/evidence.template.md`.

## Stop conditions

- The test suite fails → still write the report with Tests `failed`, list the failures under Open
  issues, and make no Tests claim. A failed run is evidence too.
