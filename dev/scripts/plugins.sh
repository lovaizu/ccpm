#!/bin/sh
# The plugins of the repository, a name a line, for the checks given none: each plugin keeps its
# tests in dev/<plugin>/tests/ (dev/plugin-best-practice.md, Unit: code).
ls -d dev/*/tests | cut -d/ -f2
