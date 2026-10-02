(function (SS) {
  "use strict";

  function nowIso() {
    // UTC ISO-8601 seconds precision, "+00:00" offset (not "Z")
    return new Date().toISOString().replace(/\.\d{3}Z$/, "+00:00");
  }

  function manifestSourceType(m) {
    if (m.source) return m.source;
    return Object.prototype.hasOwnProperty.call(m, "repo") ? "github" : "local";
  }

  function sortedUnique(arr) {
    return Array.from(new Set(arr)).sort();
  }

  function gitignoreLinesFor(skillNames) {
    const lines = ["skills/.manifest.json"];
    for (const name of sortedUnique(skillNames)) {
      lines.push(`skills/${name}/`);
    }
    return lines;
  }

  SS.nowIso = nowIso;
  SS.manifestSourceType = manifestSourceType;
  SS.sortedUnique = sortedUnique;
  SS.gitignoreLinesFor = gitignoreLinesFor;
})(window.SS || (window.SS = {}));
