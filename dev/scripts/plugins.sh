#!/bin/sh
# Prints the plugins of the repository, one name a line, for a check given no plugin names. Each
# plugin keeps its code in plugins/<plugin>/ and its tests in dev/<plugin>/tests/, as Q1 of
# plugins/rn/domain/best-practices/plugin/best-practice.md says. dev/scripts/tests/ holds the tests
# of the checks themselves, so it names no plugin.
for tests in dev/*/tests; do
  plugin=$(echo "$tests" | cut -d/ -f2)
  if [ -d "plugins/$plugin" ]; then echo "$plugin"; fi
done
