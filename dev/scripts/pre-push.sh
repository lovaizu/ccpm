#!/bin/sh
# Before a push, `sh dev/scripts/check.sh` on each commit pushed, as CI runs it. The pre-push job
# of lefthook-repo.yml runs it, with uv on PATH, which sets up the check tools in the commits
# pushed from their uv.lock.
set -e

if ! command -v uv >/dev/null 2>&1; then
  echo "pre-push: uv isn't on PATH. Install it, as pre-push sets up the check tools with it by" \
    "\`uv sync --locked\`: https://docs.astral.sh/uv/getting-started/installation/" >&2
  exit 1
fi
if ! command -v npm >/dev/null 2>&1; then
  echo "pre-push: npm isn't on PATH. Install Node.js, as pre-push sets up Mermaid's parser with it" \
    "by \`npm ci\`: https://nodejs.org/en/download" >&2
  exit 1
fi
# Removes the copy being checked, if any, where the check fails or stops, and git's entry for it.
copy=""
remove_copy() {
  [ -z "$copy" ] || { git worktree remove --force "$copy" 2>/dev/null; rm -rf "$copy"; }
  git worktree prune
}
trap remove_copy EXIT
# A shell stopped by a signal, as when a person stops a push or a tool times it out, skips the trap
# on exit, so each signal removes the copy too, and then stops the shell by itself.
for stop in INT TERM HUP; do
  trap "remove_copy; trap - EXIT $stop; kill -s $stop \$\$" $stop
done
zero=0000000000000000000000000000000000000000
while read -r _ local _ _; do
  [ "$local" = "$zero" ] && continue
  # The commits pushed, not what the working tree holds beside them, in a worktree.
  copy=$(mktemp -d)
  git worktree add -q --detach "$copy" "$local"
  # git gives a hook the repository it runs for, such as GIT_DIR, which the git repositories the
  # tests make would take as theirs.
  (cd "$copy" && unset $(git rev-parse --local-env-vars) \
    && uv sync --locked --group test-quality --quiet \
    && (cd dev/scripts && npm ci --ignore-scripts --no-audit --no-fund --silent) \
    && uv run --no-sync sh dev/scripts/check.sh)
  git worktree remove --force "$copy"
  copy=""
done
