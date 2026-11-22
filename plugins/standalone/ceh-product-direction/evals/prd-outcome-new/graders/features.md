---
type: llm
focus:
  source: file
  path: .agents_workspace/product/PRD.yaml
---

The repo is Shelf, a read-later app for one person. Its vision refuses sharing, public profiles
and recommendations, and its goals are instant saving, nothing saved is lost (pages readable with
the network off, a backup restores every page), and anything saved can be found. Its strategy
says to build search of saved pages' text next. Saving links is already built, by plan
20261002-091500-save-links.yaml.

PASS only if every one of these holds for the PRD.yaml shown:

1. No feature in `features` is sharing, public profiles or recommendations.
2. `non_goals` names at least one tempting feature, each with a reason.
3. Saving links is a feature with status built.
4. The first feature with status todo is search over the text of saved pages.
5. Reading saved pages offline and backup with restore each appear as a feature.
6. No requirement names an implementation (SQLite, FTS5, a table, a library, a framework)
   instead of behaviour a user or caller can observe.
7. No feature bundles capabilities that would need more than one build plan, such as search,
   tags and offline reading in one feature.

FAIL if any of them fails, or the file is missing or empty.
