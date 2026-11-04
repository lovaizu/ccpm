---
name: json
description: Adds a JSON output to the notes app's `notes list`, its design settled with the person first. Use when the person types /maker:json.
argument-hint: "<what the person wants of the JSON output>"
---

You carry the person's request to the agent `maker:maker` and its messages back, word for word,
until it is done. You make and decide nothing of the work yourself.

1. Start the agent `maker:maker` in the background, its prompt the request, "$ARGUMENTS".
2. Each time `maker:maker` ends, its last message says what to do:
   - headed `For the person:`, put the rest to the person as it is, and end your turn to wait for
     their answer. Resume `maker:maker` by SendMessage to its `agentId`, with the message
     `The person's answer, word for word:` and on the next line their answer as they wrote it.
   - headed `Done:`, tell the person the rest as it is, and stop.
