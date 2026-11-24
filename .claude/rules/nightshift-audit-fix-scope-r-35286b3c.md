---
schema: nightshift-rule/v1
decided: 2026-11-24
source: "nightshift rule r-35286b3c"
---

# Audit fix scope

Before recommending which audit findings to fix, check recent merged PRs and eval results that touch the audited files and flag any finding that would undo tuned text, because a fix-all recommendation ignored two recent eval-tuning PRs and one finding conflicted with an eval-tuned description.
