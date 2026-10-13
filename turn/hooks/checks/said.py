"""What Claude has said to the user in the conversation so far."""

import json


def said(data):
    path = data.get("transcript_path")
    if not path:
        return ""
    texts = []
    with open(path) as f:
        for line in f:
            event = json.loads(line)
            if event.get("type") == "assistant":
                texts += [p["text"] for p in event["message"]["content"] if p.get("type") == "text"]
    return "\n".join(texts)
