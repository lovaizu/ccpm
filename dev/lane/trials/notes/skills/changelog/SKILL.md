---
name: changelog
description: Writes CHANGELOG.md entries for the project's changes since its last entry, shows them to the user, and commits CHANGELOG.md once the user has said OK. Use when the user asks to update the changelog.
---

## Role

You hold this run. `changelog-writer` writes the entries; you show them to the user and commit
`CHANGELOG.md` only once the user has said OK, since the changelog speaks for the project to its
users.

## Steps

1. Start the `notes:changelog-writer` agent with the user's request as its prompt, word for word:
   $ARGUMENTS
2. When it returns, show the user `git diff CHANGELOG.md` and ask whether to commit it.
3. Commit only once the user has said OK, with `git add CHANGELOG.md` and
   `git commit -m "changelog: update"`. If the user asks for a change, have it made and ask again.
