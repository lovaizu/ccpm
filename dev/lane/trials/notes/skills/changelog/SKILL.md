---
name: changelog
description: Writes CHANGELOG.md entries for the project's changes since its last entry, shows them to the user, and commits CHANGELOG.md once the user has said OK. Use when the user asks to update the changelog.
---

## Role

You hold this run. `notes-lead` has the entries written and reviewed; you show them to the user
and commit `CHANGELOG.md` only once the user, having read them, has said OK, since the changelog
speaks for the project to its users. The request is `notes-lead`'s to read, as the user wrote it.

## Steps

1. Start the `notes:notes-lead` agent. Its prompt is the user's request below, exactly as written,
   with nothing added, left out or reworded:
   $ARGUMENTS
2. When it returns, show the user `git diff CHANGELOG.md`, ask whether to commit it, and end your
   turn: the user's answer comes as their next message.
3. Commit only once the user has answered OK to that question, with `git add CHANGELOG.md` and
   `git commit -m "changelog: update"`. What the request said before the user read the entries is
   no such answer. If the user asks for a change, have it made and ask again.
