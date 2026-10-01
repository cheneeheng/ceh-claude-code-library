#!/usr/bin/env bash
# run-system-tests.sh
# Runs full system/E2E tests. Expects the full stack to be up (or starts it via Docker).
# Usage: bash run-system-tests.sh [test_path] [--no-docker] [extra_pytest_flags...]
#   test_path:   directory to test (default: tests/system)
#   --no-docker: skip Docker Compose startup (assumes services are already running)
#
# Run from the project root.

set -euo pipefail

# --- Argument parsing ---
# First positional arg = test path; --no-docker flag can appear anywhere
TARGET=""
NO_DOCKER=false
EXTRA_ARGS=()

for arg in "$@"; do
  if [[ "$arg" == "--no-docker" ]]; then
    NO_DOCKER=true
  elif [[ -z "$TARGET" && "$arg" != --* ]]; then
    TARGET="$arg"
  else
    EXTRA_ARGS+=("$arg")
  fi
done

TARGET="${TARGET:-tests/system}"

echo "==> Running system tests: $TARGET"

# Validate env
if [[ -z "${TEST_DATABASE_URL:-}" && -z "${APP_BASE_URL:-}" ]]; then
  echo "WARNING: Neither TEST_DATABASE_URL nor APP_BASE_URL is set."
  echo "         System tests may fail if the app cannot connect to infrastructure."
fi

# Optionally start Docker services
if [[ "$NO_DOCKER" == false && -f "docker-compose.test.yml" ]]; then
  echo "==> Starting Docker test services..."
  docker compose -f docker-compose.test.yml up -d

  # Only wait for 'healthy' status if services define healthchecks.
  # Otherwise fall back to a short fixed wait.
  if grep -q "healthcheck:" docker-compose.test.yml; then
    echo "==> Waiting for services to be healthy..."
    RETRIES=30
    until docker compose -f docker-compose.test.yml ps | grep -q "healthy" || [[ $RETRIES -eq 0 ]]; do
      sleep 1
      ((RETRIES--)) || true
    done
    if [[ $RETRIES -eq 0 ]]; then
      echo "WARNING: Services did not report healthy within 30s — proceeding anyway."
    fi
  else
    echo "==> No healthchecks defined in docker-compose.test.yml — waiting 5s..."
    sleep 5
  fi
fi

# Cleanup trap — always tear down Docker on exit (success or failure)
cleanup() {
  local exit_code=$?
  if [[ "$NO_DOCKER" == false && -f "docker-compose.test.yml" ]]; then
    echo "==> Tearing down Docker test services..."
    docker compose -f docker-compose.test.yml down -v || true
  fi
  if [[ $exit_code -eq 0 ]]; then
    echo "==> System tests passed."
  else
    echo "==> System tests failed (exit code $exit_code)."
  fi
  exit $exit_code
}
trap cleanup EXIT

# Ensure uv is available
if ! command -v uv &>/dev/null; then
  echo "ERROR: uv not found. Install from https://docs.astral.sh/uv/"
  exit 1
fi

# Run system tests — longer timeout, sequential to avoid port conflicts.
# Requires: uv add --dev pytest-timeout
# Filter by marker so only @pytest.mark.system tests run, even if path is broad.
uv run pytest "$TARGET" \
  --tb=long \
  -v \
  --no-header \
  -rN \
  -p no:randomly \
  --timeout=120 \
  -m "system or e2e" \
  "${EXTRA_ARGS[@]+"${EXTRA_ARGS[@]}"}"
