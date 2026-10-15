#!/bin/sh
# What writ runs on, checked before its first question, in sh since python3 itself may be missing.
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is not found; install Python 3.9 or later (https://www.python.org/downloads/) and call writ again"
  exit 1
fi
if ! command -v jq >/dev/null 2>&1; then
  echo "jq is not found; install it (https://jqlang.org/download/) and call writ again"
  exit 1
fi
