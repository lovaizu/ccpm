"""Publishes the memo in the folder it runs in, standing in for sending it out: prints its title."""

import json

with open("memo.json", encoding="utf-8") as f:
    run = json.load(f)
print(f"Published {run['work']}.")
