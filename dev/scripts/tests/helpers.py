"""What the tests of dev/scripts stand on: the top of the repository, a git that reads no setting
of the machine the tests run on, and a PATH with one command left out."""

from __future__ import annotations

import os

TOP = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

GIT_ENV = {
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_AUTHOR_NAME": "t",
    "GIT_AUTHOR_EMAIL": "t@t",
    "GIT_COMMITTER_NAME": "t",
    "GIT_COMMITTER_EMAIL": "t@t",
}


def without(path: str, tool: str, folder: str) -> str:
    """Makes folder, which links each command of path, the first of each name, but the tool, and
    returns it as a PATH."""
    os.makedirs(folder)
    for each in path.split(os.pathsep):
        if not os.path.isdir(each):
            continue
        for name in os.listdir(each):
            command = os.path.join(each, name)
            link = os.path.join(folder, name)
            if name != tool and not os.path.lexists(link) and os.access(command, os.X_OK):
                os.symlink(command, link)
    return folder
