"""Append the hook payload read on stdin, with the time it came, as one JSON line to $REC_LOG, and
the first line of each text of a user message in the transcript at `transcript_path` that opens
`Base directory for this skill:`, as the transcript holds it when the hook runs."""

import json
import os
import sys
import time

BASE = "Base directory for this skill:"


def texts(text):
    """Each text of the transcript's line, where it's a user message."""
    try:
        entry = json.loads(text)
    except ValueError:
        return []
    content = entry.get("message", {}).get("content") if entry.get("type") == "user" else None
    return (
        [part.get("text", "") for part in content if isinstance(part, dict)]
        if isinstance(content, list)
        else []
    )


def base_directories(path):
    if not path or not os.path.exists(path):
        return []
    with open(path) as transcript:
        return [
            said.split("\n", 1)[0]
            for text in transcript
            for said in texts(text)
            if said.startswith(BASE)
        ]


payload = json.load(sys.stdin)
kept = {
    "time": time.time(),
    "payload": payload,
    "base_directories": base_directories(payload.get("transcript_path")),
}
with open(os.environ["REC_LOG"], "a") as log:
    log.write(json.dumps(kept) + "\n")
