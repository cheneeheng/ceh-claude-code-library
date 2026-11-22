#!/usr/bin/env bash
set -euo pipefail
mkdir -p "$(dirname '.agents_workspace/product/VISION.yaml')"
cat >'.agents_workspace/product/VISION.yaml' <<'EOF_FIXTURE'
schema: vision/v2
status: adopted
updated: 2026-10-01
identity:
  name: Shelf
  sentence: A self-hosted read-later app for one person, which saves any link and finds it again.
  is:
    - trait: Personal
      meaning: |
        One owner on their own server. No accounts for other people, no teams.
    - trait: Durable
      meaning: |
        A saved page can be read years later, even when the site is gone or the network is down.
  is_not:
    - A social bookmarking site
    - A feed reader
vision: |
  Saving a link takes two seconds from a phone or a laptop, and every saved page can be found
  again by a word in it and read in full without a network.
scope:
  text: |
    Saving links, keeping a readable copy of each page, and finding saved pages again.
  test: Does it help the owner save, keep or find a page they chose to save?
  refuses: |
    Discovering new content for the owner: recommendations, feeds and trending lists.
goals:
  - goal: Saving is instant
    measure: |
      A save from the browser bookmarklet returns in under 2 seconds on a Raspberry Pi 4.
  - goal: Nothing saved is lost
    measure: |
      Every saved page can be read in full with the network off, and a backup restores every page.
  - goal: Anything saved can be found
    measure: |
      A search for a word in a saved page's text lists that page first or second.
non_goals:
  - thing: Sharing saved pages with friends or public profiles
    reason: |
      Shelf is personal. Sharing needs accounts, permissions and moderation, which a
      one-person server should not carry.
  - thing: Recommendations of what to read next
    reason: |
      The owner chooses what to save. A recommender is a feed reader, which Shelf is not.
principles:
  - name: The copy is the product
    rule: |
      A link without a readable copy of its page is not saved, because sites disappear.
    ask: Does this keep a full copy of the page?
  - name: One person, one server
    rule: |
      Design for one owner on one small machine, so it stays cheap and simple to run.
    ask: Would this need a second user or a second machine?
conflicts:
  order:
    - principle: The copy is the product
      protects: that nothing saved is lost
    - principle: One person, one server
      protects: that it stays cheap and simple to run
  example: |
    For example, a full-text index that needs a separate search server keeps pages findable but
    breaks one person, one server, so search runs inside the app's own database.
gaps: []
extra_sections: []
changing: |
  The owner edits this file and sets status back to draft until they confirm the change.
EOF_FIXTURE
mkdir -p "$(dirname '.agents_workspace/product/VISION.md')"
cat >'.agents_workspace/product/VISION.md' <<'EOF_FIXTURE'
---
schema: vision/v2
generated_from: VISION.yaml
generated_note: "Do not edit. artifact.py renders this file from VISION.yaml: edit the YAML, then run artifact.py render."
status: adopted
updated: 2026-10-01
---

<!-- prettier-ignore-start -->

# Vision

## Identity

Shelf is A self-hosted read-later app for one person, which saves any link and finds it again.

It is:

- **Personal.** One owner on their own server. No accounts for other people, no teams.
- **Durable.** A saved page can be read years later, even when the site is gone or the network is down.

It is not:

- A social bookmarking site
- A feed reader

## Vision

Saving a link takes two seconds from a phone or a laptop, and every saved page can be found
again by a word in it and read in full without a network.

## Scope

Saving links, keeping a readable copy of each page, and finding saved pages again.

The test: **Does it help the owner save, keep or find a page they chose to save?** Discovering new content for the owner: recommendations, feeds and trending lists.

## Goals

1. **Saving is instant.** A save from the browser bookmarklet returns in under 2 seconds on a Raspberry Pi 4.
2. **Nothing saved is lost.** Every saved page can be read in full with the network off, and a backup restores every page.
3. **Anything saved can be found.** A search for a word in a saved page's text lists that page first or second.

## Non-goals

- **Sharing saved pages with friends or public profiles.** Shelf is personal. Sharing needs accounts, permissions and moderation, which a
  one-person server should not carry.
- **Recommendations of what to read next.** The owner chooses what to save. A recommender is a feed reader, which Shelf is not.

## Principles

### 1. The copy is the product

A link without a readable copy of its page is not saved, because sites disappear.
**Ask:** Does this keep a full copy of the page?

### 2. One person, one server

Design for one owner on one small machine, so it stays cheap and simple to run.
**Ask:** Would this need a second user or a second machine?

## When principles conflict

1. **The copy is the product.** that nothing saved is lost
2. **One person, one server.** that it stays cheap and simple to run

For example, a full-text index that needs a separate search server keeps pages findable but
breaks one person, one server, so search runs inside the app's own database.

## Where the repo does not match yet

No known gaps as of 2026-10-01.

## Changing this file

The owner edits this file and sets status back to draft until they confirm the change.

<!-- prettier-ignore-end -->
EOF_FIXTURE
mkdir -p "$(dirname '.agents_workspace/product/STRATEGY.yaml')"
cat >'.agents_workspace/product/STRATEGY.yaml' <<'EOF_FIXTURE'
schema: strategy/v2
status: adopted
updated: 2026-10-01
concept: |
  Shelf is one small web app on the owner's own server. A bookmarklet sends a link, the app
  fetches the page and keeps a readable copy, and a search page finds it again.
parts:
  columns: [Part, What it does, Takes, Passes on]
  rows:
    - [Bookmarklet, Sends the current page's link, A click in the browser, A link]
    - [Saver, Fetches the page and keeps a readable copy, A link, A saved page]
    - [Library, "Lists, searches and shows saved pages", A query, Saved pages]
work:
  rule: Build what keeps a saved page findable and readable before anything that organises pages.
  reason: |
    A page that cannot be found or read again is lost, and losing a page is the one failure the
    vision refuses.
  next:
    - work: Search the text of saved pages
      why: |
        Saving already works, and without search the library is a list nobody can use past a
        hundred pages.
measuring: |
  The owner counts the saves that failed and the searches that did not find a page they knew was
  saved.
not_to_do:
  - approach: A browser extension per browser
    reason: |
      A bookmarklet works in every browser and on phones, and one extension per browser would
      have to be kept up with each browser's store.
gaps: []
open: []
extra_sections: []
changing: |
  The owner edits this file and sets status back to draft until they confirm the change.
EOF_FIXTURE
mkdir -p "$(dirname '.agents_workspace/product/STRATEGY.md')"
cat >'.agents_workspace/product/STRATEGY.md' <<'EOF_FIXTURE'
---
schema: strategy/v2
generated_from: STRATEGY.yaml
generated_note: "Do not edit. artifact.py renders this file from STRATEGY.yaml: edit the YAML, then run artifact.py render."
status: adopted
updated: 2026-10-01
---

<!-- prettier-ignore-start -->

# Strategy

## The concept

Shelf is one small web app on the owner's own server. A bookmarklet sends a link, the app
fetches the page and keeps a readable copy, and a search page finds it again.

## The parts

| Part | What it does | Takes | Passes on |
| --- | --- | --- | --- |
| Bookmarklet | Sends the current page's link | A click in the browser | A link |
| Saver | Fetches the page and keeps a readable copy | A link | A saved page |
| Library | Lists, searches and shows saved pages | A query | Saved pages |

## How work is chosen

**Build what keeps a saved page findable and readable before anything that organises pages.** A page that cannot be found or read again is lost, and losing a page is the one failure the
vision refuses.

The likely order next:

1. **Search the text of saved pages.** Saving already works, and without search the library is a list nobody can use past a
   hundred pages.

## Measuring progress

The owner counts the saves that failed and the searches that did not find a page they knew was
saved.

## What not to do

- **A browser extension per browser.** A bookmarklet works in every browser and on phones, and one extension per browser would
  have to be kept up with each browser's store.

## Where the repo does not match yet

No known gaps as of 2026-10-01.

## Open questions

None

## Changing this file

The owner edits this file and sets status back to draft until they confirm the change.

<!-- prettier-ignore-end -->
EOF_FIXTURE
mkdir -p "$(dirname '.agents_workspace/product/business/BUSINESS_PLAN.yaml')"
cat >'.agents_workspace/product/business/BUSINESS_PLAN.yaml' <<'EOF_FIXTURE'
schema: business-plan/v1
status: draft
updated: 2026-10-05
summary: |
  Sell Shelf as a hosted plan for people who do not want to run a server.
pricing: |
  Hosted plan at EUR 4 per month or EUR 40 per year. Self-hosted stays free.
kill_criteria:
  - Fewer than 50 paying users by 2027-03-31 ends the hosted plan.
tests:
  - Landing page with a waitlist, 200 sign-ups by 2026-12-15.
contacts:
  - Possible early user, Dana, dana.reader@example.com
EOF_FIXTURE
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
mkdir -p "$(dirname '.agents_workspace/product/PRD.yaml')"
cat >'.agents_workspace/product/PRD.yaml' <<'EOF_FIXTURE'
schema: prd/v1
status: draft
updated: 2026-10-12
features:
  - id: F01
    name: Save a link
    user: The owner, from any browser
    requirements:
      - A click on the bookmarklet saves the current page, with its title and a readable copy.
      - The library lists saved pages, newest first.
    acceptance:
      - python -m unittest test_app passes.
    depends_on: []
    status: built
    plans:
      - .agents_workspace/product/plan/20261002-091500-save-links.yaml
  - id: F02
    name: Search saved pages
    user: The owner
    requirements:
      - A search for a word lists every saved page whose text holds it, best match first.
    acceptance:
      - Saving three pages and searching a word only the second holds lists the second page first.
    depends_on:
      - F01
    status: planned
    plans:
      - .agents_workspace/product/plan/20261011-140000-search.yaml
  - id: F03
    name: Export as CSV
    user: The owner, moving to another tool
    requirements:
      - The owner downloads every saved page's url, title and save date as one CSV file.
    acceptance:
      - The downloaded file opens in a spreadsheet with one row per saved page.
    depends_on:
      - F01
    status: todo
    plans: []
  - id: F04
    name: Read offline
    user: The owner, on a phone with no network
    requirements:
      - A saved page opens in full, with its images, when the device has no network.
    acceptance:
      - With the network off, opening a page saved earlier shows its full text and images.
    depends_on:
      - F01
    status: todo
    plans: []
non_functional:
  - A save returns in under 2 seconds on a Raspberry Pi 4.
non_goals:
  - item: Sharing pages with friends
    reason: Shelf is personal, per the vision's non-goals.
EOF_FIXTURE
mkdir -p "$(dirname '.agents_workspace/product/PRD.md')"
cat >'.agents_workspace/product/PRD.md' <<'EOF_FIXTURE'
---
schema: prd/v1
generated_from: PRD.yaml
generated_note: "Do not edit. artifact.py renders this file from PRD.yaml: edit the YAML, then run artifact.py render."
status: draft
updated: 2026-10-12
---

<!-- prettier-ignore-start -->

# Product requirements

**Status:** draft, updated 2026-10-12

## Contents

- [01. Features](#01-features)
  - [01.01 F01: Save a link](#0101-f01-save-a-link)
  - [01.02 F02: Search saved pages](#0102-f02-search-saved-pages)
  - [01.03 F03: Export as CSV](#0103-f03-export-as-csv)
  - [01.04 F04: Read offline](#0104-f04-read-offline)
- [02. Non-functional requirements](#02-non-functional-requirements)
- [03. Non-goals](#03-non-goals)

## 01. Features

| Id | Feature | Status | Depends on |
| --- | --- | --- | --- |
| F01 | Save a link | built | None |
| F02 | Search saved pages | planned | F01 |
| F03 | Export as CSV | todo | F01 |
| F04 | Read offline | todo | F01 |

### 01.01 F01: Save a link

**User:** The owner, from any browser

**Status:** built

**Requirements:**

- A click on the bookmarklet saves the current page, with its title and a readable copy.
- The library lists saved pages, newest first.

**Acceptance:**

- python -m unittest test_app passes.

**Depends on:** None

**Plans:** `.agents_workspace/product/plan/20261002-091500-save-links.yaml`

### 01.02 F02: Search saved pages

**User:** The owner

**Status:** planned

**Requirements:**

- A search for a word lists every saved page whose text holds it, best match first.

**Acceptance:**

- Saving three pages and searching a word only the second holds lists the second page first.

**Depends on:** F01

**Plans:** `.agents_workspace/product/plan/20261011-140000-search.yaml`

### 01.03 F03: Export as CSV

**User:** The owner, moving to another tool

**Status:** todo

**Requirements:**

- The owner downloads every saved page's url, title and save date as one CSV file.

**Acceptance:**

- The downloaded file opens in a spreadsheet with one row per saved page.

**Depends on:** F01

**Plans:** None

### 01.04 F04: Read offline

**User:** The owner, on a phone with no network

**Status:** todo

**Requirements:**

- A saved page opens in full, with its images, when the device has no network.

**Acceptance:**

- With the network off, opening a page saved earlier shows its full text and images.

**Depends on:** F01

**Plans:** None

## 02. Non-functional requirements

- A save returns in under 2 seconds on a Raspberry Pi 4.

## 03. Non-goals

- **Sharing pages with friends.** Shelf is personal, per the vision's non-goals.

<!-- prettier-ignore-end -->
EOF_FIXTURE
mkdir -p "$(dirname '.agents_workspace/product/plan/20261011-140000-search.yaml')"
cat >'.agents_workspace/product/plan/20261011-140000-search.yaml' <<'EOF_FIXTURE'
schema: plan/v2
title: Search saved pages
status: ready
created: 2026-10-11
depends_on:
  - .agents_workspace/product/plan/20261002-091500-save-links.yaml
goal: |
  The owner finds a saved page again by a word in its text.
scope:
  in:
    - "GET /search?q=<word> lists saved pages whose text holds the word, best match first."
  out:
    - item: Search by tag
      reason: Shelf has no tags.
design:
  - topic: Index
    decision: |
      SQLite FTS5 table pages_fts over title and text, kept in step by triggers.
phases:
  - name: Search route
    builds: |
      The FTS5 table, its triggers, and GET /search.
    check: |
      python -m unittest test_search passes.
    status: todo
open: []
record:
  - date: 2026-10-11
    event: Planned
    details: status ready
EOF_FIXTURE
mkdir -p "$(dirname '.agents_workspace/product/plan/20261011-140000-search.md')"
cat >'.agents_workspace/product/plan/20261011-140000-search.md' <<'EOF_FIXTURE'
---
schema: plan/v2
generated_from: 20261011-140000-search.yaml
generated_note: "Do not edit. artifact.py renders this file from 20261011-140000-search.yaml: edit the YAML, then run artifact.py render."
title: Search saved pages
status: ready
created: 2026-10-11
---

<!-- prettier-ignore-start -->

**Depends on:** .agents_workspace/product/plan/20261002-091500-save-links.yaml

## Goal

The owner finds a saved page again by a word in its text.

## Scope

**In:**

- GET /search?q=<word> lists saved pages whose text holds the word, best match first.

**Out:**

- Search by tag: Shelf has no tags.

## Design

- **Index** SQLite FTS5 table pages_fts over title and text, kept in step by triggers.

## Phases

### Phase 1: Search route

- **Builds:** The FTS5 table, its triggers, and GET /search.
- **Check:** python -m unittest test_search passes.
- **Status:** todo

## Open

None

## Record

- 2026-10-11 Planned: status ready

<!-- prettier-ignore-end -->
EOF_FIXTURE
git init -q -b main
git add -A
git -c user.name=eval -c user.email=eval@example.com commit -qm 'chore: seed'
