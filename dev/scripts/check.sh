#!/bin/sh
# The checks CI runs on every push, beside the property-based tests and the mutation testing, run
# from the top of the repository with the tools of pyproject.toml's dev group. Given plugin names,
# such as `sh dev/scripts/check.sh rn`, the type check, the tests and the manifests are those
# plugins' alone. CI gives none and checks every plugin. Given `--reached` first, as before a push,
# the tests are only those the change reaches, and it doesn't count their lines and branches.
set -e

reached=""
if [ "$1" = --reached ]; then
  reached=true
  shift
fi
plugins=${*:-$(sh dev/scripts/plugins.sh)}

ruff check .
ruff format --check .

# A fix to code copied between files lands in one and leaves the other wrong, so the repository keeps
# code more than one file needs once, as Q14 of plugins/rn/domain/best-practices/plugin/best-practice.md
# says. The check reads every file at once, whichever plugins it gets, as a copy can lie in any two.
# A link is the file it points to, so the check leaves it out.
if command -v pylint >/dev/null 2>&1; then
  git ls-files '*.py' | while read -r file; do [ -L "$file" ] || echo "$file"; done \
    | xargs pylint --disable=all --enable=duplicate-code --score=no
else
  echo "check.sh: copied code goes unchecked, as pylint isn't installed. It comes with"\
    "pyproject.toml's test-quality group, on Python 3.11 or later"
fi

for plugin in $plugins; do
  sh dev/scripts/typecheck.sh "$plugin"
done
# The checks' own Python, beside the plugins'.
pyrefly check --search-path dev/lane --search-path dev/scripts --search-path dev/scripts/tests \
  --search-path plugins/rn/domain dev/scripts/*.py dev/scripts/tests/*.py

# The check finds in each best practice the faults its form shows, its Markdown, made from its JSON
# for a person to read, left behind it, and its example, where it's a copy of a document of the
# repository, left behind that document, as each says what rn doesn't hold. It also finds each file
# in its folder that none of them holds, such as a figure the document dropped, left over. Each
# kind's best practice lies in its own folder of rn's as `best-practice.json`. Its template and its
# example lie beside it.
# An example in JSON holds to its template where that's a JSON Schema.
python3 dev/scripts/practices.py form plugins/rn/domain/best-practices/*/best-practice.json

# Each run's design tree, where the work's documents take their decisions from, as step 1 of
# .claude/rules/dev.md says, holds its form and the plan best practice's order, by rn's own check of it: a deliverable
# before what it takes from, or a kind with no best practice, fails here, not in a document made
# from the tree.
for design in .rn/*/design-tree.json; do
  if [ -f "$design" ]; then
    python3 plugins/rn/scripts/tree.py check "$design"
  fi
done

# Every figure carries the one style of dev/images/figures.css, so the figures look alike and one
# place changes a color, as step 3 of .claude/rules/dev.md says.
python3 dev/scripts/figures.py check

# A Mermaid diagram GitHub can't parse shows as an error in its place, unseen until someone opens
# the page, so Mermaid's own parser parses each.
sh dev/scripts/mermaid.sh

# The unit and architecture tests, `test*.py`, unittest's own pattern, run by pytest as
# pyproject.toml sets it, at once on each processor by pytest-xdist. dev/scripts/properties.sh runs
# apart the property-based tests, whose inputs change from run to run. Each plugin's run is a
# process of its own, as each puts its own `helpers` and code on sys.path.
if [ -n "$reached" ]; then
  # Only the tests whose code the change reaches, which pytest-testmon chooses by the code each test
  # ran when it last ran, kept in the file TESTMON_DATAFILE names, else in .testmondata. A selection
  # runs only some lines, so this run counts none. CI counts them.
  if python -c 'import testmon' 2>/dev/null; then
    choose=--testmon
  else
    choose=""
    echo "check.sh: every test runs, as pytest-testmon isn't installed. It comes with"\
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

# The tests of the checks themselves, such as pre-push.sh's and mermaid.sh's, on every run, as they're
# few and quick, whichever plugins the run gets. What they test is shell, which coverage doesn't
# count.
pytest -q -n auto dev/scripts/tests

# A malformed manifest fails for every user at install, so each plugin and the marketplace pass
# Claude Code's own check of them.
for plugin in $plugins; do
  if [ -f "plugins/$plugin/.claude-plugin/plugin.json" ]; then
    claude plugin validate "plugins/$plugin" --strict
  fi
done
claude plugin validate . --strict
