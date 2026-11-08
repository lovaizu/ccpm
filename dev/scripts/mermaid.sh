#!/bin/sh
# Every Mermaid diagram of the repository parsed as GitHub parses it, run from the top of the
# repository by dev/scripts/check.sh. dev/scripts/mermaid.mjs says how. The parser comes with
# dev/scripts/package-lock.json. Without it, the check fails, as a skipped check would pass a
# diagram that nobody parsed.
here=$(dirname "$0")
if ! command -v node >/dev/null 2>&1 || [ ! -d "$here/node_modules/mermaid" ]; then
  echo "mermaid.sh: can't parse the Mermaid diagrams, as node or $here/node_modules is missing." \
    "Fix: install Node.js, then run \`npm ci --ignore-scripts\` in $here" >&2
  exit 1
fi
exec node "$here/mermaid.mjs"
