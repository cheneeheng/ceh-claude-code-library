---
name: write-asyncpg-queries
description: >-
  Load this skill when writing asyncpg database code: parameterized queries, tenant isolation
  (owner_id filtering), atomic transactions, connection pool configuration, or raw SQL patterns.
  Auto-load whenever asyncpg is imported, a SQL query is written, or a database transaction is
  needed.
disable-model-invocation: false
user-invocable: true
compatibility: >-
  Requires Python 3.12+ with the `asyncpg` driver installed as a project dependency (via `uv
  sync`), and a reachable PostgreSQL server with a valid `DATABASE_URL`. Neither the driver nor a
  database server is assumed to be present.
license: Apache-2.0
---

# Write asyncpg Queries

Use **asyncpg** directly — no ORM. Explicit SQL with parameterized queries.

## Queries

```python
row = await conn.fetchrow(
    "SELECT session_id, topic FROM sessions WHERE session_id = $1", session_id
)
```

## Tenant isolation

Every query on user-owned data must filter by the owning user's ID. One user's data must never be reachable by another.

```python
await conn.fetchrow(
    "SELECT * FROM resources WHERE resource_id = $1 AND owner_id = $2",
    resource_id,
    current_user_id,
)
```

## Atomic transactions

Use transactions for all multi-step writes:

```python
async with pool.acquire() as conn:
    async with conn.transaction():
        await conn.executemany(
            "INSERT INTO order_items (order_id, sku, qty) VALUES ($1, $2, $3)",
            [(order_id, i.sku, i.qty) for i in items],
        )
        await conn.execute(
            "UPDATE orders SET total = $1, updated_at = NOW() WHERE order_id = $2",
            new_total,
            order_id,
        )
```

## Connection pool

```python
pool = await asyncpg.create_pool(
    dsn=settings.database_url,
    min_size=5,
    max_size=20,
    command_timeout=30,
)
```

Create the pool in the FastAPI lifespan function and expose it via `app.state.db_pool`. Never create a pool per request.
