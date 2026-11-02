---
schema: fix-record/v1
status: fixed
date: 2026-11-02
---

# A click on a folded Topic title highlights text instead of toggling it

**Symptom:** Real SGR mouse input over a pty on a mod Button in Claude Code 2.1.316: a second click
300 ms after the first → `presses +1 highlighted=True`, and a click with a one-cell slip →
`presses +0 highlighted=True`.

## Diagnosis

| Hypothesis                                                   | Refuted by                                   | Result                                                                                                                                                                    |
| ------------------------------------------------------------ | -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The mod's toggle drops a press or redraws wrongly            | A repeat press in the test kit not toggling  | refuted: `ui.press` twice toggled twice in `claude plugin test`, and the kit skips the terminal's mouse path, so it cannot see this bug                                   |
| The engine reads a quick second click as a word select       | A second click within the window pressing    | confirmed: the pty run above, and the 2.1.316 bundle counts a click within `GUn=500` ms and 1 cell as `clickCount>=2`, calls `onMultiClick`, and returns before any press |
| A drag of one cell starts a selection and swallows the press | A one-cell slip still pressing               | confirmed: the pty run above, `presses +0 highlighted=True`                                                                                                               |
| The mod's Button can opt out of the click chain              | A Button prop or handler that ends the chain | refuted: `ButtonProps` has none, and in the bundle the mod Button's `onClick` never calls `endClickChain`, which only an engine component calls                           |

**Cause:** `plugins/standalone/ceh-every-session/hooks/fold-replies.tsx` drew the title as a
`Button`, and Claude Code hands a Button's clicks to its text selection first, so a re-click inside
500 ms and one cell, or a slip between press and release, selects text and never presses.

**Prediction:** The same input on a `Client`, whose press the engine gives to `onPointerPress` before
it counts clicks, never selects → `presses +2 highlighted=False` at 300 ms, `presses +1
highlighted=False` on the slip. Both seen.

## Fix

In a terminal the title is now a `Client` (`hooks/fold-title.tsx`), which holds the pointer from
press to release, so nothing can select it. It toggles on release over the title and ignores a
toggle within 200 ms of the last, so an accidental double click counts once. Other surfaces keep the
Button, since a native button does not select.

**Tests:**

- `in a terminal a topic title takes its clicks itself, so the transcript cannot select it` —
  protects: the terminal draws no Button for a title and a click toggles it; fails_when: the title
  goes back to a Button; why_new: earlier tests pressed by key, past the mouse path.
- `an accidental double click on a topic counts once, a later click counts again` — protects: the
  200 ms window; fails_when: the window is dropped or never reopens; why_new: new behavior.
- `a click whose hand slips along the title still counts, one dragged off it does not` — protects:
  release over the title decides; fails_when: a slip is dropped or a drag off toggles; why_new: new
  behavior.

**Unverified:** A person's own clicks: every mouse run was scripted input, in a pty with a 110-column
screen. Run on a fork of a real session, the title toggled, did not select, and let the wheel scroll.
The effect of many `Client`s in a very long session was not measured.
