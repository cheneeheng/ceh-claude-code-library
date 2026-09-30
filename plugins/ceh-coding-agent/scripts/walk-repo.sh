#!/usr/bin/env bash
# walk-repo.sh
# Walks a repository and prints a filtered, sorted list of files and directories
# for the repo-tree-mapper agent to annotate.
#
# Usage: bash walk-repo.sh [target_dir] [max_depth]
#   target_dir  — directory to walk (default: current directory)
#   max_depth   — maximum depth to recurse (default: 8)
#
# Output: one path per line, relative to target_dir, directories suffixed with '/'.
#         Respects .gitignore when inside a git repo; always skips common noise dirs.
#
# Run from the project root, or pass target_dir explicitly.

set -euo pipefail

TARGET="${1:-.}"
MAX_DEPTH="${2:-8}"

if [[ ! -d "$TARGET" ]]; then
  echo "Error: '$TARGET' is not a directory" >&2
  exit 1
fi

cd "$TARGET"

# Directories we always skip regardless of .gitignore
PRUNE_DIRS=(
  ".git" "node_modules" "venv" ".venv" "__pycache__"
  "dist" "build" "target" ".next" ".nuxt" ".turbo"
  ".idea" ".vscode" ".cache" ".pytest_cache" ".mypy_cache"
  "coverage" ".nyc_output" ".gradle" ".mvn"
)

# Build the find prune expression
PRUNE_EXPR=()
for d in "${PRUNE_DIRS[@]}"; do
  PRUNE_EXPR+=(-name "$d" -o)
done
# Remove the trailing -o
unset 'PRUNE_EXPR[${#PRUNE_EXPR[@]}-1]'

# If we're inside a git repo, use git ls-files for gitignore-aware listing.
# Otherwise fall back to find.
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  # Tracked + untracked-but-not-ignored files
  {
    git ls-files
    git ls-files --others --exclude-standard
  } | sort -u | while IFS= read -r file; do
    # Skip files inside pruned dirs (git may still list some)
    skip=false
    for d in "${PRUNE_DIRS[@]}"; do
      if [[ "$file" == "$d/"* || "$file" == *"/$d/"* ]]; then
        skip=true
        break
      fi
    done
    [[ $skip == true ]] && continue

    # Depth check
    depth=$(echo "$file" | tr -cd '/' | wc -c)
    if ((depth > MAX_DEPTH)); then
      continue
    fi

    echo "$file"

    # Also emit parent directories so the agent sees folder structure
    dir=$(dirname "$file")
    while [[ "$dir" != "." && "$dir" != "/" ]]; do
      echo "$dir/"
      dir=$(dirname "$dir")
    done
  done | sort -u
else
  # No git — fall back to find. Two passes: files then dirs (avoids per-path
  # shell subprocesses to determine type).
  {
    find . -maxdepth "$MAX_DEPTH" \
      \( -type d \( "${PRUNE_EXPR[@]}" \) -prune \) -o \
      -type f -print 2>/dev/null | sed 's|^\./||'
    find . -maxdepth "$MAX_DEPTH" \
      \( -type d \( "${PRUNE_EXPR[@]}" \) -prune \) -o \
      -type d ! -name '.' -print 2>/dev/null | sed 's|^\./||; s|$|/|'
  } | sort -u | grep -v '^$'
fi
