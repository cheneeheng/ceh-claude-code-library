#!/usr/bin/env bash
# gl-detect-stack.sh
# Detects the project's language/tooling stack and existing GitLab CI configuration.
# Outputs key=value lines for the agent to parse.
# Usage: bash gl-detect-stack.sh [repo_root]

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

# --- GitLab CI detection ---
if [[ -f .gitlab-ci.yml ]]; then
  echo "gitlab_ci=present"
  # Check for deprecated only/except usage
  if grep -qE '^\s*(only|except):' .gitlab-ci.yml 2>/dev/null; then
    echo "uses_only_except=true"
  else
    echo "uses_only_except=false"
  fi
  # Check for include:
  if grep -qE '^\s*include:' .gitlab-ci.yml 2>/dev/null; then
    echo "uses_include=true"
  fi
  # Check for needs: (DAG)
  if grep -qE '^\s*needs:' .gitlab-ci.yml 2>/dev/null; then
    echo "uses_needs_dag=true"
  fi
else
  echo "gitlab_ci=absent"
fi

# Local include files
if [[ -d .gitlab/ci ]]; then
  COUNT=$(find .gitlab/ci -type f \( -name "*.yml" -o -name "*.yaml" \) | wc -l | tr -d ' ')
  echo "gitlab_ci_includes=$COUNT"
fi

# --- Legacy CI signals (migration scenarios) ---
[[ -f .travis.yml ]] && echo "legacy_ci=travis"
[[ -f .circleci/config.yml ]] && echo "legacy_ci=circleci"
[[ -f Jenkinsfile ]] && echo "legacy_ci=jenkins"
[[ -f azure-pipelines.yml ]] && echo "legacy_ci=azure"
[[ -d .github/workflows ]] && echo "also_has=github-actions"

echo "done=true"
