"""Decides remove's command line, by which a maker removes what it made for itself without a
permission prompt that a variable path in `rm` would raise: what it takes, which paths it removes,
and the exit code by which the maker reads its result: 0 where each path is removed, and 2 with
the usage, each wrong path with why, and what to do instead, or with what the system refused."""

from __future__ import annotations

import os
import shutil
import stat
import tempfile

from fault import Answer, CantRun, answered

USAGE = """\
usage: remove <path> [<path> ...]
"""

# The characters of a shell's wildcards, which a path holds only where no shell expanded them, so
# that the path names a pattern, not a file.
WILDCARDS = "*?["

# What the maker is to do instead of a wrong path: it reaches each path it made by its exact name.
_INSTEAD = (
    "remove removed nothing. Give each file or folder you made by its exact path, absolute or"
    " from the current folder, one argument each, with no wildcard: list a folder to find the"
    " paths in it. remove removes only inside the git work tree that holds the current folder,"
    " {top}, and inside the system's temporary folder, {temp}, never the top of either, and never"
    " a git repository's .git."
)


def main(argv: list[str], cwd: str) -> Answer:
    """The exit code, stdout, and stderr of `remove` with the arguments, from the folder `cwd`.

    `<path> [<path> ...]` gives 0, printing nothing, once it removed each path, a file or a folder
    whole, a link as the link, where each lies inside the git work tree that holds `cwd` or inside
    `tempfile.gettempdir()`, is neither one's top, and neither is nor holds a `.git` within the
    work tree. A path given within another given goes with it.

    2 with the usage, each wrong path with why, and what to do instead, removing nothing, where
    no path is given, or any is empty, holds a wildcard, is missing, or lies outside those places.
    2 with what's left where the system refuses a removal."""
    temp = os.path.realpath(tempfile.gettempdir())
    top = _work_tree(os.path.realpath(cwd))
    whys = [(path, _wrong(path, cwd, top, temp)) for path in argv]
    wrong = [f"remove: {path}: {why}\n" for path, why in whys if why]
    if not argv or wrong:
        instead = _INSTEAD.format(top=top or "none here", temp=temp)
        return 2, "", USAGE + "".join(wrong) + instead + "\n"
    return answered("remove", lambda: _removed(argv, cwd))


def _work_tree(folder: str) -> str | None:
    """The top of the git work tree that holds the folder, the nearest that holds a `.git`, or
    None where none does."""
    while not os.path.lexists(os.path.join(folder, ".git")):
        parent = os.path.dirname(folder)
        if parent == folder:
            return None
        folder = parent
    return folder


def _located(path: str, cwd: str) -> str:
    """Where the path from `cwd` lies, each folder on the way followed, but not its last name, so
    that a link names itself."""
    joined = os.path.join(cwd, path).rstrip("/" + os.sep) or os.sep
    folder, name = os.path.split(joined)
    if name in ("", ".", ".."):
        return os.path.realpath(joined)
    return os.path.join(os.path.realpath(folder), name)


def _within(path: str, folder: str) -> bool:
    """Whether the path lies inside the folder, below its top."""
    path, folder = os.path.normcase(path), os.path.normcase(folder)
    return path != folder and os.path.commonpath([path, folder]) == folder


def _wrong(path: str, cwd: str, top: str | None, temp: str) -> str:
    """Why remove won't remove the path, or nothing where it will."""
    if not path:
        return "is empty, so it names nothing"
    if any(each in path for each in WILDCARDS):
        return "holds a wildcard that no shell expanded, so it names a pattern, not a path"
    located = _located(path, cwd)
    if not os.path.lexists(located):
        return "no such file or folder"
    return _placed(located, top, temp)


def _placed(located: str, top: str | None, temp: str) -> str:
    """Why the place of the path that exists is wrong, or nothing where it's inside the system's
    temporary folder, or inside the work tree and none of git's own."""
    tops = (("the git work tree", top), ("the system's temporary folder", temp))
    for name, folder in tops:
        if folder is not None and os.path.normcase(located) == os.path.normcase(folder):
            return f"is the top of {name}"
    if _within(located, temp):
        return ""
    if top is None:
        return (
            "lies outside the system's temporary folder, and the current folder is in no git"
            " work tree"
        )
    if not _within(located, top):
        return "lies outside the git work tree and the system's temporary folder"
    return _gits(located, top)


def _gits(path: str, top: str) -> str:
    """Why the path of the work tree is a git repository's own, or nothing where it isn't: it is or
    lies in a `.git`, or is a folder that holds one, as a run's worktree does."""
    if ".git" in os.path.relpath(path, top).split(os.sep):
        return "is a git repository's own, in its .git"
    if os.path.isdir(path) and not os.path.islink(path):
        for _, folders, files in os.walk(path):
            if ".git" in folders or ".git" in files:
                return "holds a git repository, whose .git would go with it"
    return ""


def _removed(argv: list[str], cwd: str) -> Answer:
    """Removes each path, skipping one that a folder given before it took. Raises CantRun where the
    system refuses one, naming it and each path left."""
    for at, path in enumerate(argv):
        located = _located(path, cwd)
        if not os.path.lexists(located):
            continue
        try:
            _remove(located)
        except OSError as error:
            left = " ".join(argv[at:])
            raise CantRun(
                f"couldn't remove {path}, as the system said: {error}. It removed each path given"
                f" before it, and left these: {left}"
            ) from None
    return 0, "", ""


def _remove(path: str) -> None:
    """Removes the file or the folder whole, or the link as the link."""
    if os.path.islink(path):
        os.remove(path)
        return
    _writable(path)
    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.remove(path)


def _writable(path: str) -> None:
    """Gives the owner full access to the path and to each file and folder in it, never through a
    link, as a read-only file or folder, such as git's objects or a tool's cache, refuses its
    removal on some systems. Each is removed next, so only the owner's access matters."""
    os.chmod(path, os.lstat(path).st_mode | stat.S_IRWXU)
    for parent, folders, files in os.walk(path):
        for name in folders + files:
            child = os.path.join(parent, name)
            if not os.path.islink(child):
                os.chmod(child, os.lstat(child).st_mode | stat.S_IRWXU)
