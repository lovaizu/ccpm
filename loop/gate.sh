#!/usr/bin/env bash
# gate.sh — git-fact predicate for the rn suspend/resume loop watcher.
#
# Decides, purely from committed git facts (never by scraping the screen),
# whether /rn:bb has truly finished (bb_done) and whether /rn:hi has reset the
# session so the watcher may re-fire (rearmed).
#
# bb_done  := working tree is clean AND HEAD(ref)'s steering.md State Status == paused
# rearmed  := ref's steering.md State Status != paused   (reset by /rn:hi)
#
# CLI usage (for the watcher), exit code 0 = true, 1 = false:
#   gate.sh bb_done [ref]       # default ref: HEAD
#   gate.sh rearmed [ref]       # default ref: HEAD
#   gate.sh steering_path       # prints resolved .rn/<session>/steering.md
#   gate.sh status_at <ref>     # prints the Status value at <ref> (debug)
#
# Or source it and call the functions directly.
set -euo pipefail

# The one marker value that means "suspended by /rn:bb". Defined once.
readonly PAUSED_MARKER="paused"

# Resolve to the repo root so globs and `git` work regardless of caller CWD.
_repo_root() {
  git rev-parse --show-toplevel
}

# steering_path: locate the single active session's steering file.
# Globs .rn/*/steering.md in the working tree. If several exist, prefer the
# most recently committed (freshest activity == the active session). Among
# equally-fresh, a Status: paused at HEAD breaks the tie.
# Prints the path relative to the repo root.
steering_path() {
  local root
  root="$(_repo_root)"

  local best="" best_ts=-1 best_paused=0
  local f rel ts paused
  for f in "$root"/.rn/*/steering.md; do
    [[ -e "$f" ]] || continue
    rel="${f#"$root"/}"
    ts="$(cd "$root" && git log -1 --format=%ct -- "$rel" 2>/dev/null || echo 0)"
    ts="${ts:-0}"
    paused=0
    if [[ "$(_status_at HEAD "$rel" 2>/dev/null || true)" == "$PAUSED_MARKER" ]]; then
      paused=1
    fi
    if (( ts > best_ts )) || { (( ts == best_ts )) && (( paused > best_paused )); }; then
      best="$rel"
      best_ts="$ts"
      best_paused="$paused"
    fi
  done

  if [[ -z "$best" ]]; then
    echo "gate.sh: no .rn/*/steering.md found" >&2
    return 2
  fi
  printf '%s\n' "$best"
}

# _status_at REF PATH: extract the Status value from the `# State` section of
# PATH as committed at REF. Reads from git (a committed fact), not the working
# file. Parses only the `- **Status**:` line *within* the `# State` section so
# it never matches a stray "Status" elsewhere. Prints the trimmed value.
_status_at() {
  local ref="$1" path="$2"
  git show "${ref}:${path}" 2>/dev/null | awk '
    /^# State[[:space:]]*$/ { in_state = 1; next }
    /^# / { in_state = 0 }
    in_state && /^- \*\*Status\*\*:/ {
      sub(/^- \*\*Status\*\*:[[:space:]]*/, "")
      sub(/[[:space:]]+$/, "")
      print
      exit
    }
  '
}

# _tree_clean: true (0) when the current working tree has no changes.
# This half of bb_done is about the LIVE tree, independent of any ref.
_tree_clean() {
  [[ -z "$(git -C "$(_repo_root)" status --porcelain)" ]]
}

# bb_done [ref]: true when the working tree is clean AND the steering Status at
# ref is `paused`. Default ref: HEAD.
bb_done() {
  local ref="${1:-HEAD}"
  local path status
  path="$(steering_path)" || return 2
  _tree_clean || return 1
  status="$(_status_at "$ref" "$path")"
  [[ "$status" == "$PAUSED_MARKER" ]]
}

# rearmed [ref]: true when the steering Status at ref is no longer `paused`
# (reset by /rn:hi). Does NOT depend on tree cleanliness. Default ref: HEAD.
rearmed() {
  local ref="${1:-HEAD}"
  local path status
  path="$(steering_path)" || return 2
  status="$(_status_at "$ref" "$path")"
  [[ "$status" != "$PAUSED_MARKER" ]]
}

# CLI dispatch — only when executed, not when sourced.
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  cmd="${1:-}"
  shift || true
  case "$cmd" in
    bb_done)      bb_done "$@" ;;
    rearmed)      rearmed "$@" ;;
    steering_path) steering_path ;;
    status_at)
      [[ $# -eq 2 ]] || { echo "usage: gate.sh status_at <ref> <path>" >&2; exit 2; }
      _status_at "$1" "$2" ;;
    *)
      echo "usage: gate.sh {bb_done|rearmed [ref]|steering_path|status_at <ref> <path>}" >&2
      exit 2 ;;
  esac
fi
