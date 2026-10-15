#!/bin/sh
# What rn runs on, checked before its first question, in sh since python3 itself may be missing.
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is not found; install Python 3.9 or later (https://www.python.org/downloads/) and call rn again"
  exit 1
fi
if ! command -v jq >/dev/null 2>&1; then
  echo "jq is not found; install it (https://jqlang.org/download/) and call rn again"
  exit 1
fi
if ! command -v gh >/dev/null 2>&1; then
  echo "gh is not found; install the GitHub CLI (https://cli.github.com) and log in with push access, then call rn again"
  exit 1
fi
