---
schema: decision-rule/v2
decided: 2026-11-24
source: "user, README pilot approved 2026-11-24"
paths:
  - "plugins/**/README.md"
---

# Plugin README sections

A plugin README is written for the person deciding whether to install the plugin and learning to
use it. It has these `##` sections, in this order, with plain unnumbered headings: `Install`,
`Skills`, `Agents`, `Hooks`, `Settings`, `How it works`, `Not this plugin`,
`Where its files live`, after one intro paragraph under the H1, which may end in a short bullet
list. A section with nothing to say keeps
its heading and one line, such as "This plugin has no agents." Install links to
`docs/GETTING_STARTED.md` and carries no install command. The Skills table has the columns Skill,
Say or type, What it does, and the Agents table Agent, What it does. Slash commands take the
plugin prefix, `/ceh-<plugin>:<skill>`. Settings lists every
environment variable the plugin reads. Plugin-specific topics go under `How it works` as `###`
subsections. Maintainer-only detail (incidents, measurements, internals, contributor procedures,
history) goes to `plugins/standalone/<plugin>/docs/DESIGN_NOTES.md`, which the site does not
publish, or is deleted when a tracked file already holds it.

Why: the docs site publishes each README as the plugin's page, and the user wants a reader to know
what to expect on every page.
