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
# says. The check reads every file at once, as a copy can lie in any two.
if command -v pylint >/dev/null 2>&1; then
  printf '%s\n' "$own_python" \
    | held design xargs pylint --disable=all --enable=duplicate-code --score=no
else
  echo "check.sh: copied code goes unchecked, as pylint isn't installed. It comes with"\
    "pyproject.toml's test-quality group, on Python 3.11 or later"
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
# plugin one way only, by its dependencies, as .claude/rules/dev.md says.
python3 dev/scripts/standalone.py check

# A Mermaid diagram GitHub can't parse shows as an error in its place, unseen until someone opens
# the page, so Mermaid's own parser parses each.
sh dev/scripts/mermaid.sh

# A behavior that no test checks can break unseen, so the tests of the E2E runner and of the
# double of Claude Code run every line and branch of their code, as the architecture best practice
# says a unit passes. pyproject.toml holds what coverage counts. Mutation testing and the
# property-based tests, which check the tests and not the change, run in CI by
# dev/scripts/quality.sh, as that best practice times them.
if command -v coverage >/dev/null 2>&1; then
  # The tests run once, on each core, as coverage's own .pth starts it in each worker where
  # COVERAGE_PROCESS_START names its settings.
  COVERAGE_FILE="$scratch/.coverage" COVERAGE_PROCESS_START="$PWD/pyproject.toml" \
    coverage run --rcfile=pyproject.toml -m pytest -q -n auto -p no:cacheprovider \
    dev/scripts/tests dev/tests
  COVERAGE_FILE="$scratch/.coverage" coverage combine -q
  COVERAGE_FILE="$scratch/.coverage" held tests coverage report
else
  pytest -q -n auto dev/scripts/tests dev/tests
  echo "check.sh: which lines of the E2E runner and the double the tests run goes unchecked, as"\
    "coverage isn't installed. It comes with pyproject.toml's test-quality group, on Python 3.11"\
    "or later"
fi

for manifest in plugins/*/.claude-plugin/plugin.json; do
  claude plugin validate "${manifest%/.claude-plugin/plugin.json}" --strict
done
claude plugin validate . --strict
