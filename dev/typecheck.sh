#!/bin/sh
# The type check of one plugin, as `sh dev/typecheck.sh <plugin>`, for dev/check.sh and the test
# command of the plugin's cosmic-ray.toml, run from the top of the repository. Each plugin keeps its
# tests in dev/<plugin>/tests/ (dev/architecture.md, Test), and its scripts find their modules by
# putting their own folders on sys.path; plugins share module names, such as stop, so each is
# type-checked on its own with its folders as search paths, and dev/lane/ and dev/lane/trials/,
# where testing.py and trying.py, what every plugin's tests and trials share, are kept. What the
# plugins' hooks share is lane's, reached through a link in each plugin's own folder; a folder of
# lane's code linked whole, as turn's hooks/lane/, is checked in lane alone, as git lists the link
# and not the files in it: read through that link, lane's modules meet the plugin's of the same
# names, such as call, and the check fails.
set -e

plugin=$1
paths=$({ find "plugins/$plugin" "dev/$plugin" -name '*.py' -exec dirname {} \; &&
  echo dev/lane && echo dev/lane/trials; } | sort -u)
files=$(git ls-files --cached --others --exclude-standard "plugins/$plugin" "dev/$plugin" \
  | grep '\.py$')
pyrefly check $(printf -- '--search-path %s ' $paths) $files
