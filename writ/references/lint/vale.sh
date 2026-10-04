#!/bin/sh
# Lint a document, in any language, against writ's style rules. Findings are places to judge, not failures.
# Usage: sh vale.sh <file>
npx -y @vvago/vale@3.24.0 --no-exit --config "$(dirname "$0")/vale.ini" "$1"
