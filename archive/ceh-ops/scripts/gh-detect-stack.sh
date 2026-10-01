#!/usr/bin/env bash
# gh-detect-stack.sh
# Detects the project's language/tooling stack and existing GitHub Actions workflows.
# Outputs key=value lines for the agent to parse.
# Usage: bash gh-detect-stack.sh [repo_root]

set -euo pipefail
ROOT="${1:-$(pwd)}"
cd "$ROOT"

echo "repo_root=$ROOT"

# --- Language / stack detection ---
[[ -f package.json ]] && echo "stack=node"
if [[ -f pyproject.toml ]]; then
  [[ -f uv.lock ]] && echo "stack=python-uv" || echo "stack=python-poetry"
fi
[[ -f requirements.txt && ! -f pyproject.toml ]] && echo "stack=python-pip"
[[ -f go.mod ]] && echo "stack=go"
[[ -f Cargo.toml ]] && echo "stack=rust"
[[ -f pom.xml ]] && echo "stack=java-maven"
[[ -f build.gradle || -f build.gradle.kts ]] && echo "stack=java-gradle"
[[ -f Gemfile ]] && echo "stack=ruby"
[[ -f composer.json ]] && echo "stack=php"
[[ -f mix.exs ]] && echo "stack=elixir"

# Node package manager
if [[ -f package.json ]]; then
  [[ -f bun.lockb ]] && echo "node_pm=bun"
  [[ -f pnpm-lock.yaml ]] && echo "node_pm=pnpm"
  [[ -f yarn.lock ]] && echo "node_pm=yarn"
  [[ -f package-lock.json ]] && echo "node_pm=npm"
fi

# Container signals
[[ -f Dockerfile ]] && echo "has_dockerfile=true"
[[ -f docker-compose.yml || -f compose.yaml ]] && echo "has_compose=true"

# --- GitHub Actions detection ---
if [[ -d .github/workflows ]]; then
  COUNT=$(find .github/workflows -maxdepth 1 -type f \( -name "*.yml" -o -name "*.yaml" \) | wc -l | tr -d ' ')
  echo "github_workflows_count=$COUNT"
  find .github/workflows -maxdepth 1 -type f \( -name "*.yml" -o -name "*.yaml" \) | while read -r f; do
    echo "github_workflow=$f"
  done
else
  echo "github_workflows_count=0"
fi

[[ -d .github/actions ]] && echo "has_composite_actions=true"

# --- Unpinned actions warning ---
if [[ -d .github/workflows ]]; then
  UNPINNED=$(grep -rE 'uses:\s*[^./]+/[^@]+@v[0-9]' .github/workflows/ 2>/dev/null || true)
  if [[ -n "$UNPINNED" ]]; then
    echo "unpinned_actions=true"
  else
    echo "unpinned_actions=false"
  fi
fi

# --- Legacy CI signals (migration scenarios) ---
[[ -f .travis.yml ]] && echo "legacy_ci=travis"
[[ -f .circleci/config.yml ]] && echo "legacy_ci=circleci"
[[ -f Jenkinsfile ]] && echo "legacy_ci=jenkins"
[[ -f azure-pipelines.yml ]] && echo "legacy_ci=azure"
[[ -f .gitlab-ci.yml ]] && echo "also_has=gitlab-ci"

echo "done=true"
