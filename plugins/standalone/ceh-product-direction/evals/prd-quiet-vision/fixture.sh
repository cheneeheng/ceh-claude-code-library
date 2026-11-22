#!/usr/bin/env bash
set -euo pipefail
mkdir -p "$(dirname 'README.md')"
cat >'README.md' <<'EOF_FIXTURE'
# Shelf

A self-hosted read-later app for one person. Click the bookmarklet on any page and Shelf keeps a
readable copy of it.

## Run

```bash
python app.py   # serves on http://localhost:8080
```

Drag `bookmarklet.js` to your bookmarks bar, with the host changed to your server.
EOF_FIXTURE
mkdir -p "$(dirname 'app.py')"
cat >'app.py' <<'EOF_FIXTURE'
"""Shelf: save a link, keep a readable copy, list what was saved."""

import html.parser
import sqlite3
import urllib.request
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

DB = "shelf.db"


class _Text(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.title, self.parts, self._in_title = "", [], False

    def handle_starttag(self, tag, attrs):
        self._in_title = tag == "title"

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        self.parts.append(data)


def db():
    con = sqlite3.connect(DB)
    con.execute(
        "CREATE TABLE IF NOT EXISTS pages (id INTEGER PRIMARY KEY, url TEXT NOT NULL, "
        "title TEXT, text TEXT, html TEXT, saved_at TEXT NOT NULL)"
    )
    return con


def save(url):
    page = urllib.request.urlopen(url, timeout=10).read().decode("utf-8", "replace")
    parsed = _Text()
    parsed.feed(page)
    with db() as con:
        con.execute(
            "INSERT INTO pages (url, title, text, html, saved_at) VALUES (?, ?, ?, ?, ?)",
            (url, parsed.title.strip(), " ".join(parsed.parts), page,
             datetime.now(timezone.utc).isoformat()),
        )


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        rows = db().execute("SELECT title, url FROM pages ORDER BY saved_at DESC").fetchall()
        body = "".join(f'<li><a href="{u}">{t or u}</a></li>' for t, u in rows)
        self._send(200, f"<ul>{body}</ul>")

    def do_POST(self):
        if self.path != "/save":
            return self._send(404, "not found")
        form = parse_qs(self.rfile.read(int(self.headers["Content-Length"])).decode())
        save(form["url"][0])
        self._send(201, "saved")

    def _send(self, status, text):
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(text.encode())


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
EOF_FIXTURE
mkdir -p "$(dirname 'bookmarklet.js')"
cat >'bookmarklet.js' <<'EOF_FIXTURE'
javascript:(function(){var f=document.createElement('form');f.method='POST';f.action='http://shelf.local:8080/save';var i=document.createElement('input');i.name='url';i.value=location.href;f.appendChild(i);document.body.appendChild(f);f.submit();})();
EOF_FIXTURE
mkdir -p "$(dirname '.agents_workspace/product/plan/20261002-091500-save-links.yaml')"
cat >'.agents_workspace/product/plan/20261002-091500-save-links.yaml' <<'EOF_FIXTURE'
schema: plan/v2
title: Save links
status: built
created: 2026-10-02
goal: |
  The owner saves the page they are on with one click of a bookmarklet, and Shelf keeps a
  readable copy of it.
scope:
  in:
    - "POST /save takes a url, fetches the page, and stores its title, its readable text and its HTML."
    - A bookmarklet that sends the current page's url to POST /save.
    - GET / lists saved pages, newest first.
  out:
    - item: Search
      reason: Its own plan, after this one.
design:
  - topic: Storage
    decision: |
      One SQLite file, shelf.db, table pages(id, url, title, text, html, saved_at).
phases:
  - name: Save and list
    builds: |
      app.py with POST /save and GET /, and bookmarklet.js.
    check: |
      python -m unittest test_app passes.
    status: done
    evidence: |
      python -m unittest test_app, OK (3 tests)
open: []
record:
  - date: 2026-10-02
    event: Planned
    details: status ready
  - date: 2026-10-04
    event: Checked
    details: built as planned, python -m unittest test_app, OK (3 tests)
EOF_FIXTURE
mkdir -p "$(dirname '.agents_workspace/product/plan/20261002-091500-save-links.md')"
cat >'.agents_workspace/product/plan/20261002-091500-save-links.md' <<'EOF_FIXTURE'
---
schema: plan/v2
generated_from: 20261002-091500-save-links.yaml
generated_note: "Do not edit. artifact.py renders this file from 20261002-091500-save-links.yaml: edit the YAML, then run artifact.py render."
title: Save links
status: built
created: 2026-10-02
---

<!-- prettier-ignore-start -->

## Goal

The owner saves the page they are on with one click of a bookmarklet, and Shelf keeps a
readable copy of it.

## Scope

**In:**

- POST /save takes a url, fetches the page, and stores its title, its readable text and its HTML.
- A bookmarklet that sends the current page's url to POST /save.
- GET / lists saved pages, newest first.

**Out:**

- Search: Its own plan, after this one.

## Design

- **Storage** One SQLite file, shelf.db, table pages(id, url, title, text, html, saved_at).

## Phases

### Phase 1: Save and list

- **Builds:** app.py with POST /save and GET /, and bookmarklet.js.
- **Check:** python -m unittest test_app passes.
- **Status:** done, python -m unittest test_app, OK (3 tests)

## Open

None

## Record

- 2026-10-02 Planned: status ready
- 2026-10-04 Checked: built as planned, python -m unittest test_app, OK (3 tests)

<!-- prettier-ignore-end -->
EOF_FIXTURE
git init -q -b main
git add -A
git -c user.name=eval -c user.email=eval@example.com commit -qm 'chore: seed'
