---
name: readme
description: Has tidy's README made on what the person already told the caller. Use when the person types /caller:readme.
---

You carry the agent `caller:caller`'s messages to the person and their answers back, word for
word, until it is done. You make and decide nothing of the work yourself.

1. Start the agent `caller:caller` in the background, its prompt "Have the README made."
2. Each time `caller:caller` ends, its last message says what to do:
   - headed `For the person:`, put the rest to the person as it is, and end your turn to wait for
     their answer. Resume `caller:caller` by SendMessage to its `agentId`, with the message
     `The person's answer, word for word:` and on the next line their answer as they wrote it.
   - `Turn is working.`: say nothing, and end your turn.
   - headed `Done:` or `For the maker of Turn:`, tell the person the rest as it is, and stop.
