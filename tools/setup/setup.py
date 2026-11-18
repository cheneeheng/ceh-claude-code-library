# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Set up a machine and a folder for the ceh-claude-code-library plugins.

Finds the tools the picked plugins need, installs each one after a yes, installs or enables the
picked plugins for this folder, and sets the Claude Code settings they rely on. `--check`, or no
terminal to answer, reports all of it and changes nothing. See tools/setup/README.md.

TOOLS and PLUGINS are literal dicts: tools/validate-plugins/checks/setup_registry.py reads them
with ast.literal_eval and fails when they drift from the plugins.
"""

from __future__ import annotations

# Tool name -> how to find it, which version it needs, what names it in a `compatibility`
# field, and how to install it per platform (None: no known installer).
TOOLS = {
    "python3": {
        "probe": ["python3", "-c", "import sys; print('%d.%d' % sys.version_info[:2])"],
        "min_version": (3, 10),
        "alternatives": [],
        "words": [r"\bpython3\b"],
        "install": {
            "windows": ["winget", "install", "Python.Python.3.13"],
            "darwin": ["brew", "install", "python"],
            "linux": ["sudo", "apt-get", "install", "-y", "python3"],
        },
    },
    "bash": {
        "probe": ["bash", "--version"],
        "alternatives": [],
        "words": [r"\bbash\b"],
        "install": {
            "windows": ["winget", "install", "Git.Git"],
            "darwin": None,
            "linux": None,
        },
    },
    "git": {
        "probe": ["git", "--version"],
        "alternatives": [],
        "words": [r"\bgit\b", r"git CLI"],
        "install": {
            "windows": ["winget", "install", "Git.Git"],
            "darwin": ["brew", "install", "git"],
            "linux": ["sudo", "apt-get", "install", "-y", "git"],
        },
    },
    "gh": {
        "probe": ["gh", "--version"],
        "alternatives": [],
        "words": [r"\bgh\b", r"GitHub CLI"],
        "install": {
            "windows": ["winget", "install", "GitHub.cli"],
            "darwin": ["brew", "install", "gh"],
            "linux": ["sudo", "apt-get", "install", "-y", "gh"],
        },
    },
    "uv": {
        "probe": ["uv", "--version"],
        "alternatives": [],
        "words": [r"\buv\b"],
        "install": {
            "windows": [
                "powershell",
                "-ExecutionPolicy",
                "ByPass",
                "-c",
                "irm https://astral.sh/uv/install.ps1 | iex",
            ],
            "darwin": ["sh", "-c", "curl -LsSf https://astral.sh/uv/install.sh | sh"],
            "linux": ["sh", "-c", "curl -LsSf https://astral.sh/uv/install.sh | sh"],
        },
    },
    "bun": {
        "probe": ["bun", "--version"],
        "alternatives": ["node"],
        "words": [r"\b[Bb]un\b"],
        "install": {
            "windows": ["powershell", "-c", "irm bun.sh/install.ps1 | iex"],
            "darwin": ["bash", "-c", "curl -fsSL https://bun.sh/install | bash"],
            "linux": ["bash", "-c", "curl -fsSL https://bun.sh/install | bash"],
        },
    },
    "node": {
        "probe": ["node", "--version"],
        # less-code: one floor per tool (the web skills' 20); per-skill floors only if reported.
        "min_version": (20, 0),
        "alternatives": [],
        "words": [r"Node\.js"],
        "install": {
            "windows": ["winget", "install", "OpenJS.NodeJS.LTS"],
            "darwin": ["brew", "install", "node"],
            # Ubuntu 24.04's apt nodejs is 18.19, below the floor.
            "linux": None,
        },
    },
    "chrome-extension": {
        "probe": None,
        "alternatives": [],
        "words": [r"Claude in Chrome"],
        "install": {"windows": None, "darwin": None, "linux": None},
    },
}

GROUPS = ("core", "shape", "build", "prove", "tell", "stack", "later")

# Plugin name -> its docs/GETTING_STARTED.md group, its plugin.json dependencies, its skills, the
# tools without which it is not installed, and the skills (or "hooks") each tool's absence
# degrades. min_claude: Claude Code version -> the skills that need it.
PLUGINS = {
    "ceh-every-session": {
        "group": "core",
        "dependencies": [],
        "skills": [
            "delegate-bulk-reads",
            "find-available-guide",
            "hand-off-session",
            "prevent-repeat-mistake",
            "record-project-decisions",
            "stress-test-plan",
            "usage-limit-handoff",
            "whats-next",
            "write-questionnaire",
            "write-research-note",
        ],
        "requires": [],
        "degrades": {
            "python3": ["hooks"],
            "uv": [
                "hooks",
                "hand-off-session",
                "prevent-repeat-mistake",
                "record-project-decisions",
                "whats-next",
            ],
        },
    },
    "ceh-git-workflow": {
        "group": "core",
        "dependencies": [],
        "skills": [
            "address-review-comments",
            "commit",
            "pull-request",
            "release",
            "review-recent-work",
            "update-changelog",
            "update-readme",
            "write-code-review",
        ],
        "requires": [],
        "degrades": {
            "python3": ["hooks"],
            "uv": ["hooks"],
            "git": [
                "hooks",
                "commit",
                "pull-request",
                "release",
                "review-recent-work",
                "update-changelog",
                "update-readme",
            ],
            "gh": [
                "address-review-comments",
                "pull-request",
                "release",
                "review-recent-work",
            ],
        },
    },
    "ceh-coding-conduct": {
        "group": "core",
        "dependencies": [],
        "skills": [
            "agent-coding-contract",
            "find-root-cause",
            "refactor-repo",
            "shrink-diff",
            "write-less-code",
        ],
        "requires": [],
        "degrades": {
            "python3": ["hooks"],
            "bash": ["hooks"],
            "uv": ["hooks", "find-root-cause"],
            "git": ["refactor-repo", "shrink-diff"],
        },
    },
    "ceh-product-direction": {
        "group": "shape",
        "dependencies": [],
        "skills": [
            "develop-business-plan",
            "find-product-market-fit",
            "plan-go-to-market",
            "review-business-plan",
            "run-premortem",
            "set-operating-plan",
            "sharpen-strategy",
            "stress-test-unit-economics",
            "write-investor-materials",
            "write-vision-and-strategy",
        ],
        "requires": [],
        "degrades": {
            "python3": ["hooks"],
            "uv": [
                "hooks",
                "develop-business-plan",
                "find-product-market-fit",
                "plan-go-to-market",
                "review-business-plan",
                "run-premortem",
                "set-operating-plan",
                "sharpen-strategy",
                "stress-test-unit-economics",
                "write-investor-materials",
                "write-vision-and-strategy",
            ],
            "node": ["develop-business-plan"],
        },
    },
    "ceh-competitor-analysis": {
        "group": "shape",
        "dependencies": ["ceh-ui-design"],
        "skills": ["analyze-competitor", "compare-competitors"],
        "requires": [],
        "degrades": {
            "python3": ["hooks"],
            "uv": ["hooks", "analyze-competitor", "compare-competitors"],
            "git": ["analyze-competitor"],
        },
    },
    "ceh-build-plan": {
        "group": "build",
        "dependencies": [],
        "skills": ["implement-from-plan", "review-build-plan", "write-build-plan"],
        "requires": [],
        "degrades": {
            "python3": ["hooks"],
            "uv": [
                "hooks",
                "implement-from-plan",
                "review-build-plan",
                "write-build-plan",
            ],
        },
    },
    "ceh-documentation": {
        "group": "build",
        "dependencies": [],
        "skills": [
            "write-api-reference",
            "write-concept-docs",
            "write-examples",
            "write-guides-and-runbooks",
            "write-project-docs",
        ],
        "requires": [],
        "degrades": {
            "git": ["write-api-reference", "write-concept-docs", "write-project-docs"],
            "uv": ["write-concept-docs", "write-examples"],
            "bun": ["write-examples"],
        },
    },
    "ceh-check-build-against-plan": {
        "group": "prove",
        "dependencies": [],
        "skills": ["check-build-against-plan"],
        "requires": [],
        "degrades": {
            "python3": ["hooks"],
            "uv": ["hooks", "check-build-against-plan"],
        },
    },
    "ceh-testing": {
        "group": "prove",
        "dependencies": [],
        "skills": [
            "audit-test-suite",
            "close-test-risk-gaps",
            "design-test-cases",
            "explore-app-for-bugs",
            "measure-performance",
            "test-a-bug-fix",
            "verify-behavior-preserved",
            "write-evidence-report",
            "write-test-first",
        ],
        "requires": [],
        "degrades": {
            "python3": ["hooks"],
            "uv": [
                "hooks",
                "audit-test-suite",
                "close-test-risk-gaps",
                "explore-app-for-bugs",
                "measure-performance",
                "test-a-bug-fix",
                "verify-behavior-preserved",
                "write-evidence-report",
            ],
            "bun": [
                "audit-test-suite",
                "close-test-risk-gaps",
                "test-a-bug-fix",
                "verify-behavior-preserved",
            ],
            "git": [
                "test-a-bug-fix",
                "verify-behavior-preserved",
                "write-evidence-report",
            ],
            "chrome-extension": ["explore-app-for-bugs"],
        },
    },
    "ceh-usability-audit": {
        "group": "prove",
        "dependencies": [],
        "skills": [
            "audit-error-messages",
            "audit-interface",
            "simulate-newcomer-first-run",
            "write-plain-language",
        ],
        "requires": [],
        "degrades": {
            "python3": ["hooks"],
            "uv": [
                "hooks",
                "audit-error-messages",
                "audit-interface",
                "simulate-newcomer-first-run",
            ],
            "git": ["simulate-newcomer-first-run"],
            "chrome-extension": ["audit-interface"],
        },
    },
    "ceh-security-audit": {
        "group": "prove",
        "dependencies": [],
        "skills": ["audit-codebase-security"],
        "requires": [],
        "degrades": {
            "python3": ["hooks"],
            "uv": ["hooks", "audit-codebase-security"],
            "git": ["audit-codebase-security"],
            "bun": ["audit-codebase-security"],
        },
    },
    "ceh-blog-and-seo": {
        "group": "tell",
        "dependencies": [],
        "skills": [
            "draft-post",
            "edit-post",
            "make-page-crawlable",
            "repurpose-post",
            "write-llms-txt",
            "write-project-listing-text",
        ],
        "requires": [],
        "degrades": {
            "python3": ["hooks"],
            "uv": ["hooks", "draft-post", "edit-post", "write-project-listing-text"],
        },
    },
    "ceh-python-service": {
        "group": "stack",
        "dependencies": ["ceh-testing"],
        "skills": [
            "configure-python-service-env",
            "write-fastapi-endpoints",
            "write-postgresql-code",
            "write-pytest-service-tests",
        ],
        "requires": ["uv"],
        "degrades": {},
    },
    "ceh-python-library": {
        "group": "stack",
        "dependencies": ["ceh-testing"],
        "skills": [
            "configure-python-library-env",
            "publish-python-library",
            "write-pytest-library-tests",
        ],
        "requires": ["uv"],
        "degrades": {},
    },
    "ceh-web-frontend": {
        "group": "stack",
        "dependencies": ["ceh-testing", "ceh-ui-design"],
        "skills": [
            "check-visual-parity",
            "configure-bun-vite-env",
            "make-ui-accessible",
            "visualize-graph-cytoscape",
            "write-react-vite-code",
            "write-sveltekit-code",
            "write-vitest-playwright-tests",
        ],
        "requires": [],
        "degrades": {
            "bun": [
                "configure-bun-vite-env",
                "visualize-graph-cytoscape",
                "write-react-vite-code",
                "write-sveltekit-code",
                "write-vitest-playwright-tests",
            ],
            "git": ["check-visual-parity"],
        },
    },
    "ceh-codebase-explanation": {
        "group": "later",
        "dependencies": [],
        "skills": [
            "document-architecture",
            "explain-codebase",
            "explain-until-understood",
            "maintain-glossary",
            "trace-code-rationale",
        ],
        "requires": [],
        "degrades": {
            "python3": ["hooks"],
            "uv": ["hooks", "document-architecture", "maintain-glossary"],
            "git": ["explain-codebase", "trace-code-rationale"],
            "gh": ["trace-code-rationale"],
        },
    },
    "ceh-ui-design": {
        "group": "later",
        "dependencies": [],
        "skills": ["design-ui"],
        "requires": [],
        "degrades": {},
    },
    "ceh-ag-ui": {
        "group": "later",
        "dependencies": ["ceh-ui-design"],
        "skills": [
            "add-canvas-component",
            "add-human-approval",
            "add-live-state-panel",
            "build-ag-ui",
            "build-ag-ui-agent",
        ],
        "requires": [],
        "degrades": {
            "uv": [
                "add-canvas-component",
                "add-human-approval",
                "add-live-state-panel",
                "build-ag-ui",
                "build-ag-ui-agent",
            ],
            "bun": [
                "add-canvas-component",
                "add-human-approval",
                "add-live-state-panel",
                "build-ag-ui",
            ],
        },
    },
    "ceh-workflow-builder": {
        "group": "later",
        "dependencies": [],
        "skills": ["build-agentic-workflow", "interview-workflow-task"],
        "requires": [],
        "degrades": {
            "python3": ["hooks"],
            "uv": ["hooks", "build-agentic-workflow", "interview-workflow-task"],
        },
        "min_claude": {"2.1.248": ["build-agentic-workflow"]},
    },
    "ceh-workflow-runner": {
        "group": "later",
        "dependencies": [],
        "skills": ["run-agentic-workflow"],
        "requires": [],
        "degrades": {
            "python3": ["hooks", "run-agentic-workflow"],
            "uv": ["hooks", "run-agentic-workflow"],
        },
        "min_claude": {"2.1.269": ["run-agentic-workflow"]},
    },
    "ceh-session-learning": {
        "group": "later",
        "dependencies": [],
        "skills": ["diagnose-session", "turn-session-into-skill"],
        "requires": [],
        "degrades": {"python3": ["hooks"], "uv": ["hooks"]},
    },
}
