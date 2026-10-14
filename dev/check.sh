#!/bin/sh
# Every check CI runs on a push, run from the top of the repository with the tools of
# dev/requirements.txt.
set -e

ruff check .
ruff format --check .

# Each plugin keeps its tests in dev/<plugin>/tests/ (.claude/rules/plugin.md), and its scripts find
# their modules by putting their own folders on sys.path; plugins share module names, such as stop,
# so each is type-checked on its own with its folders as search paths.
for tests in dev/*/tests; do
  plugin="${tests#dev/}"
  plugin="${plugin%/tests}"
  paths=$(find "$plugin" "dev/$plugin" -name '*.py' -exec dirname {} \; | sort -u)
  pyrefly check $(printf -- '--search-path %s ' $paths) "$plugin" "dev/$plugin"
done

for tests in dev/*/tests; do
  plugin="${tests#dev/}"
  coverage run --source="${plugin%/tests}" -m unittest discover -s "$tests"
done
coverage combine
coverage report
