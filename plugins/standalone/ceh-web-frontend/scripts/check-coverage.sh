#!/usr/bin/env bash
# check-coverage.sh
# Runs the test suite with coverage enabled and prints the coverage line
# for a specific source file. Used by the unit tester to find the lines
# and branches of the target file that are still untested.
#
# Usage: bash check-coverage.sh <source_file> [test_file]
# Example: bash check-coverage.sh src/lib/pricing.ts src/lib/pricing.test.ts
#
# Run from the project root.
set -euo pipefail

SRC="${1:-}"
TEST="${2:-}"
if [[ -z "$SRC" ]]; then
  echo "Usage: $0 <source_file> [test_file]" >&2
  exit 2
fi
if [[ ! -f "$SRC" ]]; then
  echo "ERROR: source file not found: $SRC" >&2
  exit 2
fi

# The text reporter prints a nested file by its base name, under its directory's row.
BASE="$(basename "$SRC")"
OUT="$(mktemp)"
trap 'rm -f "$OUT"' EXIT

has_dep() {
  bun -e '
    const p = require("./package.json");
    const all = { ...(p.dependencies||{}), ...(p.devDependencies||{}) };
    process.exit(all["'"$1"'"] ? 0 : 1);
  '
}

if has_dep vitest; then
  if ! has_dep @vitest/coverage-v8 && ! has_dep @vitest/coverage-istanbul; then
    echo "ERROR: no Vitest coverage provider installed. Add one: bun add -d @vitest/coverage-v8" >&2
    exit 2
  fi
  # Coverage is collected for the one source file, from the one test file when it is given.
  bunx vitest run ${TEST:+"$TEST"} --coverage --coverage.include="$SRC" \
    --coverage.reporter=text --coverage.reporter=text-summary |
    tee "$OUT"
  echo "--- coverage for $SRC ---"
  grep -F "$BASE" "$OUT" || echo "(no line matched — file may not be in the include set)"
elif has_dep jest || has_dep ts-jest; then
  bunx jest --runInBand ${TEST:+"$TEST"} --coverage --coverageReporters=text \
    --coverageReporters=text-summary --collectCoverageFrom="$SRC" |
    tee "$OUT"
  echo "--- coverage for $SRC ---"
  grep -F "$BASE" "$OUT" || echo "(no line matched)"
else
  echo "ERROR: coverage only wired for vitest and jest here" >&2
  exit 2
fi
