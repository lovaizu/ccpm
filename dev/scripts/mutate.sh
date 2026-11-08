#!/bin/sh
# The mutation testing, as `sh dev/scripts/mutate.sh [--since <commit>] [<plugin>...]`, the command
# dev/README.md, dev/scripts/pre-push.sh and CI name. dev/scripts/mutate.py says what it does.
exec python dev/scripts/mutate.py "$@"
