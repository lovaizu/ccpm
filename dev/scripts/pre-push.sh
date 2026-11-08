#!/bin/sh
# Before a push, the checks of what the push changes, on the commits pushed:
# `sh dev/scripts/check.sh --reached`, for each plugin `sh dev/scripts/changed.sh` names, which runs
# only the tests the change reaches. Every test, the property-based tests, and the mutation testing
# are CI's. The pre-push job of lefthook.yml runs it, with uv on PATH, which sets up the check tools
# in the commits pushed from their uv.lock.
set -e

# What each test ran when it last ran, from which pytest-testmon chooses the tests a change reaches,
# kept in the clone, as the check of each push runs in a worktree of its own that goes when it ends.
TESTMON_DATAFILE="$(git rev-parse --show-toplevel)/.testmondata"
export TESTMON_DATAFILE

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
zero=0000000000000000000000000000000000000000
while read -r _ local _ remote; do
  [ "$local" = "$zero" ] && continue
  # The changes count from the commit that the branch is at on the remote, which its own push
  # checked, or, for a branch new on the remote, from where it left main. CI counts from the commit
  # before the one where its `tests` last passed, which only CI knows, or else from where the
  # branch left main too.
  if [ "$remote" = "$zero" ]; then
    base=$(git merge-base "$local" origin/main)
  else
    base=$remote
  fi
  plugins=$(sh dev/scripts/changed.sh "$base" "$local")
  [ -n "$plugins" ] || continue
  # The commits pushed, not what the working tree holds beside them, in a worktree.
  copy=$(mktemp -d)
  trap 'git worktree remove --force "$copy" 2>/dev/null; rm -rf "$copy"' EXIT
  git worktree add -q --detach "$copy" "$local"
  # git gives a hook the repository it runs for, such as GIT_DIR, which the git repositories the
  # tests make would take as theirs.
  (cd "$copy" && unset $(git rev-parse --local-env-vars) \
    && uv sync --locked --group test-quality --group push --quiet \
    && (cd dev/scripts && npm ci --ignore-scripts --no-audit --no-fund --silent) \
    && uv run --no-sync sh dev/scripts/check.sh --reached $plugins)
  git worktree remove --force "$copy"
  # Removed, so the cleanup on exit, which stops the push where it fails, has nothing left to do.
  trap - EXIT
done
