#!/bin/sh
# Every check CI runs on a push, run from the top of the repository with the tools of
# dev/requirements.txt.
set -e

ruff check .
ruff format --check .

# Each plugin keeps its tests in dev/<plugin>/tests/ (.claude/rules/plugin.md), and its scripts find
# their modules by putting their own folders on sys.path; plugins share module names, such as stop,
# so each is type-checked on its own with its folders as search paths, and the folders of common/,
# what the plugins share, and dev/common/, what their tests share. common/ is checked as a plugin.
for tests in dev/*/tests; do
  plugin="${tests#dev/}"
  plugin="${plugin%/tests}"
  paths=$(find "$plugin" "dev/$plugin" common dev/common -name '*.py' -exec dirname {} \; | sort -u)
  pyrefly check $(printf -- '--search-path %s ' $paths) "$plugin" "dev/$plugin"
done

for tests in dev/*/tests; do
  plugin="${tests#dev/}"
  coverage run --source="${plugin%/tests}" -m unittest discover -s "$tests"
done
coverage combine
coverage report

# A malformed manifest fails for every user at install, so each plugin and the marketplace pass
# Claude Code's own check of them.
for manifest in */.claude-plugin/plugin.json; do
  claude plugin validate "${manifest%/.claude-plugin/plugin.json}" --strict
done
claude plugin validate . --strict
