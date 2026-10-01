#!/usr/bin/env bash
# run-unit-tests.sh
# Runs pytest unit tests on a specific file or directory.
# Usage: bash run-unit-tests.sh [test_path] [extra_pytest_flags...]
#   test_path: file or directory to test (default: tests/unit)
#
# Run from the project root.

set -euo pipefail

TARGET="${1:-tests/unit}"
# Shift the target arg out so $@ only contains extra pytest flags (not the path again)
[[ $# -gt 0 ]] && shift

echo "==> Running unit tests: $TARGET"

# Ensure uv is available
if ! command -v uv &>/dev/null; then
  echo "ERROR: uv not found. Install from https://docs.astral.sh/uv/"
  exit 1
fi

# The -m filter excludes integration/system/e2e tests based on their markers.
# No need for --ignore flags, which would break if user passes a specific file.
uv run pytest "$TARGET" \
  --tb=short \
  -v \
  --no-header \
  -rN \
  -m "not integration and not system and not e2e" \
  "$@"

echo "==> Unit tests complete."
