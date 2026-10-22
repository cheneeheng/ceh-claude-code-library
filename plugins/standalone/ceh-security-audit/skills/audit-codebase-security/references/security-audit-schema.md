# Security audit schema

The report `audit-codebase-security` saves to
`.agents_workspace/security-audit/SECURITY_AUDIT-<YYYY-MM-DD>.md`, never a committed path. A new
report is a copy of `../assets/security-audit.template.md`, relative to this file. The
`schema: security-audit/v1` line stays as written.

## Frontmatter

- `repo`: the repo audited.
- `commit`: the short commit audited.
- `date`: the audit date.

## Sections

- **Attack surface:** the entry points, trust boundaries, assets, and attackers from step 1.
- **Findings:** one numbered row per finding. Severity is `critical`, `high`, `medium`, or `low`.
  Confidence is `confirmed` (traced end to end, or proven by a local test) or `likely`. Category is the class of hole. Attacker names who can reach it, because severity follows
  reachability. Location is a `path:line`. Attack says what the attacker does, and Fix the change
  that closes it. A row reads like
  `| 1 | high | confirmed | Access control | signed-in | app/api/orders.py:52 | GET /orders/{id} returns any user's order | Filter by owner_id == current_user.id |`.
- **Possible:** leads that could not be traced end to end, each with what would settle it.
- **Not checked:** each category or check not run, with the reason and the command that would run
  it.
