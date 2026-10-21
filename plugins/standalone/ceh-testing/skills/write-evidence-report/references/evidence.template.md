---
schema: evidence/v1
product: <product>
---

# Evidence: <product>

## YYYY-MM-DD at <short-sha>

**Tree:** clean | dirty (<n> files)

| Area        | Status                                          | Result                         | Checked at    |
| ----------- | ----------------------------------------------- | ------------------------------ | ------------- |
| Tests       | passed \| failed \| not run                     | `<command>`: <summary line>    | <sha>         |
| QA          | passed \| open issues \| stale (<n>) \| not run | <bugs found / fixed>           | <sha or date> |
| Performance | ...                                             | <metric>: <value> on <machine> | ...           |
| Security    | ...                                             | <counts by severity>           | ...           |
| Usability   | ...                                             | <blockers / friction counts>   | ...           |
| Plan        | ...                                             | <items built / missing>        | ...           |

### Open issues

- <area>: <issue, severity where the report gives one>. "None" when empty.

### Claims

- <one sentence a launch post may state> (<area>, <figure>)

### Not run

- <area>: <reason, and the skill that produces it>

<earlier sections follow, unchanged, newest first>
