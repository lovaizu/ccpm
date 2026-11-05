#!/bin/sh
# The checks CI runs on every push, beside the property-based tests and the mutation testing, run
# from the top of the repository with the tools of pyproject.toml's dev group. Given plugin names,
# such as `sh dev/scripts/check.sh rn`, the type check, the tests and the manifests are those
# plugins' alone; CI gives none and checks every plugin. Given `--reached` first, as before a push,
# the tests are only those the change reaches, and their lines and branches are not counted.
set -e

reached=""
if [ "$1" = --reached ]; then
  reached=true
  shift
fi
plugins=${*:-$(sh dev/scripts/plugins.sh)}

ruff check .
ruff format --check .

# Code copied between files is fixed in one and left wrong in the other, so code more than one file
# needs is kept once (dev/plugin-best-practice.md, Code kept once); every file is read at once, whichever plugins are
# given, as a copy can lie in any two. A link is the file it points to, so is left out.
if command -v pylint >/dev/null 2>&1; then
  git ls-files '*.py' | while read -r file; do [ -L "$file" ] || echo "$file"; done \
    | xargs pylint --disable=all --enable=duplicate-code --score=no
else
  echo "check.sh: copied code not checked, as pylint is not installed; it comes with pyproject.toml's"\
    "test-quality group, on Python 3.11 or later"
fi

for plugin in $plugins; do
  sh dev/scripts/typecheck.sh "$plugin"
done
# The checks' own Python, beside the plugins'.
pyrefly check --search-path dev/lane dev/scripts/*.py

# A best practice is checked for the faults its form shows, its Markdown, made from its JSON for a
# person to read, for being left behind it, and its example, where it is a copy of a document of the
# repository, for being left behind that document, as each says what Turn does not hold; and a file
# in its folder that none of them holds, such as a figure the document dropped, for being left over.
# Each kind's lies in its own folder as best-practice.json, beside its template and its example.
python3 plugins/turn/scripts/plan.py form plugins/turn/core/domain/best-practices/*/best-practice.json

# Every figure carries the one style of dev/images/figures.css, so the figures look alike and a
# colour is changed in one place (dev/plugin-best-practice.md, Directory structure).
python3 dev/scripts/figures.py check

# A Mermaid diagram GitHub cannot parse shows as an error in its place, unseen until someone opens
# the page, so each is parsed by Mermaid's own parser, which comes with dev/scripts/package-lock.json.
if command -v node >/dev/null 2>&1 && [ -d dev/scripts/node_modules/mermaid ]; then
  node dev/scripts/mermaid.mjs
else
  echo "check.sh: Mermaid diagrams not checked, as node or dev/scripts/node_modules is missing; run"\
    "\`npm ci --ignore-scripts\` in dev/scripts"
fi

# The unit and architecture tests, `test*.py`, unittest's own pattern, run by pytest as
# pyproject.toml sets it, at once on each processor (pytest-xdist); the property-based tests, whose
# inputs change from run to run, are run apart by dev/scripts/properties.sh. Each plugin's run is a
# process of its own, as each puts its own `helpers` and code on sys.path.
if [ -n "$reached" ]; then
  # Only the tests whose code the change reaches, which pytest-testmon chooses by the code each test
  # ran when it last ran, kept in the file TESTMON_DATAFILE names, else in .testmondata. A selection
  # runs only some lines, so none are counted; CI counts them.
  if python -c 'import testmon' 2>/dev/null; then
    choose=--testmon
  else
    choose=""
    echo "check.sh: every test run, as pytest-testmon is not installed; it comes with"\
      "pyproject.toml's push group, on Python 3.11 or later"
  fi
  for plugin in $plugins; do
    pytest -q -n auto $choose "dev/$plugin/tests"
  done
else
  # Every test, with the lines and branches each plugin's tests run counted, those of the processes
  # they start among them, as .coveragerc sets.
  for plugin in $plugins; do
    coverage run --source="plugins/$plugin" -m pytest -q -n auto "dev/$plugin/tests"
  done
  coverage combine
  coverage report
fi

# A malformed manifest fails for every user at install, so each plugin and the marketplace pass
# Claude Code's own check of them.
for plugin in $plugins; do
  if [ -f "plugins/$plugin/.claude-plugin/plugin.json" ]; then
    claude plugin validate "plugins/$plugin" --strict
  fi
done
claude plugin validate . --strict
