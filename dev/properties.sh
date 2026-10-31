#!/bin/sh
# The property tests, `dev/<plugin>/tests/properties*.py`, run from the top of the repository with
# the tools of pyproject.toml's dev and test-quality groups: many inputs each where CI is set, as
# in CI, and few elsewhere, by the profiles dev/lane/testing.py's load_hypothesis_profile loads.
# They check that the unit tests, which dev/check.sh runs, are enough, so they are run apart from
# them. Given plugin names, such as `sh dev/properties.sh rn`, those plugins' alone; given none,
# every plugin's.
set -e

plugins=${*:-$(sh dev/plugins.sh)}
for plugin in $plugins; do
  python -m unittest discover -s "dev/$plugin/tests" -p 'properties*.py'
done
