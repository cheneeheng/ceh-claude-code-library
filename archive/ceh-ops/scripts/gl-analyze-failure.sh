#!/usr/bin/env bash
# gl-analyze-failure.sh
# Extracts the first failure signal from a GitLab CI job log so the agent can
# diagnose the root cause without reading thousands of lines of noise.
# Usage: bash gl-analyze-failure.sh <logfile>

set -euo pipefail
LOG="${1:?Usage: gl-analyze-failure.sh <logfile>}"

if [[ ! -f "$LOG" ]]; then
  echo "Log file not found: $LOG" >&2
  exit 1
fi

echo "==> Scanning GitLab CI job log: $LOG"
echo "    Total lines: $(wc -l <"$LOG")"
echo

# Patterns common in GitLab CI job traces
PATTERNS='(^ERROR:|^Error:|error:|FAILED|ERROR|fatal:|FATAL|Traceback \(most recent call last\)|Exception in thread|npm ERR!|command not found|No such file or directory|permission denied|Cannot find module|ModuleNotFoundError|ImportError|SyntaxError|exit code [1-9]|returned a non-zero code|Job failed|script returned exit code)'

FIRST_LINE=$(grep -inE "$PATTERNS" "$LOG" 2>/dev/null | head -n 1 | cut -d: -f1 || true)

if [[ -z "$FIRST_LINE" ]]; then
  echo "[info] No standard failure pattern matched."
  echo "       Showing last 50 lines of log:"
  echo
  tail -n 50 "$LOG"
  exit 0
fi

START=$((FIRST_LINE > 6 ? FIRST_LINE - 6 : 1))
END=$((FIRST_LINE + 25))

echo "[first failure signal at line $FIRST_LINE]"
echo
echo "--- context (lines $START–$END) ---"
sed -n "${START},${END}p" "$LOG"
echo "--- end context ---"
echo

# Error pattern frequency summary
echo "==> Error pattern frequency"
for pattern in \
  "Job failed" \
  "script returned exit code" \
  "returned a non-zero code" \
  "npm ERR!" \
  "^ERROR:" \
  "^Error:" \
  "FAILED" \
  "fatal:" \
  "Traceback" \
  "command not found"; do
  count=$(grep -icE "$pattern" "$LOG" 2>/dev/null || true)
  [[ "$count" -gt 0 ]] && printf "  %-45s %s hits\n" "$pattern" "$count"
done

echo
echo "==> Recommended next steps"
echo "  1. Review the context above for the root cause."
echo "  2. Open the full job trace in the GitLab UI:"
echo "     GitLab project > CI/CD > Pipelines > [pipeline] > [job] > Log"
echo "  3. Run: glab ci view   (requires glab CLI + auth)"
echo "  4. Check if the issue is environment (missing dep, wrong image, missing variable)"
echo "     or code (test failure, compile error, lint error)."
