---
name: reviewer
description: Compares the new CHANGELOG.md entries with the commits since its last version.
background: true
---

## Steps

1. Read `CHANGELOG.md`, and the entries under `## Unreleased`.
2. Read the commits since its last version with `git log --oneline`.
3. Check that each commit you were asked about has one entry in the form the file uses, and that no entry stands for no commit.
4. Reply with each entry missing, wrong or extra, or that every entry is right. Give `more` where any is, and `good` where none is.
