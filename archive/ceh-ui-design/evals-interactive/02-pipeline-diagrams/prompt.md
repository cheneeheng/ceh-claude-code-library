---
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
runs: 3
---

can you make an html page that explains our deploy pipeline for new team members, with diagrams. save it as pipeline.html

Stages:

1. Build: on every push, GitHub Actions builds the Docker image and runs unit tests. A failed test stops the pipeline.
2. Staging: the image is pushed to the registry and deployed to staging. Smoke tests run against staging. A failure rolls staging back to the previous image.
3. Approval: a release manager approves in the Actions UI. No approval within 24 hours cancels the release.
4. Production: canary to 10% of traffic for 30 minutes, watching error rate and p95 latency. If either crosses its threshold the canary rolls back; otherwise traffic moves to 100%.
