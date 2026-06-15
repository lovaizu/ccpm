#!/usr/bin/env bash
# Tests for loop/gate.sh — the git-fact predicate the watcher uses to decide
# bb-done and re-armable. Written test-first.
#
# Run: ./loop/gate.test.sh   (from the repo root / worktree root)
# Exit non-zero if any case fails.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GATE="$SCRIPT_DIR/gate.sh"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# Real fixture refs in this repo's history (see task brief):
#   668bbf6 — real /rn:bb result, State Status: paused
#   HEAD    — real /rn:hi reset,  State Status: not suspended
BB_REF="668bbf6"

pass=0
fail=0

# ok NAME EXPECTED_EXIT  -- CMD...
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

# Given the real fixture ref 668bbf6 (Status: paused) and a clean tree
# When bb_done 668bbf6 → Then true (exit 0)
ok "bb_done @paused-fixture (clean tree) -> true" 0 -- "$GATE" bb_done "$BB_REF"

# Given current HEAD (Status: not suspended)
# When bb_done HEAD → Then false (exit 1)
ok "bb_done @HEAD (not suspended) -> false" 1 -- "$GATE" bb_done HEAD

# Given a paused fixture but a DIRTY tree: create a temp untracked file
# When bb_done 668bbf6 → Then false (tree not clean), then remove and confirm true again.
TMP_DIRTY="$REPO_ROOT/loop/.gate-dirty-probe.tmp"
trap 'rm -f "$TMP_DIRTY"' EXIT
: >"$TMP_DIRTY"
ok "bb_done @paused-fixture (dirty tree) -> false" 1 -- "$GATE" bb_done "$BB_REF"
rm -f "$TMP_DIRTY"
ok "bb_done @paused-fixture (tree clean again) -> true" 0 -- "$GATE" bb_done "$BB_REF"

# Given current HEAD (not suspended) → When rearmed HEAD → Then true (exit 0)
ok "rearmed @HEAD (not suspended) -> true" 0 -- "$GATE" rearmed HEAD

# Given fixture ref 668bbf6 (paused) → When rearmed 668bbf6 → Then false (exit 1)
ok "rearmed @paused-fixture -> false" 1 -- "$GATE" rearmed "$BB_REF"

# steering_path resolves to .rn/loop/steering.md
ok_out "steering_path -> .rn/loop/steering.md" ".rn/loop/steering.md" -- "$GATE" steering_path

printf '\n%d passed, %d failed\n' "$pass" "$fail"
[[ "$fail" -eq 0 ]]
