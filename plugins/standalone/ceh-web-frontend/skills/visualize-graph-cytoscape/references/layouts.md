# Layouts

A layout sets node positions. Because edge length follows from node positions, choosing
the layout is choosing what the graph looks like. Get this right before styling.

```js
const layout = cy.layout({ name: "breadthfirst", directed: true });
layout.run(); // nothing happens until you call run()
```

`cy.layout(opts)` includes every element in the graph. To lay out a subset — for
example, re-positioning only a newly expanded cluster — call `eles.layout(opts)`.

## Lifecycle

Discrete layouts (`grid`, `circle`, `concentric`, `breadthfirst`, `preset`, `random`)
finish synchronously by default. Force-directed layouts do not: `run()` returns
immediately and positions settle over time.

```js
const l = cy.layout({ name: "fcose" });
l.one("layoutstop", () => cy.fit(30));
l.run();

// or
await cy.layout({ name: "fcose" }).run().promiseOn("layoutstop");
```

Events: `layoutstart`, `layoutready` (initial positions set), `layoutstop` (finished or
stopped). Methods: `layout.run()` / `start()`, `layout.stop()`, `layout.on()`,
`layout.promiseOn()` / `pon()`, `layout.one()`, `layout.off()`.

Always keep a reference and `stop()` the previous layout before starting a new one.
Two force layouts running at once fight over positions and never settle.

## Option tips

Every built-in layout's options and defaults are in the Cytoscape.js docs. The ones that matter here:
set `nodeDimensionsIncludeLabels: true` whenever labels are long, since it stops labels
overlapping neighbouring nodes.

For `cose` and `fcose`: raise `nodeRepulsion` (to 8000–15000) and `idealEdgeLength` for airier
graphs. `animate: false` is much faster and avoids a long visible settle. `randomize:
true` helps escape bad local minima when re-running.

## Extension layouts

Install and register before use:

```js
import cytoscape from "cytoscape";
import fcose from "cytoscape-fcose";
cytoscape.use(fcose);
```

| Package                  | `name`         | Best for                           | Notes                                                                                                                                                                                                                                                                                                                             |
| ------------------------ | -------------- | ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `cytoscape-fcose`        | `fcose`        | General networks                   | The default recommendation. Supports compound nodes and placement constraints (`fixedNodeConstraint`, `alignmentConstraint`, `relativePlacementConstraint`). Options mirror `cose-bilkent` plus `quality: 'draft' \| 'default' \| 'proof'`, `randomize`, `nodeSeparation`, `idealEdgeLength`, `nodeRepulsion`, `numIter`, `tile`. |
| `cytoscape-cose-bilkent` | `cose-bilkent` | Compound-heavy graphs              | Predecessor to fcose; still good with nested parents.                                                                                                                                                                                                                                                                             |
| `cytoscape-dagre`        | `dagre`        | DAGs, flowcharts, pipelines        | Layered ranking. Key options: `rankDir` (`TB` `BT` `LR` `RL`), `ranker` (`network-simplex` `tight-tree` `longest-path`), `nodeSep`, `rankSep`, `edgeSep`, `align`. Pair with `curve-style: taxi` for a classic flowchart look. Depends on the `dagre` package.                                                                    |
| `cytoscape-elk`          | `elk`          | Complex DAGs needing clean routing | Wraps Eclipse Layout Kernel. `elk: { algorithm: 'layered' \| 'mrtree' \| 'stress' \| 'radial' \| 'force' \| 'box' \| 'disco' }`. Best orthogonal edge routing available; larger bundle and slower.                                                                                                                                |
| `cytoscape-klay`         | `klay`         | Layered DAGs                       | ELK's predecessor. Use `elk` for new work.                                                                                                                                                                                                                                                                                        |
| `cytoscape-cola`         | `cola`         | Constraint-based, live physics     | Supports alignment/inequality constraints, `flow` for directional bias, and continuous simulation via `infinite: true` — good for drag-to-rearrange UIs.                                                                                                                                                                          |
| `cytoscape-cise`         | `cise`         | Clustered graphs                   | Places each cluster on its own circle; you supply `clusters`.                                                                                                                                                                                                                                                                     |
| `cytoscape-avsdf`        | `avsdf`        | Circular, minimal crossings        | One circle, optimised crossing count.                                                                                                                                                                                                                                                                                             |
| `cytoscape-euler`        | `euler`        | Fast physics                       | Lightweight force simulation.                                                                                                                                                                                                                                                                                                     |
| `cytoscape-spread`       | `spread`       | Even space usage                   | Force + Voronoi relaxation.                                                                                                                                                                                                                                                                                                       |

## Re-running layouts

```js
let current = null;
function relayout(name, extra = {}) {
  if (current) current.stop();
  current = cy.layout({
    name,
    animate: true,
    animationDuration: 400,
    padding: 30,
    ...extra,
  });
  current.run();
}
```

After adding elements, lay out only the new ones and pin the rest, or the whole graph
jumps and the user loses their place:

```js
const added = cy.add(newElements);
cy.nodes().difference(added).lock();
cy.layout({ name: "fcose", randomize: false, animate: true }).run();
cy.nodes().unlock();
```

## Choosing under uncertainty

If you cannot tell the shape of the data ahead of time, compute it:

```js
const n = cy.nodes().length;
const e = cy.edges().length;
const isTree = e === n - 1 && cy.elements().components().length === 1;
const isDense = e / Math.max(n, 1) > 3;

const name = isTree
  ? "breadthfirst"
  : n <= 12
    ? "circle"
    : isDense
      ? "fcose"
      : "fcose";
```
