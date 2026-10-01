# Performance

## Why it degrades

Cost scales with element count, with visual richness, and with rendered canvas area.
Edges are the expensive part — especially bezier curves in multigraphs. A high device
pixel ratio multiplies the area being drawn, so retina displays are slower.

## Size tiers

| Elements     | What to do                                                                                                                        |
| ------------ | --------------------------------------------------------------------------------------------------------------------------------- |
| < 500        | Nothing. Use whatever styling you like.                                                                                           |
| 500–2,000    | Set `min-zoomed-font-size`, drop edge labels, use `animate: false` on layouts.                                                    |
| 2,000–5,000  | Add the tier-2 items plus haystack or straight edges, no dashes, no background images, `pixelRatio: 1`. Consider level-of-detail. |
| 5,000–10,000 | Interaction is sluggish even tuned. Use lazy expansion so you never render it all.                                                |
| > 10,000     | Wrong library. Sigma.js, a WebGL renderer, or server-side layout rendered to tiles.                                               |

## Optimisations, in descending order of impact

**Use `cy.$id('foo')`.** ID lookup uses a hash table; selector search walks the
collection. `cy.$('#foo')` is optimised to use the table too, but pays parsing cost.

**Batch modifications.** `cy.batch(fn)` collapses many style recalculations and redraws
into one. Worst case without it is `eles.length × numOps` style updates.

**Cut labels.** Drawing text is expensive.

- `min-zoomed-font-size: 8` — skips labels that would be unreadable anyway. Biggest
  single win.
- Drop edge labels entirely, or show them only on hover.
- Label backgrounds and outlines add cost; keep the outline (legibility) and skip the
  background.

**Simplify edges.**

- `curve-style: 'haystack'` is the fastest, but forfeits arrows, loops, and compound
  support. `straight` is the fastest style that keeps arrows.
- Solid lines only — dotted and dashed are much more expensive.
- Arrows cost; drop them if direction carries no meaning.
- Opaque edges with arrows are more than twice as fast as semi-transparent ones.

**Simplify nodes.** Background images are the costly part; the cheapest are
`background-repeat: no-repeat` with `background-clip: none`. Pre-clip images rather than
relying on software clipping. Node borders cost a little — test removing them.

**Avoid function style values.** `data()` and `mapData()` are cached; functions are
recomputed. If you must use a function, memoize it.

**Avoid compound and edge selectors** (`$node node`, `$node -> node`) — both require
traversals.

**Set `pixelRatio: 1`** for large graphs on high-density displays. Rendering gets less
crisp, noticeably faster.

**Skip compound nodes** if the grouping is not essential — they make style calculation
and rendering more expensive.

**`hideEdgesOnViewport: true`** hides edges during pan, zoom, and node drag. Only matters
on very large graphs.

**`textureOnViewport: true`** caches the viewport as a texture during pan/zoom instead of
re-rendering. The cheapest possible option, and only worth it at the extreme.

**Recycle instances** rather than `cy.destroy()` + recreate in loops — it keeps heap
growth and GC pressure lower.

**Limit overlays.** `overlay-opacity` cannot be cached. The default stylesheet applies it
only to the single active element for exactly this reason.

## Layout cost

Layout is often slower than rendering.

- `animate: false` on force layouts skips the visible settle entirely.
- `fcose` with `quality: 'draft'` is dramatically faster than `'proof'`.
- Cap `numIter` on `cose` (default 1000).
- Lay out once on load. Re-run only when topology changes, not when styles or selection
  change.
- Lock everything you are not moving before a partial re-layout — fewer nodes in the
  simulation is faster _and_ less disorienting.

## Level of detail

Simplify what is drawn as the user zooms out:

```js
cy.on("zoom", () => {
  const far = cy.zoom() < 0.5;
  cy.batch(() => {
    cy.edges().toggleClass("lod-simple", far);
    cy.nodes().toggleClass("lod-nolabel", far);
  });
});
```

```js
{ selector: 'edge.lod-simple',  style: { 'curve-style': 'straight', 'target-arrow-shape': 'none' } },
{ selector: 'node.lod-nolabel', style: { 'label': '' } }
```

Debounce or throttle the handler — `zoom` fires on every wheel step.

## Measuring

```js
console.time("layout");
cy.layout({ name: "fcose", animate: false }).run();
console.timeEnd("layout");
console.log(cy.nodes().length, "nodes;", cy.edges().length, "edges");
```

Profile with the browser's performance panel and look at which is dominant: long tasks
during layout point at the algorithm, sustained frame cost during pan points at render
complexity. They need different fixes, so measure before tuning.
