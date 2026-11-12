---
schema: evidence/v1
product: <product>
---

# Evidence: <product>

## YYYY-MM-DD at <short-sha>

**Tree:** <clean | dirty (<n> files)>

| Area        | Status   | Result                         | Checked at    |
| ----------- | -------- | ------------------------------ | ------------- |
| Tests       | <status> | `<command>`: <summary line>    | <sha>         |
| QA          | <status> | <bugs found / fixed>           | <sha or date> |
| Performance | <status> | <metric>: <value> on <machine> | <sha or date> |
| Security    | <status> | <counts by severity>           | <sha or date> |
| Usability   | <status> | <blockers / friction counts>   | <sha or date> |
| Plan        | <status> | <items built / missing>        | <sha or date> |

### Open issues

- <area>: <issue>

### Claims

- <claim> (<area>, <figure>)

### Not run

- <area>: <reason>, <skill>
