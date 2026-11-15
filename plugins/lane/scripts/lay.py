"""lay.py, as up runs it: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/lay.py <command> ...`. It runs the
code of lay.py in `domain/lay/`, whose `command` module says what each command takes and gives, with
the guard's code and the lane types of `hooks/lane/domain/`."""

from __future__ import annotations

import os
import sys

# The code lies in domain/ and hooks/lane/domain/, which come on the import path before it's
# imported, ahead of this file's own folder, so that `lay` names the package there and not this
# file.
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "hooks", "lane", "domain"))
sys.path.insert(0, os.path.join(ROOT, "domain"))

from lay.command import main

if __name__ == "__main__":
    code, out, err = main(sys.argv[1:], sys.stdin, os.environ, ROOT)
    sys.stdout.write(out)
    sys.stderr.write(err)
    raise SystemExit(code)
