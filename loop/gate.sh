#!/usr/bin/env bash
# gate.sh — git-fact predicate for the rn suspend/resume loop watcher.
#
# Decides, purely from committed git facts (never by scraping the screen),
# whether /rn:bb has truly finished (bb_done) and whether /rn:hi has reset the
# session so the watcher may re-fire (rearmed).
#
# bb_done  := working tree is clean AND ref's steering.md State Status == paused
# rearmed  := ref's steering.md State Status == "not suspended" (reset by /rn:hi)
#             A POSITIVE match — empty/unknown/paused/malformed all fail closed
#             (rearmed false), so the watcher never re-arms on garbage.
#
# Session selection (which steering.md to gate):
#   The unattended watcher MUST set STEERING_PATH (a repo-root-relative path,
#   e.g. .rn/loop/steering.md) so it gates the EXACT session it drives. When
#   STEERING_PATH is unset, steering_path()'s glob is a single-session
#   (assumption A6) convenience fallback only — under multiple coexisting
#   sessions no heuristic can know which one the watcher drives, so the glob
#   may mis-target (it warns on stderr when >1 session is present).
#
# TOCTOU note for the watcher: bb_done samples the live tree and the committed
# Status at separate instants and cannot hold a lock across the watcher's next
# action. Every degraded/racing input fails toward false/2 (never a spurious
# true), but the watcher MUST re-check bb_done immediately before sending
# /clear — treat its result as a point-in-time sample, not a held guarantee.
#
# CLI usage (for the watcher). Tri-state exit code:
#     0 = true, 1 = false, 2 = usage / resolution error.
#   gate.sh bb_done [ref]       # default ref: HEAD; at most one positional
#   gate.sh rearmed [ref]       # default ref: HEAD; at most one positional
#   gate.sh steering_path       # prints resolved .rn/<session>/steering.md
#   gate.sh status_at <ref> <path>  # prints the Status value at <ref> (debug)
#
# Environment:
#   STEERING_PATH  repo-root-relative steering.md path; overrides the glob.
#
# Or source it and call the functions directly.
set -euo pipefail

# The two marker values, each defined exactly once.
# PAUSED_MARKER         — written by /rn:bb to mean "suspended".
# NOT_SUSPENDED_MARKER  — written by /rn:hi to mean "re-armed".
readonly PAUSED_MARKER="paused"
readonly NOT_SUSPENDED_MARKER="not suspended"

# Resolve to the repo root so globs and `git` work regardless of caller CWD.
_repo_root() {
  git rev-parse --show-toplevel
}

# steering_path: locate the single active session's steering file.
# Globs .rn/*/steering.md in the working tree and mirrors rn's documented rule:
# rn's bb/hi prefer a session whose State shows `Status: paused` at the ref,
# ELSE the most recently committed. So here: prefer Status: paused first; among
# same paused-status, the most-recently-committed wins.
# NOTE: under multiple coexisting sessions neither heuristic can know which one
# the watcher drives — that is what STEERING_PATH is for.
# Prints the path relative to the repo root.
steering_path() {
  local root
  root="$(_repo_root)"

  local best="" best_ts=-1 best_paused=-1 n=0
  local f rel ts paused
  # nullglob (in a subshell-free, save/restore manner) so a no-match glob is
  # empty rather than the literal pattern; -e guard kept as belt-and-suspenders.
  local had_nullglob=0
  shopt -q nullglob && had_nullglob=1
  shopt -s nullglob
  for f in "$root"/.rn/*/steering.md; do
    [[ -e "$f" ]] || continue
    n=$((n + 1))
    rel="${f#"$root"/}"
    ts="$(cd "$root" && git log -1 --format=%ct -- "$rel" 2>/dev/null || echo 0)"
    ts="${ts:-0}"
    paused=0
    if [[ "$(_status_at HEAD "$rel" 2>/dev/null || true)" == "$PAUSED_MARKER" ]]; then
      paused=1
    fi
    # Prefer paused first; among equal paused-status, the newer commit wins.
    if (( paused > best_paused )) || { (( paused == best_paused )) && (( ts > best_ts )); }; then
      best="$rel"
      best_ts="$ts"
      best_paused="$paused"
    fi
  done
  (( had_nullglob )) || shopt -u nullglob

  if [[ -z "$best" ]]; then
    echo "gate.sh: no .rn/*/steering.md found" >&2
    return 2
  fi
  # Ambiguous fallback: the glob cannot know which session the watcher drives.
  if (( n > 1 )); then
    echo "gate.sh: WARNING: $n sessions found and STEERING_PATH unset;" \
         "glob may mis-target — set STEERING_PATH to the driven session." >&2
  fi
  printf '%s\n' "$best"
}

# _resolve_steering: STEERING_PATH override (watcher's deterministic choice)
# wins; otherwise fall back to the steering_path glob heuristic.
_resolve_steering() {
  if [[ -n "${STEERING_PATH:-}" ]]; then
    printf '%s\n' "$STEERING_PATH"
  else
    steering_path
  fi
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
# ref is exactly `paused`. Default ref: HEAD.
# A bad/unreadable ref yields empty status → false (1), never an abort (128).
bb_done() {
  local ref="${1:-HEAD}"
  local path status
  path="$(_resolve_steering)" || return 2
  _tree_clean || return 1
  status="$(_status_at "$ref" "$path" 2>/dev/null || true)"
  [[ "$status" == "$PAUSED_MARKER" ]]
}

# rearmed [ref]: true ONLY when the steering Status at ref is exactly
# `not suspended` (the /rn:hi reset signal). Fails CLOSED — empty/unknown/
# paused/malformed → false (1). Does NOT depend on tree cleanliness.
# A bad/unreadable ref yields empty status → false (1), never an abort (128).
rearmed() {
  local ref="${1:-HEAD}"
  local path status
  path="$(_resolve_steering)" || return 2
  status="$(_status_at "$ref" "$path" 2>/dev/null || true)"
  [[ "$status" == "$NOT_SUSPENDED_MARKER" ]]
}

# CLI dispatch — only when executed, not when sourced.
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  cmd="${1:-}"
  shift || true
  case "$cmd" in
    bb_done)
      [[ $# -le 1 ]] || { echo "usage: gate.sh bb_done [ref]" >&2; exit 2; }
      bb_done "$@" ;;
    rearmed)
      [[ $# -le 1 ]] || { echo "usage: gate.sh rearmed [ref]" >&2; exit 2; }
      rearmed "$@" ;;
    steering_path)
      [[ $# -eq 0 ]] || { echo "usage: gate.sh steering_path" >&2; exit 2; }
      steering_path ;;
    status_at)
      # Debug helper, NOT part of the 0/1/2 predicate contract: it prints the
      # Status value and passes git's read result through as empty on a bad ref.
      [[ $# -eq 2 ]] || { echo "usage: gate.sh status_at <ref> <path>" >&2; exit 2; }
      _status_at "$1" "$2" ;;
    *)
      echo "usage: gate.sh {bb_done [ref]|rearmed [ref]|steering_path|status_at <ref> <path>}" >&2
      echo "exit: 0=true 1=false 2=usage/resolution error" >&2
      exit 2 ;;
  esac
fi
