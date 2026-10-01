#!/usr/bin/env bash
# check-coverage.sh
# Runs the test suite with coverage enabled and prints the coverage line
# for a specific source file. Used by the unit tester to find the lines
# and branches of the target file that are still untested.
#
# Usage: bash check-coverage.sh <source_file>
# Example: bash check-coverage.sh src/lib/pricing.ts
#
# Run from the project root.
set -euo pipefail

SRC="${1:-}"
if [[ -z "$SRC" ]]; then
  echo "Usage: $0 <source_file>" >&2
  exit 2
fi
if [[ ! -f "$SRC" ]]; then
  echo "ERROR: source file not found: $SRC" >&2
  exit 2
fi

has_dep() {
  node -e '
    const p = require("./package.json");
    const all = { ...(p.dependencies||{}), ...(p.devDependencies||{}) };
    process.exit(all["'"$1"'"] ? 0 : 1);
  '
}

if has_dep vitest; then
  # Vitest uses v8 or istanbul — text-summary plus text gives us per-file lines.
  npx vitest run --coverage --coverage.reporter=text --coverage.reporter=text-summary |
    tee /tmp/_cov.out
  echo "--- coverage for $SRC ---"
  # Vitest's text reporter prints file paths relative to cwd.
  grep -F "$SRC" /tmp/_cov.out || echo "(no line matched — file may not be in the include set)"
elif has_dep jest || has_dep ts-jest; then
  npx jest --runInBand --coverage --coverageReporters=text --coverageReporters=text-summary \
    --collectCoverageFrom="$SRC" |
    tee /tmp/_cov.out
  echo "--- coverage for $SRC ---"
  grep -F "$SRC" /tmp/_cov.out || echo "(no line matched)"
else
  echo "ERROR: coverage only wired for vitest and jest here" >&2
  exit 2
fi
