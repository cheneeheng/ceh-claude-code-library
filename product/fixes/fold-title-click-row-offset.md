---
schema: fix-record/v1
status: fixed
date: 2026-11-02
previous: product/fixes/fold-title-click-selects-text.md
---

# A folded Topic title toggles from the row below it, not from the title

**Symptom:** Forked real session through VS Code's own `conpty.dll`, a harness answering the terminal
probes as VS Code's xterm.js 6.1.0-beta.304 does, with a real cell height of 18.6 px →
`title on row 27: title lights up when hovering row offsets [1]`.

## Diagnosis

| Hypothesis                                                                  | Refuted by                                            | Result                                                                                                                                             |
| --------------------------------------------------------------------------- | ----------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| The `Client` region is laid out one row off in its box                      | Hover and click landing on the title in cell reports  | refuted: with the terminal reporting cells, hover hits offset `[0]` at rows 20, 26 and 32, and a click on the title toggles it                     |
| Scrolling leaves the region's row stale                                     | Offset `[0]` after wheel scrolls in cell reports      | refuted: `after wheel up 4 [(26, [(0, [26])])]`, `after wheel up 8 [(32, [(0, [32])])]`                                                            |
| A pointer `Client` turns on pixel reports, and a rounded cell height drifts | No shift with reports in pixels and a fractional cell | confirmed: the debug log says `Mouse reports in pixels` and `cell 8x19px`, and the title's hit row moved `[1]` lower with a real height of 18.6 px |

**Cause:** `plugins/standalone/ceh-every-session/hooks/fold-replies.tsx` drew each title as a `Client`
with an `onPointer` listener. Inferred from the 2.1.316 bundle and from VS Code 1.144's xterm.js:
such a `Client` calls `jAr(v)`, which holds `retainFinePointer` and turns on mode 1016 for the whole
terminal, xterm.js answers `CSI 16 t` with `css.cell.height.toFixed(0)`, and Claude Code computes a
row as `floor(pixelY / height)`, so a fractional cell height drifts the row by one down the screen.

**Prediction:** The same run with a real cell height of 19 px, equal to the one answered →
`title on row 27: title lights up when hovering row offsets [0]`, and still `Mouse reports in pixels`.
Seen. With the title a Button, no `Client` holds the pointer → the harness sees no mode 1016 set and a
click on row 27 at 18.6 px toggles that row's title. Seen.

## Fix

The title is a Button on every surface and `hooks/fold-title.tsx` is gone, so nothing turns on pixel
reports, and the terminal reports cells exactly. This gives back the Button's own fault from the
previous record: a re-click inside 500 ms and one cell, or a slip between press and release, selects
text and does not press. The drift also moved every other click in the session, so it was the larger
fault. The drift itself belongs in Claude Code 2.1.316, which trusts a rounded cell height.

**Tests:**

- `in a terminal a topic title is a Button, since a Client switches the mouse to pixel reports` —
  protects: no `Client` in a drawn reply, and a press toggles; fails_when: the title goes back to a
  `Client`; why_new: the kit's `ui.pointer` hands events to a region directly, past the engine's hit
  test, so no earlier test could see a shifted row.

**Unverified:** A person's own clicks in VS Code. The terminal side was simulated: the harness
answered the probes and sent pixel reports itself, with a cell height I chose, since I cannot read the
user's real one. The one real thing in it is VS Code's own console host.
