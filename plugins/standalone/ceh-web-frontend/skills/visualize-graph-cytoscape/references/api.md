# API reference

Two objects matter: the **core** (`cy`, the whole graph) and the **collection** (`eles`,
a set of elements). Collections are immutable — set operations return new collections
rather than mutating. Most methods are chainable.

Documentation shorthand: `cy` core, `eles` many elements, `ele` one, `nodes`/`node`,
`edges`/`edge`, `layout`, `ani`.

## Initialisation options

```js
const cy = cytoscape({
  // core
  container: undefined, // DOM element; omit for headless
  elements: [], // elements JSON, or a Promise resolving to it
  style: [], // stylesheet, or a Promise resolving to it
  layout: { name: "grid" },
  data: {}, // graph-level data

  // initial viewport
  zoom: 1,
  pan: { x: 0, y: 0 },

  // interaction
  minZoom: 1e-50,
  maxZoom: 1e50,
  zoomingEnabled: true,
  userZoomingEnabled: true,
  panningEnabled: true,
  userPanningEnabled: true,
  boxSelectionEnabled: true,
  selectionType: "single", // or 'additive'
  touchTapThreshold: 8,
  desktopTapThreshold: 4,
  autolock: false,
  autoungrabify: false,
  autounselectify: false,
  multiClickDebounceTime: 250,

  // rendering
  headless: false,
  styleEnabled: true,
  hideEdgesOnViewport: false,
  textureOnViewport: false,
  motionBlur: false,
  motionBlurOpacity: 0.2,
  wheelSensitivity: 1,
  pixelRatio: "auto",
});
```

Notes worth knowing:

- `wheelSensitivity: 1` is tuned for mainstream mice. The docs advise against changing
  it, but in practice `0.2`–`0.4` feels far better inside a scrollable page, because it
  stops one wheel notch from zooming across the whole range.
- If you set `zoom`/`pan` at init, disable `fit` in your layout options or the layout
  will override them.
- `cytoscape.warnings(false)` silences console warnings. Leave them on in development;
  they catch malformed elements.

## Elements JSON

```js
{
  group: 'nodes',              // 'nodes' | 'edges'; inferred, but explicit gives better errors
  data: {
    id: 'n1',                  // unique string; auto-assigned if omitted
    parent: 'nparent',         // compound node parent id
    source: 'n1', target: 'n2' // edges only
    // ...any app fields
  },
  position: { x: 100, y: 100 },      // model position (centre of node)
  renderedPosition: { x: 200, y: 2 },// alternative: on-screen pixels
  scratch: { _foo: 'bar' },    // temp / non-serialisable; app keys prefixed with _
  selected: false,
  selectable: true,
  locked: false,               // position immutable
  grabbable: true,
  pannable: false,             // dragging this element pans instead of grabbing
  classes: ['foo', 'bar'],     // array or space-separated string
  style: {}                    // AVOID — use the stylesheet
}
```

Alternative grouped form:

```js
elements: {
  nodes: [ { data: { id: 'a' } } ],
  edges: [ { data: { id: 'ab', source: 'a', target: 'b' } } ]
}
```

**Model vs rendered position.** A model position is stored in the graph and is
zoom/pan-independent. A rendered position is on-screen pixels relative to the viewport.
They coincide only at zoom 1, pan (0,0). Numeric style values are in model coordinates.

## Core methods

**Graph manipulation** — `cy.add(eleObj|eleObjs|eles)`, `cy.remove(eles|selector)`,
`cy.collection()`, `cy.getElementById(id)` / `cy.$id(id)`, `cy.$(selector)`,
`cy.elements(sel)`, `cy.nodes(sel)`, `cy.edges(sel)`, `cy.filter(sel|fn)`,
`cy.batch(fn)` / `cy.startBatch()` / `cy.endBatch()`, `cy.mount(container)`,
`cy.unmount()`, `cy.destroy()`, `cy.destroyed()`.

**Data** — `cy.data()`, `cy.removeData()`, `cy.scratch()`, `cy.removeScratch()`.

**Events** — `cy.on(events [, selector], handler)`, `cy.one()`, `cy.promiseOn()` /
`cy.pon()`, `cy.off()` / `cy.removeListener()`, `cy.removeAllListeners()`,
`cy.emit()` / `cy.trigger()`, `cy.ready(fn)`.

**Viewport** — `cy.container()`, `cy.center(eles?)`, `cy.fit(eles?, padding?)`,
`cy.reset()`, `cy.pan()`, `cy.panBy()`, `cy.zoom(level|opts)`, `cy.minZoom()`,
`cy.maxZoom()`, `cy.viewport({zoom, pan})`, `cy.width()`, `cy.height()`,
`cy.extent()`, `cy.renderedExtent()`, `cy.resize()`, and the enable/disable pairs
`cy.zoomingEnabled()`, `cy.userZoomingEnabled()`, `cy.panningEnabled()`,
`cy.userPanningEnabled()`, `cy.boxSelectionEnabled()`, `cy.selectionType()`,
`cy.autolock()`, `cy.autoungrabify()`, `cy.autounselectify()`.

**Animation** — `cy.animate(opts)`, `cy.animation(opts)`, `cy.delay()`,
`cy.delayAnimation()`, `cy.stop(clearQueue, jumpToEnd)`, `cy.clearQueue()`,
`cy.animated()`.

**Layout & style** — `cy.layout(opts)` (alias `cy.makeLayout`), `cy.style()`.

**Export** — `cy.png(opts)`, `cy.jpg(opts)`. Options: `output` (`'base64uri'` default,
`'base64'`, `'blob'`, `'blob-promise'`), `bg`, `full` (whole graph vs viewport),
`scale`, `maxWidth`, `maxHeight`. Only `'blob-promise'` is non-blocking; the others can
hang the browser on large images.

### cy.batch()

Wraps many element mutations into one style recalculation and one redraw. Only reach for
it after identifying a bottleneck. Inside a batch you may modify state (`data`,
`scratch`, `addClass`, `removeClass`), build collections, compare, iterate, traverse, and
run algorithms. You may **not** reliably read style or dimensions, run layouts, or
animate — anything style-dependent is unsafe once you have changed style in the same
batch.

## Collection methods

**Data & metadata** — `eles.data()` / `eles.attr()`, `eles.removeData()`,
`ele.scratch()`, `ele.id()`, `ele.json()`, `eles.jsons()`, `ele.group()`,
`ele.isNode()`, `ele.isEdge()`, `edge.isLoop()`, `edge.isSimple()`, `node.degree()`.

**Position & dimensions** — `node.position()`, `nodes.positions(fn)`, `nodes.shift()`,
`node.renderedPosition()`, `node.relativePosition()`, `ele.width()`, `ele.height()`,
`eles.boundingBox()` / `eles.bb()`, `eles.renderedBoundingBox()`, `node.grabbed()`,
`nodes.grabify()` / `ungrabify()`, `nodes.lock()` / `unlock()`, `eles.panify()` /
`unpanify()`.

**Edge points** — `edge.controlPoints()`, `edge.segmentPoints()`,
`edge.sourceEndpoint()`, `edge.targetEndpoint()`, `edge.midpoint()`. Useful for
positioning tooltips and labels manually.

**Selection** — `ele.selected()`, `eles.select()`, `eles.unselect()`,
`ele.selectable()`, `eles.selectify()` / `unselectify()`.

**Style & classes** — `eles.addClass()`, `eles.removeClass()`, `eles.toggleClass()`,
`eles.classes()`, `eles.flashClass(cls, ms)`, `ele.hasClass()`, `eles.style()`,
`ele.numericStyle()`, `ele.visible()`, `ele.effectiveOpacity()`, `ele.transparent()`.

**Animation** — `eles.animate()`, `ele.animation()`, `eles.delay()`, `eles.stop()`,
`eles.clearQueue()`, `ele.animated()`.

**Comparison** — `eles.same()`, `eles.anySame()`, `eles.contains()`,
`eles.allAreNeighbors()`, `eles.is(selector)`, `eles.allAre()`, `eles.some()`,
`eles.every()`.

**Iteration** — `eles.size()`, `eles.empty()`, `eles.forEach()` / `each()`, `eles.eq(i)`,
`eles.slice()`, `eles.toArray()`.

**Building & filtering** — `eles.union()` (aliases `add`, `or`, `|`, `+`),
`eles.difference()` (aliases `not`, `subtract`, `-`, `!`), `eles.intersection()`
(aliases `and`, `&`), `eles.symmetricDifference()` (`xor`), `eles.absoluteComplement()`,
`eles.diff()`, `eles.merge()` / `unmerge()` (mutating — performance only),
`eles.filter()`, `eles.sort()`, `eles.map()`, `eles.reduce()`, `eles.min()`,
`eles.max()`.

**Traversing** — this is where interaction code lives:

```js
eles.neighborhood()          // connected elements, not including self
ele.closedNeighborhood()     // ...including self  ← the one you usually want
ele.openNeighborhood()       // explicit alias for neighborhood()
eles.components()            // connected components, as an array of collections
node.outgoers()  node.successors()     // one step out / transitively out
node.incomers()  node.predecessors()   // one step in  / transitively in
node.connectedEdges()  edge.connectedNodes()
edge.source()  edge.target()  edges.sources()  edges.targets()
nodes.edgesWith(other)  nodes.edgesTo(other)
edges.parallelEdges()  edges.codirectedEdges()
nodes.roots()  nodes.leaves()
```

**Compound nodes** — `node.isParent()`, `isChildless()`, `isChild()`, `isOrphan()`,
`nodes.parent()`, `nodes.ancestors()`, `nodes.commonAncestors()`, `nodes.children()`,
`nodes.descendants()`, `nodes.siblings()`, `nodes.orphans()`, `nodes.nonorphans()`.

Compound caveat: graph-theory functions like `dijkstra()` and `neighborhood()` do **not**
special-case compound parents. To treat a parent's descendants as belonging to it:

```js
const indirect = a.add(a.descendants()).neighborhood();
```

## Algorithms

All are collection methods, so scope them by calling on a subset.

**Search** — `eles.breadthFirstSearch(opts)` / `bfs`, `eles.depthFirstSearch()` / `dfs`,
`eles.dijkstra(opts)`, `eles.aStar(opts)`, `eles.floydWarshall(opts)`,
`eles.bellmanFord(opts)`, `eles.hierholzer(opts)`.

**Spanning** — `eles.kruskal(weightFn)`.

**Cut** — `eles.kargerStein()`, `eles.hopcroftTarjanBiconnected()` / `htbc`,
`eles.tarjanStronglyConnected()` / `tscc`.

**Centrality** — `eles.degreeCentrality()` / `dc`, `degreeCentralityNormalized()` / `dcn`,
`closenessCentrality()` / `cc`, `closenessCentralityNormalized()` / `ccn`,
`betweennessCentrality()` / `bc`, `eles.pageRank()`.

**Clustering** — `eles.markovClustering()` / `mcl`, `nodes.kMeans()`, `nodes.kMedoids()`,
`nodes.fuzzyCMeans()` / `fcm`, `nodes.hierarchicalClustering()` / `hca`,
`nodes.affinityPropagation()` / `ap`.

Typical shapes:

```js
// shortest path
const d = cy
  .elements()
  .dijkstra({ root: "#a", weight: (e) => e.data("cost") || 1 });
const path = d.pathTo(cy.$("#z")); // collection of nodes AND edges, in order
const dist = d.distanceTo(cy.$("#z"));

// rank nodes by importance, then size them
const bc = cy.elements().betweennessCentrality();
cy.nodes().forEach((n) => n.data("importance", bc.betweenness(n)));
// then in the stylesheet: 'width': 'mapData(importance, 0, 100, 20, 60)'

// find islands
cy.elements()
  .components()
  .forEach((comp, i) => comp.addClass("comp-" + i));
```

`pathTo` returns nodes and edges interleaved — filter with `.nodes()` or `.edges()` if
you only want one kind.

## Selectors

Cytoscape's own selector language, evaluated against the graph model.

**Group / class / id** — `node`, `edge`, `*`, `.className`, `#id`.

**Data** —
`[name]` defined · `[^name]` undefined · `[?name]` truthy · `[!name]` falsey ·
`[name = value]` · `[name != value]` · `[name > value]` `>=` `<` `<=` ·
`[name *= value]` contains · `[name ^= value]` starts with · `[name $= value]` ends with ·
`[name.0 = value]` array index · `[name.prop = value]` nested object ·
`@` prefix makes an operator case-insensitive (`[foo @= 'bar']`) ·
`!` prefix negates it (`[foo !$= 'ar']`) ·
`[[degree > 2]]` double brackets match _metadata_ (`degree`, `indegree`, `outdegree`).

**Strings must be quoted**: `'node[name = "Jerry"]'`, not `node[name = Jerry]`.
Special characters in ids need escaping — prefer `[id = "weird$id"]` over `#weird\\$id`.

**Compound** — `>` direct child, space descendant, `$` sets the selector subject
(`$node > node` selects the parents).

**Combining** — juxtapose for AND (`node[weight >= 50][height < 180]`), comma for OR
(`node#j, edge[source = "j"]`).

**State pseudo-classes** — `:selected` `:unselected` `:selectable` `:unselectable` ·
`:locked` `:unlocked` · `:grabbed` `:free` `:grabbable` `:ungrabbable` · `:active`
`:inactive` `:touch` · `:visible` `:hidden` `:transparent` · `:animated` `:unanimated` ·
`:backgrounding` `:nonbackgrounding` · `:removed` `:inside` · `:parent` `:childless`
`:child` `:orphan` `:compound` · `:loop` `:simple`.

Anywhere a selector is accepted, a filter function works too:

```js
cy.$("#j").neighborhood((ele) => ele.isEdge());
```

Performance: `cy.$id('foo')` uses a lookup table and is the fastest way to get an
element. Compound (`$node node`) and edge-traversal selectors are the most expensive.

## Events

**Event object fields** — `cy`, `target` (the originator), `type`, `namespace`,
`timeStamp`; plus `position`, `renderedPosition`, `originalEvent` for input events; plus
`layout` for layout events.

**Bubbling**: element events bubble to compound parents and then to the core. When
listening on the core, always check `evt.target === cy` to distinguish background
clicks from element clicks.

**Normalised input events** (prefer these over raw mouse/touch — they work on both):
`tap` (alias `vclick`), `tapstart`, `tapend`, `tapdrag`, `tapdragover`, `tapdragout`,
`taphold`, `onetap` / `oneclick`, `dbltap` / `dblclick`, `cxttap` (right-click or
two-finger), `cxttapstart`, `cxttapend`, `cxtdrag`, `cxtdragover`, `cxtdragout`,
`boxstart`, `boxend`, `boxselect`, `box`.

Raw ones also exist: `mousedown` `mouseup` `click` `mouseover` `mouseout` `mousemove`
`touchstart` `touchmove` `touchend`.

**Element events** — `add` `remove` `move` `select` `unselect` `tapselect` `tapunselect`
`boxselect` `box` `lock` `unlock` `grab` `grabon` `drag` `free` `freeon` `dragfree`
`dragfreeon` `position` `data` `scratch` `style` `background`.

**Graph events** — `layoutstart` `layoutready` `layoutstop` `ready` `destroy` `render`
`pan` `dragpan` `zoom` `pinchzoom` `scrollzoom` `viewport` `resize`.

Delegation works like jQuery, and is the right pattern because it survives
add/remove of elements:

```js
cy.on("tap", 'node[type = "service"]', (evt) => {
  /* ... */
});
cy.on("mouseover", "node", (evt) => evt.target.addClass("hover"));
cy.on("mouseout", "node", (evt) => evt.target.removeClass("hover"));
```

Namespaces let you tear down a feature's listeners without touching others:

```js
cy.on("tap.search", "node", handler);
cy.off(".search");
```
