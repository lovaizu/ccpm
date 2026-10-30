#!/bin/sh
# Vale's check of the repository's Markdown for plain English, by the Google developer
# documentation style and ccpm's own words (.vale.ini), for dev/check.sh, and for
# dev/githooks/pre-push and CI on a push that changes Markdown and names no plugin. Run from the top
# of the repository. Every finding fails it, whatever level its rule gives it.
set -e

sh dev/vale.sh
# Left out: the session records of .rn/, which keep each session as it was written, and
# plugins/rn/checklists/, which is being rewritten (#61) and comes in once it is done.
found=$(git ls-files -z '*.md' ':!:.rn/' ':!:plugins/rn/checklists/' \
  | xargs -0 vale --no-exit --output=line)
if [ -n "$found" ]; then
  echo "$found"
  exit 1
fi
