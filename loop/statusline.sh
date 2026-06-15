#!/bin/sh
input=$(cat)

# Context window percentage.
# The built-in indicator and .context_window.used_percentage both count input
# tokens only (input + cache_creation + cache_read), so they read low. The real
# context-limit check counts output too. Compute from current_usage's raw token
# breakdown — input + output + cache_creation + cache_read — to match it exactly.
# Fall back to used_percentage (+ output share) on older clients without
# current_usage.
c_int=$(echo "$input" | jq -r '
  .context_window as $cw
  | ($cw.context_window_size // 0) as $w
  | ($cw.current_usage) as $u
  | if ($u != null and $w > 0) then
      [100,
        ( (($u.input_tokens // 0)
         + ($u.output_tokens // 0)
         + ($u.cache_creation_input_tokens // 0)
         + ($u.cache_read_input_tokens // 0)) / $w * 100 )
      ] | min | round
    elif ($cw.used_percentage != null and $w > 0) then
      [100, (($cw.used_percentage) + (($cw.total_output_tokens // 0) / $w * 100))] | min | round
    elif ($cw.used_percentage != null) then
      ($cw.used_percentage | round)
    else
      0
    end
')
seg1="C:${c_int}%"

# Model abbreviation: Opus→O, Sonnet→S, Haiku→H + version
display=$(echo "$input" | jq -r '.model.display_name // .model.id // "unknown"')
abbrev=$(echo "$display" | sed -E \
  -e 's/Claude //' \
  -e 's/Opus ?/O/' \
  -e 's/Sonnet ?/S/' \
  -e 's/Haiku ?/H/')

# Effort level first letter
effort=$(echo "$input" | jq -r '.effort.level // empty')
if [ -n "$effort" ]; then
  e=$(printf '%.1s' "$effort")
  seg2="${abbrev}/${e}"
else
  seg2="${abbrev}"
fi

# Context window size, compact: 1000000→1m, 200000→200k
cw_size=$(echo "$input" | jq -r '.context_window.context_window_size // empty')
if [ -n "$cw_size" ] && [ "$cw_size" -gt 0 ] 2>/dev/null; then
  if [ "$cw_size" -ge 1000000 ]; then
    sz="$((cw_size / 1000000))m"
  else
    sz="$((cw_size / 1000))k"
  fi
  seg2="${seg2}/${sz}"
fi

# Directory basename @ git branch
dir=$(echo "$input" | jq -r '.workspace.current_dir // empty')
dirname=$(basename "${dir:-$(pwd)}")
branch=$(cd "${dir:-.}" 2>/dev/null && git rev-parse --abbrev-ref HEAD 2>/dev/null)
if [ -n "$branch" ]; then
  seg3="${dirname}@${branch}"
else
  seg3="${dirname}"
fi

# Max plan rate limits — append to seg1
five_h_pct=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')
seven_d_pct=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty')

if [ -n "$five_h_pct" ]; then
  five_h_int=$(printf '%.0f' "$five_h_pct")
  seg1="${seg1} 5h:${five_h_int}%"
fi
if [ -n "$seven_d_pct" ]; then
  seven_d_int=$(printf '%.0f' "$seven_d_pct")
  seg1="${seg1} 7d:${seven_d_int}%"
fi

printf '%s | %s | %s' "$seg1" "$seg2" "$seg3"

# --- PoC addition (loop task #1): write per-surface state file -------------
# Producer side of a poller contract: an external watcher repeatedly reads
# ~/.rn/ctx/<surface_id>.json to learn the current context-% and target
# surface/repo. Appended strictly AFTER the display printf so it can never
# alter or block the display, and written so it never exposes a misleading
# or half-written value. The script's exit status is preserved (always the
# display's), so the write being skipped or failing never changes it.
#
# State-file schema (the contract the watcher reads):
#   context_pct         number       context-window % shown as C:xx% (== $c_int)
#   raw_token_total     number|null  raw tokens the % is computed from
#                                    (input+output+cache_creation+cache_read);
#                                    null on older-client fallback (no usage data)
#   context_window_size number       context window size in tokens (0 if unknown)
#   surface_id          string       CMUX_SURFACE_ID (UUID-style), the target pane
#   workspace_id        string       CMUX_WORKSPACE_ID ("" if unset)
#   repo_cwd            string       workspace.current_dir, the target repo path
#   ts                  number       unix epoch seconds when this file was written
#
# Consumer notes:
#   - context_pct: 0 with raw_token_total: null is an older-client fallback with
#     no usage data (low confidence), not necessarily a genuinely empty context.
#   - File presence does NOT imply a live session: a file lingers after its pane
#     dies. The consumer must apply its own staleness threshold using `ts`
#     (now - ts > bound => stale), since the producer never deletes the file.
write_state() {
  # Skip unless we have a surface id that is safe as a filename component.
  # UUID-style ids pass; anything with "/" or ".." is rejected so the path
  # can never escape ~/.rn/ctx/.
  case "${CMUX_SURFACE_ID:-}" in
    '' ) return 0 ;;
    *[!A-Za-z0-9_-]* ) return 0 ;;
  esac

  # Skip if the percentage was not genuinely computed (display shows C:%).
  # Never write a misleading context_pct: 0 for malformed/empty input.
  case "$c_int" in
    '' ) return 0 ;;
    *[!0-9]* ) return 0 ;;
  esac

  # raw_token_total: honest. When current_usage is present, emit the real sum
  # (the same numerator c_int is computed from). When it is absent (older-client
  # fallback that still shows a real % from used_percentage), emit null rather
  # than a misleading 0. tonumber? // null coerces and guards non-numeric.
  raw_total=$(echo "$input" | jq '
    (.context_window.current_usage) as $u
    | if $u == null then null
      else (($u.input_tokens // 0)
            + ($u.output_tokens // 0)
            + ($u.cache_creation_input_tokens // 0)
            + ($u.cache_read_input_tokens // 0))
      end
  ' 2>/dev/null)
  [ -n "$raw_total" ] || raw_total=null

  # context_window_size: coerce with tonumber? so a present-but-string value
  # (e.g. "big") becomes 0 instead of aborting jq -n.
  cw_size_raw=$(echo "$input" | jq '
    (.context_window.context_window_size | tonumber?) // 0
  ' 2>/dev/null)
  case "$cw_size_raw" in '' | *[!0-9]* ) cw_size_raw=0 ;; esac

  repo_cwd=$(echo "$input" | jq -r '.workspace.current_dir // ""' 2>/dev/null)
  # Skip if there is no target repo path: an empty repo_cwd is not actionable
  # for the watcher, and the contract requires a non-empty repo cwd.
  [ -n "$repo_cwd" ] || return 0

  # ts: coerce to a bare integer so --argjson can never abort (e.g. if date
  # ever yields nothing); keeps the "every --argjson value is guarded" guarantee.
  ts=$(date +%s 2>/dev/null)
  case "$ts" in '' | *[!0-9]* ) ts=0 ;; esac

  dir="$HOME/.rn/ctx"
  mkdir -p "$dir" 2>/dev/null || return 0
  tmp="$dir/.${CMUX_SURFACE_ID}.json.tmp.$$"

  # Atomic write: build into a temp file in the same dir, then mv -f into place.
  # Rename on one filesystem is atomic, so a poller never reads a truncated file,
  # and a failed build (jq abort) leaves any prior good file untouched. tonumber?
  # on every --argjson value guarantees jq -n cannot abort on a wrong-typed input.
  # The whole build runs in a subshell with stderr suppressed so a failing ">"
  # redirect (e.g. an unwritable ctx dir) stays as silent as the original script.
  if ( jq -n \
       --argjson context_pct "$c_int" \
       --argjson raw_token_total "$raw_total" \
       --argjson context_window_size "$cw_size_raw" \
       --arg surface_id "$CMUX_SURFACE_ID" \
       --arg workspace_id "${CMUX_WORKSPACE_ID:-}" \
       --arg repo_cwd "$repo_cwd" \
       --argjson ts "$ts" \
       '{
         context_pct: ($context_pct | tonumber? // 0),
         raw_token_total: $raw_token_total,
         context_window_size: ($context_window_size | tonumber? // 0),
         surface_id: $surface_id,
         workspace_id: $workspace_id,
         repo_cwd: $repo_cwd,
         ts: ($ts | tonumber? // 0)
       }' > "$tmp" ) 2>/dev/null
  then
    mv -f -- "$tmp" "$dir/${CMUX_SURFACE_ID}.json" 2>/dev/null || rm -f -- "$tmp" 2>/dev/null
  else
    rm -f -- "$tmp" 2>/dev/null
  fi
  return 0
}
write_state || true
