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
# A shell stopped by a signal, as when a person stops a push or a tool times it out, skips the trap
# on exit, so each signal removes the folder too, and then stops the shell by itself.
for stop in INT TERM HUP; do
  trap "rm -r \"\$scratch\"; trap - EXIT $stop; kill -s $stop \$\$" $stop
done

held design ruff check .
ruff format --check .

# The repository's own Python, which the checks below read whole. A link is the file it points to,
# so the list leaves it out.
own_python=$(git ls-files '*.py' | while read -r file; do
  [ -L "$file" ] || echo "$file"
done)

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

# Code that nothing uses still asks its maintainer to read it and keep it in line with the rest, so
# the repository keeps none. vulture names each name that no file reads, by pyproject.toml.
held design vulture

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

# The checks' own Python, and rn's code with its tests, as a type that doesn't fit across a call is a
# fault no test may reach.
held design pyrefly check --search-path dev/scripts dev/scripts/*.py

held design pyrefly check --search-path plugins/rn/domain/scripts --search-path dev/rn/tests \
  plugins/rn/domain/scripts/*.py plugins/rn/domain/scripts/*/*.py \
  dev/rn/tests/*.py dev/rn/tests/*/*.py

# Each kind's best practice lies in a folder of its own in rn, as `best-practice.json`. Its template
# lies beside it. The check fails on:
# - a fault in a best practice's form
# - a template that is a JSON Schema in a form that schema.py doesn't read whole
# - a file in the folder that neither uses, such as a figure that the template dropped
# Each of these would make the folder say what rn doesn't hold.
python3 dev/scripts/practices.py form plugins/rn/domain/best-practices/*/best-practice.json

# Each plugin's product vision, README, and architecture holds its kind's template and nothing
# beside it, so a section or sentence that drifts from the template shows on the push that adds it.
for vision in dev/*/product-vision.md; do
  python3 plugins/rn/domain/scripts/template product-vision "$vision"
done
for readme in plugins/*/README.md; do
  python3 plugins/rn/domain/scripts/template readme "$readme"
done
for architecture in dev/*/architecture.md; do
  python3 plugins/rn/domain/scripts/template architecture "$architecture"
done

# Each decision of an architecture's views tags the story or rule it carries out, and each story
# and rule is carried out somewhere, as the architecture best practice's template says, so a
# decision that serves nothing, or a rule that nothing carries out, shows before any case is written.
for architecture in dev/*/architecture.md; do
  plugin="${architecture#dev/}"
  python3 dev/scripts/trace.py tags "${plugin%/architecture.md}"
done

# Every figure carries the one style of dev/images/figures.css and sets no font or color of its own,
# so the figures look alike and one place changes a look, as .claude/rules/figures.md says.
python3 dev/scripts/figures.py check

# Claude Code installs only a plugin's folder, so each plugin works from its own, and uses another
# plugin one way only, by its dependencies, as the plugin guide says of a plugin's folder.
python3 dev/scripts/standalone.py check

# A Mermaid diagram GitHub can't parse shows as an error in its place, unseen until someone opens
# the page, so Mermaid's own parser parses each.
sh dev/scripts/mermaid.sh

# The unit tests of each plugin run on each push.
plugin_tests=""
for architecture in dev/*/architecture.md; do
  plugin="${architecture#dev/}"
  plugin="${plugin%/architecture.md}"
  [ ! -d "dev/$plugin/tests/unit" ] || plugin_tests="$plugin_tests dev/$plugin/tests/unit"
done

# A double that gives what the real thing never would passes a test that the real one fails, so each
# double of the plugins' tests takes each result from a line of a record that names its source, as
# the plugin guide's Test says. This part of the check needs no network, so it runs on each push;
# CI checks the documentation's pages each night, as a page changes apart from any push.
python3 dev/scripts/trace.py doubles

# A behavior that no test checks can break unseen, so the tests run every line and branch of what
# pyproject.toml has coverage count, as the code best practice's N7 asks.
if command -v coverage >/dev/null 2>&1; then
  # The tests run once, on each core, as coverage's own .pth starts it in each worker where
  # COVERAGE_PROCESS_START names its settings.
  COVERAGE_FILE="$scratch/.coverage" COVERAGE_PROCESS_START="$PWD/pyproject.toml" \
    coverage run --rcfile=pyproject.toml -m pytest -q -n auto -p no:cacheprovider $plugin_tests
  COVERAGE_FILE="$scratch/.coverage" coverage combine -q
  COVERAGE_FILE="$scratch/.coverage" held tests coverage report
else
  pytest -q -n auto $plugin_tests
  echo "check.sh: which lines of rn's code the tests run goes unchecked, as"\
    "coverage isn't installed. It comes with pyproject.toml's test-quality group, on Python 3.11"\
    "or later"
fi

for manifest in plugins/*/.claude-plugin/plugin.json; do
  claude plugin validate "${manifest%/.claude-plugin/plugin.json}" --strict
done
claude plugin validate . --strict
