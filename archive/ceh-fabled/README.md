# ceh-fabled

Claude Code plugin that encodes the _process_ separating a rushed first-pass answer from
frontier-grade output: deliberate reasoning before answering, generating alternatives, adversarial
self-review, explicit verification, and calibrated, conviction-forward delivery. It raises the
floor on any non-trivial task without pretending to add capability the underlying model lacks.

## Skills

| Skill                | Description                                                                                                                                                                                                                                                                                                                                                                                                              |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `fabled`             | Apply frontier-grade reasoning discipline to analysis, decisions, tradeoffs, debugging, architecture, planning, evaluation, research, and substantive writing                                                                                                                                                                                                                                                            |
| `fabled-plan-review` | Review an existing plan against frontier-grade planning discipline — problem fidelity, alternatives, decomposition, pre-mortem, verifiability — delivering a verdict and concrete fixes                                                                                                                                                                                                                                  |
| `fabled-stuck`       | Escape a failure loop after repeated failed fix attempts — freeze, inventory the attempts, attack their shared assumption, re-derive the diagnosis from raw evidence, probe before fixing                                                                                                                                                                                                                                |
| `fabled-voice`       | Deliver responses in fable's writing style — form only, never content: finding-first progress lines between tool calls, verdict-first advisory answers that close on a calibration, and closing reports built from bold inline labels, hard numbers, a validated/not-validated ledger, and a standing offer instead of a permission question. **Always on** — a SessionStart hook loads it at the start of every session |

Invoke manually:

```
/ceh-fabled:fabled
/ceh-fabled:fabled-plan-review
/ceh-fabled:fabled-stuck
/ceh-fabled:fabled-voice
```

Or load automatically when the task involves:

- Analysis, decisions, tradeoffs, or evaluation with more than one plausible answer
- Debugging, architecture, or planning where a shallow answer risks being wrong
- Research and fact-finding where accuracy is the product
- A challenge to a previous answer, a reported error, or a request for a review or audit
- A failure loop — two or more failed fixes for the same symptom, "still broken", "same error"

## Hooks

| Event                                              | Script                  | Effect                                                                                                                                                                                         |
| -------------------------------------------------- | ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `SessionStart` (`startup\|resume\|clear\|compact`) | `scripts/load-voice.sh` | Injects a directive to invoke `fabled-voice`, so every session's responses are delivered in fable's form. Ordered after the `ceh-coding-agent` load directive when both plugins are installed. |

Requires `bash` on `PATH`. To opt out, disable the `ceh-fabled` plugin's hooks or remove
`hooks/hooks.json`.

## The Core Loop

The skill runs six stages in order, scaled to task difficulty (trivial / standard / hard):

| Stage                                 | What it does                                                                              |
| ------------------------------------- | ----------------------------------------------------------------------------------------- |
| 1. Understand the actual problem      | Restate the task; surface the unstated end, implied constraints, and likely failure mode  |
| 2. Generate alternatives              | Produce at least two genuinely different candidates before converging on one              |
| 3. Do the work at full depth          | Decompose into checkable parts; separate known from inferred; resolve uncertainties       |
| 4. Adversarial self-review            | Attack the draft as a skeptical expert; fix real flaws instead of caveating them          |
| 5. Verify what's verifiable           | Run or trace code, recompute arithmetic, check post-cutoff facts and internal consistency |
| 6. Deliver with calibrated conviction | Lead with the verdict; commit where the evidence supports it; state confidence honestly   |

## Reference files

The skill loads reference files by task type (`ceh-fabled/skills/fabled/references/`):

| Reference                   | Load for                                                          |
| --------------------------- | ----------------------------------------------------------------- |
| `reasoning-moves.md`        | Any hard or novel task, or when stuck — the core thinking toolkit |
| `decision-standards.md`     | Decisions, evaluations, recommendations, tradeoff analysis        |
| `technical-rigor.md`        | Debugging, code review, code, architecture, math, data analysis   |
| `research-epistemics.md`    | Research, fact-finding, current-events questions                  |
| `writing-standards.md`      | Prose the user will keep, publish, send, or read closely          |
| `interaction-discipline.md` | Challenges, corrections, ambiguity, or long multi-step work       |

## Anti-patterns it prevents

First-thought commitment, confidence laundering, menu hedging, caveat patching, sycophantic drift,
format inflation, verification skipping, scope drift, pushback capitulation, fabricated specifics,
rumination as thinking, and over-processing trivial tasks.
