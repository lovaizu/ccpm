---
name: on
description: Start a new rn work session from a goal — restate the goal, decompose it into verifiable tasks in a steering.md, open a draft PR for review, then begin task #1 once approved. Has side effects (writes files, commits, pushes, opens a PR) — run only on explicit /rn:on.
disable-model-invocation: true
---

# /rn:on — Start a session

Turns a goal into verifiable tasks in `steering.md`, opens a draft PR, then executes task #1 after approval.

## Steps

1. **Plan the session.** Read `${CLAUDE_PLUGIN_ROOT}/references/planning-workflow.md` and run it in sequence.

2. **Check version.** Compare the newly written `steering.md`'s `Rn version:` line to the installed plugin's version (`${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`'s `version` field); on a mismatch, run `${CLAUDE_PLUGIN_ROOT}/references/migration-workflow.md` first — on a match, do nothing. Since step 1 just stamped that line from this same installed version, this branch can never actually fire here — it's kept only so `on`'s step matches `dn`/`up`/`ty`/`gm`'s, not because `on` has its own drift to detect.

3. **Begin task #1.** After approval, read `${CLAUDE_PLUGIN_ROOT}/references/task-execute-workflow.md` then `${CLAUDE_PLUGIN_ROOT}/references/task-verify-workflow.md` and execute task #1 following them in sequence.
