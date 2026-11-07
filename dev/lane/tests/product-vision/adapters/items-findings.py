"""The items port of changelog's reviews: each `## Finding <n>` heading is the item F<n>."""

import json
import re
import sys

text = json.load(sys.stdin)["text"]
print(
    json.dumps(
        {"items": ["F" + n for n in re.findall(r"^## Finding ([0-9]+)", text, re.MULTILINE)]}
    )
)
