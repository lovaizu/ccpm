#!/bin/sh
# The plugins a change from one commit to another touches, as `sh dev/changed.sh <from> <to>`, for
# dev/githooks/pre-push and CI: each plugin whose files or dev/<plugin>/ files it changes, each
# plugin with a link to a file it changes, or every plugin where it changes what they all stand on,
# a file of no plugin or dev/lane/testing.py, what their tests stand on. Nothing where it changes
# only what no check reads: the session records, the rules for the assistant, the documents of dev/
# and of each dev/<plugin>/, and the root's README and licence.
set -e

all=""
for tests in dev/*/tests; do
  plugin="${tests#dev/}"
  all="$all ${plugin%/tests}"
done
changed=$(git diff --name-only "$1" "$2" | grep -vE '^(\.rn/|\.claude/rules/|dev/([^/]+/)?[^/]+\.md$|README\.md$|LICENSE$)' || true)
[ -n "$changed" ] || exit 0
if printf '%s\n' "$changed" | grep -qvE "^(dev/)?($(echo $all | tr ' ' '|'))/" \
  || printf '%s\n' "$changed" | grep -qxF 'dev/lane/testing.py'; then
  echo $all
  exit 0
fi
# Each link of the commit, as the plugin it is in and the path it points to from the top, as a
# plugin takes another's code through a link (dev/architecture.md, Code).
links=$(git ls-tree -r "$2" | awk '$1 == "120000" {print $3, $4}' | while read -r blob link; do
  echo "${link%%/*} $(dirname "$link")/$(git cat-file -p "$blob")"
done | awk '{
  n = split($2, part, "/"); k = 0
  for (i = 1; i <= n; i++) if (part[i] == "..") k--; else if (part[i] != ".") kept[++k] = part[i]
  path = kept[1]; for (i = 2; i <= k; i++) path = path "/" kept[i]
  print $1, path
}')
plugins=""
for plugin in $all; do
  if printf '%s\n' "$changed" | grep -qE "^(dev/)?$plugin/"; then
    plugins="$plugins $plugin"
    continue
  fi
  for target in $(printf '%s\n' "$links" | awk -v p="$plugin" '$1 == p {print $2}'); do
    if printf '%s\n' "$changed" | grep -qE "^$target(/|$)"; then
      plugins="$plugins $plugin"
      break
    fi
  done
done
echo $plugins
