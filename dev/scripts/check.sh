#!/bin/sh
# The checks CI runs on every push, run from the top of the repository with the tools of
# pyproject.toml's dev group: the checks' own code, the best practices, the figures, and the
# manifests.
set -e

ruff check .
ruff format --check .

# A fix to code copied between files lands in one and leaves the other wrong, so the repository keeps
# code more than one file needs once, as N14 of plugins/rn/domain/best-practices/plugin/best-practice.md
# says. The check reads every file at once, as a copy can lie in any two.
# A link is the file it points to, so the check leaves it out.
if command -v pylint >/dev/null 2>&1; then
  git ls-files '*.py' | while read -r file; do [ -L "$file" ] || echo "$file"; done \
    | xargs pylint --disable=all --enable=duplicate-code --score=no
else
  echo "check.sh: copied code goes unchecked, as pylint isn't installed. It comes with"\
    "pyproject.toml's test-quality group, on Python 3.11 or later"
fi

# The checks' own Python.
pyrefly check --search-path dev/scripts --search-path dev/scripts/tests dev/scripts/*.py \
  dev/scripts/tests/*.py

# Lane's code, laid into each plugin, and its tests.
pyrefly check --search-path plugins/lane/hooks/lane --search-path plugins/lane/scripts \
  --search-path dev/lane/tests plugins/lane/hooks/lane/*.py plugins/lane/hooks/lane/domain/*.py \
  plugins/lane/hooks/lane/domain/lanes/*.py plugins/lane/scripts/*.py dev/lane/tests/*.py \
  dev/lane/tests/*/*.py

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

# Every figure carries the one style of dev/images/figures.css, so the figures look alike and one
# place changes a color, as step 3 of .claude/rules/dev.md says.
python3 dev/scripts/figures.py check

# A Mermaid diagram GitHub can't parse shows as an error in its place, unseen until someone opens
# the page, so Mermaid's own parser parses each.
sh dev/scripts/mermaid.sh

pytest -q -n auto dev/scripts/tests dev/lane/tests

# A behavior that no test checks can break unseen, so the tests of Lane run every line and branch of
# its code, and fail under every small change to it, as N7 of
# plugins/rn/domain/best-practices/code/best-practice.md says. pyproject.toml and dev/lane/cosmic-ray.toml hold what each check counts.
if command -v cosmic-ray >/dev/null 2>&1; then
  scratch="$(mktemp -d)"
  trap 'rm -r "$scratch"' EXIT
  COVERAGE_FILE="$scratch/.coverage" coverage run -m pytest -q -p no:cacheprovider dev/lane/tests
  COVERAGE_FILE="$scratch/.coverage" coverage combine -q
  COVERAGE_FILE="$scratch/.coverage" coverage report
  cosmic-ray init dev/lane/cosmic-ray.toml "$scratch/mutants.sqlite"
  cr-filter-pragma "$scratch/mutants.sqlite"
  cosmic-ray exec dev/lane/cosmic-ray.toml "$scratch/mutants.sqlite"
  cr-report --surviving-only --show-diff "$scratch/mutants.sqlite"
  cr-rate --fail-over 0 "$scratch/mutants.sqlite"
else
  echo "check.sh: how well Lane's tests catch faults goes unchecked, as cosmic-ray isn't"\
    "installed. It comes with pyproject.toml's test-quality group, on Python 3.11 or later"
fi

for manifest in plugins/*/.claude-plugin/plugin.json; do
  claude plugin validate "${manifest%/.claude-plugin/plugin.json}" --strict
done
claude plugin validate . --strict
