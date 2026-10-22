"""Prints the state of the memo in the folder it runs in: the lines of the memo and the review."""

import json

with open("memo.json", encoding="utf-8") as f:
    run = json.load(f)
for name in (run["work"], run["review"]):
    try:
        with open(name, encoding="utf-8") as f:
            print(f"{name}: {len(f.read().splitlines())} lines")
    except OSError:
        print(f"{name}: missing")
