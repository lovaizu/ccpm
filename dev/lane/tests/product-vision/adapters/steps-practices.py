"""The steps port of changelog's practices: each intent the start's `intents` names is a step list,
each practice of it a step with its trace, as domain/practices.json keeps them."""

import json
import os
import sys

with open(os.path.join(os.environ["CLAUDE_PLUGIN_ROOT"], "domain", "practices.json")) as f:
    practices = json.load(f)
values = json.load(sys.stdin)["values"]
lists = [
    {"list": q, "steps": [{"says": p["says"], "lanes": [p["trace"]]} for p in practices[q]]}
    for q in values.get("vital_few") or []
    if q in practices
]
print(json.dumps({"lists": lists}))
