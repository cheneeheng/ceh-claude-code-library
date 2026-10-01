#!/usr/bin/env bash
# detect-test-framework.sh
# Detects which TypeScript test framework(s) a project uses by inspecting
# package.json dependencies and config files. Outputs a human-readable summary
# and sets exit code 0 if at least one framework was detected.
#
# Usage: bash detect-test-framework.sh [project_root]
set -euo pipefail

ROOT="${1:-.}"
PKG="$ROOT/package.json"

if [[ ! -f "$PKG" ]]; then
  echo "ERROR: no package.json found at $PKG" >&2
  exit 2
fi

# Collect dependency names from dependencies + devDependencies.
# Uses node for robust JSON parsing — every TS project has node available.
DEPS=$(node -e '
  const p = require("'"$PKG"'");
  const all = { ...(p.dependencies||{}), ...(p.devDependencies||{}) };
  console.log(Object.keys(all).join("\n"));
')

has() { grep -qx "$1" <<<"$DEPS"; }

FOUND=0

echo "=== Test framework detection for $ROOT ==="

# Unit/integration runners
if has vitest; then
  echo "unit_runner: vitest"
  for cfg in vitest.config.ts vitest.config.js vitest.config.mjs; do
    [[ -f "$ROOT/$cfg" ]] && echo "  config: $cfg"
  done
  FOUND=1
fi

if has jest || has ts-jest; then
  echo "unit_runner: jest"
  for cfg in jest.config.ts jest.config.js jest.config.mjs jest.config.json; do
    [[ -f "$ROOT/$cfg" ]] && echo "  config: $cfg"
  done
  FOUND=1
fi

if has mocha; then
  echo "unit_runner: mocha"
  [[ -f "$ROOT/.mocharc.json" ]] && echo "  config: .mocharc.json"
  [[ -f "$ROOT/.mocharc.cjs" ]] && echo "  config: .mocharc.cjs"
  FOUND=1
fi

# Integration-relevant
has supertest && echo "integration_helper: supertest"
has testcontainers && echo "integration_helper: testcontainers"
has "@nestjs/testing" && echo "integration_helper: @nestjs/testing"
has msw && echo "integration_helper: msw"
has nock && echo "integration_helper: nock"

# DB drivers (integration boundary signal)
has prisma && echo "db: prisma"
has typeorm && echo "db: typeorm"
has drizzle-orm && echo "db: drizzle"
has pg && echo "db: pg"
has mysql2 && echo "db: mysql2"
has better-sqlite3 && echo "db: better-sqlite3"

# E2E runners
if has "@playwright/test" || has playwright; then
  echo "e2e_runner: playwright"
  [[ -f "$ROOT/playwright.config.ts" ]] && echo "  config: playwright.config.ts"
  [[ -f "$ROOT/playwright.config.js" ]] && echo "  config: playwright.config.js"
  FOUND=1
fi

if has cypress; then
  echo "e2e_runner: cypress"
  [[ -f "$ROOT/cypress.config.ts" ]] && echo "  config: cypress.config.ts"
  [[ -f "$ROOT/cypress.config.js" ]] && echo "  config: cypress.config.js"
  FOUND=1
fi

# Compose files (system-test stack)
for f in docker-compose.test.yml docker-compose.test.yaml compose.test.yml; do
  [[ -f "$ROOT/$f" ]] && echo "e2e_stack: $f"
done

# Existing test globs (best-effort)
echo "--- test file globs ---"
find "$ROOT" \
  -type d \( -name node_modules -o -name dist -o -name build -o -name .next \) -prune -o \
  -type f \( -name "*.test.ts" -o -name "*.test.tsx" -o -name "*.spec.ts" -o -name "*.spec.tsx" \) -print |
  head -n 20

if [[ $FOUND -eq 0 ]]; then
  echo "WARNING: no test framework detected"
  exit 1
fi
