#!/usr/bin/env bash
# Tests for loop/gate.sh — the git-fact predicate the watcher uses to decide
# bb-done and re-armable. Deterministic: predicate cases pin a full SHA and an
# explicit STEERING_PATH; degraded-input and ordering cases run inside throwaway
# git repos so they never depend on this repo's mutable .rn/ layout.
#
# Run: ./loop/gate.test.sh   (from anywhere)
# Exit non-zero if any case fails.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GATE="$SCRIPT_DIR/gate.sh"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# Full SHA of the real /rn:bb commit; .rn/loop/steering.md is Status: paused there.
BB_REF="668bbf6069c6264546a17e985b774dcdfcb160fa"
# Predicate cases use an explicit path so they test predicate logic, not the
# resolution heuristic, independent of how many sessions exist.
LOOP_PATH=".rn/loop/steering.md"

pass=0
fail=0

# ok NAME EXPECTED_EXIT -- CMD...
# Runs CMD (allowed to exit non-zero) and compares its exit code to EXPECTED_EXIT.
ok() {
  local name="$1" expected="$2"
  shift 3 # name, expected, and the literal "--"
  local got=0
  "$@" >/dev/null 2>&1 || got=$?
  if [[ "$got" -eq "$expected" ]]; then
    printf 'PASS  %s (exit %s)\n' "$name" "$got"
    pass=$((pass + 1))
  else
    printf 'FAIL  %s (expected exit %s, got %s)\n' "$name" "$expected" "$got"
    fail=$((fail + 1))
  fi
}

# ok_out NAME EXPECTED_STDOUT -- CMD...
ok_out() {
  local name="$1" expected="$2"
  shift 3
  local got
  got="$("$@" 2>/dev/null || true)"
  if [[ "$got" == "$expected" ]]; then
    printf 'PASS  %s (%q)\n' "$name" "$got"
    pass=$((pass + 1))
  else
    printf 'FAIL  %s (expected %q, got %q)\n' "$name" "$expected" "$got"
    fail=$((fail + 1))
  fi
}

# --------------------------------------------------------------------------
# Predicate logic — explicit STEERING_PATH, pinned fixture SHA.
# --------------------------------------------------------------------------
export STEERING_PATH="$LOOP_PATH"

# Given the paused fixture (668bbf6...) and a clean tree
# When bb_done $BB_REF → Then true (exit 0)
ok "bb_done @paused-fixture (clean tree) -> true" 0 -- "$GATE" bb_done "$BB_REF"

# Given current HEAD (loop Status: not suspended)
# When bb_done HEAD → Then false (exit 1)
ok "bb_done @HEAD (not suspended) -> false" 1 -- "$GATE" bb_done HEAD

# Given the paused fixture but a DIRTY tree (temp untracked file)
# When bb_done $BB_REF → Then false (tree not clean), then remove → true again.
TMP_DIRTY="$REPO_ROOT/loop/.gate-dirty-probe.tmp"
: >"$TMP_DIRTY"
ok "bb_done @paused-fixture (dirty tree) -> false" 1 -- "$GATE" bb_done "$BB_REF"
rm -f "$TMP_DIRTY"
ok "bb_done @paused-fixture (tree clean again) -> true" 0 -- "$GATE" bb_done "$BB_REF"

# Given current HEAD (not suspended) → When rearmed HEAD → Then true (exit 0)
ok "rearmed @HEAD (not suspended) -> true" 0 -- "$GATE" rearmed HEAD

# Given the paused fixture → When rearmed $BB_REF → Then false (exit 1)
ok "rearmed @paused-fixture (paused) -> false" 1 -- "$GATE" rearmed "$BB_REF"

# --------------------------------------------------------------------------
# Error / degraded input — prove fail-closed (no 128, no true on garbage).
# --------------------------------------------------------------------------

# Given a nonexistent ref → When bb_done → Then false (exit 1), not 128.
ok "bb_done @bad-ref -> false (not 128)" 1 -- "$GATE" bb_done deadbeefdeadbeef

# Given a nonexistent ref → When rearmed → Then false (exit 1), not 128/true.
ok "rearmed @bad-ref -> false (not 128)" 1 -- "$GATE" rearmed deadbeefdeadbeef

# Extra positional args → usage error (exit 2), not silent misparse.
ok "bb_done extra-arg -> usage error (exit 2)" 2 -- "$GATE" bb_done HEAD extra
ok "rearmed extra-arg -> usage error (exit 2)" 2 -- "$GATE" rearmed HEAD extra

unset STEERING_PATH

# --------------------------------------------------------------------------
# Throwaway repo: garbage Status → rearmed false (fail-closed).
# --------------------------------------------------------------------------
TMP_GARBAGE="$(mktemp -d)"
# Single trap cleaning both temp repos.
TMP_ORDER=""
cleanup() { rm -rf "$TMP_GARBAGE" "$TMP_ORDER" "$TMP_DIRTY"; }
trap cleanup EXIT

(
  cd "$TMP_GARBAGE"
  git init -q
  git config user.email t@t && git config user.name t
  mkdir -p .rn/x
  cat >.rn/x/steering.md <<'EOF'
# State

- **Status**: frobnicated
- **Date**: YYYY-MM-DD
EOF
  git add -A && git commit -qm garbage
)
# Given a committed garbage Status → When rearmed → Then false (exit 1).
# gate resolves the repo root from CWD, so run with the temp repo as CWD and
# STEERING_PATH pointing at the repo-root-relative path inside it.
ok_garbage() {
  local got=0
  ( cd "$TMP_GARBAGE" && STEERING_PATH=".rn/x/steering.md" "$GATE" rearmed HEAD ) >/dev/null 2>&1 || got=$?
  if [[ "$got" -eq 1 ]]; then
    printf 'PASS  %s (exit %s)\n' "rearmed @garbage-status (CWD=temp) -> false" "$got"
    pass=$((pass + 1))
  else
    printf 'FAIL  %s (expected exit 1, got %s)\n' "rearmed @garbage-status (CWD=temp) -> false" "$got"
    fail=$((fail + 1))
  fi
}
ok_garbage

# --------------------------------------------------------------------------
# Throwaway repo: steering_path ordering — paused beats most-recent.
# Two committed sessions: OLDER one paused, NEWER one not suspended.
# rn's rule → steering_path resolves to the PAUSED (older) one.
# --------------------------------------------------------------------------
TMP_ORDER="$(mktemp -d)"
(
  cd "$TMP_ORDER"
  git init -q
  git config user.email t@t && git config user.name t

  mkdir -p .rn/older .rn/newer
  cat >.rn/older/steering.md <<'EOF'
# State

- **Status**: paused
EOF
  git add -A && GIT_COMMITTER_DATE="2020-01-01T00:00:00" git commit -q \
    --date="2020-01-01T00:00:00" -m "older paused session"

  cat >.rn/newer/steering.md <<'EOF'
# State

- **Status**: not suspended
EOF
  git add -A && GIT_COMMITTER_DATE="2025-01-01T00:00:00" git commit -q \
    --date="2025-01-01T00:00:00" -m "newer not-suspended session"
)
# Given an OLDER paused session and a NEWER not-suspended one
# When steering_path → Then resolves to the PAUSED (older) one.
ok_order() {
  local got
  got="$( cd "$TMP_ORDER" && "$GATE" steering_path 2>/dev/null || true )"
  if [[ "$got" == ".rn/older/steering.md" ]]; then
    printf 'PASS  %s (%q)\n' "steering_path -> paused wins over most-recent" "$got"
    pass=$((pass + 1))
  else
    printf 'FAIL  %s (expected %q, got %q)\n' \
      "steering_path -> paused wins over most-recent" ".rn/older/steering.md" "$got"
    fail=$((fail + 1))
  fi
}
ok_order

printf '\n%d passed, %d failed\n' "$pass" "$fail"
[[ "$fail" -eq 0 ]]
