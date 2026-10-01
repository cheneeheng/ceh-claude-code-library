# Verification checklist

Run through this before delivering. Each item corresponds to a failure that only shows
up at runtime, which is exactly the kind an agent is most likely to ship.

## Renders at all

- [ ] Container has an explicit non-zero height, set in CSS parsed before init.
- [ ] Container is an empty div with no children of your own.
- [ ] The library loaded — no 404 on the CDN URL, no `cytoscape is not defined`.
- [ ] Extensions are registered with `cytoscape.use(...)` **before** `cytoscape()` runs.
- [ ] Console has no Cytoscape warnings. Leave `cytoscape.warnings(true)` on while
      developing; the warnings name the malformed element.

## Data is valid

- [ ] Every element has a unique string `id`.
- [ ] Every edge's `source` and `target` name nodes that exist in the same element list.
- [ ] No duplicate ids between nodes and edges.
- [ ] Empty-data case handled — zero nodes should show a placeholder message, not a
      blank canvas or a thrown error.
- [ ] Single-node case handled — layouts and `cy.fit()` behave oddly with one element;
      set a sensible zoom.

## Looks right

- [ ] If the graph is directed, `curve-style` is set to something other than `haystack`,
      and arrows actually appear.
- [ ] `target-arrow-color` matches `line-color` unless the mismatch is intentional.
- [ ] Labels are readable: not overlapping nodes, not clipped, with a `text-outline` or
      background where they cross edges.
- [ ] Long labels are handled — `text-wrap: 'ellipsis'` with a `text-max-width`, or
      `'wrap'`. Untruncated labels overlap and look broken.
- [ ] **Readability measured at real data volume**, not on a small fixture. After the
      layout settles, compute `Math.min(cy.width()/bb.w, cy.height()/bb.h)`; if
      `fitZoom × font-size` is under your `min-zoomed-font-size` (~7px), do not `cy.fit()`
      — set a readable zoom and give the user search or collapse instead. Gate on the
      pixel size, never on a zoom constant.
- [ ] The readability check actually ran. A layout passed as the `layout:` constructor
      option never emits a `layoutstop` your code can hear — use `cy.ready()` there, or
      move the layout out of the constructor. Confirm the branch fired, don't assume it.
- [ ] `minZoom` is no lower than `min-zoomed-font-size / font-size`, so users cannot
      hand-zoom into unreadability.
- [ ] Nothing is cut off at the edges — `padding` on the layout and on `cy.fit()`.
- [ ] Colours encode a category, not an arbitrary sequence. Two or three ramps, not six.
- [ ] Dark mode tested. Every colour was resolved in JS, not left as a CSS variable.

## Behaves

- [ ] Tapping a node does something visible.
- [ ] Tapping the background clears the selection or highlight.
- [ ] `minZoom` and `maxZoom` set — unbounded zoom lets users lose the graph entirely.
- [ ] `wheelSensitivity` tuned if the graph sits in a scrollable page.
- [ ] Layout completes: for force layouts, `layoutstop` fires and `cy.fit()` runs after
      it, not before — and the handler is bound to a layout you created with `cy.layout()`,
      not to one the constructor already ran.
- [ ] Only one layout runs at a time — the previous one is `stop()`ed.
- [ ] `ResizeObserver` calls `cy.resize()`, and taps land where you click after the
      container changes size.
- [ ] Works on touch: pinch-zoom, drag-pan, tap-select. Test at a narrow viewport.

## Cleans up

- [ ] `cy.destroy()` runs on unmount / teardown.
- [ ] `ResizeObserver` disconnected, `MutationObserver` disconnected, document-level
      keyboard listeners removed.
- [ ] `cy` is held in a ref, not in framework state.
- [ ] Re-rendering the component does not recreate the instance — zoom, pan, and
      selection survive a data update.
- [ ] **On polling or live data, a refresh preserves zoom, pan, and selection.** Test it:
      select a node, zoom in, wait for one refresh cycle. If the view resets, the update
      path is doing `remove()` + `add()` instead of `syncGraph`.

## Scales

- [ ] `min-zoomed-font-size` set if over ~500 elements.
- [ ] Mutations that touch many elements are wrapped in `cy.batch()`.
- [ ] `zoom` / `pan` handlers are throttled.
- [ ] Centrality and clustering computed once at load, not per interaction.

## Degrades honestly

- [ ] Dropped or invalid input is reported to the user, not silently swallowed —
      `sanitize()` warnings are rendered, not just returned.
- [ ] Loading and error states exist for any async data.
- [ ] A text or table alternative to the canvas exists, and the container has an
      `aria-label` plus a short summary. Canvas is invisible to assistive tech.

## Quick smoke test in the console

```js
console.assert(cy.container().clientHeight > 0, "container has no height");
console.assert(cy.nodes().length > 0, "no nodes rendered");
console.assert(
  cy.edges().every((e) => e.source().nonempty() && e.target().nonempty()),
  "dangling edge",
);
console.log("extent", cy.extent(), "zoom", cy.zoom());
```
