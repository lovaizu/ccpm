---
name: make
description: Writes a memo of the project's notes, has it reviewed against the checklist, and publishes it once the user has said OK. Use when the user asks for the project's memo.
---

## Role

You hold this run. Each subagent does one part; you pass on what each needs and put the user's
decision to publish to them.

## Steps

1. Start the `memo:writer` agent with the prompt `Write the memo.`
2. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/given.py"`, and start the `memo:reviewer` agent with
   the prompt `{"work": "<work>", "checklist": "<checklist>", "notes": <notes>, "review": "<review>"}`,
   each value as it printed.
3. Start the `memo:runner` agent with the prompt `Publish the memo.` When it replies, show the user
   its reply and ask whether to publish; once the user has said OK, send `OK` to the runner with
   SendMessage, which resumes it.
4. Reply with what the runner said last.
