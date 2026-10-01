#!/usr/bin/env bash
# run-unit-tests.sh
# Runs unit tests using whichever runner the project has installed.
# Auto-detects jest / vitest / mocha from package.json.
#
# Usage: bash run-unit-tests.sh [test_file_or_pattern]
#        bash run-unit-tests.sh                  # run all
#        bash run-unit-tests.sh src/foo.test.ts  # run one file
#
# Run from the project root.
set -euo pipefail

TARGET="${1:-}"

if [[ ! -f package.json ]]; then
  echo "ERROR: must be run from project root (no package.json here)" >&2
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
  RUNNER=vitest
elif has_dep jest || has_dep ts-jest; then
  RUNNER=jest
elif has_dep mocha; then
  RUNNER=mocha
else
  echo "ERROR: no supported test runner found (expected vitest, jest, or mocha)" >&2
  exit 2
fi

echo ">> running unit tests with $RUNNER${TARGET:+ — target: $TARGET}"

case "$RUNNER" in
vitest)
  # --run = single-shot, no watch. --reporter=verbose for per-test visibility.
  npx vitest run --reporter=verbose ${TARGET:+"$TARGET"}
  ;;
jest)
  # --runInBand avoids flakes from parallel workers when the agent is iterating.
  npx jest --runInBand --colors ${TARGET:+"$TARGET"}
  ;;
mocha)
  # Assume ts-node/register is already configured in .mocharc; if not, add -r ts-node/register.
  npx mocha --reporter spec ${TARGET:+"$TARGET"}
  ;;
esac
