#!/bin/sh
# sh, not Python: python3 is one of the tools checked here, and may be missing.

need() {
  command -v "$1" >/dev/null 2>&1 && return
  echo "$1 is not found; $2"
  exit 1
}

need python3 "install Python 3.9 or later (https://www.python.org/downloads/) and run rn again"
need jq "install it (https://jqlang.org/download/) and run rn again"
need gh "install the GitHub CLI (https://cli.github.com) and log in with push access, then run rn again"
