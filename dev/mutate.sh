#!/bin/sh
# Mutation testing of each plugin that has dev/<plugin>/cosmic-ray.toml, run from the top of the
# repository with the tools of dev/requirements.txt and dev/requirements-test-quality.txt; fails on any mutant no test catches.
# cr-rate is not used for that: it takes a limit of 0 as no limit.
# Cosmic Ray changes the files it tests, so it runs on a copy of the repository.
set -e

copy=$(mktemp -d)
trap 'rm -rf "$copy"' EXIT
cp -R . "$copy"
cd "$copy"
for config in dev/*/cosmic-ray.toml; do
  db="$copy/mutants.sqlite"
  rm -f "$db"
  cosmic-ray init "$config" "$db"
  cr-filter-pragma "$db"
  cr-filter-operators "$db" "$config"
  cosmic-ray exec "$config" "$db"
  cr-report --surviving-only --show-diff "$db" | tee "$copy/report.txt"
  grep -q '^surviving mutants: 0 ' "$copy/report.txt"
done
