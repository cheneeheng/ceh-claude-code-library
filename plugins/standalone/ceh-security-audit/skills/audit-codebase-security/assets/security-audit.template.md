---
schema: security-audit/v1
repo: <repo>
commit: <short commit>
date: YYYY-MM-DD
---

# Security audit: <repo> at <short commit>, <YYYY-MM-DD>

## Attack surface

<Entry points, trust boundaries, assets, and attackers from step 1.>

## Findings

| #   | Severity | Confidence | Category       | Attacker  | Location               | Attack                                    | Fix                                     |
| --- | -------- | ---------- | -------------- | --------- | ---------------------- | ----------------------------------------- | --------------------------------------- |
| 1   | high     | confirmed  | Access control | signed-in | `app/api/orders.py:52` | GET /orders/{id} returns any user's order | Filter by `owner_id == current_user.id` |

## Possible

<Leads that could not be traced end to end, each with what would settle it.>

## Not checked

<Each category or check not run, with the reason and the command that would run it.>
