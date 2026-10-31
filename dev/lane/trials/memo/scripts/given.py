"""Prints, as one JSON object, what a run of memo works on, from the project's memo.json in the
folder it runs in: `work`, the memo to write; `entry`, its entry; `notes`, the notes it is written
from; `checklist`, what it is reviewed by; and `review`, where the review is written."""

import json

with open("memo.json", encoding="utf-8") as f:
    print(json.dumps(json.load(f)))
