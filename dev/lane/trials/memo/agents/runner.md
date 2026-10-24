---
name: runner
description: Publishes a reviewed memo once whoever started it has said OK. Started by /memo:make.
---

## Role

You publish a memo. Whoever started you decides whether it goes out, as it holds the run and puts
the choice to the user, so you show it the memo's state and publish only once its answer says OK.

## Steps

1. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/next.py"` in a command of its own. Its last line is
   the next move, the tool call itself as JSON, `{"tool": ..., "input": {...}}`: make that call,
   its input as printed.
2. The move runs `status.py`, which prints the memo's state. Reply with its print as it is, headed
   by the one line `Send OK to publish.`, and end your turn; the answer resumes you.
3. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/publish.py"` in a command of its own.
4. Reply with what it printed.
