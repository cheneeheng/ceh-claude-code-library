#!/usr/bin/env bash
# run-integration-tests.sh
# Runs pytest integration tests. Requires TEST_DATABASE_URL to be set.
# Usage: bash run-integration-tests.sh [test_path] [extra_pytest_flags...]
#   test_path: file or directory to test (default: tests/integration)
#
# Run from the project root.

set -euo pipefail

TARGET="${1:-tests/integration}"
# Shift the target arg out so $@ only contains extra pytest flags
[[ $# -gt 0 ]] && shift

echo "==> Running integration tests: $TARGET"

# Validate required env vars
if [[ -z "${TEST_DATABASE_URL:-}" ]]; then
  echo "ERROR: TEST_DATABASE_URL is not set."
  echo "       Set it to a test database, e.g.:"
  echo "       export TEST_DATABASE_URL=postgresql://user:pass@localhost:5432/testdb"
  exit 1
fi

# Ensure uv is available
if ! command -v uv &>/dev/null; then
  echo "ERROR: uv not found. Install from https://docs.astral.sh/uv/"
  exit 1
fi

echo "==> Using database: $TEST_DATABASE_URL"

# Filter by marker so tests without @pytest.mark.integration are skipped.
# The integration agent is instructed to add this marker to every test.
uv run pytest "$TARGET" \
  --tb=short \
  -v \
  --no-header \
  -rN \
  -m "integration" \
  "$@"

echo "==> Integration tests complete."
