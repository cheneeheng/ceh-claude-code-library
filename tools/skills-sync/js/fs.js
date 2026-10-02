(function (SS) {
  "use strict";

  async function getDirPath(root, segments, create) {
    let dir = root;
    for (const seg of segments) {
      dir = await dir.getDirectoryHandle(seg, { create: !!create });
    }
    return dir;
  }

  async function getFilePath(root, dirSegments, fileName, create) {
    const dir = await getDirPath(root, dirSegments, create);
    return dir.getFileHandle(fileName, { create: !!create });
  }

  async function tryGetFilePath(root, dirSegments, fileName) {
    try {
      let dir = root;
      for (const seg of dirSegments) {
        dir = await dir.getDirectoryHandle(seg, { create: false });
      }
      return await dir.getFileHandle(fileName, { create: false });
    } catch (e) {
      if (e && (e.name === "NotFoundError" || e.name === "TypeMismatchError")) {
        return null;
      }
      throw e;
    }
  }

  async function readManifest(root) {
    const fh = await tryGetFilePath(root, [".claude", "skills"], ".manifest.json");
    if (!fh) return null;
    const file = await fh.getFile();
    const text = await file.text();
    try {
      return JSON.parse(text);
    } catch (e) {
      throw new Error(".manifest.json exists but is not valid JSON: " + e.message);
    }
  }

  async function writeManifest(root, manifestObj) {
    const fh = await getFilePath(root, [".claude", "skills"], ".manifest.json", true);
    const writable = await fh.createWritable();
    const text = JSON.stringify(manifestObj, null, 2) + "\n";
    await writable.write(text);
    await writable.close();
  }

  async function ensureGitignore(root, skillNames) {
    const dir = await getDirPath(root, [".claude"], true);
    let existing = "";
    let exists = false;
    try {
      const fh = await dir.getFileHandle(".gitignore", { create: false });
      const file = await fh.getFile();
      existing = await file.text();
      exists = true;
    } catch (e) {
      if (e && e.name !== "NotFoundError") throw e;
    }

    let lines = exists ? existing.split(/\r\n|\r|\n/) : [];
    if (lines.length > 0 && lines[lines.length - 1] === "") {
      lines = lines.slice(0, -1);
    }
    const before = lines.join("\n");

    lines = lines.filter((line) => line !== SS.OLD_GITIGNORE_LINE);

    for (const line of SS.gitignoreLinesFor(skillNames)) {
      if (!lines.includes(line)) {
        lines.push(line);
      }
    }

    const after = lines.join("\n");
    if (after === before) return;

    const fh = await dir.getFileHandle(".gitignore", { create: true });
    const writable = await fh.createWritable();
    await writable.write(after + "\n");
    await writable.close();
  }

  async function removeGitignoreLines(root, skillNames) {
    const fh = await tryGetFilePath(root, [".claude"], ".gitignore");
    if (!fh) return;

    const file = await fh.getFile();
    const existing = await file.text();
    let lines = existing.split(/\r\n|\r|\n/);
    if (lines.length > 0 && lines[lines.length - 1] === "") {
      lines = lines.slice(0, -1);
    }

    const toRemove = new Set(skillNames.map((name) => `skills/${name}/`));
    const newLines = lines.filter((line) => !toRemove.has(line));
    if (newLines.length === lines.length) return;

    const writable = await fh.createWritable();
    await writable.write(newLines.length > 0 ? newLines.join("\n") + "\n" : "");
    await writable.close();
  }

  async function getSkillsRoot(root, create) {
    return getDirPath(root, [".claude", "skills"], !!create);
  }

  async function wipeSkillDir(root, name) {
    const skillsRoot = await getSkillsRoot(root, true);
    try {
      await skillsRoot.removeEntry(name, { recursive: true });
    } catch (e) {
      if (e && e.name !== "NotFoundError") throw e;
    }
  }

  async function copyDirHandle(srcDirHandle, destDirHandle) {
    for await (const [name, handle] of srcDirHandle.entries()) {
      if (handle.kind === "directory") {
        const subDest = await destDirHandle.getDirectoryHandle(name, { create: true });
        await copyDirHandle(handle, subDest);
      } else {
        const file = await handle.getFile();
        const buf = await file.arrayBuffer();
        const destFile = await destDirHandle.getFileHandle(name, { create: true });
        const writable = await destFile.createWritable();
        await writable.write(buf);
        await writable.close();
      }
    }
  }

  async function detectLocalSkills(root) {
    const found = new Map(); // name -> { handle, pathForWarning }
    async function walk(dirHandle, isRoot, pathSoFar) {
      let hasSkillMd = false;
      const subdirs = [];
      for await (const [name, handle] of dirHandle.entries()) {
        if (handle.kind === "file" && name === "SKILL.md") {
          hasSkillMd = true;
        } else if (handle.kind === "directory") {
          subdirs.push([name, handle]);
        }
      }
      if (hasSkillMd && !isRoot) {
        const name = dirHandle.name;
        const fullPath = pathSoFar.join("/") || name;
        if (found.has(name) && found.get(name).path !== fullPath) {
          SS.log(`warning: duplicate skill name '${name}' found at '${fullPath}' and ` +
              `'${found.get(name).path}' — using the latter`);
        }
        found.set(name, { handle: dirHandle, path: fullPath });
      }
      for (const [name, handle] of subdirs) {
        await walk(handle, false, pathSoFar.concat([name]));
      }
    }
    await walk(root, true, [root.name]);
    const result = new Map();
    for (const [name, info] of found.entries()) {
      result.set(name, info.handle);
    }
    return result;
  }

  SS.getDirPath = getDirPath;
  SS.getFilePath = getFilePath;
  SS.tryGetFilePath = tryGetFilePath;
  SS.readManifest = readManifest;
  SS.writeManifest = writeManifest;
  SS.ensureGitignore = ensureGitignore;
  SS.removeGitignoreLines = removeGitignoreLines;
  SS.getSkillsRoot = getSkillsRoot;
  SS.wipeSkillDir = wipeSkillDir;
  SS.copyDirHandle = copyDirHandle;
  SS.detectLocalSkills = detectLocalSkills;
})(window.SS || (window.SS = {}));
