#!/usr/bin/env bash
# gh-validate.sh
# Validates a GitHub Actions workflow file.
# Runs YAML syntax check, actionlint (if available), and a security scan.
# Usage: bash gh-validate.sh <workflow_file>

set -euo pipefail
FILE="${1:?Usage: gh-validate.sh <workflow_file>}"

if [[ ! -f "$FILE" ]]; then
  echo "File not found: $FILE" >&2
  exit 1
fi

PASS=0
WARN=0
FAIL=0

echo "==> Validating GitHub Actions workflow: $FILE"
echo

# 1. YAML syntax
echo "[1/4] YAML syntax check"
if command -v python3 >/dev/null 2>&1; then
  if python3 -c "import yaml, sys; yaml.safe_load(open('$FILE'))" 2>&1; then
    echo "  [ok] YAML is valid"
    ((PASS++))
  else
    echo "  [FAIL] YAML syntax error — fix before proceeding"
    ((FAIL++))
    exit 1
  fi
else
  echo "  [skip] python3 not available"
fi

# 2. actionlint
echo
echo "[2/4] actionlint"
if command -v actionlint >/dev/null 2>&1; then
  if actionlint "$FILE"; then
    echo "  [ok] actionlint passed"
    ((PASS++))
  else
    echo "  [FAIL] actionlint found issues"
    ((FAIL++))
  fi
else
  echo "  [skip] actionlint not installed"
  echo "         Install: brew install actionlint"
  echo "             or:  go install github.com/rhysd/actionlint/cmd/actionlint@latest"
  ((WARN++))
fi

# 3. Unpinned third-party actions
echo
echo "[3/4] Supply-chain: unpinned actions check"
UNPINNED=$(grep -nE 'uses:\s*[^./]+/[^@]+@v[0-9]' "$FILE" 2>/dev/null || true)
if [[ -n "$UNPINNED" ]]; then
  echo "  [WARN] Third-party actions not pinned to a commit SHA:"
  echo "$UNPINNED" | sed 's/^/    /'
  echo "  Pin format: uses: owner/action@<full-sha>  # vX.Y.Z"
  ((WARN++))
else
  echo "  [ok] No tag-pinned third-party actions detected"
  ((PASS++))
fi

# 4. Hardcoded secrets scan
echo
echo "[4/4] Hardcoded secrets scan"
SECRET_HITS=$(grep -inE \
  '(password|api[_-]?key|api[_-]?secret|access[_-]?token|secret[_-]?key)\s*[:=]\s*["'"'"'][^"'"'"'$\{][^"'"'"']*["'"'"']' \
  "$FILE" 2>/dev/null || true)
if [[ -n "$SECRET_HITS" ]]; then
  echo "  [WARN] Possible hardcoded secret(s) detected — review carefully:"
  echo "$SECRET_HITS" | sed 's/^/    /'
  ((WARN++))
else
  echo "  [ok] No obvious hardcoded secrets"
  ((PASS++))
fi

# Summary
echo
echo "==> Summary: $PASS passed, $WARN warnings, $FAIL failures"
[[ $FAIL -gt 0 ]] && exit 1 || exit 0
