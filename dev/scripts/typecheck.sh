#!/bin/sh
# The type check of one plugin, as `sh dev/scripts/typecheck.sh <plugin>`, for dev/scripts/check.sh and the test
# command of the plugin's cosmic-ray.toml, run from the top of the repository. Each plugin keeps its
# tests in dev/<plugin>/tests/, as Q1 of plugins/rn/domain/best-practices/plugin/best-practice.md
# says, and its scripts find their modules by putting their own folders on sys.path. Plugins share
# module names, such as stop, so the check takes each on its own with its folders as search paths,
# and dev/lane/ and dev/lane/trials/, which keep testing.py and trying.py, what every plugin's tests
# and trials share. What the plugins' hooks share is lane's, reached through a link in each plugin's
# own folder. The check takes a folder of lane's code linked whole, as rn's hooks/lane/, in lane
# alone, as git lists the link and not the files in it: read through that link, lane's modules meet the plugin's of the same
# names, such as call, and the check fails.
set -e

plugin=$1
# The repository a product vision trial works in, such as dev/rn/tests/product-vision/tidy/, is
# the trial's subject, a project of its own, and not the plugin's code, so it's left out.
paths=$({ find "plugins/$plugin" "dev/$plugin" -name '*.py' -not -path '*/product-vision/tidy/*' \
  -exec dirname {} \; && echo dev/lane && echo dev/lane/trials; } | sort -u)
files=$(git ls-files --cached --others --exclude-standard "plugins/$plugin" "dev/$plugin" \
  | grep '\.py$' | grep -v '/product-vision/tidy/')
pyrefly check $(printf -- '--search-path %s ' $paths) $files
