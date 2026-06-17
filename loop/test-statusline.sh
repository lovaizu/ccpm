#!/bin/sh
# Test for the statusline state-file spike (PoC task #1) + review fixes.
# Verifies:
#   (a) spike copy's display output is byte-for-byte identical to the original
#   (b) spike copy writes a per-surface state file whose ctx% equals the
#       displayed C:xx% integer, with a non-empty surface id and repo cwd
#   (c) degradation path: with CMUX_SURFACE_ID unset, display still prints
#       and no state file is written
# Review-fix guards:
#   (d) malformed/empty input -> NO file written (no context_pct:0), display
#       still prints, exit 0
#   (e) present-but-non-numeric context_window_size -> write does not crash, a
#       prior good file is NOT clobbered (atomicity/coercion), output (if any)
#       is valid JSON
#   (f) invalid CMUX_SURFACE_ID (a/b, ../x) -> no file written, nothing escapes
#       ~/.rn/ctx/, exit 0
#   (g) older-client fallback (no current_usage, has used_percentage) -> file
#       written with a real context_pct and raw_token_total: null
#   (h) forced write failure (unwritable HOME) -> still exits 0, display identical
#   (i) input with no workspace.current_dir -> NO file (non-empty repo cwd is
#       part of the contract), display still prints, exit 0
#   (j) ctx dir present but unwritable -> no stderr leak (as silent as original),
#       exit 0, display identical
set -u

here=$(cd "$(dirname "$0")" && pwd)
orig="$HOME/.claude/scripts/statusline.sh"
spike="$here/statusline.sh"
fixture="$here/fixtures/statusline-input.json"
fb_fixture="$here/fixtures/statusline-fallback.json"

# Throwaway, namespaced surface ids so we never clobber a real session file.
TEST_SURFACE="poc-test-$$"
TEST_WORKSPACE="poc-ws-$$"
state_file="$HOME/.rn/ctx/${TEST_SURFACE}.json"

fail() { echo "NG: $1" >&2; exit 1; }

rm -f "$state_file"

# --- (a) byte-for-byte identical display -----------------------------------
out_orig=$(CMUX_SURFACE_ID="$TEST_SURFACE" CMUX_WORKSPACE_ID="$TEST_WORKSPACE" sh "$orig" < "$fixture")
out_spike=$(CMUX_SURFACE_ID="$TEST_SURFACE" CMUX_WORKSPACE_ID="$TEST_WORKSPACE" sh "$spike" < "$fixture")
if [ "$out_orig" = "$out_spike" ]; then
  echo "OK (a): display byte-for-byte identical"
  echo "    display: $out_spike"
else
  echo "  original: $out_orig" >&2
  echo "  spike   : $out_spike" >&2
  fail "(a) display differs between original and spike"
fi

# --- (b) state file written, ctx% matches display --------------------------
[ -f "$state_file" ] || fail "(b) state file not created: $state_file"
jq -e . "$state_file" >/dev/null 2>&1 || fail "(b) state file is not valid JSON"

# Extract the displayed C:xx% integer from spike stdout.
disp_pct=$(printf '%s' "$out_spike" | sed -E 's/^C:([0-9]+)%.*/\1/')
file_pct=$(jq -r '.context_pct' "$state_file")
[ "$disp_pct" = "$file_pct" ] || fail "(b) ctx% mismatch: display=$disp_pct file=$file_pct"

file_surface=$(jq -r '.surface_id // ""' "$state_file")
file_cwd=$(jq -r '.repo_cwd // ""' "$state_file")
[ -n "$file_surface" ] || fail "(b) surface id empty in state file"
[ -n "$file_cwd" ] || fail "(b) repo cwd empty in state file"
[ "$file_surface" = "$TEST_SURFACE" ] || fail "(b) surface id mismatch: $file_surface"
# Happy path keeps the real numeric token total.
file_raw=$(jq -r '.raw_token_total' "$state_file")
[ "$file_raw" = "50000" ] || fail "(b) raw_token_total expected 50000, got $file_raw"

echo "OK (b): state file written, ctx%=$file_pct matches display, surface=$file_surface, cwd=$file_cwd, raw=$file_raw"

# --- (c) degradation path: no CMUX_SURFACE_ID, no file, display still prints
rm -f "$state_file"
out_nosurf=$(unset CMUX_SURFACE_ID; sh "$spike" < "$fixture") || fail "(c) spike errored with surface unset"
[ -n "$out_nosurf" ] || fail "(c) display empty when surface unset"
[ "$out_nosurf" = "$out_orig" ] || fail "(c) display changed when surface unset"
[ ! -f "$state_file" ] || fail "(c) state file written despite empty surface id"
echo "OK (c): degradation path clean (display printed, no file written)"

# --- (d) malformed/empty input -> no file, no context_pct:0, display, exit 0
rm -f "$state_file"
# Empty stdin: C: percentage cannot be computed (display shows C:%).
out_d=$(printf '' | CMUX_SURFACE_ID="$TEST_SURFACE" sh "$spike"); rc_d=$?
out_d_orig=$(printf '' | CMUX_SURFACE_ID="$TEST_SURFACE" sh "$orig")
[ "$rc_d" -eq 0 ] || fail "(d) spike exit status $rc_d (expected 0) on empty input"
[ "$out_d" = "$out_d_orig" ] || fail "(d) display differs from original on empty input"
[ ! -f "$state_file" ] || fail "(d) state file written for malformed input (would be context_pct:0)"
echo "OK (d): malformed/empty input -> no file, display='$out_d', exit 0"

# --- (e) non-numeric context_window_size -> no crash, prior good file kept --
# Seed a known-good file, then feed input whose context_window_size is a string.
rm -f "$state_file"
CMUX_SURFACE_ID="$TEST_SURFACE" CMUX_WORKSPACE_ID="$TEST_WORKSPACE" sh "$spike" < "$fixture" >/dev/null
[ -f "$state_file" ] || fail "(e) precondition: seed good file failed"
good_before=$(cat "$state_file")
bad_input='{"model":{"display_name":"Claude Opus 4.8"},"context_window":{"context_window_size":"big","current_usage":{"input_tokens":12000,"output_tokens":3000,"cache_creation_input_tokens":5000,"cache_read_input_tokens":30000}},"workspace":{"current_dir":"/tmp"}}'
out_e=$(printf '%s' "$bad_input" | CMUX_SURFACE_ID="$TEST_SURFACE" sh "$spike"); rc_e=$?
[ "$rc_e" -eq 0 ] || fail "(e) spike crashed (exit $rc_e) on non-numeric context_window_size"
jq -e . "$state_file" >/dev/null 2>&1 || fail "(e) state file not valid JSON after non-numeric input"
good_after=$(cat "$state_file")
# Either prior good file is untouched (atomic, mv only on success) OR file is
# a valid coerced write (size 0). Assert validity + size coerced to 0 if changed.
if [ "$good_before" != "$good_after" ]; then
  cws=$(jq -r '.context_window_size' "$state_file")
  [ "$cws" = "0" ] || fail "(e) non-numeric size not coerced to 0 (got $cws)"
  echo "OK (e): non-numeric size coerced to 0, valid JSON, no crash (exit 0)"
else
  echo "OK (e): non-numeric size handled, prior good file preserved, no crash (exit 0)"
fi
# No leftover temp files in the ctx dir.
tmpleft=$(ls "$HOME/.rn/ctx/".${TEST_SURFACE}.json.tmp.* 2>/dev/null | wc -l | tr -d ' ')
[ "$tmpleft" = "0" ] || fail "(e) temp file(s) left behind: $tmpleft"
rm -f "$state_file"

# --- (f) invalid CMUX_SURFACE_ID -> no file, nothing escapes ~/.rn/ctx ------
guard_root="$HOME/.rn/ctx"
# a/b would create ~/.rn/ctx/a/b.json if unguarded; ../x would escape.
canary_sub="$guard_root/poc-canary-$$"
canary_esc="$HOME/.rn/poc-escape-$$.json"
rm -f "$canary_esc"; rm -rf "$canary_sub"
for badid in "a/b-$$" "../poc-escape-$$"; do
  out_f=$(printf '%s' "$(cat "$fixture")" | CMUX_SURFACE_ID="$badid" sh "$spike"); rc_f=$?
  [ "$rc_f" -eq 0 ] || fail "(f) exit $rc_f for invalid id '$badid'"
done
[ ! -e "$guard_root/a" ] || fail "(f) created subdir for id with slash"
[ ! -e "$canary_esc" ] || fail "(f) wrote file escaping ctx dir"
[ ! -e "$HOME/.rn/poc-escape-$$.json" ] || fail "(f) escaped to ~/.rn"
echo "OK (f): invalid surface ids rejected (no file in/outside ctx dir, exit 0)"

# --- (g) older-client fallback: no current_usage -> real ctx%, raw null -----
fb_surface="poc-fb-$$"
fb_state="$HOME/.rn/ctx/${fb_surface}.json"
rm -f "$fb_state"
out_g=$(CMUX_SURFACE_ID="$fb_surface" sh "$spike" < "$fb_fixture"); rc_g=$?
[ "$rc_g" -eq 0 ] || fail "(g) exit $rc_g on fallback fixture"
[ -f "$fb_state" ] || fail "(g) no file written for fallback input"
jq -e . "$fb_state" >/dev/null 2>&1 || fail "(g) fallback file not valid JSON"
g_pct=$(jq -r '.context_pct' "$fb_state")
g_disp=$(printf '%s' "$out_g" | sed -E 's/^C:([0-9]+)%.*/\1/')
[ "$g_pct" = "$g_disp" ] || fail "(g) ctx% mismatch fallback: file=$g_pct disp=$g_disp"
[ "$g_pct" -gt 0 ] 2>/dev/null || fail "(g) fallback ctx% not a real positive value: $g_pct"
g_raw=$(jq -r '.raw_token_total' "$fb_state")
[ "$g_raw" = "null" ] || fail "(g) raw_token_total expected null on fallback, got $g_raw"
echo "OK (g): fallback -> ctx%=$g_pct (real), raw_token_total=null"
rm -f "$fb_state"

# --- (h) forced write failure (unwritable HOME) -> exit 0, display identical -
fakehome=$(mktemp -d)
chmod 000 "$fakehome"
out_h=$(HOME="$fakehome" CMUX_SURFACE_ID="$TEST_SURFACE" sh "$spike" < "$fixture"); rc_h=$?
chmod 755 "$fakehome"; rmdir "$fakehome" 2>/dev/null
[ "$rc_h" -eq 0 ] || fail "(h) exit $rc_h on unwritable HOME (must stay 0)"
[ "$out_h" = "$out_spike" ] || fail "(h) display changed under write failure"
echo "OK (h): write failure under unwritable HOME -> exit 0, display identical"

# --- (i) no workspace.current_dir -> no file (contract needs non-empty cwd) --
rm -f "$state_file"
nocwd_input='{"model":{"display_name":"Claude Opus 4.8"},"context_window":{"context_window_size":200000,"current_usage":{"input_tokens":12000,"output_tokens":3000,"cache_creation_input_tokens":5000,"cache_read_input_tokens":30000}}}'
out_i=$(printf '%s' "$nocwd_input" | CMUX_SURFACE_ID="$TEST_SURFACE" sh "$spike"); rc_i=$?
out_i_orig=$(printf '%s' "$nocwd_input" | CMUX_SURFACE_ID="$TEST_SURFACE" sh "$orig")
[ "$rc_i" -eq 0 ] || fail "(i) exit $rc_i with no current_dir"
[ "$out_i" = "$out_i_orig" ] || fail "(i) display differs from original with no current_dir"
[ ! -f "$state_file" ] || fail "(i) state file written with empty repo_cwd"
echo "OK (i): no current_dir -> no file written (non-empty repo cwd enforced), exit 0"

# --- (j) unwritable ctx dir -> no stderr leak, exit 0, display identical -----
jhome=$(mktemp -d)
mkdir -p "$jhome/.rn/ctx"
chmod 555 "$jhome/.rn/ctx"
errf=$(mktemp)
out_j=$(HOME="$jhome" CMUX_SURFACE_ID="$TEST_SURFACE" sh "$spike" < "$fixture" 2>"$errf"); rc_j=$?
err_j=$(cat "$errf"); rm -f "$errf"
chmod 755 "$jhome/.rn/ctx"; rm -rf "$jhome"
[ "$rc_j" -eq 0 ] || fail "(j) exit $rc_j on unwritable ctx dir (must stay 0)"
[ "$out_j" = "$out_spike" ] || fail "(j) display changed on unwritable ctx dir"
[ -z "$err_j" ] || fail "(j) stderr leak on unwritable ctx dir: $err_j"
echo "OK (j): unwritable ctx dir -> no stderr leak, exit 0, display identical"

# Cleanup any throwaway files.
rm -f "$state_file" "$fb_state"
rm -f "$HOME/.rn/ctx/.${TEST_SURFACE}.json.tmp."* 2>/dev/null

echo "ALL PASS"
