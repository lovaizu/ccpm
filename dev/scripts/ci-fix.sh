#!/bin/sh
# Watches the runs of Test quality and Nightly on each branch named, and has Claude Code mend their
# failures, by the brief of dev/scripts/ci-fix.md, as `sh dev/scripts/ci-fix.sh <branch>...` from
# the top of the repository. It runs until stopped. The developer names the branches, as only they
# know which branches the work goes on in. The watch itself calls no model: it asks GitHub for
# failed runs every five minutes, and starts `claude -p` on Opus only for failures it hasn't
# handled, which may run only the checks and the git commands its brief names, and push only its
# own branch.
#
# For each branch, Claude Code mends every failure not yet handled at once, on the branch's head,
# from the oldest commit that those pushes started from, so that the fix lands on the code that
# lives and no two fixes cover the same lines. It works in a worktree of its own under
# .claude/worktrees/, on a branch `ci-fix/<branch>-<head>` that it pushes, so it touches no work in
# progress. The next fix of a branch waits until the developer has merged the last one into it, as
# a fix made beside an unmerged one would cover its lines again. Each report lands in the
# repository's git folder, under ci-fix/reports/, and its first line on the standard output.
set -eu

if [ $# -eq 0 ]; then
  echo "usage: sh dev/scripts/ci-fix.sh <branch>..." >&2
  exit 2
fi

top=$(git rev-parse --show-toplevel)
common=$(git rev-parse --path-format=absolute --git-common-dir)
state="$common/ci-fix"
mkdir -p "$state/reports"
touch "$state/handled"
tab=$(printf '\t')

# Prints each failed run of the branch $1 not yet handled: its ID, its workflow, and the commit its
# push started from, or none for a nightly run, which checks the whole.
failed() {
  for workflow in "Test quality" "Nightly"; do
    gh run list --workflow "$workflow" --branch "$1" --status failure --limit 20 \
      --json databaseId --jq '.[].databaseId' 2>/dev/null \
      | while read -r run; do
        grep -qxF "$run" "$state/handled" && continue
        base=""
        if [ "$workflow" = "Test quality" ]; then
          base=$(gh run view "$run" --log 2>/dev/null \
            | grep -o 'quality.sh: the lines changed since [0-9a-f]*' | head -n 1 \
            | awk '{ print $NF }')
        fi
        printf '%s\t%s\t%s\n' "$run" "$workflow" "$base"
      done
  done
}

# Whether a fix of the branch $1 is pushed and not yet merged into it.
waiting() {
  git -C "$top" for-each-ref --format='%(refname)' "refs/remotes/origin/ci-fix/$1-*" \
    | while read -r ref; do
      git -C "$top" merge-base --is-ancestor "$ref" "origin/$1" || echo "$ref"
    done | grep -q .
}

# Mends the failures that the file $2 lists, as failed prints them, on the branch $1.
handle() {
  branch=$1 list=$2
  head=$(git -C "$top" rev-parse --short=8 "origin/$branch")
  fix="ci-fix/$branch-$head"
  name=$(echo "$fix" | tr / -)
  runs=$(cut -f 1 "$list" | tr '\n' ' ' | sed 's/ $//')
  # A nightly run checks the whole, so it needs no commit to start from, nor does a run whose log
  # names none. Else the oldest commit that the pushes started from covers the lines of each.
  base=""
  if ! cut -f 2 "$list" | grep -qxF Nightly && ! cut -f 3 "$list" | grep -qx ''; then
    # shellcheck disable=SC2046 # Each commit is one word.
    base=$(git -C "$top" merge-base --octopus $(cut -f 3 "$list"))
  fi
  # Beside the other worktrees, so that no file Claude Code writes lies in the git folder.
  tree="$(dirname "$common")/.claude/worktrees/$name"
  log="$state/log-$name"
  for run in $runs; do
    gh run view "$run" --log-failed 2>&1 || true
  done >"$log"
  git -C "$top" worktree add --quiet -b "$fix" "$tree" "origin/$branch"
  (
    cd "$tree"
    uv sync --locked --group test-quality --quiet
    (cd dev/scripts && npm ci --ignore-scripts --no-audit --no-fund --silent)
    values=$(printf '{"runs": "%s", "branch": "%s", "fix_branch": "%s", "base": "%s",' \
      "$runs" "$branch" "$fix" "$base")
    values="$values$(printf ' "log": "%s"}' "$log")"
    printf '%s\n\n%s\n' "$(cat dev/scripts/ci-fix.md)" "$values" \
      | claude -p --model opus --permission-mode acceptEdits --add-dir "$state" \
        --allowedTools "Bash(uv run --no-sync sh dev/scripts/check.sh)" \
        "Bash(uv run --no-sync sh dev/scripts/quality.sh:*)" "Bash(uv run --no-sync pytest:*)" \
        "Bash(git status:*)" "Bash(git diff:*)" "Bash(git log:*)" "Bash(git show:*)" \
        "Bash(git add:*)" "Bash(git commit:*)" "Bash(git push origin $fix)" \
        "Bash(git push -u origin $fix)" \
        >"$state/reports/$name.md" 2>&1 || true
  )
  git -C "$top" worktree remove --force "$tree"
  rm "$log"
  cut -f 1 "$list" >>"$state/handled"
  echo "ci-fix: runs $runs on $branch: $(head -n 1 "$state/reports/$name.md")"
}

list="$state/failed"
while :; do
  for branch in "$@"; do
    git -C "$top" fetch --quiet --prune origin
    waiting "$branch" && continue
    failed "$branch" >"$list"
    [ -s "$list" ] && handle "$branch" "$list" </dev/null
  done
  rm -f "$list"
  sleep 300
done
