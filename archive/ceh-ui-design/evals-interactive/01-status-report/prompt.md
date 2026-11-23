---
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
runs: 3
---

make a single html page for this project status report, it has to stay one file so i can email it. save it as report.html

# Atlas migration: status report, November

## Summary

The migration of the billing service to the new cluster is 70% done. Two of five services are live on the new cluster. We are one week behind the plan because of the database cutover.

## Progress

### Done

- Auth service moved and live since 3 Nov.
- Notifications service moved and live since 10 Nov.

### In progress

- Billing service: data copy running, cutover planned for 28 Nov.

### Not started

- Reporting service.
- Admin service.

## Risks

### Database cutover

The billing database needs a 30-minute write freeze. Finance has not yet agreed a window.

### Staff

One of three engineers is on leave from 1 to 12 Dec.

## Budget

Spent 41,000 EUR of 60,000 EUR. Forecast at completion: 58,500 EUR.

## Decisions needed

1. Agree the billing write-freeze window with Finance by 21 Nov.
2. Decide whether reporting moves before or after the holidays.

## Next steps

- Run the billing cutover rehearsal on 24 Nov.
- Start the reporting service move on 1 Dec.
