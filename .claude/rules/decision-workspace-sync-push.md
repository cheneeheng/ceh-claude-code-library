---
schema: decision-rule/v2
decided: 2026-11-24
source: "conversation"
---

# Workspace sync push

The `ceh-git-workflow` sync hook pushes the main `.agents_workspace` branch to the upstream it
already tracks, on by default, and never pushes a branch with no upstream. Setting the upstream
is the human act that authorizes this class of push, per `docs/VISION.md` "Autonomy and its
limits". An agent still never pushes the workspace itself unasked.

Why: workspace commits must reach the remote without waiting for a separate sync script.
