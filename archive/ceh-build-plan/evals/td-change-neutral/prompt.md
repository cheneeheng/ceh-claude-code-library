---
tags: [trigger, single-arm]
max_turns: 60
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
plugins:
  [
    "../..",
    "../../../ceh-codebase-explanation",
    "../../../ceh-product-direction",
  ]
---

I've decided shelf runs on two servers behind a load balancer from now on, I'll update the vision myself. so sqlite has to go, move it to postgres
