#!/bin/sh
# The property tests, `dev/<plugin>/tests/properties*.py`, run from the top of the repository with
# the tools of dev/requirements.txt and dev/requirements-test-quality.txt: many inputs each in CI
# and few elsewhere. They check that the unit tests, which dev/check.sh runs, are enough, so
# they are run apart from them. Given plugin names, such as `sh dev/properties.sh rn`, those
# plugins' alone; given none, every plugin's.
set -e

plugins="$*"
if [ -z "$plugins" ]; then
  for tests in dev/*/tests; do
    plugin="${tests#dev/}"
    plugins="$plugins ${plugin%/tests}"
  done
fi
for plugin in $plugins; do
  python -m unittest discover -s "dev/$plugin/tests" -p 'properties*.py'
done
