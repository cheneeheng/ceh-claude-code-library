/**
 * to-elements.js — convert common real-world data shapes into Cytoscape.js elements JSON.
 *
 * Works in Node (require) and the browser (script tag → window.toElements).
 *
 * Every converter routes through sanitize(), which guarantees the output can be handed
 * to cytoscape() without throwing: unique string ids, and no edge pointing at a node
 * that does not exist. What it drops comes back in `warnings` — show those to the user
 * rather than swallowing them, because dangling references are common in real exports
 * and a silently smaller graph is a quietly wrong graph.
 *
 * Every function returns { elements, warnings }.
 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.toElements = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  function sanitize(rawNodes, rawEdges) {
    const nodes = [], edges = [], ids = new Set(), warnings = [];

    for (const n of rawNodes) {
      const d = n.data || n;
      const id = d.id == null ? '' : String(d.id);
      if (!id) { warnings.push('A record had no id and was dropped.'); continue; }
      if (ids.has(id)) { warnings.push('Duplicate id "' + id + '" — later copy dropped.'); continue; }
      ids.add(id);
      nodes.push({ group: 'nodes', data: Object.assign({}, d, { id: id }) });
    }

    const seenEdge = new Set();
    for (const e of rawEdges) {
      const d = e.data || e;
      const s = d.source == null ? '' : String(d.source);
      const t = d.target == null ? '' : String(d.target);
      if (!s || !t) { warnings.push('An edge was missing source or target and was dropped.'); continue; }
      if (!ids.has(s)) { warnings.push('"' + s + '" is referenced but not present — link to "' + t + '" dropped.'); continue; }
      if (!ids.has(t)) { warnings.push('"' + t + '" is referenced but not present — link from "' + s + '" dropped.'); continue; }
      let id = d.id == null ? s + '__' + t : String(d.id);
      if (seenEdge.has(id)) { let i = 2; while (seenEdge.has(id + '#' + i)) i++; id = id + '#' + i; }
      seenEdge.add(id);
      edges.push({ group: 'edges', data: Object.assign({}, d, { id: id, source: s, target: t }) });
    }

    return { elements: nodes.concat(edges), warnings: warnings };
  }

  /**
   * Rows where each record names its parent. Org charts, file trees, category trees,
   * comment threads. Edges point parent -> child.
   *   fromParentPointer(rows, { id: 'email', parent: 'manager_email', label: 'name' })
   */
  function fromParentPointer(rows, keys) {
    const k = Object.assign({ id: 'id', parent: 'parent', label: 'label' }, keys);
    const nodes = rows.map(function (r) {
      return { data: Object.assign({}, r, { id: r[k.id], label: r[k.label] != null ? r[k.label] : r[k.id] }) };
    });
    const edges = [];
    for (const r of rows) {
      const p = r[k.parent];
      if (p == null || p === '') continue;            // a root, not an error
      edges.push({ data: { source: p, target: r[k.id] } });
    }
    return sanitize(nodes, edges);
  }

  /**
   * Rows carrying an array of things they depend on. Terraform, package manifests,
   * import graphs, build targets. Edges point dependency -> dependent, so that
   * successors() reads as "what breaks if this breaks".
   *   fromDependsOn(resources, { id: 'id', deps: 'depends_on' })
   */
  function fromDependsOn(rows, keys) {
    const k = Object.assign({ id: 'id', deps: 'depends_on', label: null }, keys);
    const nodes = rows.map(function (r) {
      const label = k.label ? r[k.label] : String(r[k.id]);
      return { data: Object.assign({}, r, { id: r[k.id], label: label }) };
    });
    const edges = [];
    for (const r of rows) {
      const list = r[k.deps] || [];
      for (const dep of list) edges.push({ data: { source: dep, target: r[k.id] } });
    }
    return sanitize(nodes, edges);
  }

  /**
   * An edge list, with an optional node list. If nodes are omitted they are inferred
   * from the endpoints, so a bare list of pairs works.
   *   fromEdgeList(links, notes, { source: 'from', target: 'to', id: 'id', label: 'title' })
   */
  function fromEdgeList(edgeRows, nodeRows, keys) {
    const k = Object.assign({ source: 'source', target: 'target', id: 'id', label: 'label' }, keys);
    let nodes;
    if (nodeRows && nodeRows.length) {
      nodes = nodeRows.map(function (n) {
        return { data: Object.assign({}, n, { id: n[k.id], label: n[k.label] != null ? n[k.label] : n[k.id] }) };
      });
    } else {
      const seen = new Set();
      nodes = [];
      for (const e of edgeRows) {
        for (const end of [e[k.source], e[k.target]]) {
          if (end == null || seen.has(String(end))) continue;
          seen.add(String(end));
          nodes.push({ data: { id: end, label: String(end) } });
        }
      }
    }
    const edges = edgeRows.map(function (e) {
      return { data: Object.assign({}, e, { source: e[k.source], target: e[k.target] }) };
    });
    return sanitize(nodes, edges);
  }

  /**
   * A square adjacency matrix plus labels. Truthy cells become edges; a `directed: false`
   * option keeps only the upper triangle so undirected graphs do not get doubled edges.
   *   fromAdjacency(matrix, labels, { directed: false, threshold: 0 })
   */
  function fromAdjacency(matrix, labels, opts) {
    const o = Object.assign({ directed: true, threshold: 0 }, opts);
    const names = labels || matrix.map(function (_, i) { return 'n' + i; });
    const nodes = names.map(function (n, i) { return { data: { id: String(i), label: String(n) } }; });
    const edges = [];
    for (let i = 0; i < matrix.length; i++) {
      for (let j = 0; j < matrix[i].length; j++) {
        if (i === j) continue;
        if (!o.directed && j < i) continue;
        const w = matrix[i][j];
        if (!w || w <= o.threshold) continue;
        edges.push({ data: { source: String(i), target: String(j), weight: w } });
      }
    }
    return sanitize(nodes, edges);
  }

  return {
    sanitize: sanitize,
    fromParentPointer: fromParentPointer,
    fromDependsOn: fromDependsOn,
    fromEdgeList: fromEdgeList,
    fromAdjacency: fromAdjacency
  };
});
