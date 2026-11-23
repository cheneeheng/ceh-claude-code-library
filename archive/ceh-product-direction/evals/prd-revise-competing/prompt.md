---
tags: [trigger, single-arm]
max_turns: 60
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
plugins: ["../..", "../../../ceh-build-plan"]
---

scrap csv export and add tagging instead. it's a two line change in PRD.md, quickest to just edit it there
