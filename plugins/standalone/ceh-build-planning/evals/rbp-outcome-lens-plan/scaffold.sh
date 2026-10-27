#!/usr/bin/env bash
set -euo pipefail
mkdir -p "$(dirname 'product/plans/habit-tracker.md')"
cat >'product/plans/habit-tracker.md' <<'EOF_FIXTURE'
---
schema: plan/v1
title: Habit tracker MVP
status: ready
created: 2026-10-20
---

## Goal

Signed-in users track their daily habits in a web app and get one reminder email each morning for
the habits they have not done yet.

## Scope

**In:**

- Sign in with an email magic link
- Create, list, and archive habits
- Mark a habit done for today
- A daily reminder email listing the habits not yet done
- A dark mode toggle

**Out:**

- Mobile apps: the web app works on phones
- Streak statistics: not needed to track a habit

## Design

Python 3.12, FastAPI with Jinja templates, Postgres. Tables: `users` (`id`, `email`), `habits`
(`id`, `user_id`, `name`, `archived_at`), `checkins` (`id`, `habit_id`, `day`). Routes:
`GET /habits` renders the habits page, `POST /habits`, `POST /habits/{id}/archive`,
`POST /habits/{id}/done`. Email goes through Postmark, key in `POSTMARK_TOKEN`. Migrations with
Alembic.

## Phases

### Phase 1: Data model and sign-in

- **Builds:** the `users`, `habits`, and `checkins` tables, magic-link sign-in
- **Check:** `pytest tests/test_auth.py` passes
- **Status:** todo

### Phase 2: Habits page

- **Builds:** `GET /habits` listing the user's habits with a Done button each, `POST /habits`,
  `POST /habits/{id}/archive`, `POST /habits/{id}/done`
- **Check:** creating a habit and clicking Done shows it as done for today
- **Status:** todo

### Phase 3: Reminders

- **Builds:** `app/remind.py`, run by cron at 08:00, sends each user one email listing their
  habits with no check-in today. When a send fails, the cron job re-runs, up to three times.
- **Check:** running `python -m app.remind` sends an email to a test user
- **Status:** todo

### Phase 4: Dark mode

- **Builds:** a dark mode toggle in the page header, the choice stored in a cookie
- **Check:** clicking the toggle switches the page colours
- **Status:** todo

## Open

None.

## Record

- 2026-10-20 Planned: four phases
EOF_FIXTURE
