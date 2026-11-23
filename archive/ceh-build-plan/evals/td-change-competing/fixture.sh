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

A self-hosted read-later app for one person. Nothing is built yet: the vision, the strategy and the
product requirements are in `.agents_workspace/product/`.
EOF_FIXTURE
mkdir -p "$(dirname '.agents_workspace/product/PRD.yaml')"
cat >'.agents_workspace/product/PRD.yaml' <<'EOF_FIXTURE'
schema: prd/v1
status: adopted
updated: 2026-10-08
features:
  - id: F01
    name: Save a link
    user: The owner, from any browser or phone
    requirements:
      - A click on the bookmarklet saves the current page, with its title and a readable copy of its text and images.
      - Saving a url that is already saved keeps one copy and says it was saved before.
    acceptance:
      - Saving the same url twice leaves one page in the library and the second save says "already saved".
      - A save of a 1 MB page returns in under 2 seconds on a Raspberry Pi 4.
    depends_on: []
    status: todo
    plans: []
  - id: F02
    name: Library
    user: The owner
    requirements:
      - The library lists saved pages, newest first, 50 to a page.
      - Opening a page shows its saved copy, not the live site.
    acceptance:
      - With 120 pages saved, the library shows 50, then 50, then 20.
    depends_on:
      - F01
    status: todo
    plans: []
  - id: F03
    name: Search saved pages
    user: The owner
    requirements:
      - A search for a word lists every saved page whose title or text holds it, best match first.
    acceptance:
      - Saving three pages and searching a word only the second holds lists the second page first.
    depends_on:
      - F02
    status: todo
    plans: []
  - id: F04
    name: Read offline
    user: The owner, on a phone with no network
    requirements:
      - A page opened once on the phone opens again in full with no network.
    acceptance:
      - With the network off, a page opened earlier shows its full text and images.
    depends_on:
      - F02
    status: todo
    plans: []
  - id: F05
    name: Backup and restore
    user: The owner, moving to a new server
    requirements:
      - The owner downloads one backup file holding every saved page, and restores it on a new server.
    acceptance:
      - Restoring a backup on an empty server lists the same pages, and each opens in full.
    depends_on:
      - F02
    status: todo
    plans: []
non_functional:
  - Runs on a Raspberry Pi 4 with 4 GB of memory, as one process.
  - A save returns in under 2 seconds.
  - Only the owner can save, read or search, and the server is reachable from the internet.
  - Holds 20,000 saved pages without the library or search slowing past 1 second.
non_goals:
  - item: Sharing pages with friends or public profiles
    reason: Shelf is personal, per the vision's non-goals.
  - item: Recommendations
    reason: The owner chooses what to save, per the vision's non-goals.
EOF_FIXTURE
mkdir -p "$(dirname '.agents_workspace/product/PRD.md')"
cat >'.agents_workspace/product/PRD.md' <<'EOF_FIXTURE'
---
schema: prd/v1
generated_from: PRD.yaml
generated_note: "Do not edit. artifact.py renders this file from PRD.yaml: edit the YAML, then run artifact.py render."
status: adopted
updated: 2026-10-08
---

<!-- prettier-ignore-start -->

# Product requirements

**Status:** adopted, updated 2026-10-08

## Contents

- [01. Features](#01-features)
  - [01.01 F01: Save a link](#0101-f01-save-a-link)
  - [01.02 F02: Library](#0102-f02-library)
  - [01.03 F03: Search saved pages](#0103-f03-search-saved-pages)
  - [01.04 F04: Read offline](#0104-f04-read-offline)
  - [01.05 F05: Backup and restore](#0105-f05-backup-and-restore)
- [02. Non-functional requirements](#02-non-functional-requirements)
- [03. Non-goals](#03-non-goals)

## 01. Features

| Id | Feature | Status | Depends on |
| --- | --- | --- | --- |
| F01 | Save a link | todo | None |
| F02 | Library | todo | F01 |
| F03 | Search saved pages | todo | F02 |
| F04 | Read offline | todo | F02 |
| F05 | Backup and restore | todo | F02 |

### 01.01 F01: Save a link

**User:** The owner, from any browser or phone

**Status:** todo

**Requirements:**

- A click on the bookmarklet saves the current page, with its title and a readable copy of its text and images.
- Saving a url that is already saved keeps one copy and says it was saved before.

**Acceptance:**

- Saving the same url twice leaves one page in the library and the second save says "already saved".
- A save of a 1 MB page returns in under 2 seconds on a Raspberry Pi 4.

**Depends on:** None

**Plans:** None

### 01.02 F02: Library

**User:** The owner

**Status:** todo

**Requirements:**

- The library lists saved pages, newest first, 50 to a page.
- Opening a page shows its saved copy, not the live site.

**Acceptance:**

- With 120 pages saved, the library shows 50, then 50, then 20.

**Depends on:** F01

**Plans:** None

### 01.03 F03: Search saved pages

**User:** The owner

**Status:** todo

**Requirements:**

- A search for a word lists every saved page whose title or text holds it, best match first.

**Acceptance:**

- Saving three pages and searching a word only the second holds lists the second page first.

**Depends on:** F02

**Plans:** None

### 01.04 F04: Read offline

**User:** The owner, on a phone with no network

**Status:** todo

**Requirements:**

- A page opened once on the phone opens again in full with no network.

**Acceptance:**

- With the network off, a page opened earlier shows its full text and images.

**Depends on:** F02

**Plans:** None

### 01.05 F05: Backup and restore

**User:** The owner, moving to a new server

**Status:** todo

**Requirements:**

- The owner downloads one backup file holding every saved page, and restores it on a new server.

**Acceptance:**

- Restoring a backup on an empty server lists the same pages, and each opens in full.

**Depends on:** F02

**Plans:** None

## 02. Non-functional requirements

- Runs on a Raspberry Pi 4 with 4 GB of memory, as one process.
- A save returns in under 2 seconds.
- Only the owner can save, read or search, and the server is reachable from the internet.
- Holds 20,000 saved pages without the library or search slowing past 1 second.

## 03. Non-goals

- **Sharing pages with friends or public profiles.** Shelf is personal, per the vision's non-goals.
- **Recommendations.** The owner chooses what to save, per the vision's non-goals.

<!-- prettier-ignore-end -->
EOF_FIXTURE
mkdir -p "$(dirname '.agents_workspace/product/ARCHITECTURE.yaml')"
cat >'.agents_workspace/product/ARCHITECTURE.yaml' <<'EOF_FIXTURE'
schema: architecture/v3
overview:
  bullets:
    - Shelf saves the page its owner is reading and keeps a readable copy on the owner's server.
    - The bookmarklet sends a link, the saver fetches and stores the page, and the library lists and searches what was saved.
  flow: |
    flowchart LR
        Bookmarklet --> Saver --> Library
diagrams:
  - name: Components
    planned: true
    walkthrough: |
      Read it left to right: a link comes in from the browser and ends as a stored page.
    notice:
      - The saver and the library share one database file and no other state.
    mermaid: |
      flowchart LR
          B[Bookmarklet] -->|POST /api/pages| S[Saver]
          S --> D[(shelf.db)]
          L[Library] --> D
  - name: Data model
    planned: true
    walkthrough: |
      One table holds every saved page, and a full-text index mirrors two of its columns.
    notice: []
    mermaid: |
      erDiagram
          PAGE {
              int id PK
              text url UK
              text title
              text text
              text html
              text saved_at
          }
technical_design:
  - topic: Stack
    choice: |
      - Python 3.13, standard library only, one process: `python -m shelf` serves on port 8080.
      - Code in `shelf/`, tests in `tests/` with `unittest`: `python -m unittest` runs them.
    reason: |
      F01 to F05 all run inside this one process, and the Pi target rules out a second service.
      Flask was rejected because the five routes need nothing the standard library lacks.
  - topic: Persistence
    choice: |
      One SQLite file, `shelf.db`, in WAL mode.

      | Table     | Columns                                                                                    |
      | --------- | ------------------------------------------------------------------------------------------ |
      | pages     | id INTEGER PK, url TEXT UNIQUE NOT NULL, title TEXT, text TEXT, html TEXT, saved_at TEXT NOT NULL |
      | pages_fts | FTS5 over pages.title and pages.text, kept in step by triggers                              |
    reason: |
      F01 to F05 read and write the same pages, and F03 needs a full-text index. PostgreSQL was
      rejected because a second server breaks the vision's one person, one server principle.
  - topic: Interfaces
    choice: |
      | Route                | Body        | Success                  | Errors                    |
      | -------------------- | ----------- | ------------------------ | ------------------------- |
      | POST /api/pages      | url (form)  | 201, page id             | 400 bad url, 409 saved before |
      | GET /api/pages?page= | none        | 200, 50 pages, newest first | 400 bad page           |
      | GET /api/search?q=   | none        | 200, pages, best first   | 400 empty q               |

      Every error body is JSON: `{"error": "<code>", "message": "<text>"}`.
    reason: |
      The bookmarklet, the library and the phone's offline copy all call these routes. HTML-only
      responses were rejected because the offline copy needs JSON.
key_decisions:
  - date: 2026-09-20
    title: Python standard library only
    status: Accepted
    context: |
      The app must run on a Raspberry Pi 4 with nothing to install but Python.
    decision: |
      Use Python 3 and its standard library, with no third-party packages.
    consequences: |
      HTML parsing and the HTTP server are the standard library's, which is enough for one user.
  - date: 2026-09-20
    title: Store pages in SQLite
    status: Accepted
    context: |
      Pages need one durable store on the owner's server, and a backup should be one file.
    decision: |
      Keep every page in one SQLite database file.
    consequences: |
      A backup is a copy of one file. Only one process should write at a time.
EOF_FIXTURE
mkdir -p "$(dirname '.agents_workspace/product/ARCHITECTURE.md')"
cat >'.agents_workspace/product/ARCHITECTURE.md' <<'EOF_FIXTURE'
---
schema: architecture/v3
generated_from: ARCHITECTURE.yaml
generated_note: "Do not edit. artifact.py renders this file from ARCHITECTURE.yaml: edit the YAML, then run artifact.py render."
---

<!-- prettier-ignore-start -->

# Architecture

## Contents

- [01. Overview](#01-overview)
- [02. Components](#02-components)
- [03. Data model](#03-data-model)
- [04. Technical Design](#04-technical-design)
  - [04.01 Stack](#0401-stack)
  - [04.02 Persistence](#0402-persistence)
  - [04.03 Interfaces](#0403-interfaces)
- [05. Key Decisions](#05-key-decisions)

## 01. Overview

- Shelf saves the page its owner is reading and keeps a readable copy on the owner's server.
- The bookmarklet sends a link, the saver fetches and stores the page, and the library lists and searches what was saved.

```mermaid
flowchart LR
    Bookmarklet --> Saver --> Library
```

## 02. Components

**Planned:** not built yet.

Read it left to right: a link comes in from the browser and ends as a stored page.

- The saver and the library share one database file and no other state.

```mermaid
flowchart LR
    B[Bookmarklet] -->|POST /api/pages| S[Saver]
    S --> D[(shelf.db)]
    L[Library] --> D
```

## 03. Data model

**Planned:** not built yet.

One table holds every saved page, and a full-text index mirrors two of its columns.

```mermaid
erDiagram
    PAGE {
        int id PK
        text url UK
        text title
        text text
        text html
        text saved_at
    }
```

## 04. Technical Design

### 04.01 Stack

- Python 3.13, standard library only, one process: `python -m shelf` serves on port 8080.
- Code in `shelf/`, tests in `tests/` with `unittest`: `python -m unittest` runs them.

**Reason:** F01 to F05 all run inside this one process, and the Pi target rules out a second service.
Flask was rejected because the five routes need nothing the standard library lacks.

### 04.02 Persistence

One SQLite file, `shelf.db`, in WAL mode.

| Table     | Columns                                                                                    |
| --------- | ------------------------------------------------------------------------------------------ |
| pages     | id INTEGER PK, url TEXT UNIQUE NOT NULL, title TEXT, text TEXT, html TEXT, saved_at TEXT NOT NULL |
| pages_fts | FTS5 over pages.title and pages.text, kept in step by triggers                              |

**Reason:** F01 to F05 read and write the same pages, and F03 needs a full-text index. PostgreSQL was
rejected because a second server breaks the vision's one person, one server principle.

### 04.03 Interfaces

| Route                | Body        | Success                  | Errors                    |
| -------------------- | ----------- | ------------------------ | ------------------------- |
| POST /api/pages      | url (form)  | 201, page id             | 400 bad url, 409 saved before |
| GET /api/pages?page= | none        | 200, 50 pages, newest first | 400 bad page           |
| GET /api/search?q=   | none        | 200, pages, best first   | 400 empty q               |

Every error body is JSON: `{"error": "<code>", "message": "<text>"}`.

**Reason:** The bookmarklet, the library and the phone's offline copy all call these routes. HTML-only
responses were rejected because the offline copy needs JSON.

## 05. Key Decisions

### 2026-09-20 — Python standard library only

**Status:** Accepted
**Context:** The app must run on a Raspberry Pi 4 with nothing to install but Python.
**Decision:** Use Python 3 and its standard library, with no third-party packages.
**Consequences:** HTML parsing and the HTTP server are the standard library's, which is enough for one user.

### 2026-09-20 — Store pages in SQLite

**Status:** Accepted
**Context:** Pages need one durable store on the owner's server, and a backup should be one file.
**Decision:** Keep every page in one SQLite database file.
**Consequences:** A backup is a copy of one file. Only one process should write at a time.

<!-- prettier-ignore-end -->
EOF_FIXTURE
git init -q -b main
git add -A
git -c user.name=eval -c user.email=eval@example.com commit -qm 'chore: seed'
