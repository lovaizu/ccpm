"""What turn:up runs for what must come out the same on every run, and each role for what it is
given: the steps are run.py's. Python looks first in this file's folder, so run.py is found."""

import sys

import run

sys.exit(run.main(sys.argv[1:], sys.stdin))
