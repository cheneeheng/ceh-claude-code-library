# ceh-scenario-editorial

CEH scenario bundle: writing and publishing what readers see — blog posts, user and operator docs, discoverability.

This plugin ships **no skills, agents, or hooks**. It is a scenario bundle: a manifest whose only
job is to name the set of `ceh-*` plugins that belong together for one situation, so you install
one thing instead of remembering a catalogue.

## Install

```
/plugin install ceh-scenario-editorial@ceh-claude-code-library --scope user
```

Its dependencies are resolved and installed automatically, and enabling this plugin enables all of
them at the same scope.

## What it pulls in

| Plugin              |
| ------------------- |
| `ceh-every-session` |
| `ceh-git-workflow`  |
| `ceh-blog`          |
| `ceh-documentation` |
| `ceh-seo`           |

## Route

The Tell stage of the lifecycle in [`docs/STRATEGY.md`](../../../docs/STRATEGY.md). It reads what
earlier stages committed and writes what readers see. Nothing enforces the order.

| Stage | Skill that fires                       | Reads                                  | Writes                        |
| ----- | -------------------------------------- | -------------------------------------- | ----------------------------- |
| Tell  | `ceh-blog:draft-post`                  | `BUSINESS_PLAN.md`, `docs/EVIDENCE.md` | a post                        |
| Tell  | `ceh-seo:write-project-listing-text`   | `BUSINESS_PLAN.md`, `docs/EVIDENCE.md` | README first screen, listings |
| Tell  | `ceh-seo:make-page-crawlable`          | the site                               | page markup                   |
| Tell  | `ceh-documentation:write-project-docs` | the code                               | user and operator docs        |

Before: `BUSINESS_PLAN.md` comes from `ceh-scenario-ideation`, and `docs/EVIDENCE.md` from
`ceh-testing:write-evidence-report` in a build bundle. Without them the skills still run and say
which claims rest on nothing proven.

## Notes

- Disabling any plugin above is refused while this bundle is enabled. Disable the bundle first.
- Experimental plugins are deliberately **not** bundled. Install them on their own when you want
  them.
