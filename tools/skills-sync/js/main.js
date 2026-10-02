(function (SS) {
  "use strict";

  const dom = SS.dom;
  const state = SS.state;
  const log = SS.log;
  const setBusy = SS.setBusy;

  // ---------------------------------------------------------------------
  // Feature detection
  // ---------------------------------------------------------------------
  if (!("showDirectoryPicker" in window)) {
    dom.banner.hidden = false;
    dom.stepProject.style.display = "none";
    dom.stepSource.style.display = "none";
    dom.stepSkills.style.display = "none";
    document.getElementById("step-log").style.display = "none";
    return;
  }

  // ---------------------------------------------------------------------
  // Project folder pick
  // ---------------------------------------------------------------------

  dom.btnPickProject.addEventListener("click", async () => {
    if (state.busy) return;
    try {
      setBusy(true);
      const handle = await window.showDirectoryPicker({ mode: "readwrite" });
      state.projectHandle = handle;
      dom.projectNameEl.textContent = `Selected: ${handle.name}`;
      log(`Project folder selected: ${handle.name}`);

      state.manifest = await SS.readManifest(state.projectHandle);
      state.manifestExisted = state.manifest !== null;

      if (state.manifest) {
        log("Existing manifest found.");
        const st = SS.manifestSourceType(state.manifest);
        if (st === "github") {
          state.sourceType = "github";
          document.querySelector('input[name="source-type"][value="github"]').checked = true;
          dom.ghRepoInput.value = state.manifest.repo || "";
          dom.ghRefInput.value = state.manifest.ref || "main";
          updateSourceFieldsVisibility();
          log(`Manifest source: github ${state.manifest.repo}@${state.manifest.ref || "main"}`);
        } else {
          state.sourceType = "local";
          document.querySelector('input[name="source-type"][value="local"]').checked = true;
          updateSourceFieldsVisibility();
          dom.sourceNameEl.textContent =
            `Pick this folder again: ${state.manifest.path || "(unknown)"}`;
          log(`Manifest source: local — pick this folder again: ${state.manifest.path || "(unknown)"}`);
        }
      } else {
        log("No existing manifest — this will be a fresh install.");
      }

      SS.renderCurrentState();
      dom.stepSource.hidden = false;
      state.availableSkills = null;
      SS.fullRenderSkillList();
    } catch (e) {
      if (e && e.name === "AbortError") {
        log("Project folder selection cancelled.");
      } else {
        log("Error selecting project folder: " + e.message);
      }
    } finally {
      setBusy(false);
    }
  });

  // ---------------------------------------------------------------------
  // Source type toggling
  // ---------------------------------------------------------------------

  function updateSourceFieldsVisibility() {
    const checked = document.querySelector('input[name="source-type"]:checked');
    state.sourceType = checked ? checked.value : "github";
    dom.githubFields.hidden = state.sourceType !== "github";
    dom.localFields.hidden = state.sourceType !== "local";
  }

  for (const radio of dom.sourceTypeRadios) {
    radio.addEventListener("change", () => {
      updateSourceFieldsVisibility();
      state.availableSkills = null;
      SS.fullRenderSkillList();
    });
  }
  updateSourceFieldsVisibility();

  // ---------------------------------------------------------------------
  // GitHub source loading
  // ---------------------------------------------------------------------

  dom.btnLoadGithub.addEventListener("click", async () => {
    if (state.busy) return;
    if (!state.projectHandle) {
      log("Pick a project folder first.");
      return;
    }
    const repo = dom.ghRepoInput.value.trim();
    const ref = dom.ghRefInput.value.trim() || "main";
    const token = dom.ghTokenInput.value || "";

    if (!repo || !repo.includes("/")) {
      log("Enter a repo in 'owner/repo' format.");
      return;
    }

    try {
      setBusy(true);
      log(`Loading skill list from ${repo}@${ref}...`);
      const skillsMap = await SS.detectGithubSkills(repo, ref, token);
      if (state.githubTreeTruncated) {
        log("warning: GitHub tree response was truncated (very large repo) — " +
            "skill listing may be incomplete.");
      }
      if (skillsMap.size === 0) {
        log(`No skills (SKILL.md) found in ${repo}@${ref}.`);
      } else {
        log(`Found ${skillsMap.size} skill(s): ${Array.from(skillsMap.keys()).sort().join(", ")}`);
      }
      state.availableSkills = new Map();
      for (const [name, info] of skillsMap.entries()) {
        state.availableSkills.set(name, { kind: "github", repo, ref, token, info });
      }
      SS.fullRenderSkillList();
    } catch (e) {
      log("Error loading from GitHub: " + e.message);
      state.availableSkills = null;
      SS.fullRenderSkillList();
    } finally {
      setBusy(false);
    }
  });

  // ---------------------------------------------------------------------
  // Local source loading
  // ---------------------------------------------------------------------

  dom.btnPickSource.addEventListener("click", async () => {
    if (state.busy) return;
    if (!state.projectHandle) {
      log("Pick a project folder first.");
      return;
    }
    try {
      setBusy(true);
      const handle = await window.showDirectoryPicker({ mode: "read" });

      const targetSkillsHandle = await SS.getSkillsRoot(state.projectHandle, true);
      let resolved = null;
      try {
        resolved = await targetSkillsHandle.resolve(handle);
      } catch (e) {
        resolved = null;
      }
      if (resolved !== null) {
        log("Error: source folder is the target's .claude/skills/ (or a subdirectory " +
            "within it) — refusing to self-copy. Choose a different source folder.");
        setBusy(false);
        return;
      }

      state.sourceHandle = handle;
      state.sourceLabel = handle.name;
      dom.sourceNameEl.textContent = `Selected: ${state.sourceLabel}`;
      log(`Source folder selected: ${state.sourceLabel}`);

      log("Scanning for skills (SKILL.md)...");
      const skillsMap = await SS.detectLocalSkills(state.sourceHandle);
      if (skillsMap.size === 0) {
        log(`No skills (SKILL.md) found under '${state.sourceLabel}'.`);
      } else {
        log(`Found ${skillsMap.size} skill(s): ${Array.from(skillsMap.keys()).sort().join(", ")}`);
      }
      state.availableSkills = new Map();
      for (const [name, dirHandle] of skillsMap.entries()) {
        state.availableSkills.set(name, { kind: "local", handle: dirHandle });
      }
      SS.fullRenderSkillList();
    } catch (e) {
      if (e && e.name === "AbortError") {
        log("Source folder selection cancelled.");
      } else {
        log("Error selecting source folder: " + e.message);
      }
    } finally {
      setBusy(false);
    }
  });

  // ---------------------------------------------------------------------
  // Sync (install / update / add — union semantics)
  // ---------------------------------------------------------------------

  dom.btnSync.addEventListener("click", async () => {
    if (state.busy) return;
    if (!state.projectHandle) {
      log("Pick a project folder first.");
      return;
    }
    if (!state.availableSkills || state.availableSkills.size === 0) {
      log("No skills available to sync.");
      return;
    }

    const checked = Array.from(dom.skillListEl.querySelectorAll('input[type="checkbox"]:not([disabled])'))
      .filter((cb) => cb.checked)
      .map((cb) => cb.dataset.skill)
      .filter((name) => state.availableSkills.has(name));

    if (checked.length === 0) {
      log("No skills checked — nothing to sync.");
      return;
    }

    try {
      setBusy(true);
      log(`Syncing ${checked.length} skill(s): ${checked.slice().sort().join(", ")}...`);

      const skillsRoot = await SS.getSkillsRoot(state.projectHandle, true);

      for (const name of checked.sort()) {
        const entry = state.availableSkills.get(name);
        log(`  ${name}: removing existing copy (if any)...`);
        await SS.wipeSkillDir(state.projectHandle, name);

        const destDir = await skillsRoot.getDirectoryHandle(name, { create: true });

        if (entry.kind === "local") {
          log(`  ${name}: copying from local source...`);
          await SS.copyDirHandle(entry.handle, destDir);
        } else {
          log(`  ${name}: downloading from GitHub (${entry.repo}@${entry.ref})...`);
          await SS.copyGithubSkill(entry.repo, entry.ref, entry.token, entry.info, destDir);
        }
        log(`  ${name}: done.`);
      }

      const existingSkills = (state.manifest && Array.isArray(state.manifest.skills)) ? state.manifest.skills : [];
      const newSkills = SS.sortedUnique(existingSkills.concat(checked));
      const updated = SS.nowIso();

      let newManifest;
      if (state.manifest) {
        newManifest = JSON.parse(JSON.stringify(state.manifest));
        newManifest.skills = newSkills;
        newManifest.updated = updated;
        if (!newManifest.source) {
          newManifest.source = SS.manifestSourceType(state.manifest);
        }
      } else {
        if (state.sourceType === "github") {
          const repo = dom.ghRepoInput.value.trim();
          const ref = dom.ghRefInput.value.trim() || "main";
          newManifest = {
            source: "github",
            repo: repo,
            ref: ref,
            updated: updated,
            skills: newSkills,
          };
        } else {
          newManifest = {
            source: "local",
            path: state.sourceLabel,
            updated: updated,
            skills: newSkills,
          };
        }
      }

      await SS.writeManifest(state.projectHandle, newManifest);
      await SS.ensureGitignore(state.projectHandle, newSkills);

      state.manifest = newManifest;
      state.manifestExisted = true;
      SS.renderCurrentState();
      SS.fullRenderSkillList();

      log(`Sync complete. Manifest now lists ${newSkills.length} skill(s): ${newSkills.join(", ")}`);
    } catch (e) {
      log("Error during sync: " + e.message);
    } finally {
      setBusy(false);
    }
  });

  // ---------------------------------------------------------------------
  // Per-skill remove
  // ---------------------------------------------------------------------

  async function removeSkill(name) {
    if (state.busy) return;
    if (!state.projectHandle) {
      log("Pick a project folder first.");
      return;
    }
    if (!state.manifest) {
      log("No manifest found — nothing to remove.");
      return;
    }

    try {
      setBusy(true);
      log(`Removing '${name}'...`);

      await SS.wipeSkillDir(state.projectHandle, name);

      const skills = Array.isArray(state.manifest.skills) ? state.manifest.skills.slice() : [];
      const idx = skills.indexOf(name);
      let removed = false;
      if (idx !== -1) {
        skills.splice(idx, 1);
        removed = true;
      }

      const newManifest = JSON.parse(JSON.stringify(state.manifest));
      newManifest.skills = SS.sortedUnique(skills);
      newManifest.updated = SS.nowIso();
      if (!newManifest.source) {
        newManifest.source = SS.manifestSourceType(state.manifest);
      }

      await SS.writeManifest(state.projectHandle, newManifest);
      await SS.removeGitignoreLines(state.projectHandle, [name]);
      state.manifest = newManifest;

      SS.renderCurrentState();
      SS.fullRenderSkillList();

      log(removed ? `Removed '${name}'.` : `'${name}' was not in the manifest; folder removed if present.`);
    } catch (e) {
      log("Error removing '" + name + "': " + e.message);
    } finally {
      setBusy(false);
    }
  }

  SS.removeSkill = removeSkill;

  // ---------------------------------------------------------------------
  // Initial state
  // ---------------------------------------------------------------------
  setBusy(false);
  log("Ready. Choose a project folder to begin.");
})(window.SS || (window.SS = {}));
