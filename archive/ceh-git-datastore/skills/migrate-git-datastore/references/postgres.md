# Loading into Postgres

## Create the schema

Apply the DDL from `gitexport.py infer --dialect postgres`, after reviewing it
against `schema-design.md`. Create the `projects` table first so foreign keys
have somewhere to point:

```sql
CREATE TABLE projects (
  id          text PRIMARY KEY,
  name        text,
  created_at  timestamptz NOT NULL,
  meta        jsonb
);
```

## Load the JSONL

Do not insert row by row. Stage the JSON, then transform in SQL — it is faster,
and it means a bad cast fails in one place rather than 10,000 times.

```sql
CREATE UNLOGGED TABLE stage_tasks (doc jsonb);
```

```bash
psql "$DB" -c "\copy stage_tasks (doc) FROM 'export/tasks.jsonl'"
```

`\copy` treats each line as one text field. If any record contains a literal tab
or backslash this will misparse, so set the format explicitly:

```bash
psql "$DB" -c "\copy stage_tasks (doc) FROM 'export/tasks.jsonl' WITH (FORMAT csv, QUOTE E'\x01', DELIMITER E'\x02')"
```

The control characters are placeholders that cannot appear in the JSON, which
effectively disables CSV quoting and delimiting. It looks odd and it is the
standard way to load JSONL through `\copy` without corruption.

`UNLOGGED` skips WAL for the staging table and is meaningfully faster. Drop it
afterwards.

## Transform into the real table

```sql
INSERT INTO tasks (project_id, id, created_at, updated_at, status, title, labels, extra)
SELECT
  doc->>'project_id',
  doc->>'id',
  (doc->>'created_at')::timestamptz,
  (doc->>'updated_at')::timestamptz,
  doc->>'status',
  doc->>'title',
  doc->'labels',
  doc - '{project_id,id,created_at,updated_at,status,title,labels}'::text[]
FROM stage_tasks
ON CONFLICT (project_id, id) DO UPDATE SET
  updated_at = EXCLUDED.updated_at,
  status     = EXCLUDED.status,
  title      = EXCLUDED.title,
  labels     = EXCLUDED.labels,
  extra      = EXCLUDED.extra;
```

Points worth noting:

- `doc - '{...}'::text[]` removes the promoted keys, so `extra` holds exactly
  what was not given a column. Listing them by hand drifts from the DDL; deriving
  by subtraction does not.
- `ON CONFLICT ... DO UPDATE` makes the load idempotent, so the same file can be
  replayed during catch-up without a separate code path.
- `doc->>'x'` yields NULL for both an absent key and a JSON null. That is the
  absent-vs-null collapse `infer` warns about, happening right here.

## Order of operations

Create indexes **after** the bulk load, not before — building once over a full
table is much faster than maintaining them per row:

```sql
-- load first, then:
CREATE INDEX CONCURRENTLY ON tasks (project_id, created_at DESC);
CREATE INDEX CONCURRENTLY ON tasks (project_id, status);
ANALYZE tasks;
```

`CONCURRENTLY` matters once the table is serving traffic. `ANALYZE` matters
immediately — without fresh statistics the planner will make poor choices on a
freshly loaded table and you will conclude the migration made things slower.

## Dump for verification

`verify.py` compares against what the database actually returns:

```bash
psql "$DB" -At -c \
  "SELECT row_to_json(t) FROM tasks t" > db_tasks.jsonl

python scripts/verify.py export/tasks.jsonl db_tasks.jsonl --unnest extra
```

`row_to_json` renders `timestamptz` as `+00:00` where git wrote `Z`; `verify.py`
normalises that, so any diff it reports is real.

## Types and gotchas

- **`jsonb` not `json`.** `json` stores the literal text including whitespace and
  duplicate keys; `jsonb` is parsed, deduplicated, and indexable. There is no
  reason to choose `json` here.
- **`timestamptz` not `timestamp`.** `timestamp` discards the offset, which
  silently reinterprets UTC data as local time.
- **Key order is not preserved in `jsonb`.** Never compare `jsonb` values as
  strings; compare them as `jsonb`.
- **Reserved words.** `user`, `order`, `group`, `check` need double quotes.
  Renaming during migration is usually better than quoting forever.
- **Empty string is not NULL** in Postgres, unlike in some engines. If the JSON
  has `""` and you expect NULL, coerce explicitly with `NULLIF`.
- **Statement timeouts.** A large `INSERT ... SELECT` can exceed a default
  `statement_timeout` on managed hosting. Raise it for the session or batch by
  project.

## Row-level security

Once `project_id` is a real column, tenant isolation can be enforced by the
database rather than remembered by every query:

```sql
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant ON tasks
  USING (project_id = current_setting('app.project_id', true));
```

Optional, and it does make debugging harder — an empty result set with no error
is confusing the first few times. Enable it deliberately, not by default, and
only after the migration is verified.
