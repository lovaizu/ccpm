"""The moves tidy makes in a folder: each file into the folder of its kind, never over a file of
the same name, and never into a folder of its own."""

import os
import shutil

from .kinds import kind_of


def plan(folder):
    """Each move tidy would make in the folder, as (name, kind), and each file that stays, as
    (name, why), in the order of the names."""
    moves, stays = [], []
    for name in sorted(os.listdir(folder)):
        path = os.path.join(folder, name)
        if os.path.isdir(path):
            continue
        kind = kind_of(name)
        if kind is None:
            stays.append((name, "it has no extension"))
        elif os.path.exists(os.path.join(folder, kind, name)):
            stays.append((name, f"{kind}/{name} is there already"))
        else:
            moves.append((name, kind))
    return moves, stays


def move(folder, moves):
    """Makes the moves in the folder, making each kind's folder where it is not there."""
    for name, kind in moves:
        os.makedirs(os.path.join(folder, kind), exist_ok=True)
        shutil.move(os.path.join(folder, name), os.path.join(folder, kind, name))
