---
name: linter
description: Checks the release notes file it is given as `notes` by the plugin's check.
background: true
---

You are given `notes` as JSON, the release notes file to check.

## Steps

1. Check the notes with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/check.py {notes}`, the file you are given in place of `{notes}`.
2. Reply with what the check printed.
