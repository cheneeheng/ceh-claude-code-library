---
name: write-engineering-retro
description: >-
  Load this skill when looking back over a period of work in a repo: what shipped, how work flowed,
  and at most three changes, every claim tied to a commit or PR. Trigger on "write a retro", "what
  did we ship this week", "sprint retrospective", "how did the last month go".
argument-hint: "[since] [until]"
disable-model-invocation: false
user-invocable: true
compatibility: >-
  Requires the git CLI and a git working tree. The GitHub CLI (gh), authenticated, adds PR open and
  merge times and review counts. Without it, the retro uses merge commits only and says so.
license: Apache-2.0
---

# Write an engineering retro

Summarise a period of work from what the repository recorded, not from memory. Done means the
retro file is written and its path, headline numbers, and proposed changes are reported.

## Procedure

1. **Fix the period.** From `$ARGUMENTS`, otherwise from the day after the newest file in
   `.agents_workspace/retros/`, otherwise the last 14 days. State both dates in the retro.
2. **Collect the history.** Every number comes from a command, and the retro names the command:

   ```bash
   git log --since=<since> --until=<until> --no-merges --pretty='%h %ad %s' --date=short
   git log --since=<since> --until=<until> --merges --first-parent <default-branch> --pretty='%h %ad %s' --date=short
   git log --since=<since> --until=<until> --no-merges --name-only --pretty=format: | sort | uniq -c | sort -rn | head -10
   git log --since=<since> --until=<until> --grep='^Revert' --pretty='%h %s'
   ```

   With `gh`, add the merged PRs:
   `gh pr list --state merged --search "merged:<since>..<until>" --json number,title,createdAt,mergedAt,additions,deletions,reviews --limit 200`.

3. **Group what shipped** by Conventional Commits type and scope, or by top-level directory when
   the repo does not use them. One line per group, with the PRs or commits that make it up.
4. **Read the flow.** Compute only what the history supports: PRs merged, median and slowest time
   from open to merge, the largest diffs, reverts, fixes that touch a file changed earlier in the
   same period (a fix-of-a-fix), and the files changed most often (churn hotspots).
5. **Draw at most three changes.** Each one names the evidence that prompted it and one concrete
   action ("split PRs over 800 changed lines: #41 and #47 each took over 5 days to merge"). A
   change with no evidence behind it is left out.
6. **Save and report** per Output.

## Rules

- Facts from history only. Something the history cannot show (why a PR stalled, how the team felt)
  is a question in the retro, not a finding.
- Measure the work, not the people. No per-person counts, rankings, or blame. Commits per author
  measure nothing worth improving and invite gaming.
- A small number is reported as a count, not a trend. Three PRs are not a velocity.
- Merge commits, bots, and generated files (lockfiles, snapshots) are excluded from churn counts.

## Output

Save to `.agents_workspace/retros/<YYYYMMDD>-retro.md`, creating the directory if needed.

```markdown
# Retro <since> to <until>

## Shipped

- <type(scope)>: <one line> — #<PR>, #<PR>

## Flow

| Measure              | Value | From                       |
| -------------------- | ----- | -------------------------- |
| PRs merged           | <n>   | `gh pr list ...` or merges |
| Median time to merge | <d>   | PR createdAt to mergedAt   |
| Reverts              | <n>   | `git log --grep='^Revert'` |

Churn hotspots: `<path>` (<n> commits), ...

## Changes

1. <Action> — because <evidence with commit or PR>.

## Questions the history cannot answer

- <Question>
```
