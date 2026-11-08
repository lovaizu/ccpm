#!/bin/sh
# The property-based tests, `dev/<plugin>/tests/properties*.py`, run from the top of the repository
# with the tools of pyproject.toml's dev and test-quality groups. Each test tries many inputs where
# the environment sets CI, as CI does, and few elsewhere, by the profiles that load_hypothesis_profile
# in dev/lane/testing.py loads.
# They check that the unit tests, which dev/scripts/check.sh runs, are enough, so they run apart from
# them. Given plugin names, such as `sh dev/scripts/properties.sh rn`, they're those plugins' alone.
# Given none, they're every plugin's.
set -e

plugins=${*:-$(sh dev/scripts/plugins.sh)}
for plugin in $plugins; do
  python -m unittest discover -s "dev/$plugin/tests" -p 'properties*.py'
done
