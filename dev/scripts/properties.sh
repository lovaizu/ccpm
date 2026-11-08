#!/bin/sh
# The property-based tests, `dev/<plugin>/tests/properties*.py`, run from the top of the repository
# with the tools of pyproject.toml's dev and test-quality groups: many inputs each where the environment sets CI,
# as in CI, and few elsewhere, by the profiles dev/lane/testing.py's load_hypothesis_profile loads.
# They check that the unit tests, which dev/scripts/check.sh runs, are enough, so they run apart from
# them. Given plugin names, such as `sh dev/scripts/properties.sh rn`, they're those plugins' alone.
# Given none, they're every plugin's.
set -e

plugins=${*:-$(sh dev/scripts/plugins.sh)}
for plugin in $plugins; do
  python -m unittest discover -s "dev/$plugin/tests" -p 'properties*.py'
done
