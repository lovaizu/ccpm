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

# Each kind's best practice lies in a folder of its own in rn, as `best-practice.json`. Its template
# and its example lie beside it. The check fails on:
# - a fault in a best practice's form
# - a best practice's Markdown that lags behind its JSON, from which practices.py makes it for a
#   person to read
# - an example that copies a document of the repository and lags behind that document
# - an example in JSON that breaks its template, where the template is a JSON Schema
# - a file in the folder that none of them uses, such as a figure that the document dropped
# Each of these would make the folder say what rn doesn't hold.
python3 dev/scripts/practices.py form plugins/rn/domain/best-practices/*/best-practice.json

# Each run's design tree is where the work's documents take their decisions from, as step 1 of
# .claude/rules/dev.md says. rn's own check holds the tree to its form and to the order of the plan
# best practice. So the check here fails each of these, before a document made from the tree
# rests on it: a deliverable placed before what it takes from, one started before its
# preconditions finish, and a kind with no best practice.
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

# The unit and architecture tests, `test*.py` as unittest names them, run by pytest as
# pyproject.toml sets it, on every processor at once through pytest-xdist. The property-based tests,
# whose inputs change from run to run, run apart in dev/scripts/properties.sh. Each plugin runs in a
# process of its own, as each puts its own `helpers` and code on sys.path.
if [ -n "$reached" ]; then
  # Only the tests whose code the change reaches. pytest-testmon chooses them by the code that each
  # test ran last time, kept in the file that TESTMON_DATAFILE names, or else in .testmondata. A
  # selection runs only some lines, so this run counts no coverage. CI counts it.
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
  # Every test, counting the lines and branches that each plugin's tests run, including those of the
  # processes they start, as .coveragerc sets.
  for plugin in $plugins; do
    coverage run --source="plugins/$plugin" -m pytest -q -n auto "dev/$plugin/tests"
  done
  coverage combine
  coverage report
fi

# The tests of the checks themselves, such as those of pre-push.sh and mermaid.sh, run every time,
# whichever plugins the run gets, as they're few and quick. They test shell, which coverage doesn't
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
