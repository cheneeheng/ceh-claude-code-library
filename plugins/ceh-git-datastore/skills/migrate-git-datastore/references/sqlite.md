# Loading into SQLite

For a single-node app, SQLite is frequently the right target and the migration is
an afternoon rather than a week. It keeps the operational model of the git store
— it is a file you back up by copying — while adding indexes, joins, aggregates,
constraints, and full-text search.

## Configure the database

```sql
PRAGMA journal_mode = WAL;      -- readers do not block the writer
PRAGMA synchronous  = NORMAL;   -- sensible durability/throughput with WAL
PRAGMA foreign_keys = ON;       -- OFF by default; must be set per connection
PRAGMA busy_timeout = 5000;     -- wait rather than fail on a locked write
```

`foreign_keys = ON` is per connection, not per database. Set it in the connection
factory or the constraints silently do nothing — which is a familiar failure,
since it is the same "nothing enforces this" property you just migrated away from.

WAL mode is what makes SQLite viable for a web app: readers and the writer no
longer block each other. Note it still allows only **one writer at a time**, so
if the migration trigger was write contention, SQLite will not solve it.

## Schema

Use the DDL from `gitexport.py infer --dialect sqlite`, plus:

```sql
CREATE TABLE projects (
  id          text PRIMARY KEY,
  name        text,
  created_at  text NOT NULL,
  meta        text
);
```

Timestamps as `text` in ISO-8601 UTC sort and compare correctly as strings, which
is why the format discipline from the git store matters. Do not switch to Unix
epochs during migration — it makes every row unreadable in a shell and buys
nothing.

`STRICT` tables (SQLite 3.37+) enforce declared types instead of accepting
anything. Worth using: the reason you are here is partly that nothing enforced
types before.

```sql
CREATE TABLE tasks (
  project_id text NOT NULL,
  id         text NOT NULL,
  created_at text NOT NULL,
  status     text NOT NULL,
  title      text NOT NULL,
  extra      text,
  PRIMARY KEY (project_id, id)
) STRICT;
```

## Load

One transaction for the whole load. Without it SQLite commits per statement and
the load is orders of magnitude slower.

```python
import json, sqlite3

con = sqlite3.connect("app.db")
con.execute("PRAGMA journal_mode=WAL")
COLS = ["project_id", "id", "created_at", "updated_at", "status", "title"]


def rows(path):
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        extra = {k: v for k, v in r.items() if k not in COLS}
        yield [r.get(c) for c in COLS] + [json.dumps(extra, sort_keys=True)]


with con:  # one transaction
    con.executemany(
        f"INSERT INTO tasks ({','.join(COLS)},extra) "
        f"VALUES ({','.join('?' * len(COLS))},?) "
        f"ON CONFLICT(project_id,id) DO UPDATE SET "
        f"  updated_at=excluded.updated_at, status=excluded.status, "
        f"  title=excluded.title, extra=excluded.extra",
        rows("export/tasks.jsonl"),
    )
con.execute("ANALYZE")
```

`ON CONFLICT DO UPDATE` makes it idempotent so the same file can be replayed
during catch-up. Create indexes after the load, then `ANALYZE`.

## Dump for verification

```bash
sqlite3 -json app.db "SELECT * FROM tasks" \
  | python3 -c "import json,sys; [print(json.dumps(r)) for r in json.load(sys.stdin)]" \
  > db_tasks.jsonl

python scripts/verify.py export/tasks.jsonl db_tasks.jsonl --unnest extra
```

`--unnest extra` parses the JSON text column back into fields. `verify.py`
handles `extra` being a JSON _string_ here rather than a native object as in
Postgres.

## Full-text search

If search was the migration trigger, FTS5 is often the entire reason to move and
it is a few lines:

```sql
CREATE VIRTUAL TABLE tasks_fts USING fts5(
  title, body, content='tasks', content_rowid='rowid'
);
INSERT INTO tasks_fts(rowid, title, body) SELECT rowid, title, body FROM tasks;
```

Keep it in sync with triggers on insert/update/delete, or rebuild periodically.

## Gotchas

- **Type affinity.** Without `STRICT`, SQLite stores a string in an `integer`
  column without complaint. Given type drift is the most common problem in these
  migrations, use `STRICT`.
- **`ALTER TABLE` is limited.** Adding a column is fine; changing or dropping one
  historically meant recreating the table. Get the schema right during migration
  while it is cheap.
- **One writer.** WAL allows concurrent readers, not concurrent writers.
- **The file is the database.** Back up with `sqlite3 app.db ".backup out.db"` or
  the online backup API — not `cp` on a live database, which can capture a torn
  file.
- **No native array or JSON type.** JSON lives in `text`; the `json_*()` functions
  query it. `json_extract(extra,'$.due_date')` works and can even be indexed via
  a generated column, but if you are doing that often the field wanted a column.
