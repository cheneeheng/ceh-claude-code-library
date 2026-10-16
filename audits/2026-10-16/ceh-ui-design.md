# Model audit: ceh-ui-design

- Date: 2026-10-16
- claude-code 2.1.301
- Edits applied: no

## Unpinned audit against fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5

Audit model: sonnet-5-5, effort: medium. Raw output: [ceh-ui-design.doctor.md](ceh-ui-design.doctor.md).

## Kept changes

### plugins/standalone/ceh-ui-design/skills/design-ui/SKILL.md:327
**Rule 3.** This is a model-independent defect: two instructions contradict each other. The file says "Animate `transform` and `opacity` only" at :327. It also tells the model to use `--dur-fast` for "color changes" (:321–322), to "lift with a deeper shadow" (:312) and to have state changes "transition color" (:313).

Backing quote: none needed beyond the file's own text. Under rule 3 the fault is the contradiction. The reflow reason the file gives covers `width`, `height`, `top` and `margin`, not color or shadow.

Before:
```
- **Animate `transform` and `opacity` only.** Animating `width`, `height`, `top`, or `margin`
  reflows the page on every frame and jank shows first on slow hardware. Expand a panel with a
  `transform` or a `grid-template-rows` transition, not `height: auto` hacks.
```
After:
```
- **Move and resize with `transform` and `opacity`.** Animating `width`, `height`, `top`, or
  `margin` reflows the page on every frame and jank shows first on slow hardware. Expand a panel
  with a `transform` or a `grid-template-rows` transition, not `height: auto` hacks. Color,
  background, and shadow transitions at `--dur-fast` do not reflow and are fine.
```

### plugins/standalone/ceh-ui-design/skills/design-ui/SKILL.md:374
**Rule 3.** This is a model-independent defect: the review pass contradicts the shipped examples. The checklist says "no hardcoded hex, px sizes, or shadows" (:374), but `references/examples.md` hardcodes `10px` nodes, `28px`, `38px` and `1200px`. Line 103 already limits the rule to spacing, with "Use only the theme's spacing tokens (4px grid)".

Backing quote: none needed beyond the file's own text. Under rule 3 the fault is that the two passages disagree.

Before:
```
6. **Token compliance:** no hardcoded hex, px sizes, or shadows — `var(--token)` everywhere.
```
After:
```
6. **Token compliance:** no hardcoded hex, shadows, or font sizes, and spacing only from
   `--space-*`. A px value is allowed for a fixed component dimension no token covers (a stepper
   node, a monogram tile, a content-column cap).
```

### plugins/standalone/ceh-ui-design/skills/design-ui/SKILL.md:407
**Rule 3.** This is the same contradiction as the previous change, in the sentence the report's hunk 2 did not cover. The contract section says "never hardcode a hex, px size, or shadow", which the examples also break.

Backing quote: none needed beyond the file's own text. Under rule 3 the fault is that the two passages disagree.

Before:
```
Use the tokens and classes below — never hardcode a hex, px size, or shadow. Anything the template
does not cover, build with `var(--token)` values so it re-themes with the rest.
```
After:
```
Use the tokens and classes below — never hardcode a hex, shadow, or font size, and take spacing
from `--space-*`. A px value is fine for a fixed component dimension no token covers. Anything the
template does not cover, build with `var(--token)` values so it re-themes with the rest.
```

### plugins/standalone/ceh-ui-design/skills/design-ui/references/examples.md:32
**Rule 3.** This is a model-independent defect: the example's off-scale padding breaks the file's own rule that spacing comes only from the theme's tokens (:103). `var(--space-1)` is 4px on the 4px grid.

Backing quote: none needed beyond the file's own text. Under rule 3 the fault is that the example and the rule disagree.

Before:
```
padding: 2px var(--space-2);
```
After:
```
padding: var(--space-1) var(--space-2);
```

### plugins/standalone/ceh-ui-design/skills/design-ui/SKILL.md:394
**Rule 3.** This is a model-independent defect: the claim is false, and the file contradicts itself. :394–395 and :443–444 say the swap needs "no markup changes". But `--shadow-lg` and `--weight-heavy` exist only in Meridian, and :414 and :420 already say so.

Backing quote: none needed beyond the file's own text. Under rule 3 the fault is that the claim contradicts :414 and :420.

Before (:394–395):
```
  the same token names and component classes, so the choice is purely look-and-feel — swap later
  by replacing one CSS file, with no markup changes. To preview, open
```
After:
```
  the same token names and component classes except Meridian's `--shadow-lg` and `--weight-heavy`,
  so the choice is look-and-feel — swap later by replacing one CSS file, and keep markup off those
  two tokens so it survives the swap. To preview, open
```
Before (:443–444):
```
To restyle the whole app later: replace the project's `brand.css` with the other template's — the
shared token + class contract means markup does not change.
```
After:
```
To restyle the whole app later: replace the project's `brand.css` with the other template's — the
shared token + class contract means markup does not change, provided it avoids Meridian's
`--shadow-lg` and `--weight-heavy`.
```

I dropped three items from the report:
- **Vocabulary flag (report item 4).** It is flag-only and proposes no change.
- **Ask-the-user steps (:392, :59).** The report leaves this to the user, and no page above settles it.
- **Micro-interactions "one property group" line (:311–314).** I considered it and left it out, because it needs the user's design call.
