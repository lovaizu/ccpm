#!/bin/sh
# The checks CI runs on every push, beside the property tests and the mutation testing, run from the
# top of the repository with the tools of pyproject.toml's dev group. Given plugin names, such as
# `sh dev/check.sh rn`, the type check, the tests and the manifests are those plugins' alone, as
# before a push that changes them; CI gives none and checks every plugin.
set -e

plugins=${*:-$(sh dev/plugins.sh)}

ruff check .
ruff format --check .
# The Markdown is read whole, whichever plugins are given, as a document can lie anywhere.
sh dev/prose.sh

# Code copied between files is fixed in one and left wrong in the other, so code more than one file
# needs is kept once (dev/architecture.md, Code); every file is read at once, whichever plugins are
# given, as a copy can lie in any two. A link is the file it points to, so is left out.
if command -v pylint >/dev/null 2>&1; then
  git ls-files '*.py' | while read -r file; do [ -L "$file" ] || echo "$file"; done \
    | xargs pylint --disable=all --enable=duplicate-code --score=no
else
  echo "check.sh: copied code not checked, as pylint is not installed; it comes with pyproject.toml's"\
    "test-quality group, on Python 3.11 or later"
fi

for plugin in $plugins; do
  sh dev/typecheck.sh "$plugin"
done
# The checks' own Python, beside the plugins'.
pyrefly check --search-path dev/lane dev/*.py

# The unit tests, `test*.py`, unittest's own pattern, count the lines and branches; the property
# tests, whose inputs change from run to run, are run apart by dev/properties.sh.
for plugin in $plugins; do
  coverage run --source="plugins/$plugin" -m unittest discover -s "dev/$plugin/tests"
done
coverage combine
coverage report

# A malformed manifest fails for every user at install, so each plugin and the marketplace pass
# Claude Code's own check of them.
for plugin in $plugins; do
  if [ -f "plugins/$plugin/.claude-plugin/plugin.json" ]; then
    claude plugin validate "plugins/$plugin" --strict
  fi
done
claude plugin validate . --strict
