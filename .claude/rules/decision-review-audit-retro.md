---
schema: decision-rule/v2
decided: 2026-11-19
source: "conversation"
---

# Review, audit, retro

A **review** checks work that is finished but not yet marked done or shipped, and ends in a
verdict: done, or not yet. An **audit** checks work that is already marked done or shipped, by a
reader independent of whoever built and checked it, and ends in findings on its state. A **retro**
looks back at how the work went, not at the work itself, and ends in learnings that change the
next piece of work. Two questions sort a request. Is it about how the work went? Then it is a
retro. Otherwise, has the work been marked done or shipped? No is a review, yes is an audit. The
state of the work decides, not the word the user typed. For an agent, an independent reader is one
that has not seen the session that built the work. A review saves to `product/review/<kind>/` and
is edited in place as its findings are fixed. An audit saves to `product/audit/<kind>/` and a
retro to `product/retro/`, each written once, so a rerun is a new file. A new skill, schema or
folder takes the word that matches.

Why: the folders and the file-name forms already treat the three as different kinds, and without a test a new skill has nothing to choose its verb or its save folder by.
