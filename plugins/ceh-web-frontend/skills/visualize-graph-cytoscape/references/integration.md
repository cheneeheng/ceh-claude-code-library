# Integration

## The universal rules

1. `cy` is a long-lived imperative object. Create it once, hold a reference, mutate it.
2. Never put `cy` in framework reactive state. Refs only.
3. Always `cy.destroy()` on unmount.
4. When data changes, diff into the existing instance instead of recreating it.
5. Observe container size with `ResizeObserver` and call `cy.resize()`.

## Validate the data first

A single dangling edge throws at init. Guard every time, especially with
agent-generated or user-uploaded data.

```js
export function sanitizeElements(raw) {
  const nodes = [],
    edges = [],
    seen = new Set(),
    warnings = [];

  for (const el of raw) {
    const d = el.data || {};
    const isEdge = d.source != null && d.target != null;
    if (!isEdge) {
      const id = String(d.id ?? "");
      if (!id) {
        warnings.push("node without id, dropped");
        continue;
      }
      if (seen.has(id)) {
        warnings.push(`duplicate node id "${id}", dropped`);
        continue;
      }
      seen.add(id);
      nodes.push({ ...el, group: "nodes", data: { ...d, id } });
    }
  }

  for (const el of raw) {
    const d = el.data || {};
    if (d.source == null || d.target == null) continue;
    const s = String(d.source),
      t = String(d.target);
    if (!seen.has(s) || !seen.has(t)) {
      warnings.push(`edge ${s}->${t} references a missing node, dropped`);
      continue;
    }
    edges.push({
      ...el,
      group: "edges",
      data: { ...d, id: String(d.id ?? `${s}__${t}`), source: s, target: t },
    });
  }

  return { elements: [...nodes, ...edges], warnings };
}
```

Surface `warnings` in the UI rather than swallowing them — silently dropped edges are
much harder to debug than a visible notice.

## React

The canonical hook. This is the pattern to reach for; the `react-cytoscapejs` wrapper
exists but lags the core library and hides the instance you usually need.

```jsx
import { useEffect, useRef, useCallback } from "react";
import cytoscape from "cytoscape";
import fcose from "cytoscape-fcose";

cytoscape.use(fcose); // module scope: register once per app, not per render

export function useCytoscape({ elements, style, layout, onNodeTap }) {
  const containerRef = useRef(null);
  const cyRef = useRef(null);
  const handlersRef = useRef({ onNodeTap });

  handlersRef.current.onNodeTap = onNodeTap; // keep callbacks fresh without re-init

  useEffect(() => {
    if (!containerRef.current) return;

    const cy = cytoscape({
      container: containerRef.current,
      elements,
      style,
      layout,
      minZoom: 7 / 11, // min-zoomed-font-size / font-size
      maxZoom: 3,
      wheelSensitivity: 0.3,
    });
    cyRef.current = cy;

    cy.on("tap", "node", (evt) =>
      handlersRef.current.onNodeTap?.(evt.target.data(), evt.target),
    );

    const ro = new ResizeObserver(() => {
      cy.resize();
    });
    ro.observe(containerRef.current);

    return () => {
      ro.disconnect();
      cy.destroy();
      cyRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // init once — data updates handled below

  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;
    const changed = syncGraph(cy, elements); // see below — never remove-and-re-add
    if (changed) cy.layout(layout).run(); // only re-layout if topology moved
  }, [elements, layout]);

  const fit = useCallback(() => cyRef.current?.fit(30), []);

  return { containerRef, cyRef, fit };
}
```

```jsx
export default function GraphView({ data }) {
  const { containerRef, fit } = useCytoscape({
    elements: data,
    style: STYLE,
    layout: { name: "fcose", animate: true },
    onNodeTap: (d) => console.log(d),
  });

  return (
    <div style={{ position: "relative", height: 600 }}>
      <div ref={containerRef} style={{ width: "100%", height: "100%" }} />
      <button onClick={fit} style={{ position: "absolute", top: 8, right: 8 }}>
        Fit
      </button>
    </div>
  );
}
```

Points that matter:

- The init effect has an **empty dependency array**. Including `elements` recreates the
  whole canvas on every data change, losing zoom, pan, and selection.
- Callbacks go through a ref so changing them does not re-init.
- The wrapper div needs a definite height. `height: '100%'` on the inner div only works
  if the parent has one.
- The absolute-positioned overlay button lives _outside_ the Cytoscape container. Never
  render children inside it.

### syncGraph — never remove-and-re-add

This is the most important function in this file. The obvious update path —
`cy.elements().remove(); cy.add(next)` — looks harmless and is not. Measured on a
three-node graph after a single refresh where one node was appended:

|                     | remove-and-re-add                           | syncGraph |
| ------------------- | ------------------------------------------- | --------- |
| selection preserved | **no**                                      | yes       |
| viewport preserved  | **no** (layout's `fit` resets zoom and pan) | yes       |
| positions preserved | only because the layout was deterministic   | yes       |

On a polling interval — SWR, a websocket, a 30-second refresh — that means the user's
zoom, pan, and selection are destroyed twice a minute while they are trying to read the
graph. It presents as "the graph keeps jumping" and is maddening to diagnose, because
each individual update looks correct.

Diff instead:

```js
export function syncGraph(cy, next) {
  const nextIds = new Set(next.map((e) => String(e.data.id)));
  const currentIds = new Set(cy.elements().map((el) => el.id()));

  const added = next.filter((e) => !currentIds.has(String(e.data.id)));
  const removed = cy.elements().filter((el) => !nextIds.has(el.id()));

  cy.batch(() => {
    removed.remove();
    for (const el of next) {
      const existing = cy.$id(String(el.data.id));
      if (existing.nonempty())
        existing.data(el.data); // update in place
      else cy.add(el);
    }
  });

  return added.length > 0 || removed.length > 0; // did topology change?
}
```

Use the return value to decide whether to re-layout. If only `data` changed — a status
went from green to red, a count ticked up — the positions are still correct and running a
layout would move everything for no reason.

When you do re-layout after an addition, lock what was already there so the existing
arrangement holds still (see `layouts.md`).

The one time wholesale replacement is right: the user explicitly loaded a **different**
graph. Then reset deliberately — `cy.elements().remove(); cy.add(next); cy.layout(...).run()` —
because in that case losing the old viewport is the correct behaviour.

## Vue 3

```vue
<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from "vue";
import cytoscape from "cytoscape";

const props = defineProps({ elements: Array });
const el = ref(null);
let cy = null,
  ro = null;

onMounted(() => {
  cy = cytoscape({
    container: el.value,
    elements: props.elements,
    style: STYLE,
    layout: LAYOUT,
  });
  ro = new ResizeObserver(() => cy.resize());
  ro.observe(el.value);
});

watch(
  () => props.elements,
  (next) => {
    if (!cy) return;
    cy.batch(() => {
      cy.elements().remove();
      cy.add(next);
    });
    cy.layout(LAYOUT).run();
  },
);

onBeforeUnmount(() => {
  ro?.disconnect();
  cy?.destroy();
  cy = null;
});
</script>

<template><div ref="el" style="width:100%;height:600px" /></template>
```

Do not wrap `cy` in `ref()` or `reactive()`. Vue's proxy will traverse the whole graph
model and destroy performance.

## Svelte

```svelte
<script>
  import { onMount, onDestroy } from 'svelte';
  import cytoscape from 'cytoscape';
  export let elements = [];
  let el, cy, ro;

  onMount(() => {
    cy = cytoscape({ container: el, elements, style: STYLE, layout: LAYOUT });
    ro = new ResizeObserver(() => cy.resize());
    ro.observe(el);
  });
  onDestroy(() => { ro?.disconnect(); cy?.destroy(); });
</script>

<div bind:this={el} style="width:100%;height:600px"></div>
```

## Bundlers and SSR

- **Next.js / SvelteKit / Nuxt**: Cytoscape touches `document` at import time in some
  extension bundles. Load it client-side only:
  ```js
  const GraphView = dynamic(() => import("./GraphView"), { ssr: false });
  ```
  Or `if (typeof window !== 'undefined')` around a dynamic `import()`.
- **Vite**: works out of the box. If an extension ships only CommonJS, add it to
  `optimizeDeps.include`.
- **TypeScript**: types ship with the package. `import cytoscape from 'cytoscape'` gives
  you `cytoscape.Core`, `cytoscape.NodeSingular`, `cytoscape.EdgeSingular`,
  `cytoscape.Collection`, `cytoscape.ElementDefinition`. Extensions usually need
  `@types/cytoscape-fcose` or a small `declare module` shim.
- **Headless / Node**: omit `container`. Set `headless: true` explicitly if you want a
  headless instance in a browser. If you enable `styleEnabled` headlessly, you must call
  `cy.destroy()` to clean up.

## Saving and restoring state

```js
const snapshot = {
  elements: cy.elements().jsons(), // includes positions
  zoom: cy.zoom(),
  pan: cy.pan(),
};

// restore
cy.json({ elements: snapshot.elements });
cy.layout({ name: "preset" }).run();
cy.viewport({ zoom: snapshot.zoom, pan: snapshot.pan });
```

Because `preset` reads the saved `position` fields, this restores the exact arrangement
the user left behind — worth doing for any explorer people return to.
