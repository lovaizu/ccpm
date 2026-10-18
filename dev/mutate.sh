#!/bin/sh
# Mutation testing of each plugin that has dev/<plugin>/cosmic-ray.toml, run from the top of the
# repository with the tools of dev/requirements.txt and dev/requirements-test-quality.txt; fails on any mutant no test catches.
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
  cr-report --surviving-only --show-diff "$db"
  cr-rate --fail-over 0 "$db"
done
