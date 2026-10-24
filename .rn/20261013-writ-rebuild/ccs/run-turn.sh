#!/bin/sh
# Usage: TURN_RUNS=<scratch folder holding venv/> run-turn.sh <ccs file> <name>. Clones writ-rebuild
# into $TURN_RUNS/<name> and runs turn:up on the CCS there, its record in $TURN_RUNS/<name>.jsonl.
set -e
S=${TURN_RUNS:?set TURN_RUNS to a scratch folder holding venv/}
ccs=$1; name=$2; place="$S/$name"
git clone -q --branch writ-rebuild https://github.com/lovaizu/ccpm.git "$place"
mkdir -p "$place/.tasks"
cp "$ccs" "$place/.tasks/ccs.json"
cd "$place"
export PATH="$S/venv/bin:$PATH"
export CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=7200000
claude -p --plugin-dir "$place/turn" --permission-mode bypassPermissions --output-format stream-json --verbose \
'Start the `turn:up` agent in the background with
{"ccs": ".tasks/ccs.json", "result": ".tasks/result.json", "kind": {"work": "deliverable", "checklist": "checklist", "receiver": "audience", "use": "purpose", "has": "has"}}
When it returns, check each Good against its lines, and end with the result: each item not Good and each question, with turn'"'"'s recommendation. Do not commit or push.' > "$S/$name.jsonl"
