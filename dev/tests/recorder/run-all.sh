#!/bin/sh
# Record the three states into <out-folder>, as the records of dev/tests/recorded/ were made.
# Usage: sh run-all.sh <runs-folder> <out-folder>
# The runs folder must not exist yet; it keeps each run's hooks.jsonl, stream.jsonl, and repo.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
runs=$1
out=$2
version=$(claude --version | cut -d' ' -f1)
mkdir -p "$runs" "$out"
for n in 1 2 3; do python3 "$here/record.py" two-subagents "$runs/s2-$n" & done
python3 "$here/record.py" skill-command-while-subagent "$runs/s1" &
python3 "$here/record.py" compact-while-subagent "$runs/s3" &
wait
python3 "$here/convert.py" "$out/claude-code-$version-skill-command-while-subagent.jsonl" \
  "the setup of the run in which the person types a skill command of rec while a background subagent started in the run still runs" \
  "-" "$runs/s1"
python3 "$here/convert.py" "$out/claude-code-$version-two-subagents.jsonl" \
  "the setup of the three runs in which one assistant message makes two Agent calls of rec:sleeper in the background" \
  "start two sleepers in the background in one message" \
  "$runs/s2-1:in run 1" "$runs/s2-2:in run 2" "$runs/s2-3:in run 3"
python3 "$here/convert.py" "$out/claude-code-$version-compact-while-subagent.jsonl" \
  "the setup of the run in which the person types /compact while a background subagent still runs" \
  "start sleeper in the background" "$runs/s3"
