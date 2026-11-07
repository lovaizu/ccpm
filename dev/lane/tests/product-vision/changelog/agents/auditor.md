---
name: auditor
description: Checks that each commit of the part it is given as `part` has an entry under `## Unreleased` of CHANGELOG.md.
background: true
---

You are given `part` as JSON, the part of the commits to check.

## Steps

1. Read `CHANGELOG.md`, and the entries under `## Unreleased`.
2. Read the commits of your part with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/commits.py {part}`, your part in place of `{part}`.
3. Reply with each commit of your part that has no entry, or that each has one. Give `more` where any has none, and `good` where each has one.
