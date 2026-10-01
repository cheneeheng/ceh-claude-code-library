#!/usr/bin/env python3
"""
verify.py - Prove the backfill landed correctly. Python stdlib only.

Compares the JSONL exported from git against a JSONL dump of what actually
made it into the database. It deliberately does NOT connect to your database:
you dump the target with whatever tool you already trust (psql \\copy ... to
program 'cat', sqlite3 -json, an ORM script), and this compares the two files.
That keeps the check driver-free, works for any engine, and -- more usefully --
verifies what the database will actually hand back to your application rather
than what you believe you inserted.

  python verify.py git.jsonl db.jsonl \\
      --key project_id,id \\
      --unnest extra \\
      --ignore schema_version \\
      --coerce points:int

Exit code is 0 only when the two sides match, so it drops straight into a
deploy script as a gate before you flip reads.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from typing import Any


def load(
    path: str,
    key: list[str],
    unnest: list[str],
    ignore: set[str],
    coerce: dict[str, str],
) -> tuple[dict[tuple, dict], list[str]]:
    rows: dict[tuple, dict] = {}
    problems: list[str] = []
    dupes = Counter()
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as e:
                problems.append(f"{path}:{lineno}: unparseable ({e})")
                continue
            for field in unnest:
                blob = rec.pop(field, None)
                if isinstance(blob, str):
                    try:
                        blob = json.loads(blob)
                    except json.JSONDecodeError:
                        blob = None
                if isinstance(blob, dict):
                    # Merge the JSONB column back to the flat shape git had, so
                    # the two sides are comparable regardless of which fields
                    # you chose to promote to real columns.
                    for k, v in blob.items():
                        rec.setdefault(k, v)
            for k, t in coerce.items():
                if k in rec and rec[k] is not None:
                    rec[k] = _coerce(rec[k], t)
            for k in ignore:
                rec.pop(k, None)
            try:
                kv = tuple(rec[k] for k in key)
            except KeyError:
                problems.append(f"{path}:{lineno}: missing key field(s) {key}")
                continue
            if kv in rows:
                dupes[kv] += 1
            rows[kv] = rec
    for kv, n in dupes.most_common(5):
        problems.append(f"{path}: duplicate key {kv} appears {n + 1} times")
    return rows, problems


def _coerce(v: Any, t: str) -> Any:
    try:
        if t == "int":
            return int(float(v))
        if t == "float":
            return float(v)
        if t == "str":
            return str(v)
        if t == "bool":
            return v if isinstance(v, bool) else str(v).lower() in ("1", "true", "t")
    except (TypeError, ValueError):
        return v
    return v


def norm(v: Any) -> Any:
    """Fold away differences that are representational, not semantic.

    Timestamps are the usual culprit: git stored `...T10:00:00.000Z`, Postgres
    hands back `...T10:00:00+00:00`, and a naive string compare reports every
    single row as different -- which trains you to ignore the report."""
    if isinstance(v, str):
        s = v.strip()
        if s.endswith("+00:00"):
            s = s[:-6] + "Z"
        if len(s) > 19 and s.endswith("Z") and "." in s:
            head, _, frac = s[:-1].partition(".")
            frac = (frac + "000")[:3]
            s = f"{head}.{frac}Z"
        return s
    if isinstance(v, float) and v.is_integer():
        return int(v)
    if isinstance(v, list):
        return [norm(x) for x in v]
    if isinstance(v, dict):
        return {k: norm(x) for k, x in sorted(v.items())}
    return v


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("source")
    ap.add_argument("target")
    ap.add_argument("--key", default="project_id,id")
    ap.add_argument("--unnest", default="")
    ap.add_argument("--ignore", default="")
    ap.add_argument("--coerce", default="", help="field:type,field:type")
    ap.add_argument("--max-report", type=int, default=15)
    a = ap.parse_args()

    key = [k for k in a.key.split(",") if k]
    unnest = [u for u in a.unnest.split(",") if u]
    ignore = {i for i in a.ignore.split(",") if i}
    coerce = dict(p.split(":", 1) for p in a.coerce.split(",") if ":" in p)

    src, p1 = load(a.source, key, [], ignore, coerce)
    tgt, p2 = load(a.target, key, unnest, ignore, coerce)
    problems = p1 + p2

    missing = sorted(set(src) - set(tgt))
    extra = sorted(set(tgt) - set(src))
    diffs = []
    for k in sorted(set(src) & set(tgt)):
        s, t = src[k], tgt[k]
        fields = set(s) | set(t)
        bad = {
            f: (s.get(f, "<absent>"), t.get(f, "<absent>"))
            for f in fields
            if norm(s.get(f)) != norm(t.get(f))
        }
        if bad:
            diffs.append((k, bad))

    print(f"source (git) : {len(src):,} records")
    print(f"target (db)  : {len(tgt):,} records")
    print(f"missing in db: {len(missing):,}")
    print(f"only in db   : {len(extra):,}")
    print(f"field diffs  : {len(diffs):,}")

    for label, items in (("MISSING IN DB", missing), ("ONLY IN DB", extra)):
        if items:
            print(f"\n{label} (first {a.max_report}):")
            for k in items[: a.max_report]:
                print(f"  {'/'.join(map(str, k))}")

    if diffs:
        print(f"\nFIELD DIFFS (first {a.max_report}):")
        by_field = Counter()
        for k, bad in diffs:
            for f in bad:
                by_field[f] += 1
        for k, bad in diffs[: a.max_report]:
            print(f"  {'/'.join(map(str, k))}")
            for f, (sv, tv) in sorted(bad.items()):
                print(f"      {f}: git={sv!r}  db={tv!r}")
        print("\n  diffs by field (this is the useful column -- a single field")
        print("  accounting for nearly every diff is one bad cast, not 900 bad rows):")
        for f, c in by_field.most_common(10):
            print(f"      {f:<20}{c:>8,}")

    if problems:
        print(f"\nINPUT PROBLEMS ({len(problems)}):")
        for p in problems[: a.max_report]:
            print(f"  {p}")

    okay = not (missing or extra or diffs or problems)
    print(
        "\n"
        + (
            "PASS - the two sides are identical."
            if okay
            else "FAIL - do not flip reads until this is clean."
        )
    )
    return 0 if okay else 1


if __name__ == "__main__":
    sys.exit(main())
