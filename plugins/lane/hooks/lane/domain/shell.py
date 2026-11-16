"""How each of Lane's scripts that a role runs meets the shell: its arguments, its environment, and
the plugin's folder in, and its words and exit code out."""

from __future__ import annotations

import os
import sys
from collections.abc import Callable, Mapping, Sequence
from typing import NoReturn

# A script's main: what it takes from the shell, and its exit code, standard output, and standard
# error.
Main = Callable[[Sequence[str], Mapping[str, str], str], tuple[int, str, str]]


def run(main: Main, here: str) -> NoReturn:
    """Runs a script's main as the shell called it.

    Takes: the script's main, and the script's folder, hooks/lane/ in the plugin.
    Gives: nothing; it exits with the exit code that main gives.
    Changes: standard output and standard error, each written with main's words for it.
    Refuses: nothing.
    Carries: the exit of result.py, step.py, and item.py in S2, S5, and S6, such as S6
    `R-->>SA: exits 0`, `SP-->>SA: exits 0`, and `IP-->>SA: exits 0`, and each refusal.
    """
    code, out, err = main(sys.argv[1:], os.environ, os.path.dirname(os.path.dirname(here)))
    sys.stdout.write(out)
    sys.stderr.write(err)
    raise SystemExit(code)
