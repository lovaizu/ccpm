#!/bin/sh
# The checks of how well the tests of each plugin's code catch faults, as the architecture best
# practice times them: mutation testing, which fails on any mutant under which every test still
# passes, and the property-based tests. A plugin's code comes under them once
# dev/<plugin>/cosmic-ray.toml names it, and its property-based tests lie in
# dev/<plugin>/tests/properties/. Run from the top of the repository with
# the tools of pyproject.toml's test-quality group, as `sh dev/scripts/quality.sh [<base>]`. Given
# the commit a push started from, it checks only the lines of each code changed since it, as CI does
# on each push. Given nothing, it checks the whole, with the property-based tests at their most
# inputs, as CI does each night. check.sh leaves both to it, as they check the tests and not the
# change.
set -e
# Each check reports what it's for around its findings.
. dev/scripts/findings.sh

base="$1"
if [ -n "$base" ] && ! git cat-file -e "$base^{commit}" 2>/dev/null; then
  # A new branch, or a push that rewrote history, gives no commit to compare with.
  echo "quality.sh: $base isn't a commit here, so the whole is checked"
  base=""
fi
if [ -n "$base" ]; then
  # dev/scripts/ci-fix.sh finds the commit in the run's log by this line.
  echo "quality.sh: the lines changed since $base"
fi

scratch="$(mktemp -d)"
trap 'rm -r "$scratch"' EXIT

# Whether a line under the paths changed since the base, or the whole is checked.
changed() {
  [ -z "$base" ] || ! git diff --quiet "$base" -- "$@"
}

# Prints each mutant of the database $1 under which every test passes, and fails where there's one.
survived() {
  cr-report --surviving-only --show-diff "$1"
  # cr-rate's --fail-over takes 0 as no limit, so quality.sh fails on any rate but 0 itself.
  cr-rate "$1" | awk '{ exit $1 != 0 }'
}

# Runs each mutant of the code that the config names, of the lines changed since the base where one
# is given, and fails on any that every test passes under.
mutants() {
  config="$scratch/$1-cosmic-ray.toml"
  db="$scratch/$1-mutants.sqlite"
  cp "$2" "$config"
  cosmic-ray init "$config" "$db"
  cr-filter-pragma "$db"
  cr-filter-operators "$db" "$config"
  if [ -n "$base" ]; then
    printf '\n[cosmic-ray.filters.git-filter]\nbranch = "%s"\n' "$base" >>"$config"
    cr-filter-git --config "$config" "$db"
  fi
  cosmic-ray exec "$config" "$db"
  held tests survived "$db"
}

profile=night
[ -z "$base" ] || profile=push
found=""
for toml in dev/*/cosmic-ray.toml; do
  # A glob that matches nothing stays as it is.
  [ -f "$toml" ] || continue
  found=yes
  plugin=$(basename "$(dirname "$toml")")
  properties="dev/$plugin/tests/properties"
  if changed "plugins/$plugin" "$properties" "$toml"; then
    if [ -d "$properties" ]; then
      held tests env HYPOTHESIS_PROFILE=$profile pytest -q -p no:cacheprovider "$properties"
    fi
    mutants "$plugin" "$toml"
  else
    echo "quality.sh: no line of $plugin's code or of its property-based tests changed since $base"
  fi
done
[ -n "$found" ] || echo "quality.sh: no dev/<plugin>/cosmic-ray.toml names code to mutate"
