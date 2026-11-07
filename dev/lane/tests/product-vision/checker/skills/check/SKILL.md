---
name: check
description: Checks that a CHANGELOG.md has an `## Unreleased` heading.
---

Check the file by running `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/check.py CHANGELOG.md`, word for word, from the folder the file is in. It prints `ok` where the file holds the heading.

## Steps

1. Have examiner tell whether `CHANGELOG.md` has an `## Unreleased` heading, where its routes are laid.
