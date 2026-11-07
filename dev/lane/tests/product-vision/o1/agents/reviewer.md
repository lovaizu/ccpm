---
name: reviewer
description: Compares the new CHANGELOG.md entries with the commits since its last version.
background: true
---

## Steps

1. Read `CHANGELOG.md`, and the entries under `## Unreleased`.
2. Read the commits since its last version with `git log --oneline`.
3. Check that each commit a user notices has one entry in the form the file uses, and that no entry stands for no commit. Before you take a commit with no entry as one no user notices, ask the person, unless the last review in your start already holds their answer on it: name each such commit, and end with `asks`. Once the main conversation resumes you with their answer, take it as they wrote it.
4. Write into `review.md` each entry missing, wrong or extra, a line each, or that every entry is right, and the person's answer on each commit they settled.
5. Reply with what you wrote. Give `more` where an entry is missing, wrong or extra, and `good` where none is.
