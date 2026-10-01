# Interaction recipes

Working implementations of the features almost every graph visualizer needs. Copy and
adapt. All assume the class names from the default stylesheet in `style.md`
(`dimmed`, `hot`, `hidden`).

## Tap to highlight a neighbourhood

The baseline interaction. Users expect it; without it a graph feels dead.

```js
function clearHighlight() {
  cy.elements().removeClass("dimmed hot");
}

cy.on("tap", "node", (evt) => {
  const node = evt.target;
  const hood = node.closedNeighborhood();
  cy.batch(() => {
    cy.elements().addClass("dimmed").removeClass("hot");
    hood.removeClass("dimmed").addClass("hot");
  });
  showDetails(node.data());
});

cy.on("tap", (evt) => {
  if (evt.target === cy) {
    clearHighlight();
    hideDetails();
  }
});
```

Use `closedNeighborhood()` (includes the node itself), not `neighborhood()` — the latter
leaves the tapped node dimmed, which looks like a bug.

For directed graphs, offer upstream/downstream instead:

```js
const upstream = node.predecessors().union(node);
const downstream = node.successors().union(node);
```

## Multi-hop expansion

```js
function nHop(node, hops) {
  let acc = node;
  for (let i = 0; i < hops; i++) acc = acc.union(acc.closedNeighborhood());
  return acc;
}
```

## Search and focus

```js
const input = document.getElementById("search");

input.addEventListener("input", () => {
  const q = input.value.trim().toLowerCase();
  clearHighlight();
  if (!q) return;

  const hits = cy.nodes().filter((n) =>
    String(n.data("label") ?? "")
      .toLowerCase()
      .includes(q),
  );

  if (hits.empty()) {
    setStatus("No matches");
    return;
  }

  cy.batch(() => {
    cy.elements().addClass("dimmed");
    hits.union(hits.connectedEdges()).removeClass("dimmed").addClass("hot");
  });
  setStatus(`${hits.length} match${hits.length === 1 ? "" : "es"}`);
});

input.addEventListener("keydown", (e) => {
  if (e.key !== "Enter") return;
  const hits = cy.nodes(".hot");
  if (hits.nonempty())
    cy.animate({ fit: { eles: hits, padding: 60 } }, { duration: 400 });
});
```

Cytoscape's `*=` selector is case-sensitive, which is why the JS filter above is used
instead. If case matters little and speed matters more, use `[label @*= "query"]` — the
`@` prefix makes the operator case-insensitive.

## Filtering by category

`display: none` removes elements from layout and viewport fitting, which is what you
want for a real filter. `opacity` is for dimming.

```js
function applyFilter(activeTypes) {
  cy.batch(() => {
    cy.nodes().forEach((n) => {
      n.toggleClass("hidden", !activeTypes.has(n.data("type")));
    });
    // hide edges whose endpoints are hidden
    cy.edges().forEach((e) => {
      e.toggleClass(
        "hidden",
        e.source().hasClass("hidden") || e.target().hasClass("hidden"),
      );
    });
  });
}
```

Re-run the layout after filtering only if the remaining graph would otherwise look
sparse and scattered — many users prefer positions to stay put so they keep their mental
map.

## Expand and collapse (lazy loading)

For large graphs, render a seed set and fetch neighbours on demand.

```js
cy.on("dbltap", "node", async (evt) => {
  const node = evt.target;
  if (node.data("expanded")) return collapse(node);

  node.addClass("loading");
  const { nodes, edges } = await fetchNeighbors(node.id());
  node.removeClass("loading");

  const existing = new Set(cy.nodes().map((n) => n.id()));
  const fresh = [...nodes.filter((n) => !existing.has(n.data.id)), ...edges];
  const added = cy.add(fresh);

  // place new nodes near their parent so the graph does not jump
  added.nodes().positions(() => ({ ...node.position() }));

  cy.nodes().difference(added).lock();
  cy.layout({
    name: "fcose",
    randomize: false,
    animate: true,
    animationDuration: 400,
  }).run();
  cy.nodes().unlock();

  node.data("expanded", true);
});

function collapse(node) {
  // remove leaf descendants that are not reachable from elsewhere
  const removable = node
    .successors()
    .nodes()
    .filter((n) => n.degree() <= 1);
  cy.remove(removable);
  node.data("expanded", false);
}
```

Locking the existing nodes before re-layout is the key move. Without it, the whole graph
rearranges and the user loses their place.

## Tooltips

Two options.

**HTML overlay positioned from rendered coordinates** — no dependencies, exact control:

```js
const tip = document.getElementById("tooltip");

cy.on("mouseover", "node", (evt) => {
  const p = evt.target.renderedPosition();
  const box = cy.container().getBoundingClientRect();
  tip.textContent = evt.target.data("label");
  tip.style.left = `${box.left + p.x}px`;
  tip.style.top = `${box.top + p.y - 28}px`;
  tip.hidden = false;
});
cy.on("mouseout", "node", () => {
  tip.hidden = true;
});
cy.on("pan zoom", () => {
  tip.hidden = true;
});
```

Note `renderedPosition()`, not `position()` — you need on-screen pixels.

**`cytoscape-popper` + Tippy.js** — proper flipping, arrows, and interactive content, at
the cost of two dependencies. Use it when tooltips contain buttons or links.

Do not forget the `pan zoom` handler; a tooltip that stays put while the graph moves
underneath looks broken.

## Context menu

```js
cy.on("cxttap", "node", (evt) => {
  const p = evt.renderedPosition;
  openMenu(p.x, p.y, [
    {
      label: "Focus",
      run: () =>
        cy.animate({
          fit: { eles: evt.target.closedNeighborhood(), padding: 50 },
        }),
    },
    { label: "Hide", run: () => evt.target.addClass("hidden") },
    {
      label: "Copy id",
      run: () => navigator.clipboard.writeText(evt.target.id()),
    },
  ]);
});
cy.on("tap pan zoom", closeMenu);
```

`cxttap` covers both right-click and two-finger tap, so this works on touch devices too.
The `cytoscape-cxtmenu` extension gives a radial menu if you prefer.

## Drawing edges by dragging

Use `cytoscape-edgehandles`:

```js
import edgehandles from "cytoscape-edgehandles";
cytoscape.use(edgehandles);

const eh = cy.edgehandles({
  snap: true,
  canConnect: (src, tgt) => !src.same(tgt) && src.edgesWith(tgt).empty(),
  edgeParams: () => ({ data: { kind: "new" } }),
});

cy.on("ehcomplete", (evt, src, tgt, addedEdge) => {
  persistEdge(src.id(), tgt.id(), addedEdge.id());
});
```

## Shortest path between two selected nodes

```js
let picks = [];

cy.on("tap", "node", (evt) => {
  picks.push(evt.target);
  if (picks.length < 2) return;

  const [a, b] = picks.slice(-2);
  const d = cy.elements().dijkstra({
    root: a,
    weight: (e) => e.data("weight") ?? 1,
    directed: true,
  });
  const path = d.pathTo(b);

  cy.batch(() => {
    cy.elements().addClass("dimmed").removeClass("hot");
    path.removeClass("dimmed").addClass("hot");
  });

  setStatus(
    Number.isFinite(d.distanceTo(b))
      ? `${path
          .nodes()
          .map((n) => n.data("label"))
          .join(" → ")} (cost ${d.distanceTo(b)})`
      : "No path",
  );
  picks = [];
});
```

`distanceTo` returns `Infinity` when unreachable — check it, or you print "cost Infinity".

## Sizing nodes by importance

```js
const bc = cy.elements().betweennessCentrality();
let max = 0;
cy.nodes().forEach((n) => {
  const v = bc.betweenness(n);
  n.data("bc", v);
  max = Math.max(max, v);
});
cy.nodes().forEach((n) => n.data("bcNorm", max ? n.data("bc") / max : 0));
```

```js
{ selector: 'node[bcNorm]', style: {
    'width':  'mapData(bcNorm, 0, 1, 24, 64)',
    'height': 'mapData(bcNorm, 0, 1, 24, 64)'
}}
```

Betweenness is O(V·E) — compute it once after load, not on every interaction. For large
graphs, `degreeCentralityNormalized()` is nearly free and often communicates the same
thing.

## Export as an image

```js
async function download() {
  const blob = await cy.png({
    output: "blob-promise",
    full: true, // entire graph, not just the viewport
    scale: 2,
    bg: palette().bg, // canvas is transparent; set this or you get a see-through PNG
  });
  const url = URL.createObjectURL(blob);
  const a = Object.assign(document.createElement("a"), {
    href: url,
    download: "graph.png",
  });
  a.click();
  URL.revokeObjectURL(url);
}
```

`'blob-promise'` is the only non-blocking output. The others can freeze the tab on a
large graph.

## Keyboard accessibility

Canvas graphs are invisible to screen readers. At minimum:

- Put an `aria-label` and a short text summary next to the container describing the graph
  (node count, edge count, what it shows).
- Offer a parallel list or table view of the same data.
- Wire keys for the core actions:

```js
document.addEventListener("keydown", (e) => {
  if (e.target.matches("input, textarea")) return;
  if (e.key === "f") cy.fit(30);
  if (e.key === "r") {
    clearHighlight();
    cy.reset();
  }
  if (e.key === "Escape") clearHighlight();
});
```

A graph that can only be explored by mouse-dragging excludes a real fraction of users.
The list view is the accommodation that actually works.
