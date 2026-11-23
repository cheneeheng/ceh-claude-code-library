---
description: >-
  Outcome: a new page from an empty folder, graded on the theme install and the unhappy-path
  states the skill promises. Synthetic.
tags: [outcome]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Skill, Read, Glob, Grep, Edit, Write]
append_system_prompt: No user is present to answer questions. Do not ask, make the conservative choice and continue.
---

build projects.html, a plain HTML page for our internal tool that lists projects from GET
/api/projects. it returns [{id, name, status, updated}], status is draft, active or archived.
