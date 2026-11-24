# ceh-testing design notes

Maintainer detail moved out of the plugin README on 2026-11-24, when the README was rewritten for
the person installing the plugin. The site does not publish this file.

## Hook wiring

| Hook                     | Event                                        | Script                    | Default |
| ------------------------ | -------------------------------------------- | ------------------------- | ------- |
| Skill-started guard      | `PreToolUse` (`Edit`, `Write`, `MultiEdit`)  | `skill-started-guard.py`  | on      |
| Evidence render          | `PostToolUse` (`Edit`, `Write`, `MultiEdit`) | `artifact-render-hook.py` | on      |
| Generated Markdown guard | `PreToolUse` (`Edit`, `Write`, `MultiEdit`)  | `generated-md-guard.py`   | on      |

The skill-started guard needs `python3` on PATH (stdlib only) and fails open without it.

## Evidence render and generated Markdown guard

`write-evidence-report` saves `.agents_workspace/product/EVIDENCE.yaml` (`evidence/v2`), `explore-app-for-bugs`
saves `QA_REPORT.yaml` (`qa-report/v2`), and `measure-performance` saves `<metric>.yaml`
(`perf-report/v2`). After every write to one, the render hook checks the YAML against its model
through `uv` and renders the Markdown beside it, or reports each error back to the agent and leaves
the Markdown as it was. It checks a `<YYYYMMDD-HHMMSS>-<session-id>-security-audit.yaml`, `UX_AUDIT.yaml` and
`ERROR_MESSAGES.yaml` too, through `write-evidence-report`'s copies of their models, so with
`ceh-security-audit` or `ceh-usability-audit` installed an error in one is reported by both
plugins. `test-a-bug-fix` completes or creates a fix record, `.agents_workspace/product/fix/<YYYYMMDD-HHMMSS>-<slug>.yaml`
(`fix-record/v3`), which the hook checks through the skill's model too, as `ceh-coding-conduct`'s
does. `audit-test-suite` saves its audit as a `.yaml` in `.agents_workspace/product/audit/test/`
(`test-audit/v2`), which the hook checks and renders too.

## Skill checks

Moved from the README Skills table on 2026-11-24.

- `write-test-first`: It worked if each slice in the hand-over quotes the failure seen before its code existed.
- `measure-performance`: It worked if every number is a median with its spread and a kept change clears the noise band.
- `explore-app-for-bugs`: It worked if the QA report lists each bug as confirmed or unconfirmed with its steps and evidence.
- `write-evidence-report`: It worked if every area shows passed, open issues, stale, or not run, and every claim names its figure.

## Why the out-of-scope list exists

Listed so a gap reads as a decision rather than an oversight.
