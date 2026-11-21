"""Which state of a bench each Given leaves, kept once for its arguments, so that each case that
takes the same Given starts from a copy of that state in place of playing the Given again. A Given
of rn's walkthrough plays a run from /rn:up on, some 2300 runs of a script or a hook, the same for
each case that takes it."""

from __future__ import annotations

import copy
import functools
import os
import shutil
from collections.abc import Callable
from typing import Any, Protocol, TypeVar

Given = TypeVar("Given", bound=Callable[..., Any])


class Kept(Protocol):
    """A bench whose Givens are kept: its files, all under `root`, and the folder that keeps a copy
    of them for each Given played, or None where its Givens are played each time."""

    root: str
    givens: str | None


# The copy of the bench's files that each Given left, and a copy of what it gave, by the bench's
# root, the Given's name, and its arguments.
_KEPT: dict[tuple[str, str, str], tuple[str, Any]] = {}


def kept(play: Given) -> Given:
    """The Given, played once for each bench root and arguments where the bench keeps its Givens.

    Takes: a function whose first argument is a Kept bench, and whose other arguments' repr tells
    them apart, such as dicts and strings; each path in what it gives lies under the bench's root
    or outside the bench, as the bench's files come back at the same root.
    Gives: a function that plays the Given and keeps a copy of the bench's files and of what it
    gave, the first time; and each time after, puts the bench's files back as the Given left them,
    in place of what the root held, and gives a copy of what it gave, which the case may change.
    """

    @functools.wraps(play)
    def played(bench: Kept, *args: Any, **kwargs: Any) -> Any:
        if bench.givens is None:
            return play(bench, *args, **kwargs)
        key = (bench.root, play.__qualname__, repr((args, sorted(kwargs.items()))))
        if key in _KEPT:
            folder, gave = _KEPT[key]
            shutil.rmtree(bench.root)
            shutil.copytree(folder, bench.root, symlinks=True)
            return copy.deepcopy(gave)
        gave = play(bench, *args, **kwargs)
        folder = os.path.join(bench.givens, str(len(_KEPT)))
        shutil.copytree(bench.root, folder, symlinks=True)
        _KEPT[key] = (folder, copy.deepcopy(gave))
        return gave

    return played  # type: ignore[return-value]
