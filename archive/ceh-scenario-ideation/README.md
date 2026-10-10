# ceh-scenario-ideation

CEH scenario bundle: shaping an idea before a stack is chosen — testing it for product-market fit and planning the build.

This plugin ships **no skills, agents, or hooks**. It is a scenario bundle: a manifest whose only
job is to name the set of `ceh-*` plugins that belong together for one situation, so you install
one thing instead of remembering a catalogue.

## Install

```
/plugin install ceh-scenario-ideation@ceh-claude-code-library --scope user
```

Its dependencies are resolved and installed automatically, and enabling this plugin enables all of
them at the same scope.

## What it pulls in

| Plugin               |
| -------------------- |
| `ceh-every-session`  |
| `ceh-git-workflow`   |
| `ceh-business-plan`  |
| `ceh-build-planning` |

## Route

The Shape stage of the lifecycle in [`docs/STRATEGY.md`](../../../docs/STRATEGY.md), plus the
first step of Build. Each step writes a committed file the next one reads. Nothing enforces the
order.

| Stage | Skill that fires                            | Reads                    | Writes              |
| ----- | ------------------------------------------- | ------------------------ | ------------------- |
| Shape | `ceh-business-plan:find-product-market-fit` | the idea, a conversation | `BUSINESS_PLAN.md`  |
| Build | `ceh-build-planning:write-build-plan`       | `BUSINESS_PLAN.md`       | `docs/plans/mvp.md` |

Next: a build bundle (`ceh-scenario-service`, `ceh-scenario-library`, or `ceh-scenario-webapp`)
builds from the plan. `ceh-build-planning` is here as the bridge, because whoever has just shaped
an idea usually wants the first plan straight after.

## Notes

- Disabling any plugin above is refused while this bundle is enabled. Disable the bundle first.
- Experimental plugins are deliberately **not** bundled. Install them on their own when you want
  them.
