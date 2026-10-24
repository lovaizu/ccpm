#!/bin/sh
# The checks CI runs on every push, beside the property tests and the mutation testing, run from the
# top of the repository with the tools of dev/requirements.txt. Given plugin names, such as
# `sh dev/check.sh rn`, the type check, the tests and the manifests are those plugins' alone, as
# before a push that changes them; CI gives none and checks every plugin.
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

# Code copied between files is fixed in one and left wrong in the other, so code more than one file
# needs is kept once (dev/architecture.md, Code); every file is read at once, whichever plugins are
# given, as a copy can lie in any two. A link is the file it points to, so is left out. pylint is in
# dev/requirements-test-quality.txt, as it needs a newer Python than 3.9 only to check, not to run.
if command -v pylint >/dev/null 2>&1; then
  git ls-files '*.py' | while read -r file; do [ -L "$file" ] || echo "$file"; done \
    | xargs pylint --disable=all --enable=duplicate-code --score=no
fi

# Each plugin keeps its tests in dev/<plugin>/tests/ (dev/architecture.md, Test), and its scripts
# find their modules by putting their own folders on sys.path; plugins share module names, such as
# stop, so each is type-checked on its own with its folders as search paths, and dev/lane/, where
# testing.py, what every plugin's tests share, is kept. What the plugins' hooks share is lane's,
# reached through a link in each plugin's own folder; a folder of lane's code linked whole, as
# turn's hooks/lane/, is checked in lane alone, as git lists the link and not the files in it.
for plugin in $plugins; do
  paths=$({ find "$plugin" "dev/$plugin" -name '*.py' -exec dirname {} \; && echo dev/lane; } | sort -u)
  files=$(git ls-files --cached --others --exclude-standard "$plugin" "dev/$plugin" | grep '\.py$')
  pyrefly check $(printf -- '--search-path %s ' $paths) $files
done

# The unit tests, `test*.py`, unittest's own pattern, count the lines and branches; the property
# tests, whose inputs change from run to run, are run apart by dev/properties.sh.
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
