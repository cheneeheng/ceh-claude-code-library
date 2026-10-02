(function (SS) {
  "use strict";

  const dom = SS.dom;
  const state = SS.state;

  function renderCurrentState() {
    if (!state.manifest) {
      dom.currentStateWrap.hidden = true;
      dom.currentStateEl.textContent = "";
      return;
    }
    dom.currentStateWrap.hidden = false;
    const st = SS.manifestSourceType(state.manifest);
    let label;
    if (st === "github") {
      label = `${state.manifest.repo}@${state.manifest.ref || "main"}`;
    } else {
      label = state.manifest.path || "(unknown path)";
    }
    const skills = state.manifest.skills || [];
    const lines = [
      `${label} (updated ${state.manifest.updated || "unknown"})`,
    ];
    if (skills.length === 0) {
      lines.push("  (no skills installed)");
    } else {
      for (const s of skills) lines.push("  " + s);
    }
    dom.currentStateEl.textContent = lines.join("\n");
  }

  function installedSet() {
    if (!state.manifest || !Array.isArray(state.manifest.skills)) return new Set();
    return new Set(state.manifest.skills);
  }

  function renderSkillList() {
    dom.skillListEl.innerHTML = "";
    if (!state.availableSkills) {
      dom.stepSkills.hidden = true;
      dom.btnSync.disabled = true;
      return;
    }
    dom.stepSkills.hidden = false;
    const installed = installedSet();
    const names = Array.from(state.availableSkills.keys()).sort();

    if (names.length === 0) {
      const li = document.createElement("li");
      li.textContent = "No skills (SKILL.md) found in this source.";
      dom.skillListEl.appendChild(li);
      dom.btnSync.disabled = true;
      return;
    }

    for (const name of names) {
      const li = document.createElement("li");

      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.dataset.skill = name;
      checkbox.checked = installed.has(name);

      const nameSpan = document.createElement("span");
      nameSpan.className = "name";
      nameSpan.textContent = name;

      const badge = document.createElement("span");
      if (installed.has(name)) {
        badge.className = "badge installed";
        badge.textContent = "installed";
      } else {
        badge.className = "badge new";
        badge.textContent = "new";
      }

      li.appendChild(checkbox);
      li.appendChild(nameSpan);
      li.appendChild(badge);

      if (installed.has(name)) {
        const removeBtn = document.createElement("button");
        removeBtn.className = "danger";
        removeBtn.textContent = "×";
        removeBtn.title = `Remove ${name} now`;
        removeBtn.addEventListener("click", () => SS.removeSkill(name));
        li.appendChild(removeBtn);
      }

      dom.skillListEl.appendChild(li);
    }

    dom.btnSync.disabled = !state.projectHandle;
  }

  function renderOrphanInstalled() {
    if (!state.manifest || !Array.isArray(state.manifest.skills) || !state.availableSkills) return;
    const sourceNames = new Set(state.availableSkills.keys());
    const orphans = state.manifest.skills.filter((n) => !sourceNames.has(n)).sort();
    for (const name of orphans) {
      const li = document.createElement("li");

      const spacer = document.createElement("input");
      spacer.type = "checkbox";
      spacer.disabled = true;
      spacer.title = "Not present in current source — cannot be re-synced from here";

      const nameSpan = document.createElement("span");
      nameSpan.className = "name";
      nameSpan.textContent = name;

      const badge = document.createElement("span");
      badge.className = "badge installed";
      badge.textContent = "installed (not in source)";

      const removeBtn = document.createElement("button");
      removeBtn.className = "danger";
      removeBtn.textContent = "×";
      removeBtn.title = `Remove ${name} now`;
      removeBtn.addEventListener("click", () => SS.removeSkill(name));

      li.appendChild(spacer);
      li.appendChild(nameSpan);
      li.appendChild(badge);
      li.appendChild(removeBtn);
      dom.skillListEl.appendChild(li);
    }
  }

  function fullRenderSkillList() {
    renderSkillList();
    if (state.availableSkills) renderOrphanInstalled();
  }

  SS.renderCurrentState = renderCurrentState;
  SS.installedSet = installedSet;
  SS.renderSkillList = renderSkillList;
  SS.renderOrphanInstalled = renderOrphanInstalled;
  SS.fullRenderSkillList = fullRenderSkillList;
})(window.SS || (window.SS = {}));
