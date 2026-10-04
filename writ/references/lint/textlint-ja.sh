#!/bin/sh
# Lint a Japanese document with textlint's Japanese technical writing preset. Findings are places to judge, not failures.
# Usage: sh textlint-ja.sh <file>
npx -y -p textlint@15.8.0 -p textlint-rule-preset-ja-technical-writing@12.0.2 \
  textlint --config "$(dirname "$0")/textlintrc.json" "$1"
