#!/bin/sh
# The plugins of the repository, a name a line, for the checks given none: each plugin keeps its
# tests in dev/<plugin>/tests/ (dev/plugin-best-practice.md, Unit: code), beside its code in
# plugins/<plugin>/. dev/scripts/tests/ holds the tests of the checks themselves.
for tests in dev/*/tests; do
  plugin=$(echo "$tests" | cut -d/ -f2)
  if [ -d "plugins/$plugin" ]; then echo "$plugin"; fi
done
