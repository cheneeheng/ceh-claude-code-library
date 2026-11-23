---
schema: plugin-eval-report/v1
plugin: <plugin>
date: YYYY-MM-DD
criteria: <confirmed | unconfirmed>
ceiling_usd: <usd>
spend_usd: <usd>
---

# Eval: <plugin>

<summary>

## Results

### <component>

| Group                                    | Cases | Runs | Pass with | Pass without | Δ   | Noise floor | Cost  |
| ---------------------------------------- | ----- | ---- | --------- | ------------ | --- | ----------- | ----- |
| <must act \| must stay quiet \| outcome> | <n>   | <n>  | <n>/<n>   | <n>/<n>      | <Δ> | <floor>     | <usd> |

## Failures

- **<case>:** <cause>. "<grader explanation>"

## Fixes

| Fix      | Before  | After   | Kept        |
| -------- | ------- | ------- | ----------- |
| <change> | <n>/<n> | <n>/<n> | <yes \| no> |

## Unproven

- <item>
