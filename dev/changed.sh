#!/bin/sh
# The plugins a change from one commit to another touches, as `sh dev/changed.sh <from> <to>`, for
# dev/githooks/pre-push and CI: each plugin whose files or dev/<plugin>/ files it changes, or every
# plugin where it changes what they all stand on, a file of no plugin, lane's hook code the plugins'
# hooks take through a link, or dev/lane/testing.py, what their tests stand on. Nothing where it
# changes only what no check reads: the session records, the decisions, the rules for the
# assistant, and the root's README and licence.
set -e

all=""
for tests in dev/*/tests; do
  plugin="${tests#dev/}"
  all="$all ${plugin%/tests}"
done
changed=$(git diff --name-only "$1" "$2" | grep -vE '^(\.rn/|\.claude/rules/|README\.md$|LICENSE$)' || true)
[ -n "$changed" ] || exit 0
if printf '%s\n' "$changed" | grep -qvE "^(dev/)?($(echo $all | tr ' ' '|'))/" \
  || printf '%s\n' "$changed" | grep -qE '^(lane/hooks/lane/(hook|shell)\.py|dev/lane/testing\.py)$'; then
  echo $all
  exit 0
fi
plugins=""
for plugin in $all; do
  if printf '%s\n' "$changed" | grep -qE "^(dev/)?$plugin/"; then
    plugins="$plugins $plugin"
  fi
done
echo $plugins
