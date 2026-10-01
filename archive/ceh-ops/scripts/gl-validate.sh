#!/usr/bin/env bash
# gl-validate.sh
# Validates a GitLab CI pipeline file.
# Runs YAML syntax check, glab ci lint (if available), and a security scan.
# Usage: bash gl-validate.sh <pipeline_file>

set -euo pipefail
FILE="${1:?Usage: gl-validate.sh <pipeline_file>}"

if [[ ! -f "$FILE" ]]; then
  echo "File not found: $FILE" >&2
  exit 1
fi

PASS=0
WARN=0
FAIL=0

echo "==> Validating GitLab CI pipeline: $FILE"
echo

# 1. YAML syntax
echo "[1/5] YAML syntax check"
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

# 2. glab ci lint
echo
echo "[2/5] glab ci lint"
if command -v glab >/dev/null 2>&1; then
  if glab ci lint --filename "$FILE" 2>/dev/null; then
    echo "  [ok] glab ci lint passed"
    ((PASS++))
  else
    echo "  [WARN] glab ci lint reported issues (may need auth or GitLab connectivity)"
    ((WARN++))
  fi
else
  echo "  [skip] glab CLI not installed"
  echo "         Install: brew install glab"
  echo "             or:  https://gitlab.com/gitlab-org/cli#installation"
  ((WARN++))
fi

# 3. Deprecated only/except usage
echo
echo "[3/5] Deprecated only/except check"
ONLY_EXCEPT=$(grep -nE '^\s+(only|except):' "$FILE" 2>/dev/null || true)
if [[ -n "$ONLY_EXCEPT" ]]; then
  echo "  [WARN] Deprecated only/except syntax found — migrate to rules:"
  echo "$ONLY_EXCEPT" | sed 's/^/    /'
  ((WARN++))
else
  echo "  [ok] No deprecated only/except found"
  ((PASS++))
fi

# 4. Artifacts without expire_in
echo
echo "[4/5] Artifacts expire_in check"
# Look for artifacts: blocks missing expire_in
ARTIFACT_JOBS=$(grep -n 'artifacts:' "$FILE" 2>/dev/null || true)
if [[ -n "$ARTIFACT_JOBS" ]]; then
  # Simple heuristic: count artifacts: vs expire_in:
  ART_COUNT=$(grep -cE '^\s+artifacts:' "$FILE" 2>/dev/null || true)
  EXP_COUNT=$(grep -cE '^\s+expire_in:' "$FILE" 2>/dev/null || true)
  if [[ "$EXP_COUNT" -lt "$ART_COUNT" ]]; then
    echo "  [WARN] Some artifact blocks may be missing expire_in: (found $ART_COUNT artifacts:, $EXP_COUNT expire_in:)"
    echo "         Artifacts without expiry accumulate storage costs."
    ((WARN++))
  else
    echo "  [ok] All artifact blocks appear to have expire_in:"
    ((PASS++))
  fi
else
  echo "  [ok] No artifacts: blocks found"
  ((PASS++))
fi

# 5. Hardcoded secrets scan
echo
echo "[5/5] Hardcoded secrets scan"
SECRET_HITS=$(grep -inE \
  '(password|api[_-]?key|api[_-]?secret|access[_-]?token|secret[_-]?key)\s*[:=]\s*["'"'"'][^"'"'"'$\{][^"'"'"']*["'"'"']' \
  "$FILE" 2>/dev/null || true)
if [[ -n "$SECRET_HITS" ]]; then
  echo "  [WARN] Possible hardcoded secret(s) detected — review carefully:"
  echo "$SECRET_HITS" | sed 's/^/    /'
  echo "  Use GitLab CI/CD variables (Settings > CI/CD > Variables) instead."
  ((WARN++))
else
  echo "  [ok] No obvious hardcoded secrets"
  ((PASS++))
fi

# Summary
echo
echo "==> Summary: $PASS passed, $WARN warnings, $FAIL failures"
[[ $FAIL -gt 0 ]] && exit 1 || exit 0
