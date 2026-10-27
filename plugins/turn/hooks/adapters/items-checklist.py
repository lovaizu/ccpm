"""turn's adapter of lane's items port: given {"input": <path>, "text": <its text>} on stdin, prints
{"items": [<ID>, ...]}, the ID of each item of a turn checklist in the order it stands, as turn's
scripts/items.py reads them; lane's own reading takes list items instead. A Python 3 script on the
standard library alone, which lane runs beside its proposal and in the plugin, with
CLAUDE_PLUGIN_ROOT the plugin's folder, where it finds items.py in scripts/, as rn takes it through
a link."""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.environ["CLAUDE_PLUGIN_ROOT"], "scripts"))

from items import items

print(json.dumps({"items": [i for _, i in items(json.load(sys.stdin)["text"])]}))
