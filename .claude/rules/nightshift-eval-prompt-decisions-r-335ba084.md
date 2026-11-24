---
schema: nightshift-rule/v1
decided: 2026-11-24
source: "nightshift rule r-335ba084"
---

# Eval prompt decisions

When writing eval prompts, state the simulated user's decision explicitly so only the intended behaviour passes, and read the first trace before trusting the verdict, because a prompt that left a vision conflict open made the model stop and load the build-plan skill instead of the technical-design skill, wasting the first probe.
