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

## Options shared by the built-in layouts

Almost all of them accept:

`fit` (default `true`), `padding` (`30`), `boundingBox` (`{x1,y1,x2,y2}` or
`{x1,y1,w,h}`), `avoidOverlap` (`true`), `nodeDimensionsIncludeLabels` (`false`),
`spacingFactor`, `animate`, `animationDuration` (`500`), `animationEasing`,
`animateFilter`, `ready`, `stop`, `transform`.

`nodeDimensionsIncludeLabels: true` is worth setting whenever labels are long — it stops
labels overlapping neighbouring nodes.

## Built-in layouts, with real defaults

### `null`

Puts every node at (0, 0). Useful only as a no-op.

### `random`

Random positions within the bounding box.

### `preset`

Uses each node's existing `position`, or a `positions` map/function you supply. Options:
`positions`, `zoom`, `pan`, `fit`, `padding`, `animate`, `animationDuration`,
`animationEasing`, `transform`. Use this when the server computed layout, or to restore
a saved arrangement.

### `grid`

```js
{
  fit: true, padding: 30, boundingBox: undefined,
  avoidOverlap: true, avoidOverlapPadding: 10,
  nodeDimensionsIncludeLabels: false,
  spacingFactor: undefined,
  condense: false,        // false uses all available space
  rows: undefined, cols: undefined,
  position: node => {},   // return { row, col } to place manually
  sort: undefined,        // (a, b) => number
  animate: false, animationDuration: 500, animationEasing: undefined,
  ready: undefined, stop: undefined, transform: (node, pos) => pos
}
```

### `circle`

```js
{
  fit: true, padding: 30, boundingBox: undefined,
  avoidOverlap: true, nodeDimensionsIncludeLabels: false,
  spacingFactor: undefined,
  radius: undefined,
  startAngle: 3/2 * Math.PI,
  sweep: undefined,        // radians between first and last node
  clockwise: true,
  sort: undefined,
  animate: false, animationDuration: 500,
  ready: undefined, stop: undefined, transform: (node, pos) => pos
}
```

### `concentric`

Rings by a numeric score; higher scores sit nearer the centre.

```js
{
  fit: true, padding: 30,
  startAngle: 3/2 * Math.PI, sweep: undefined, clockwise: true,
  equidistant: false,
  minNodeSpacing: 10,
  boundingBox: undefined, avoidOverlap: true,
  nodeDimensionsIncludeLabels: false,
  height: undefined, width: undefined, spacingFactor: undefined,
  concentric: node => node.degree(),          // ← the ranking function
  levelWidth: nodes => nodes.maxDegree() / 4, // ← ring granularity
  animate: false, animationDuration: 500,
  ready: undefined, stop: undefined, transform: (node, pos) => pos
}
```

Swap `concentric` for `node => node.data('importance')` to rank by anything.

### `breadthfirst`

The go-to built-in for trees and DAGs.

```js
{
  fit: true,
  directed: false,          // set true for DAGs so edge direction is respected
  direction: 'downward',    // 'downward' | 'upward' | 'rightward' | 'leftward'
  padding: 30,
  circle: false,            // true = concentric rings by depth
  grid: false,              // even grid placement (circle: false only)
  spacingFactor: 1.75,
  boundingBox: undefined,
  avoidOverlap: true,
  nodeDimensionsIncludeLabels: false,
  roots: undefined,         // selector, array of ids, or collection
  depthSort: undefined,     // (a, b) => number, orders nodes within a depth
  animate: false, animationDuration: 500,
  ready: undefined, stop: undefined, transform: (node, pos) => pos
}
```

Also accepts the deprecated `maximal` and `acyclic` flags, which push nodes down to
their deepest natural BFS depth to avoid upward edges. `acyclic: true` implies
`maximal: true`; only set it if you are certain the graph has no cycles, or you risk an
infinite loop.

Almost always set `roots` explicitly. Left to guess, it picks nodes with no incoming
edges, which is rarely the semantic root the user has in mind. Pass a **collection**, not
a selector string, when ids contain `@`, `$`, `/`, `:` or spaces — `roots:
cy.$id('ceo@corp.com')` needs no escaping, whereas `roots: '#ceo@corp.com'` matches
nothing and lets the layout pick its own roots without complaint.

**Trees get wide fast, and this is the layout's main failure mode.** Width grows with the
widest level, so depth-4 trees blow out quickly. Measured on a 116-person org chart in an
1828×559 viewport:

| Settings                                       | Bounding box | Aspect ratio | Fit zoom |
| ---------------------------------------------- | ------------ | ------------ | -------- |
| `direction: 'downward'`, `spacingFactor: 1.15` | 4268 × 393   | 10.9 : 1     | 0.47     |
| `circle: true`, `spacingFactor: 1.0`           | 1142 × 1115  | 1.02 : 1     | 0.50     |

Rotating to `rightward` swaps a very wide chart for a very tall one; it does not fix the
zoom. Lowering `spacingFactor` helps a little. `circle: true` fixes the aspect ratio and
makes the hierarchy legible as a shape, but note that it barely moved the fit zoom — at
`font-size: 10` both rows above put labels under 5px, so both are still unreadable when
fitted. The genuine fixes are collapsing to the top two levels with expand-on-demand, or
not fitting at all — see "Sizing and readable defaults" in SKILL.md. Check the aspect
ratio on real data volumes, not on a ten-node fixture where every setting looks fine.

### `cose`

The built-in force-directed layout. **Prefer the `fcose` extension** — it is faster and
produces better results — but `cose` needs no extra dependency.

```js
{
  ready: () => {}, stop: () => {},
  animate: true,            // true | false | 'end'
  animationEasing: undefined, animationDuration: undefined,
  animateFilter: (node, i) => true,
  animationThreshold: 250,
  refresh: 20,              // iterations between position updates
  fit: true, padding: 30, boundingBox: undefined,
  nodeDimensionsIncludeLabels: false,
  randomize: false,
  componentSpacing: 40,
  nodeRepulsion: node => 2048,
  nodeOverlap: 4,
  idealEdgeLength: edge => 32,
  edgeElasticity: edge => 32,
  nestingFactor: 1.2,
  gravity: 1,
  numIter: 1000,
  initialTemp: 1000,
  coolingFactor: 0.99,
  minTemp: 1.0
}
```

Tuning notes: raise `nodeRepulsion` (to 8000–15000) and `idealEdgeLength` for airier
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
