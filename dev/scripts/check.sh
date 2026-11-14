#!/bin/sh
# The checks CI runs on every push, run from the top of the repository with the tools of
# pyproject.toml's dev group: the checks' own code, the best practices, the figures, and the
# manifests.
set -e
# Each check of how the code is laid out reports what it's for around its findings.
. dev/scripts/findings.sh
# What the checks write for themselves, such as complexipy's cache and coverage's data.
scratch="$(mktemp -d)"
trap 'rm -r "$scratch"' EXIT

held design ruff check .
ruff format --check .

# The repository's own Python, which the checks below read whole. A link is the file it points to,
# so the list leaves it out.
own_python=$(git ls-files '*.py' | while read -r file; do [ -L "$file" ] || echo "$file"; done)

# A fix to code copied between files lands in one and leaves the other wrong, so the repository keeps
# code more than one file needs once, as Code kept once of dev/plugin-development-guide.md
# says. Two modules that import each other can't change or be tested apart, so each architecture's
# Test strategy checks for import cycles too. The check reads every file at once, as a copy or a
# cycle can lie in any two.
if command -v pylint >/dev/null 2>&1; then
  printf '%s\n' "$own_python" \
    | held design xargs pylint --disable=all --enable=duplicate-code,cyclic-import --score=no
else
  echo "check.sh: copied code and import cycles go unchecked, as pylint isn't installed. It comes"\
    "with pyproject.toml's test-quality group, on Python 3.11 or later"
fi

# A function whose maintainer must hold more in mind at once than one reading gives, by how deep its
# branches and loops nest, does more than one thing, as N5 of the refactor-code best practice says.
# complexipy counts it as cognitive complexity, up to pyproject.toml's limit.
if command -v complexipy >/dev/null 2>&1; then
  printf '%s\n' "$own_python" \
    | held design xargs complexipy --failed --plain --cache-dir "$scratch/complexipy"
else
  echo "check.sh: how deep each function nests goes unchecked, as complexipy isn't installed. It"\
    "comes with pyproject.toml's test-quality group, on Python 3.11 or later"
fi

# The checks' own Python, and the double of Claude Code with its tests.
held design pyrefly check --search-path dev/scripts --search-path dev/scripts/tests \
  --search-path dev/tests dev/scripts/*.py dev/scripts/tests/*.py dev/tests/*.py

# Lane's parts and its test cases, which call them, as a type that doesn't fit across a handoff is a
# gap between the parts, as N13 of the architecture best practice says. Each folder on the search
# path is one that Claude Code, lay.py, or pytest puts on the import path of the code in it.
held design pyrefly check --search-path plugins/lane/hooks/lane --search-path plugins/lane/scripts \
  --search-path dev/tests --search-path dev/lane/tests --search-path dev/lane/tests/unit \
  --search-path dev/lane/tests/e2e --search-path dev/lane/tests/prompts \
  plugins/lane/hooks/lane/*.py plugins/lane/hooks/lane/domain/*.py \
  plugins/lane/hooks/lane/domain/lanes/*.py plugins/lane/scripts/*.py dev/lane/tests/*.py \
  dev/lane/tests/*/*.py

# Each kind's best practice lies in a folder of its own in rn, as `best-practice.json`. Its template
# lies beside it. The check fails on:
# - a fault in a best practice's form
# - a best practice's Markdown that lags behind its JSON, from which practices.py makes it for a
#   person to read
# - a template that is a JSON Schema in a form that schema.py doesn't read whole
# - a file in the folder that neither uses, such as a figure that the template dropped
# Each of these would make the folder say what rn doesn't hold.
python3 dev/scripts/practices.py form plugins/rn/domain/best-practices/*/best-practice.json

# Every figure carries the one style of dev/images/figures.css and sets no font or color of its own,
# so the figures look alike and one place changes a look, as .claude/rules/figures.md says.
python3 dev/scripts/figures.py check

# Claude Code installs only a plugin's folder, so each plugin works from its own, and uses another
# plugin one way only, by its dependencies, as the plugin guide says of a plugin's folder.
python3 dev/scripts/standalone.py check

# A Mermaid diagram GitHub can't parse shows as an error in its place, unseen until someone opens
# the page, so Mermaid's own parser parses each.
sh dev/scripts/mermaid.sh

# Each test case of a plugin names what it supports one level up, and each element of its
# architecture has an integration case, as the plugin guide's Test says, so a gap between the
# parts shows before anyone builds around it. A plugin comes under the check once
# dev/<plugin>/tests/ holds its cases, as its developers write every case before any part.
plugin_tests=""
for architecture in dev/*/architecture.md; do
  plugin="${architecture#dev/}"
  plugin="${plugin%/architecture.md}"
  if [ -d "dev/$plugin/tests" ]; then
    python3 dev/scripts/trace.py check "$plugin"
  else
    echo "check.sh: the trace of $plugin's cases goes unchecked, as dev/$plugin/tests/ holds"\
      "none yet"
  fi
  # The unit and integration tests of each plugin run on each push, as the plugin guide's Test says.
  for level in unit integration; do
    [ ! -d "dev/$plugin/tests/$level" ] || plugin_tests="$plugin_tests dev/$plugin/tests/$level"
  done
done

# A double that gives what the real thing never would passes a test that the real one fails, so each
# double of the plugins' tests takes each result from a line of a record that names its source, as
# the plugin guide's Test says. This part of the check needs no network, so it runs on each push;
# quality.sh checks the documentation's pages.
python3 dev/scripts/trace.py doubles

# A behavior that no test checks can break unseen, so the tests of the checks' own code, the E2E
# runner and the double of Claude Code among them, run every line and branch of what
# pyproject.toml has coverage count, as the architecture best practice says a unit passes. Mutation
# testing and the property-based tests, which check the tests and not the change, run in CI by
# dev/scripts/quality.sh, as that best practice times them.
if command -v coverage >/dev/null 2>&1; then
  # The tests run once, on each core, as coverage's own .pth starts it in each worker where
  # COVERAGE_PROCESS_START names its settings.
  COVERAGE_FILE="$scratch/.coverage" COVERAGE_PROCESS_START="$PWD/pyproject.toml" \
    coverage run --rcfile=pyproject.toml -m pytest -q -n auto -p no:cacheprovider \
    dev/scripts/tests dev/tests $plugin_tests
  COVERAGE_FILE="$scratch/.coverage" coverage combine -q
  COVERAGE_FILE="$scratch/.coverage" held tests coverage report
else
  pytest -q -n auto dev/scripts/tests dev/tests $plugin_tests
  echo "check.sh: which lines of the checks' own code the tests run goes unchecked, as"\
    "coverage isn't installed. It comes with pyproject.toml's test-quality group, on Python 3.11"\
    "or later"
fi

for manifest in plugins/*/.claude-plugin/plugin.json; do
  claude plugin validate "${manifest%/.claude-plugin/plugin.json}" --strict
done
claude plugin validate . --strict
