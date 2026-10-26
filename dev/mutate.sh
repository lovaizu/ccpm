#!/bin/sh
# The mutation testing, as `sh dev/mutate.sh [--since <commit>] [<plugin>...]`, the command
# dev/README.md, dev/githooks/pre-push and CI name; dev/mutate.py says what it does.
exec python dev/mutate.py "$@"
