(function (SS) {
  "use strict";

  const dom = SS.dom;
  const state = SS.state;

  function log(msg) {
    const ts = new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
    const line = `[${ts}] ${msg}`;
    if (dom.logEl.textContent === "(no activity yet)") {
      dom.logEl.textContent = line;
    } else {
      dom.logEl.textContent += "\n" + line;
    }
    dom.logEl.scrollTop = dom.logEl.scrollHeight;
  }

  function isButtonDisabledByState(b) {
    if (b === dom.btnSync) {
      return !state.projectHandle || !state.availableSkills;
    }
    if (b === dom.btnLoadGithub || b === dom.btnPickSource) {
      return !state.projectHandle;
    }
    return false;
  }

  function setBusy(v) {
    state.busy = v;
    const buttons = [
      dom.btnPickProject, dom.btnLoadGithub, dom.btnPickSource, dom.btnSync,
    ];
    for (const b of buttons) b.disabled = v || isButtonDisabledByState(b);
    document.querySelectorAll("button.danger").forEach((b) => { b.disabled = v; });
  }

  SS.log = log;
  SS.setBusy = setBusy;
})(window.SS || (window.SS = {}));
