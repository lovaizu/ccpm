"""What Claude has said to the user in the conversation so far. On Stop, the last message may not
be in the record yet, so it is taken from the hook's input."""

import json


def said(data):
    path = data.get("transcript_path")
    texts = [data.get("last_assistant_message") or ""]
    if not path:
        return texts[0]
    with open(path) as f:
        for line in f:
            event = json.loads(line)
            if event.get("type") == "assistant":
                texts += [p["text"] for p in event["message"]["content"] if p.get("type") == "text"]
    return "\n".join(texts)
