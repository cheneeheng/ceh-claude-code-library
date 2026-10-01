# Designing the target schema

`gitexport.py infer` proposes DDL from the records that actually exist. This is
how to read that proposal and decide what to change.

## Read the profile before the DDL

The profile is the more useful half of the output. For each field it reports how
often it is present, how often it is null, how many distinct values it has, and
which JSON types appear:

```
field            present   null  distinct  types                 ->
assignee            88%    189         4  str:873,null:189      extra
created_at         100%      0      200+  str:1200              column
due_date            25%      0         9  str:297               extra
points              98%      0        10  int:1138,str:32       extra
status             100%      0         3  str:1200              column
```

Four readings from that:

- `points` shows two types. Nothing about the schema is decidable until that is
  fixed at the source.
- `due_date` at 25% is almost certainly a recently added field, not an optional
  one. It probably wants to be a nullable column, not buried in `extra`.
- `status` with 3 distinct values across 1,200 records is an index candidate, and
  possibly a CHECK constraint or enum.
- `assignee` is absent in some records and explicitly null in others. Someone has
  to decide whether that distinction ever meant anything.

## Column or JSONB

Default rule: a field present in ≥95% of records with one consistent type becomes
a real column. Everything else goes into a single `extra` JSONB column.

Override the rule in three cases:

- **You filter, sort, or join on it → column, always.** Even at 20% presence.
  A nullable column with an index beats a JSONB field you cannot index usefully.
- **It is genuinely sparse and never queried → `extra`.** Even at 99% presence.
  Per-tenant custom fields belong here.
- **Type drift → fix it, then decide.** A drifted field should not be promoted;
  fix the source, re-run `infer`, and let it become a column properly. Leaving it
  in `extra` is a workaround, not an answer.

The trap is treating `extra` as a place to defer decisions. Every field in there
is invisible to the query planner and to anyone reading the schema. Deciding
later is much more expensive than deciding now, because by then application code
depends on the JSON path.

## Keys and tenancy

`project_id` was implicit in the ref name and does not exist inside the records —
the export injects it. Two consequences:

- **The primary key is `(project_id, id)`.** Ids were unique within a project,
  never globally. Assuming global uniqueness is how you get a key violation
  partway through a backfill.
- **Every index leads with `project_id`.** Every query in a per-tenant app is
  scoped to one tenant, and an index that does not lead with the scoping column
  will not be used for those queries.

Keep the ULIDs as `text` (or `uuid` if you migrate the format deliberately). Do
not replace them with a serial integer: the ids are already in URLs, logs,
exports, and cross-references, and swapping them means rewriting all of those
during the one operation where you most want stable identifiers.

Row-level security in Postgres is worth considering once `project_id` is a real
column — it turns tenant isolation from a thing every query must remember into a
thing the database enforces. It is optional and adds debugging friction; decide
deliberately.

## Types

| JSON               | Postgres                            | SQLite                            |
| ------------------ | ----------------------------------- | --------------------------------- |
| string             | `text`                              | `text`                            |
| ISO-8601 timestamp | `timestamptz`                       | `text` (ISO-8601 sorts correctly) |
| integer            | `bigint`                            | `integer`                         |
| float              | `double precision`                  | `real`                            |
| bool               | `boolean`                           | `integer`                         |
| array              | `jsonb`, or `text[]` if homogeneous | `text` (JSON)                     |
| object             | `jsonb`                             | `text` (JSON)                     |

Two notes. Store timestamps as `timestamptz`, not `text` — otherwise every date
filter is a string comparison and every index on it is nearly useless. And
`bigint` over `integer` for anything countable: the cost is nothing and the
overflow is embarrassing.

## Indexes

Start with these and add more from measured slow queries:

```sql
-- listing a collection newest-first
CREATE INDEX ON tasks (project_id, created_at DESC);

-- filtering on a low-cardinality field
CREATE INDEX ON tasks (project_id, status);

-- foreign-key-ish lookups
CREATE INDEX ON comments (project_id, task_id);
```

Do not add an index duplicating `(project_id, id)` — the primary key already
covers it. `infer` deliberately does not emit one.

A GIN index on `extra` only pays off if you genuinely query inside it. If you do
that often, those fields wanted to be columns.

## Constraints

The git store enforced nothing but path uniqueness, so this is where months of
quiet breakage surfaces. Add constraints and expect the backfill to fail:

```sql
ALTER TABLE tasks ADD CONSTRAINT tasks_status_check
  CHECK (status IN ('open','done','blocked'));

ALTER TABLE comments ADD CONSTRAINT comments_task_fk
  FOREIGN KEY (project_id, task_id) REFERENCES tasks (project_id, id);
```

The failures are the value. Each one is a bug that has been silently corrupting
data. Fix the data at the source and re-export; do not loosen the constraint to
make the load pass. A constraint added "later, once things settle" is a
constraint that never gets added.

NOT NULL is the one to be careful with. `infer` proposes it only for fields
present in 100% of records with no nulls, which is right for the data you have —
but ask whether the application could ever legitimately omit it before locking
it in.

## Collection to table

Usually one collection, one table. Two cases deserve thought:

- **A collection with a `type` discriminator** and mostly disjoint fields is two
  tables wearing one coat. Splitting during migration is much cheaper than
  splitting after.
- **A collection with a handful of records per project** (settings, config) may
  belong as columns on a `projects` table instead of a table of its own.

Create a `projects` table from the `meta.json` documents. It gives foreign keys
somewhere to point, and it is where per-project settings, plan, and status
belong once they are no longer a file on a branch.

## What to do with history

The git store has full history. The database will not. Three options:

**Archive the bundle (default).** `git bundle create archive.bundle --all`, keep
it in object storage. One file, all history, restorable with `git clone`. Costs
nothing and answers "what did this look like in March" whenever it comes up.

**Load commit metadata into an audit table.** One row per commit: project,
sha, author, timestamp, message, changed paths. Useful if you want an admin
timeline. Note it stores _that_ something changed, not what it changed to.

**Load full per-record history.** One row per record version. Do this only for a
real product requirement, because it multiplies row count by revision depth and
nobody has ever queried it in most systems that built it.

Default to the bundle. If a product feature needs history, that feature should
have its own `events` table going forward, populated by the application — not
reconstructed from git commits, which stops being updated the moment you cut over.
