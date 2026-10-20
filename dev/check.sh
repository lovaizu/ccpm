#!/bin/sh
# Every check CI runs on a push, run from the top of the repository with the tools of
# dev/requirements.txt. Given plugin names, such as `sh dev/check.sh rn`, the type check, the tests
# and the manifests are those plugins' alone, as before a push that changes them; CI gives none and
# checks every plugin.
set -e

plugins="$*"
if [ -z "$plugins" ]; then
  for tests in dev/*/tests; do
    plugin="${tests#dev/}"
    plugins="$plugins ${plugin%/tests}"
  done
fi

ruff check .
ruff format --check .

# Each plugin keeps its tests in dev/<plugin>/tests/ (.claude/rules/plugin.md), and its scripts find
# their modules by putting their own folders on sys.path; plugins share module names, such as stop,
# so each is type-checked on its own with its folders as search paths, and the folders of common/,
# what the plugins share, and dev/common/, what their tests share. common/ is checked as a plugin.
for plugin in $plugins; do
  paths=$(find "$plugin" "dev/$plugin" common dev/common -name '*.py' -exec dirname {} \; | sort -u)
  pyrefly check $(printf -- '--search-path %s ' $paths) "$plugin" "dev/$plugin"
done

for plugin in $plugins; do
  coverage run --source="$plugin" -m unittest discover -s "dev/$plugin/tests"
done
coverage combine
coverage report

# A malformed manifest fails for every user at install, so each plugin and the marketplace pass
# Claude Code's own check of them.
for plugin in $plugins; do
  if [ -f "$plugin/.claude-plugin/plugin.json" ]; then
    claude plugin validate "$plugin" --strict
  fi
done
claude plugin validate . --strict
