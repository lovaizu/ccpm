"""`python3 -m tidy`, the same as the `tidy` command."""

import sys

from .cli import main

sys.exit(main(sys.argv[1:]))
