(function (SS) {
  "use strict";

  // Pre-existing, currently unused — kept for parity with the
  // skills-sync.py/.sh/.ps1 layout constants.
  SS.MANIFEST_PATH = [".claude", "skills", ".manifest.json"]; // relative to project root
  SS.GITIGNORE_PATH = [".claude", ".gitignore"];
  SS.OLD_GITIGNORE_LINE = "skills/"; // legacy blanket-ignore line; migrated away from

  // ---------------------------------------------------------------------
  // Shared mutable state
  // ---------------------------------------------------------------------
  SS.state = {
    projectHandle: null,    // FileSystemDirectoryHandle (readwrite)
    manifest: null,          // parsed manifest object, or null
    manifestExisted: false,  // whether a manifest file existed on disk
    sourceType: "github",    // "github" | "local"
    sourceHandle: null,      // FileSystemDirectoryHandle for local source
    sourceLabel: "",         // label string for local source (folder name)
    availableSkills: null,   // Map<name, handle | githubEntries>
    githubTreeTruncated: false,
    busy: false,
  };

  // ---------------------------------------------------------------------
  // DOM references
  // ---------------------------------------------------------------------
  SS.dom = {
    banner: document.getElementById("banner"),
    stepProject: document.getElementById("step-project"),
    stepSource: document.getElementById("step-source"),
    stepSkills: document.getElementById("step-skills"),
    btnPickProject: document.getElementById("btn-pick-project"),
    projectNameEl: document.getElementById("project-name"),
    currentStateWrap: document.getElementById("current-state-wrap"),
    currentStateEl: document.getElementById("current-state"),
    sourceTypeRadios: document.querySelectorAll('input[name="source-type"]'),
    githubFields: document.getElementById("github-fields"),
    localFields: document.getElementById("local-fields"),
    ghRepoInput: document.getElementById("gh-repo"),
    ghRefInput: document.getElementById("gh-ref"),
    ghTokenInput: document.getElementById("gh-token"),
    btnLoadGithub: document.getElementById("btn-load-github"),
    btnPickSource: document.getElementById("btn-pick-source"),
    sourceNameEl: document.getElementById("source-name"),
    skillListEl: document.getElementById("skill-list"),
    btnSync: document.getElementById("btn-sync"),
    logEl: document.getElementById("log"),
  };
})(window.SS || (window.SS = {}));
