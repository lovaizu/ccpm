#!/bin/sh
# The plugins of the repository, a name a line, for the checks given none: each plugin keeps its
# tests in dev/<plugin>/tests/, beside its code in plugins/<plugin>/, as an install copies only the
# plugin's folder. dev/scripts/tests/ holds the tests of the checks themselves.
for tests in dev/*/tests; do
  plugin=$(echo "$tests" | cut -d/ -f2)
  if [ -d "plugins/$plugin" ]; then echo "$plugin"; fi
done
