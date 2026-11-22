"""Which modules of the plugins' code a case's process holds no copy of while the case runs, so that
each script and hook that the double of Claude Code runs imports the code of the bench's copy it
runs from, as a new process of Python would."""

from __future__ import annotations

import contextlib
import sys
from collections.abc import Collection, Generator


@contextlib.contextmanager
def without(names: Collection[str]) -> Generator[None, None, None]:
    """Takes each module of the names, and each module inside one, out of the process while the
    block runs, and then puts back those it held before, as a case at another level may have
    imported them."""

    def named(module: str) -> bool:
        return module.split(".")[0] in names

    held = {module: code for module, code in sys.modules.items() if named(module)}
    for module in held:
        del sys.modules[module]
    yield
    for module in [module for module in sys.modules if named(module)]:
        del sys.modules[module]
    sys.modules.update(held)
