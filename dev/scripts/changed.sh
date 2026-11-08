#!/bin/sh
# Prints the plugins that a change from one commit to another touches, for dev/scripts/pre-push.sh
# and CI: `sh dev/scripts/changed.sh <from> <to>`.
# - The change touches a plugin when it edits the plugin's files or its dev/<plugin>/ files, or a
#   file that one of the plugin's links points to.
# - It touches every plugin when it edits what they all rest on: a file outside any plugin, or
#   dev/lane/testing.py, which their tests use.
# - It touches none when it edits only files that no check reads: the session records, the rules for
#   the assistant, the license, the root README, and the documents of dev/ and of each dev/<plugin>/.
#   A check reads a document with a Mermaid diagram, so such a document still counts.
set -e

all=$(sh dev/scripts/plugins.sh)
changed=$(git diff --name-only "$1" "$2" | grep -vE '^(\.rn/|\.claude/rules/|dev/([^/]+/)?[^/]+\.md$|README\.md$|LICENSE$)' || true)
# dev/scripts/mermaid.mjs, which check.sh runs, reads a document with a Mermaid diagram.
diagrams=$(git diff --name-only "$1" "$2" -- '*.md' ':!.rn/' | while read -r file; do
  if git show "$2:$file" 2>/dev/null | grep -q '^ *```mermaid'; then echo "$file"; fi
done)
changed=$(printf '%s\n%s\n' "$changed" "$diagrams" | sort -u | grep . || true)
[ -n "$changed" ] || exit 0
if printf '%s\n' "$changed" | grep -qvE "^(plugins|dev)/($(echo $all | tr ' ' '|'))/" \
  || printf '%s\n' "$changed" | grep -qxF 'dev/lane/testing.py'; then
  echo $all
  exit 0
fi
# Each link of the commit, as the plugin that holds it and the path it points to from the top. A
# plugin uses another's code through a link, as Q14 of
# plugins/rn/domain/best-practices/plugin/best-practice.md says.
links=$(git ls-tree -r "$2" | awk '$1 == "120000" {print $3, $4}' | while read -r blob link; do
  plugin=${link#plugins/}
  echo "${plugin%%/*} $(dirname "$link")/$(git cat-file -p "$blob")"
done | awk '{
  n = split($2, part, "/"); k = 0
  for (i = 1; i <= n; i++) if (part[i] == "..") k--; else if (part[i] != ".") kept[++k] = part[i]
  path = kept[1]; for (i = 2; i <= k; i++) path = path "/" kept[i]
  print $1, path
}')
plugins=""
for plugin in $all; do
  if printf '%s\n' "$changed" | grep -qE "^(plugins|dev)/$plugin/"; then
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
