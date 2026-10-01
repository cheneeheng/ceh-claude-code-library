---
name: design-postgresql-schema
description: >-
  Load this skill when designing or modifying a PostgreSQL schema: defining tables and columns,
  choosing column types (TIMESTAMPTZ, JSONB), adding indexes, or naming conventions. Auto-load
  whenever a table or column is added or a schema is designed. Not for query, transaction,
  connection-pool, and tenant-isolation code (use ceh-python-service:write-asyncpg-queries) or
  migration tooling and safety (use ceh-python-service:write-alembic-migration).
disable-model-invocation: false
user-invocable: true
compatibility: >-
  Requires a reachable PostgreSQL server (14+) and a client to reach it - `psql` for ad-hoc
  queries, `asyncpg` for the application path - plus `alembic` for the schema changes described
  here. None is assumed installed; PostgreSQL is a separate server, not a Python package.
license: Apache-2.0
---

# Design a PostgreSQL Schema

## Schema design

```sql
CREATE TABLE entities (
    entity_id      TEXT PRIMARY KEY,
    owner_id       TEXT NOT NULL,
    status         TEXT NOT NULL DEFAULT 'active',
    state_snapshot JSONB NOT NULL DEFAULT '{}',
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_entities_owner_id ON entities(owner_id);
CREATE INDEX idx_entities_status ON entities(status) WHERE status != 'deleted';
```

- `TIMESTAMPTZ` (not `TIMESTAMP`) for all timestamps. Store UTC; display local in UI.
- `JSONB` for flexible/evolving data. Typed columns for fields you filter or sort on.
- All names: `snake_case`. Table names: plural.
- Every user-owned table carries an `owner_id` column so queries can enforce tenant isolation (see `ceh-python-service:write-asyncpg-queries`).

## Access and migrations

- Query, transaction, connection-pool, and parameterized-query / tenant-isolation code lives in `ceh-python-service:write-asyncpg-queries`.
- Migration tooling, reversibility, and deploy-safety rules live in `ceh-python-service:write-alembic-migration` — schema changes are Alembic-managed, backward-compatible, and destructive changes are two-step (stop using, then drop).
