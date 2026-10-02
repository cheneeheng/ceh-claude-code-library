(function (SS) {
  "use strict";

  function ghHeaders(token) {
    const headers = {};
    if (token) headers["Authorization"] = "Bearer " + token;
    return headers;
  }

  async function fetchGithubTree(repo, ref, token) {
    const url = `https://api.github.com/repos/${repo}/git/trees/${encodeURIComponent(ref)}?recursive=1`;
    let resp;
    try {
      resp = await fetch(url, { headers: ghHeaders(token) });
    } catch (e) {
      throw new Error(`network error fetching ${url}: ${e.message}`);
    }
    if (!resp.ok) {
      let hint = "";
      if (resp.status === 404) {
        hint = " (check repo/ref/token — private repos 404 without a token)";
      }
      throw new Error(`HTTP ${resp.status} fetching ${url}${hint}`);
    }
    return resp.json();
  }

  async function fetchGithubBlob(repo, sha, token) {
    const url = `https://api.github.com/repos/${repo}/git/blobs/${sha}`;
    let resp;
    try {
      resp = await fetch(url, { headers: ghHeaders(token) });
    } catch (e) {
      throw new Error(`network error fetching ${url}: ${e.message}`);
    }
    if (!resp.ok) {
      let hint = "";
      if (resp.status === 404) {
        hint = " (check repo/ref/token — private repos 404 without a token)";
      }
      throw new Error(`HTTP ${resp.status} fetching ${url}${hint}`);
    }
    return resp.json();
  }

  function base64ToBytes(b64) {
    const binStr = atob(b64.replace(/\n/g, ""));
    return Uint8Array.from(binStr, (c) => c.charCodeAt(0));
  }

  async function detectGithubSkills(repo, ref, token) {
    const data = await fetchGithubTree(repo, ref, token);
    SS.state.githubTreeTruncated = !!data.truncated;
    const tree = data.tree || [];

    const skillDirs = new Map(); // name -> dirPath (last wins)
    for (const entry of tree) {
      if (entry.type === "blob" && entry.path.endsWith("/SKILL.md")) {
        const dirPath = entry.path.slice(0, -"/SKILL.md".length);
        const name = dirPath.split("/").pop();
        if (skillDirs.has(name) && skillDirs.get(name) !== dirPath) {
          SS.log(`warning: duplicate skill name '${name}' found at '${dirPath}' and ` +
              `'${skillDirs.get(name)}' — using the latter`);
        }
        skillDirs.set(name, dirPath);
      }
    }

    const result = new Map(); // name -> array of tree entries under dirPath/
    for (const [name, dirPath] of skillDirs.entries()) {
      const prefix = dirPath + "/";
      const entries = tree.filter((e) => e.path.startsWith(prefix) && e.type === "blob");
      result.set(name, { dirPath, entries });
    }
    return result;
  }

  async function copyGithubSkill(repo, ref, token, skillInfo, destSkillDir) {
    const { dirPath, entries } = skillInfo;
    for (const entry of entries) {
      const rel = entry.path.slice(dirPath.length + 1);
      const segments = rel.split("/");
      const fileName = segments.pop();
      const dirSegments = segments;

      const blob = await fetchGithubBlob(repo, entry.sha, token);
      const bytes = base64ToBytes(blob.content || "");

      let dir = destSkillDir;
      for (const seg of dirSegments) {
        dir = await dir.getDirectoryHandle(seg, { create: true });
      }
      const fh = await dir.getFileHandle(fileName, { create: true });
      const writable = await fh.createWritable();
      await writable.write(bytes);
      await writable.close();
    }
  }

  SS.ghHeaders = ghHeaders;
  SS.fetchGithubTree = fetchGithubTree;
  SS.fetchGithubBlob = fetchGithubBlob;
  SS.base64ToBytes = base64ToBytes;
  SS.detectGithubSkills = detectGithubSkills;
  SS.copyGithubSkill = copyGithubSkill;
})(window.SS || (window.SS = {}));
