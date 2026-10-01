#!/usr/bin/env bash
# run-e2e.sh
# Drives end-to-end tests: optionally brings up a docker-compose.test.yml stack,
# runs the detected E2E runner (Playwright or Cypress) against it, and tears down.
# Refuses to run against what looks like a production URL.
#
# Usage:
#   bash run-e2e.sh up              # stack only, no tests
#   bash run-e2e.sh down            # teardown
#   bash run-e2e.sh test [pattern]  # run suite (default: full)
#   bash run-e2e.sh smoke           # run tests tagged @smoke
#
# Run from the project root.
set -euo pipefail

CMD="${1:-test}"
PATTERN="${2:-}"

COMPOSE_FILE=""
for f in docker-compose.test.yml docker-compose.test.yaml compose.test.yml; do
  [[ -f "$f" ]] && COMPOSE_FILE="$f" && break
done

has_dep() {
  node -e '
    const p = require("./package.json");
    const all = { ...(p.dependencies||{}), ...(p.devDependencies||{}) };
    process.exit(all["'"$1"'"] ? 0 : 1);
  '
}

compose_up() {
  [[ -z "$COMPOSE_FILE" ]] && {
    echo ">> no compose file; assuming stack is already up"
    return
  }
  echo ">> bringing up stack from $COMPOSE_FILE"
  docker compose -f "$COMPOSE_FILE" up -d --wait
}

compose_down() {
  [[ -z "$COMPOSE_FILE" ]] && return
  echo ">> tearing down stack from $COMPOSE_FILE"
  docker compose -f "$COMPOSE_FILE" down -v
}

# Safety rail: refuse to target what looks like production.
guard_target() {
  local url="${E2E_BASE_URL:-${BASE_URL:-}}"
  if [[ -n "$url" ]]; then
    # Block anything that smells like prod unless the caller explicitly tagged it smoke-safe.
    if [[ "$url" =~ prod|production ]] && [[ "$CMD" != "smoke" ]]; then
      echo "ERROR: refusing to run full E2E against prod-looking URL: $url" >&2
      echo "       use 'smoke' for read-only checks, or override by unsetting the URL." >&2
      exit 3
    fi
    if [[ "${NODE_ENV:-}" == "production" ]] && [[ "$CMD" != "smoke" ]]; then
      echo "ERROR: NODE_ENV=production with non-smoke E2E is not allowed" >&2
      exit 3
    fi
  fi
}

run_tests() {
  guard_target
  local extra=()
  if has_dep "@playwright/test" || has_dep playwright; then
    echo ">> running Playwright${PATTERN:+ — $PATTERN}"
    if [[ "$CMD" == "smoke" ]]; then
      extra+=(--grep "@smoke")
    fi
    npx playwright test "${extra[@]}" ${PATTERN:+"$PATTERN"}
  elif has_dep cypress; then
    echo ">> running Cypress${PATTERN:+ — $PATTERN}"
    if [[ "$CMD" == "smoke" ]]; then
      npx cypress run --env grepTags=@smoke ${PATTERN:+--spec "$PATTERN"}
    else
      npx cypress run ${PATTERN:+--spec "$PATTERN"}
    fi
  else
    echo "ERROR: no E2E runner found (expected @playwright/test or cypress)" >&2
    exit 2
  fi
}

case "$CMD" in
up) compose_up ;;
down) compose_down ;;
test | smoke)
  # If there's a compose file and nothing is up yet, bring it up; tear down on exit.
  if [[ -n "$COMPOSE_FILE" ]]; then
    compose_up
    trap compose_down EXIT
  fi
  run_tests
  ;;
*)
  echo "Usage: $0 {up|down|test [pattern]|smoke}" >&2
  exit 2
  ;;
esac
