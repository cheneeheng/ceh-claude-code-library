#!/usr/bin/env bash
set -euo pipefail
mkdir -p "$(dirname 'product/plans/notes-api.md')"
cat >'product/plans/notes-api.md' <<'EOF_FIXTURE'
---
schema: plan/v1
title: Notes API MVP
status: ready
created: 2026-10-20
---

## Goal

A small HTTP API where one user stores and searches short text notes.

## Scope

**In:**

- Create, list, and delete notes
- Search notes by keyword
- Export all notes as CSV

**Out:**

- Multi-user accounts: one user for the MVP

## Design

Python 3.12, FastAPI, SQLite. A note has `id`, `body`, and `created_at`.
Routes: `POST /notes`, `GET /notes`, `DELETE /notes/{id}`, `GET /notes/search?q=`.

## Phases

### Phase 1: Data model

- **Builds:** SQLite table `notes` with `id`, `text`, `created_at`
- **Check:** `pytest tests/test_db.py` passes
- **Status:** todo

### Phase 2: Routes

- **Builds:** `POST /notes`, `GET /notes`, `DELETE /notes/{id}`, `GET /notes/search`
- **Check:** the app starts
- **Status:** todo

## Open

TODO

## Record

- 2026-10-20 Planned: two phases
EOF_FIXTURE
