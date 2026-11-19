---
schema: decision-rule/v2
decided: 2026-11-19
source: "conversation"
---

# Audit vs review

A **review** judges a proposal or a change before someone acts on it (a plan before the build, a
diff before the merge) and ends in a verdict. An **audit** examines something that already exists
(a codebase, a test suite, an interface) and ends in findings, with no verdict. The test: is
someone waiting on a verdict before acting on the subject? Yes is a review, no is an audit. A
review saves to `product/review/<kind>/` and is edited in place as its findings are fixed. An audit
saves to `product/audit/<kind>/` and is written once, so a rerun is a new file. A new skill, schema
or folder takes the word that matches.

Why: the folders and the file-name forms already treat the two as different kinds, and without a test a new skill has nothing to choose its verb or its save folder by.
