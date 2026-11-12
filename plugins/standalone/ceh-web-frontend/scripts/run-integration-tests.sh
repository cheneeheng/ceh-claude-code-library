#!/usr/bin/env bash
# run-integration-tests.sh
# Runs integration tests with NODE_ENV=test. Prefers a dedicated integration
# folder/pattern if one exists; otherwise falls back to *.integration.test.ts.
#
# Usage: bash run-integration-tests.sh [pattern]
#
# Run from the project root.
set -euo pipefail

PATTERN="${1:-}"

if [[ ! -f package.json ]]; then
  echo "ERROR: must be run from project root" >&2
  exit 2
fi

has_dep() {
  bun -e '
    const p = require("./package.json");
    const all = { ...(p.dependencies||{}), ...(p.devDependencies||{}) };
    process.exit(all["'"$1"'"] ? 0 : 1);
  '
}

# Pick the default pattern if the caller didn't supply one.
if [[ -z "$PATTERN" ]]; then
  if [[ -d tests/integration ]]; then
    PATTERN="tests/integration"
  elif [[ -d test/integration ]]; then
    PATTERN="test/integration"
  elif [[ -d src/__tests__/integration ]]; then
    PATTERN="src/__tests__/integration"
  elif [[ -d src/routes ]]; then
    # Component tests sit beside the page they render, as src/routes/<page>/<Component>.test.ts.
    PATTERN="src/routes"
  else
    PATTERN="src"
  fi
fi

echo ">> integration test target: $PATTERN"

export NODE_ENV=test

if has_dep vitest; then
  # --pool=forks gives each test file its own process — safer when tests touch
  # shared resources (stores, in-memory singletons).
  bunx vitest run --pool=forks --reporter=verbose "$PATTERN"
elif has_dep jest || has_dep ts-jest; then
  # --runInBand keeps tests that share state from running at once.
  bunx jest --runInBand --colors --testPathPattern="$PATTERN"
elif has_dep mocha; then
  bunx mocha --reporter spec --recursive "$PATTERN"
else
  echo "ERROR: no supported test runner found" >&2
  exit 2
fi
