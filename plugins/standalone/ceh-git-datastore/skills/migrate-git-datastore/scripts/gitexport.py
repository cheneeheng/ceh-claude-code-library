#!/usr/bin/env python3
"""
gitexport.py - Inspect and export a git-backed datastore ahead of a migration.
Python stdlib only; no database driver required.

Assumed layout (the one `git-backed-datastore` produces):

    refs/heads/project/<pid>
      meta.json
      collections/<collection>/<record-id>.json

Subcommands:

  inventory <repo>
      Size up the store: projects, collections, record counts, bytes, commit
      depth. Run this first -- migration effort scales with the shape of the
      data, not with how long you have been running.

  infer <repo> [--collection C] [--dialect postgres|sqlite] [--column-threshold F]
      Profile every field in every collection across all projects and propose
      DDL. Flags the three things that actually break backfills: fields whose
      type drifts between records, fields that are sometimes absent and
      sometimes explicitly null, and values that will not fit the column type
      you were about to choose.

  export <repo> <outdir> [--collection C]
      Dump each collection to JSONL at a PINNED commit per project, and write
      manifest.json recording which commit each project was read at. The pin is
      the whole point: it turns "migrate a moving target" into "migrate a
      snapshot, then replay a known-bounded diff".

  changed <repo> <manifest.json>
      List records added/modified/deleted in each project since its pinned
      commit. This is your catch-up set at cutover -- exact, not a guess based
      on updated_at.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections import Counter, defaultdict
from typing import Any, Iterator

PREFIX = "refs/heads/project/"


# --------------------------------------------------------------------------
# git helpers
# --------------------------------------------------------------------------


def git(repo: str, *args: str, stdin: bytes | None = None, check: bool = True):
    p = subprocess.run(
        ["git", "--git-dir", repo, *args], input=stdin, capture_output=True
    )
    if check and p.returncode != 0:
        raise SystemExit(
            f"git {' '.join(args)} failed: {p.stderr.decode('utf-8', 'replace').strip()}"
        )
    return p


def out(repo: str, *args: str, **kw) -> str:
    return git(repo, *args, **kw).stdout.decode("utf-8", "replace").strip()


def projects(repo: str) -> list[tuple[str, str]]:
    """(project_id, pinned commit sha) for every project ref."""
    rows = out(repo, "for-each-ref", "--format=%(refname)%09%(objectname)", PREFIX)
    res = []
    for line in rows.splitlines():
        if not line:
            continue
        ref, sha = line.split("\t")
        res.append((ref[len(PREFIX) :], sha))
    return sorted(res)


def collections(repo: str, sha: str) -> list[str]:
    p = git(repo, "ls-tree", "--name-only", f"{sha}:collections", check=False)
    return sorted(n for n in p.stdout.decode().split("\n") if n)


def record_paths(repo: str, sha: str, coll: str) -> list[str]:
    p = git(repo, "ls-tree", "--name-only", f"{sha}:collections/{coll}", check=False)
    return [n for n in p.stdout.decode().split("\n") if n.endswith(".json")]


def read_many(repo: str, specs: list[str]) -> Iterator[bytes | None]:
    """Stream many blobs through ONE cat-file process.

    Reading N records as N subprocess calls is the difference between a
    migration that takes seconds and one that takes an hour; on a 10k-record
    store that is 10k fork/exec cycles you do not need."""
    if not specs:
        return
    p = git(repo, "cat-file", "--batch", stdin=("\n".join(specs) + "\n").encode())
    data, i, n = p.stdout, 0, len(p.stdout)
    while i < n:
        j = data.index(b"\n", i)
        header = data[i:j].decode("utf-8", "replace")
        i = j + 1
        parts = header.split()
        if parts[-1] in ("missing", "ambiguous"):
            yield None
            continue
        size = int(parts[-1])
        yield data[i : i + size]
        i += size + 1


def iter_records(
    repo: str, pid: str, sha: str, coll: str
) -> Iterator[tuple[str, dict]]:
    names = record_paths(repo, sha, coll)
    specs = [f"{sha}:collections/{coll}/{n}" for n in names]
    for name, blob in zip(names, read_many(repo, specs)):
        if blob is None:
            continue
        try:
            yield name[:-5], json.loads(blob)
        except json.JSONDecodeError as e:
            print(f"  !! unparseable {pid}/{coll}/{name}: {e}", file=sys.stderr)


# --------------------------------------------------------------------------
# inventory
# --------------------------------------------------------------------------


def cmd_inventory(a) -> None:
    per_coll = defaultdict(lambda: {"records": 0, "bytes": 0, "projects": 0})
    per_proj: dict[str, dict] = {}
    for pid, sha in projects(a.repo):
        colls = collections(a.repo, sha)
        commits = int(out(a.repo, "rev-list", "--count", sha))
        n = b = 0
        for coll in colls:
            names = record_paths(a.repo, sha, coll)
            size = sum(
                len(x)
                for x in read_many(
                    a.repo, [f"{sha}:collections/{coll}/{m}" for m in names]
                )
                if x
            )
            c = per_coll[coll]
            c["records"] += len(names)
            c["bytes"] += size
            c["projects"] += 1
            n += len(names)
            b += size
        per_proj[pid] = {"records": n, "bytes": b, "commits": commits}

    total_rec = sum(v["records"] for v in per_proj.values())
    total_b = sum(v["bytes"] for v in per_proj.values())
    npro = len(per_proj)
    empty = [p for p, v in per_proj.items() if v["records"] == 0]

    print(f"{'collection':<18}{'records':>10}{'bytes':>13}{'avg':>8}{'projects':>10}")
    print("-" * 59)
    for coll in sorted(per_coll, key=lambda c: -per_coll[c]["records"]):
        c = per_coll[coll]
        avg = c["bytes"] // c["records"] if c["records"] else 0
        print(
            f"{coll:<18}{c['records']:>10,}{c['bytes']:>13,}{avg:>8,}{c['projects']:>10}"
        )
    print("-" * 59)
    print(f"{'TOTAL':<18}{total_rec:>10,}{total_b:>13,}")

    print(f"\nprojects: {npro}  ({len(empty)} empty)   on-disk: {_du(a.repo)}")
    ranked = sorted(per_proj.items(), key=lambda kv: -kv[1]["records"])
    show = [r for r in ranked if r[1]["records"]][:10]
    if show:
        print(f"\n{'largest projects':<18}{'records':>10}{'bytes':>13}{'commits':>10}")
        for pid, v in show:
            print(f"{pid:<18}{v['records']:>10,}{v['bytes']:>13,}{v['commits']:>10,}")

    # Interpretation, not just numbers -- the point of an inventory is to help
    # you decide whether to migrate at all, and in what order.
    print("\nread:")
    if total_rec < 5_000:
        print("  - small store; a single-pass backfill finishes in seconds.")
        print("    If nothing else is forcing the move, staying on git is defensible.")
    elif total_rec < 100_000:
        print("  - mid-size; backfill per collection, expect minutes not hours.")
    else:
        print(
            "  - large; stream per project and checkpoint. Do not hold it all in RAM."
        )
    if npro > 50:
        print(f"  - {npro} independent refs, so per-project cutover is cheap:")
        print("    migrate and verify a handful, leave the rest on git until proven.")
    if empty:
        print(f"  - {len(empty)} project(s) hold no records. Confirm they are live")
        print("    tenants and not abandoned refs before you create rows for them.")
    deep = [p for p, v in per_proj.items() if v["commits"] > 5000]
    if deep:
        print(f"  - deep history on {len(deep)} project(s); run `git gc` before export")
        print("    so reads come from packfiles instead of loose objects.")
    skew = ranked[0][1]["records"] / max(1, total_rec) if ranked else 0
    if npro > 3 and skew > 0.5:
        print(f"  - one project holds {skew:.0%} of all records. Migrate that one")
        print("    first: it is where the schema surprises and the slow queries live.")


def _du(path: str) -> str:
    return subprocess.run(
        ["du", "-sh", path], capture_output=True, text=True
    ).stdout.split()[0]


# --------------------------------------------------------------------------
# schema inference
# --------------------------------------------------------------------------

RESERVED = {
    "user",
    "order",
    "group",
    "table",
    "select",
    "from",
    "where",
    "index",
    "check",
    "default",
    "primary",
    "references",
    "column",
    "constraint",
    "all",
    "end",
    "limit",
    "offset",
    "desc",
    "asc",
    "case",
    "when",
    "then",
    "values",
}


def json_type(v: Any) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, int):
        return "int"
    if isinstance(v, float):
        return "float"
    if isinstance(v, str):
        return "str"
    if isinstance(v, list):
        return "array"
    return "object"


def cmd_infer(a) -> None:
    profiles: dict[str, dict[str, dict]] = defaultdict(
        lambda: defaultdict(
            lambda: {
                "present": 0,
                "null": 0,
                "types": Counter(),
                "maxlen": 0,
                "distinct": set(),
                "example": None,
            }
        )
    )
    counts: Counter = Counter()

    for pid, sha in projects(a.repo):
        for coll in collections(a.repo, sha):
            if a.collection and coll != a.collection:
                continue
            for _rid, rec in iter_records(a.repo, pid, sha, coll):
                counts[coll] += 1
                for k, v in rec.items():
                    f = profiles[coll][k]
                    f["present"] += 1
                    f["types"][json_type(v)] += 1
                    if v is None:
                        f["null"] += 1
                    if isinstance(v, str):
                        f["maxlen"] = max(f["maxlen"], len(v))
                    if isinstance(v, (str, int, bool)) and len(f["distinct"]) < 200:
                        f["distinct"].add(v)
                    if f["example"] is None and v is not None:
                        f["example"] = v

    for coll in sorted(profiles):
        n = counts[coll]
        print(f"\n{'=' * 74}\ncollection: {coll}   ({n:,} records)\n{'=' * 74}")
        w = max(12, max(len(k) for k in profiles[coll]) + 2)
        print(
            f"{'field':<{w}}{'present':>8}{'null':>7}{'distinct':>10}  "
            f"{'types':<22}{'->'}"
        )
        cols, jsonb, warns, drifted = [], [], [], []
        for k in sorted(profiles[coll]):
            f = profiles[coll][k]
            rate = f["present"] / n if n else 0
            nonnull = {t: c for t, c in f["types"].items() if t != "null"}
            types = ",".join(f"{t}:{c}" for t, c in f["types"].most_common())
            scalar = f["types"].keys() - {"array", "object", "null"}
            card = (
                "-"
                if not scalar
                else f"{len(f['distinct'])}"
                + ("+" if len(f["distinct"]) >= 200 else "")
            )
            drift = len(nonnull) > 1
            if drift:
                drifted.append(k)
                warns.append(
                    f"TYPE DRIFT  {k}: {types}. Coerce to one type during export. "
                    f"Left in `extra` for now -- fix the drift and re-run infer to "
                    f"promote it to a real column."
                )
            absent = n - f["present"]
            if absent and f["null"]:
                warns.append(
                    f"ABSENT vs NULL  {k}: missing in {absent} record(s), explicitly "
                    f"null in {f['null']}. SQL collapses both to NULL -- confirm you "
                    f"do not need the distinction, because it is gone after this."
                )
            if 0.05 < rate < a.column_threshold and not drift:
                warns.append(
                    f"PARTIAL  {k}: present in only {rate:.0%}. If this is a field you "
                    f"added recently rather than an optional one, make it a nullable "
                    f"column instead of burying it in `extra` where you cannot index it."
                )
            promote = rate >= a.column_threshold and not drift
            (cols if promote else jsonb).append((k, f, rate))
            print(
                f"{k:<{w}}{rate:>7.0%}{f['null']:>7}{card:>10}  {types:<22}"
                f"{'column' if promote else 'extra'}"
            )

        print(f"\n-- proposed DDL ({a.dialect})")
        print(_ddl(coll, cols, jsonb, a.dialect))
        if warns:
            print("\n-- settle these BEFORE backfilling:")
            for wmsg in warns:
                print(f"--   {wmsg}")


def _sqltype(f: dict, dialect: str) -> str:
    t = f["types"].most_common(1)[0][0] if f["types"] else "str"
    if t == "null":
        t = "str"
    pg = {
        "int": "bigint",
        "float": "double precision",
        "bool": "boolean",
        "array": "jsonb",
        "object": "jsonb",
    }
    lite = {
        "int": "integer",
        "float": "real",
        "bool": "integer",
        "array": "text",
        "object": "text",
    }
    if t == "str":
        # A field that always parses as an ISO-8601 instant should land as a
        # real timestamp, not text -- otherwise every future date filter is a
        # string comparison and every index on it is useless.
        ex = f["example"]
        if isinstance(ex, str) and len(ex) >= 10 and ex[4:5] == "-" and ex[7:8] == "-":
            return "timestamptz" if dialect == "postgres" else "text"
        if dialect == "postgres":
            return "text"
        return "text"
    return (pg if dialect == "postgres" else lite)[t]


def _ddl(coll: str, cols, jsonb, dialect: str) -> str:
    q = lambda s: f'"{s}"' if s.lower() in RESERVED else s
    jsonb_t = "jsonb" if dialect == "postgres" else "text"
    defs = [("project_id", "text", " NOT NULL", ""), ("id", "text", " NOT NULL", "")]
    for k, f, rate in cols:
        if k in ("project_id", "id"):
            continue
        nn = " NOT NULL" if rate >= 0.999 and not f["null"] else ""
        defs.append((q(k), _sqltype(f, dialect), nn, ""))
    if jsonb:
        defs.append(("extra", jsonb_t, "", "-- " + ", ".join(k for k, _, _ in jsonb)))
    nw = max(len(d[0]) for d in defs) + 2
    tw = max(len(d[1]) for d in defs) + 2
    body = []
    for i, (name, typ, nn, note) in enumerate(defs):
        comma = "," if i < len(defs) - 1 else ","
        col = f"  {name:<{nw}}{typ:<{tw}}{nn.strip()}".rstrip()
        body.append(col + comma + (f"  {note}" if note else ""))
    body.append("  PRIMARY KEY (project_id, id)")
    lines = [f"CREATE TABLE {q(coll)} ("] + body + [");"]

    # Index suggestions. A composite PK on (project_id, id) already covers
    # lookups and project scans, so repeating it buys nothing -- what is worth
    # indexing is whatever you filter and sort by. Every index leads with
    # project_id because in a per-tenant app every query is scoped to one.
    idx = []
    for k, f, rate in cols:
        if k in ("id", "project_id", "schema_version"):
            continue
        t = _sqltype(f, dialect)
        if t == "timestamptz" or k in ("created_at", "updated_at"):
            idx.append(
                f"CREATE INDEX ON {q(coll)} (project_id, {q(k)} DESC);"
                f"  -- recent-first listing"
            )
        elif 1 < len(f["distinct"]) <= 20 and rate > 0.9:
            idx.append(
                f"CREATE INDEX ON {q(coll)} (project_id, {q(k)});"
                f"  -- {len(f['distinct'])} distinct values, good filter"
            )
    if jsonb and dialect == "postgres":
        idx.append(
            f"-- CREATE INDEX ON {q(coll)} USING gin (extra);"
            f"  -- only if you actually query inside extra"
        )
    return "\n".join(lines + ([""] + idx if idx else []))


# --------------------------------------------------------------------------
# export
# --------------------------------------------------------------------------


def cmd_export(a) -> None:
    os.makedirs(a.outdir, exist_ok=True)
    manifest = {"repo": os.path.abspath(a.repo), "pins": {}, "counts": {}}
    handles: dict[str, Any] = {}
    try:
        for pid, sha in projects(a.repo):
            manifest["pins"][pid] = sha  # the snapshot contract
            for coll in collections(a.repo, sha):
                if a.collection and coll != a.collection:
                    continue
                if coll not in handles:
                    handles[coll] = open(
                        os.path.join(a.outdir, f"{coll}.jsonl"), "w", encoding="utf-8"
                    )
                fh = handles[coll]
                k = 0
                for rid, rec in iter_records(a.repo, pid, sha, coll):
                    # project_id is injected here, not stored in the record:
                    # in git it was implicit in the ref, in SQL it has to be a
                    # real column or every row loses its tenant.
                    rec["project_id"] = pid
                    rec.setdefault("id", rid)
                    fh.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")
                    k += 1
                manifest["counts"][f"{pid}/{coll}"] = k
    finally:
        for fh in handles.values():
            fh.close()
    path = os.path.join(a.outdir, "manifest.json")
    with open(path, "w") as fh:
        json.dump(manifest, fh, indent=2)
    total = sum(manifest["counts"].values())
    print(
        f"exported {total:,} records from {len(manifest['pins'])} projects "
        f"to {a.outdir}"
    )
    print(f"pinned commits recorded in {path}")
    print("Keep this manifest. `changed` uses it to compute the exact catch-up set.")


# --------------------------------------------------------------------------
# changed-since
# --------------------------------------------------------------------------


def cmd_changed(a) -> None:
    manifest = json.load(open(a.manifest))
    pins = manifest["pins"]
    live = dict(projects(a.repo))
    total = 0
    for pid, sha in sorted(live.items()):
        old = pins.get(pid)
        if old is None:
            print(f"{pid}: NEW project since export -- full load required")
            continue
        if old == sha:
            continue
        # --diff-filter tells you add vs modify vs delete; deletes matter most
        # because a dual-write that only replays upserts silently resurrects
        # rows the user deleted during the migration window.
        p = git(a.repo, "diff", "--name-status", old, sha)
        for line in p.stdout.decode().splitlines():
            if not line:
                continue
            status, path = line.split("\t", 1)
            if not path.startswith("collections/"):
                continue
            _, coll, fname = path.split("/", 2)
            print(f"{status[0]}\t{pid}\t{coll}\t{fname[:-5]}")
            total += 1
    for pid in pins:
        if pid not in live:
            print(f"D\t{pid}\t*\t* (project deleted since export)")
    print(f"\n{total} record change(s) since export", file=sys.stderr)


# --------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("inventory")
    p.add_argument("repo")
    p.set_defaults(fn=cmd_inventory)

    p = sub.add_parser("infer")
    p.add_argument("repo")
    p.add_argument("--collection")
    p.add_argument("--dialect", default="postgres", choices=["postgres", "sqlite"])
    p.add_argument("--column-threshold", type=float, default=0.95)
    p.set_defaults(fn=cmd_infer)

    p = sub.add_parser("export")
    p.add_argument("repo")
    p.add_argument("outdir")
    p.add_argument("--collection")
    p.set_defaults(fn=cmd_export)

    p = sub.add_parser("changed")
    p.add_argument("repo")
    p.add_argument("manifest")
    p.set_defaults(fn=cmd_changed)

    a = ap.parse_args()
    a.fn(a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
