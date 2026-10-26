"""turn's adapter of lane's items port: given {"input": <path>, "text": <its text>} on stdin, prints
{"items": [<ID>, ...]}, the ID of each item of a turn checklist in the order it stands, as turn's
scripts/items.py reads them; lane's own reading takes list items instead. A Python 3 script on the
standard library alone, which lane runs in the plugin, where it finds items.py in the plugin's
scripts/ by its own real path, as rn takes it through a link."""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "scripts"))

from items import items

if (
    __name__ == "__main__"  # pragma: no mutate
):
    print(json.dumps({"items": [i for _, i in items(json.load(sys.stdin)["text"])]}))
