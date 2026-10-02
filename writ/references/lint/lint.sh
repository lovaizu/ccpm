#!/bin/sh
# Lint a document against writ's style rules. Findings are places to judge, not failures.
# Usage: sh lint.sh <file>
set -u
here=$(cd "$(dirname "$0")" && pwd)
file=$1
command -v npx >/dev/null 2>&1 || { echo "npx not found: check the style rules by reading."; exit 0; }
npx -y @vvago/vale@3.24.0 --no-exit --config "$here/vale.ini" "$file"
# Japanese text gets textlint's Japanese technical writing preset as well.
if grep -q '[ぁ-んァ-ン]' "$file"; then
  npx -y -p textlint@15.8.0 -p textlint-rule-preset-ja-technical-writing@12.0.2 \
    textlint --config "$here/textlintrc.json" "$file"
fi
exit 0
