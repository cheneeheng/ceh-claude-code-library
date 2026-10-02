#!/usr/bin/env bash
#
# skills-sync — copy Claude Code skills from a GitHub repo or local folder
# into a project's .claude/skills/ directory.
#
# Usage:
#   skills-sync.sh install (--repo owner/name [--ref REF] | --path DIR) \
#       [--skills a,b|all] [--target DIR] [--token TOKEN]
#   skills-sync.sh update [--skills a,b|all] [--target DIR] [--token TOKEN]
#   skills-sync.sh add --skills a,b [--target DIR] [--token TOKEN]
#   skills-sync.sh remove --skills a,b [--target DIR]
#   skills-sync.sh list [--target DIR]
#
# Requires: bash, curl, tar, jq.

set -euo pipefail

MANIFEST_NAME=".manifest.json"
OLD_GITIGNORE_LINE="skills/" # legacy blanket-ignore line; migrated away from

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

err() {
  echo "error: $*" >&2
  exit 1
}

now_iso() {
  date -u +"%Y-%m-%dT%H:%M:%S+00:00"
}

skills_dir() {
  # $1 = target
  printf '%s/.claude/skills' "$1"
}

manifest_path() {
  # $1 = target
  printf '%s/%s' "$(skills_dir "$1")" "$MANIFEST_NAME"
}

# Detect skills under a source root.
# Prints lines of "name<TAB>absolute_path", one per skill, sorted by name.
# If two directories share a basename, the later one found (per `find` order,
# which is sorted lexically by path because we sort the SKILL.md list) wins;
# a warning is printed to stderr.
detect_skills() {
  # $1 = source root (must already be an absolute, resolved path)
  local root="$1"
  local -A skill_paths=()
  local skill_dir name

  while IFS= read -r skill_dir; do
    if [[ "$skill_dir" == "$root" ]]; then
      continue
    fi
    name="$(basename "$skill_dir")"
    if [[ -n "${skill_paths[$name]:-}" && "${skill_paths[$name]}" != "$skill_dir" ]]; then
      echo "warning: duplicate skill name '$name' found at '$skill_dir' and '${skill_paths[$name]}' — using the latter" >&2
    fi
    skill_paths[$name]="$skill_dir"
  done < <(find "$root" -name SKILL.md -exec dirname {} \; | sort)

  local n
  for n in "${!skill_paths[@]}"; do
    printf '%s\t%s\n' "$n" "${skill_paths[$n]}"
  done | sort -k1,1
}

# Look up the path for a given skill name in a "name<TAB>path" listing.
lookup_skill_path() {
  # $1 = available listing (newline separated "name\tpath")
  # $2 = skill name
  local available="$1" name="$2"
  awk -F'\t' -v n="$name" '$1 == n {print $2; found=1} END {exit !found}' <<<"$available"
}

# Sorted, deduped list of available skill names, one per line.
available_names() {
  # $1 = available listing
  awk -F'\t' '{print $1}' <<<"$1" | sort -u
}

# Resolve a --skills value ('all', a comma list, or empty/unset) against the
# skills available in the source. Errors out (to stderr, exit non-zero) on
# unknown names. Prints the resolved selection, one name per line, sorted
# and deduped.
resolve_selection() {
  # $1 = requested value (may be empty string)
  # $2 = available listing ("name\tpath" lines)
  local requested="$1" available="$2"
  local lower
  lower="$(printf '%s' "$requested" | tr '[:upper:]' '[:lower:]' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"

  if [[ "$lower" == "all" ]]; then
    available_names "$available"
    return 0
  fi

  local names
  names="$(printf '%s' "$requested" | tr ',' '\n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | grep -v '^$' | sort -u || true)"

  local avail_names
  avail_names="$(available_names "$available")"

  local unknown
  unknown="$(comm -23 <(printf '%s\n' "$names") <(printf '%s\n' "$avail_names") || true)"

  if [[ -n "$unknown" ]]; then
    local unknown_csv avail_csv
    unknown_csv="$(printf '%s\n' "$unknown" | paste -sd, - | sed 's/,/, /g')"
    if [[ -z "$avail_names" ]]; then
      avail_csv="(none)"
    else
      avail_csv="$(printf '%s\n' "$avail_names" | paste -sd, - | sed 's/,/, /g')"
    fi
    err "unknown skill(s): ${unknown_csv}. Available: ${avail_csv}"
  fi

  printf '%s\n' "$names"
}

# Wipe-and-replace copy of a skill directory into <target>/.claude/skills/<name>/
copy_skill() {
  # $1 = source skill dir, $2 = skills root, $3 = name
  local src="$1" skills_root="$2" name="$3"
  local dest="${skills_root}/${name}"
  rm -rf "${dest:?}"
  mkdir -p "$dest"
  cp -r "${src}/." "${dest}/"
}

# Lines that should be present in .claude/.gitignore: one for the manifest
# itself, plus one per currently-installed skill folder.
# $1 = newline-separated skill names (may be empty/blank)
gitignore_lines_for() {
  printf 'skills/%s\n' "$MANIFEST_NAME"
  printf '%s\n' "$1" | while IFS= read -r name; do
    [[ -z "$name" ]] && continue
    printf 'skills/%s/\n' "$name"
  done
}

# Ensure .claude/.gitignore ignores the manifest and each given skill's
# folder individually (not the whole skills/ directory), so a project can
# track its own custom skills alongside synced ones.
#
# Migrates away from the old blanket "skills/" line if present. Appends any
# missing lines without reordering existing content; never duplicates a line.
ensure_gitignore() {
  # $1 = target, $2 = newline-separated skill names
  local target="$1" names="$2"
  local gi_dir="${target}/.claude"
  local gi_path="${gi_dir}/.gitignore"
  mkdir -p "$gi_dir"

  local existing=""
  [[ -f "$gi_path" ]] && existing="$(cat "$gi_path")"

  # Migration: drop the old blanket "skills/" line.
  local filtered
  filtered="$(printf '%s\n' "$existing" | grep -vxF "$OLD_GITIGNORE_LINE" || true)"

  local wanted line
  local -a to_append=()
  wanted="$(gitignore_lines_for "$names")"
  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    if ! grep -qxF "$line" <<<"$filtered"; then
      to_append+=("$line")
    fi
  done <<<"$wanted"

  if [[ "$filtered" == "$existing" && "${#to_append[@]}" -eq 0 ]]; then
    return 0
  fi

  {
    if [[ -n "$filtered" ]]; then
      printf '%s\n' "$filtered"
    fi
    for line in "${to_append[@]}"; do
      printf '%s\n' "$line"
    done
  } >"$gi_path"
}

# Remove the gitignore line for each given skill name ("skills/<name>/"),
# preserving all other lines and their order. No-op if the file is absent.
remove_gitignore_lines() {
  # $1 = target, $2 = newline-separated skill names to remove
  local target="$1" names="$2"
  local gi_path="${target}/.claude/.gitignore"
  [[ -f "$gi_path" ]] || return 0

  local -a args=()
  local name
  while IFS= read -r name; do
    [[ -z "$name" ]] && continue
    args+=(-e "skills/${name}/")
  done <<<"$names"
  [[ "${#args[@]}" -eq 0 ]] && return 0

  local tmp
  tmp="$(mktemp "${gi_path}.XXXXXX")"
  grep -vxF "${args[@]}" "$gi_path" >"$tmp" || true
  mv "$tmp" "$gi_path"
}

# Read the manifest as raw JSON text, or empty string if absent.
load_manifest() {
  # $1 = target
  local path
  path="$(manifest_path "$1")"
  if [[ -f "$path" ]]; then
    cat "$path"
  fi
}

# Write manifest JSON (read from stdin) with 2-space indent + trailing newline.
save_manifest() {
  # $1 = target, reads JSON from stdin
  local target="$1"
  local s_dir path
  s_dir="$(skills_dir "$target")"
  mkdir -p "$s_dir"
  path="$(manifest_path "$target")"
  jq '.' >"${path}.tmp"
  mv "${path}.tmp" "$path"
}

# ---------------------------------------------------------------------------
# Source acquisition
# ---------------------------------------------------------------------------

# Fetch and extract a GitHub repo tarball. Sets globals SRC_ROOT and
# CLEANUP_DIR (caller is responsible for relying on the EXIT trap to clean up
# CLEANUP_DIR).
fetch_github() {
  # $1 = repo (owner/name), $2 = ref, $3 = token (may be empty)
  local repo="$1" ref="$2" token="$3"
  local url tmpdir tarball_path extract_dir http_code

  tmpdir="$(mktemp -d)"
  CLEANUP_DIR="$tmpdir"

  tarball_path="${tmpdir}/repo.tar.gz"

  if [[ -n "$token" ]]; then
    url="https://api.github.com/repos/${repo}/tarball/${ref}"
    http_code="$(curl -sS -L -w '%{http_code}' -o "$tarball_path" \
      -H "Authorization: Bearer ${token}" \
      -H "User-Agent: skills-sync" \
      "$url")"
  else
    url="https://codeload.github.com/${repo}/tar.gz/${ref}"
    http_code="$(curl -sS -L -w '%{http_code}' -o "$tarball_path" \
      -H "User-Agent: skills-sync" \
      "$url")"
  fi

  if [[ "$http_code" != "200" ]]; then
    local hint=""
    if [[ "$http_code" == "404" ]]; then
      hint=" (check repo/ref/token — private repos 404 without a token)"
    fi
    err "HTTP ${http_code} fetching ${url}${hint}"
  fi

  extract_dir="${tmpdir}/extracted"
  mkdir -p "$extract_dir"
  tar -xzf "$tarball_path" -C "$extract_dir"

  # The tarball contains a single root folder (owner-repo-<sha>/) — descend
  # into it before scanning, if that's the layout.
  local entries entry_count first_entry
  entry_count=0
  first_entry=""
  for entry in "$extract_dir"/*; do
    entry_count=$((entry_count + 1))
    first_entry="$entry"
  done

  if [[ "$entry_count" -eq 1 && -d "$first_entry" ]]; then
    SRC_ROOT="$first_entry"
  else
    SRC_ROOT="$extract_dir"
  fi
}

# Resolve and validate a local source path. Sets global SRC_ROOT.
acquire_local() {
  # $1 = path, $2 = target
  local path="$1" target="$2"
  local src target_skills

  if [[ ! -e "$path" ]]; then
    err "local source path does not exist or is not a directory: $(realpath -m -- "$path")"
  fi

  src="$(realpath -- "$path")"

  if [[ ! -d "$src" ]]; then
    err "local source path does not exist or is not a directory: $src"
  fi

  # Self-copy guard: the resolved source directory must not be the same as,
  # or nested inside, the target's .claude/skills/.
  target_skills="$(realpath -m -- "$(skills_dir "$target")")"
  if [[ "$src" == "$target_skills" || "$src" == "$target_skills"/* ]]; then
    err "source path '$src' is inside the target's .claude/skills/ — refusing to self-copy"
  fi

  SRC_ROOT="$src"
}

# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

cmd_install() {
  local repo="" path="" ref="" skills="all" target="." token=""
  local have_repo=0 have_path=0 have_ref=0

  while [[ $# -gt 0 ]]; do
    case "$1" in
    --repo)
      repo="$2"
      have_repo=1
      shift 2
      ;;
    --path)
      path="$2"
      have_path=1
      shift 2
      ;;
    --ref)
      ref="$2"
      have_ref=1
      shift 2
      ;;
    --skills)
      skills="$2"
      shift 2
      ;;
    --target)
      target="$2"
      shift 2
      ;;
    --token)
      token="$2"
      shift 2
      ;;
    *) err "unknown argument: $1" ;;
    esac
  done

  if [[ "$have_repo" -eq 1 && "$have_path" -eq 1 ]]; then
    err "exactly one of --repo or --path is required (both given)"
  fi
  if [[ "$have_repo" -eq 0 && "$have_path" -eq 0 ]]; then
    err "exactly one of --repo or --path is required"
  fi
  if [[ "$have_path" -eq 1 && "$have_ref" -eq 1 ]]; then
    err "--ref is only valid with --repo"
  fi

  local available
  if [[ "$have_repo" -eq 1 ]]; then
    if [[ -z "$ref" ]]; then
      ref="main"
    fi
    fetch_github "$repo" "$ref" "$token"
    available="$(detect_skills "$SRC_ROOT")"
    if [[ -z "$available" ]]; then
      err "no skills (SKILL.md) found in ${repo}@${ref}"
    fi
  else
    acquire_local "$path" "$target"
    available="$(detect_skills "$SRC_ROOT")"
    if [[ -z "$available" ]]; then
      err "no skills (SKILL.md) found under '$SRC_ROOT'"
    fi
  fi

  local selection
  selection="$(resolve_selection "$skills" "$available")"
  if [[ -z "$selection" ]]; then
    err "no skills selected"
  fi

  local s_dir
  s_dir="$(skills_dir "$target")"
  mkdir -p "$s_dir"

  local name src_path
  while IFS= read -r name; do
    [[ -z "$name" ]] && continue
    src_path="$(lookup_skill_path "$available" "$name")"
    copy_skill "$src_path" "$s_dir" "$name"
  done <<<"$selection"

  local skills_json updated
  updated="$(now_iso)"
  skills_json="$(printf '%s\n' "$selection" | grep -v '^$' | jq -R . | jq -s .)"

  if [[ "$have_repo" -eq 1 ]]; then
    jq -n \
      --arg source "github" \
      --arg repo "$repo" \
      --arg ref "$ref" \
      --arg updated "$updated" \
      --argjson skills "$skills_json" \
      '{source: $source, repo: $repo, ref: $ref, updated: $updated, skills: $skills}' |
      save_manifest "$target"
  else
    jq -n \
      --arg source "local" \
      --arg path "$SRC_ROOT" \
      --arg updated "$updated" \
      --argjson skills "$skills_json" \
      '{source: $source, path: $path, updated: $updated, skills: $skills}' |
      save_manifest "$target"
  fi

  ensure_gitignore "$target" "$selection"

  local count joined
  count="$(printf '%s\n' "$selection" | grep -c . || true)"
  joined="$(printf '%s\n' "$selection" | grep -v '^$' | paste -sd, - | sed 's/,/, /g')"
  echo "Installed ${count} skill(s): ${joined}"
}

cmd_update_or_add() {
  # $1 = "update" or "add" (controls whether --skills is required)
  local mode="$1"
  shift

  local skills="" target="." token="" have_skills=0

  while [[ $# -gt 0 ]]; do
    case "$1" in
    --skills)
      skills="$2"
      have_skills=1
      shift 2
      ;;
    --target)
      target="$2"
      shift 2
      ;;
    --token)
      token="$2"
      shift 2
      ;;
    *) err "unknown argument: $1" ;;
    esac
  done

  if [[ "$mode" == "add" && ("$have_skills" -eq 0 || -z "$skills") ]]; then
    err "--skills is required for 'add'"
  fi

  local manifest_json
  manifest_json="$(load_manifest "$target")"
  if [[ -z "$manifest_json" ]]; then
    err "no manifest found — run install first"
  fi

  local source
  source="$(jq -r '.source // empty' <<<"$manifest_json")"
  if [[ -z "$source" ]]; then
    if jq -e 'has("repo")' <<<"$manifest_json" >/dev/null; then
      source="github"
    else
      source="local"
    fi
  fi

  local available
  if [[ "$source" == "github" ]]; then
    local repo ref
    repo="$(jq -r '.repo' <<<"$manifest_json")"
    ref="$(jq -r '.ref // "main"' <<<"$manifest_json")"
    fetch_github "$repo" "$ref" "$token"
    available="$(detect_skills "$SRC_ROOT")"
  elif [[ "$source" == "local" ]]; then
    local src_path
    src_path="$(jq -r '.path' <<<"$manifest_json")"
    if [[ ! -d "$src_path" ]]; then
      err "local source path no longer exists: ${src_path}. If the folder moved, re-run 'install --path' instead."
    fi
    SRC_ROOT="$src_path"
    available="$(detect_skills "$SRC_ROOT")"
  else
    err "unknown manifest source: '${source}'"
  fi

  local selection
  if [[ "$have_skills" -eq 1 && -n "$skills" ]]; then
    selection="$(resolve_selection "$skills" "$available")"
  else
    # manifest skills ∩ available
    local manifest_skills avail_names
    manifest_skills="$(jq -r '.skills[]?' <<<"$manifest_json" | sort -u)"
    avail_names="$(available_names "$available")"
    selection="$(comm -12 <(printf '%s\n' "$manifest_skills") <(printf '%s\n' "$avail_names") || true)"
  fi

  local s_dir
  s_dir="$(skills_dir "$target")"
  mkdir -p "$s_dir"

  local name src_skill_path
  while IFS= read -r name; do
    [[ -z "$name" ]] && continue
    src_skill_path="$(lookup_skill_path "$available" "$name")"
    copy_skill "$src_skill_path" "$s_dir" "$name"
  done <<<"$selection"

  # New manifest skills = old skills ∪ selection, sorted + deduped
  local manifest_skills union_skills union_json updated
  manifest_skills="$(jq -r '.skills[]?' <<<"$manifest_json" | sort -u)"
  union_skills="$(printf '%s\n%s\n' "$manifest_skills" "$selection" | grep -v '^$' | sort -u)"
  union_json="$(printf '%s\n' "$union_skills" | grep -v '^$' | jq -R . | jq -s .)"
  updated="$(now_iso)"

  jq --arg updated "$updated" --argjson skills "$union_json" \
    '.skills = $skills | .updated = $updated' \
    <<<"$manifest_json" | save_manifest "$target"

  ensure_gitignore "$target" "$union_skills"

  local count joined
  count="$(printf '%s\n' "$selection" | grep -c . || true)"
  if [[ "$count" -eq 0 ]]; then
    joined="(none)"
  else
    joined="$(printf '%s\n' "$selection" | grep -v '^$' | paste -sd, - | sed 's/,/, /g')"
  fi

  echo "Updated ${count} skill(s): ${joined}"
}

cmd_remove() {
  local skills="" target="." have_skills=0

  while [[ $# -gt 0 ]]; do
    case "$1" in
    --skills)
      skills="$2"
      have_skills=1
      shift 2
      ;;
    --target)
      target="$2"
      shift 2
      ;;
    *) err "unknown argument: $1" ;;
    esac
  done

  local manifest_json
  manifest_json="$(load_manifest "$target")"
  if [[ -z "$manifest_json" ]]; then
    err "no manifest found — run install first"
  fi

  if [[ "$have_skills" -eq 0 ]]; then
    err "--skills is required for 'remove'"
  fi

  local names
  names="$(printf '%s' "$skills" | tr ',' '\n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | grep -v '^$' | sort -u || true)"
  if [[ -z "$names" ]]; then
    err "--skills is required for 'remove'"
  fi

  local s_dir
  s_dir="$(skills_dir "$target")"

  local removed=()
  local name skill_path
  while IFS= read -r name; do
    [[ -z "$name" ]] && continue
    skill_path="${s_dir}/${name}"
    if [[ -e "$skill_path" ]]; then
      rm -rf "${skill_path:?}"
    fi
    if jq -e --arg n "$name" '.skills // [] | index($n) != null' <<<"$manifest_json" >/dev/null; then
      removed+=("$name")
    fi
  done <<<"$names"

  # Remove the named skills from the manifest's skills array (regardless of
  # whether they were present, mirrors the reference: removal from manifest
  # only happens if present, but recomputing via set difference covers it).
  local names_json updated
  names_json="$(printf '%s\n' "$names" | grep -v '^$' | jq -R . | jq -s .)"
  updated="$(now_iso)"

  jq --arg updated "$updated" --argjson remove "$names_json" \
    '.skills = ((.skills // []) - $remove | sort) | .updated = $updated' \
    <<<"$manifest_json" | save_manifest "$target"

  remove_gitignore_lines "$target" "$names"

  local joined
  if [[ "${#removed[@]}" -eq 0 ]]; then
    joined="(none found)"
  else
    joined="$(printf '%s\n' "${removed[@]}" | paste -sd, - | sed 's/,/, /g')"
  fi
  echo "Removed ${#removed[@]} skill(s): ${joined}"
}

cmd_list() {
  local target="."

  while [[ $# -gt 0 ]]; do
    case "$1" in
    --target)
      target="$2"
      shift 2
      ;;
    *) err "unknown argument: $1" ;;
    esac
  done

  local manifest_json
  manifest_json="$(load_manifest "$target")"
  if [[ -z "$manifest_json" ]]; then
    err "no manifest found — run install first"
  fi

  local source
  source="$(jq -r '.source // empty' <<<"$manifest_json")"
  if [[ -z "$source" ]]; then
    if jq -e 'has("repo")' <<<"$manifest_json" >/dev/null; then
      source="github"
    else
      source="local"
    fi
  fi

  local label updated
  updated="$(jq -r '.updated // "unknown"' <<<"$manifest_json")"
  if [[ "$source" == "github" ]]; then
    local repo ref
    repo="$(jq -r '.repo' <<<"$manifest_json")"
    ref="$(jq -r '.ref // "main"' <<<"$manifest_json")"
    label="${repo}@${ref}"
  else
    label="$(jq -r '.path // "(unknown path)"' <<<"$manifest_json")"
  fi

  echo "${label} (updated ${updated})"
  jq -r '.skills[]?' <<<"$manifest_json" | while IFS= read -r name; do
    echo "  ${name}"
  done
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

CLEANUP_DIR=""
cleanup() {
  if [[ -n "$CLEANUP_DIR" ]]; then
    rm -rf "${CLEANUP_DIR:?}"
  fi
}
trap cleanup EXIT

main() {
  if [[ $# -lt 1 ]]; then
    err "usage: skills-sync.sh <install|update|add|remove|list> [options]"
  fi

  local command="$1"
  shift

  case "$command" in
  install) cmd_install "$@" ;;
  update) cmd_update_or_add "update" "$@" ;;
  add) cmd_update_or_add "add" "$@" ;;
  remove) cmd_remove "$@" ;;
  list) cmd_list "$@" ;;
  *) err "unknown command: $command (expected install|update|add|remove|list)" ;;
  esac
}

main "$@"
