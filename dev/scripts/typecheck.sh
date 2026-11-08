#!/bin/sh
# The type check of one plugin, run from the top of the repository as
# `sh dev/scripts/typecheck.sh <plugin>`, for dev/scripts/check.sh and the test command of the
# plugin's cosmic-ray.toml.
# - Each plugin keeps its tests in dev/<plugin>/tests/, as Q1 of
#   plugins/rn/domain/best-practices/plugin/best-practice.md says, and its scripts find their modules
#   by putting their own folders on sys.path.
# - Plugins share module names, such as stop, so the check takes each plugin on its own. Its search
#   paths are the plugin's folders, plus dev/lane/ and dev/lane/trials/, which keep testing.py and
#   trying.py for every plugin's tests and trials.
# - The plugins' hooks share lane's code through a link in each plugin's folder. Where that link is a
#   whole folder, such as rn's hooks/lane/, the check reads the code only in lane. git lists the link
#   and not the files in it, and lane's modules read through the link would clash with the plugin's
#   modules of the same names, such as call.
set -e

plugin=$1
# The repository a product vision trial works in, such as dev/rn/tests/product-vision/tidy/, is
# the trial's subject, a project of its own, and not the plugin's code, so it's left out.
paths=$({ find "plugins/$plugin" "dev/$plugin" -name '*.py' -not -path '*/product-vision/tidy/*' \
  -exec dirname {} \; && echo dev/lane && echo dev/lane/trials; } | sort -u)
files=$(git ls-files --cached --others --exclude-standard "plugins/$plugin" "dev/$plugin" \
  | grep '\.py$' | grep -v '/product-vision/tidy/')
pyrefly check $(printf -- '--search-path %s ' $paths) $files
