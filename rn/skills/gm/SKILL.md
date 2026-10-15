---
name: gm
description: Records the user's feedback on the sign-off the rn session on the current branch is waiting for, from the words given or from the user's comments on the pull request, and stops, so the session goes back to before that sign-off. Used when the user types /rn:gm instead of approving a proposal.
disable-model-invocation: true
---

## Role

You are the conductor of an rn session. `/rn:gm` records the user's feedback on the sign-off the
session is waiting for and stops, so that the session goes back to before that sign-off. Feedback
shows that the user and the session do not yet see the same thing. Keep the user's words whole,
since every work of the session is measured by them, and a summary would shift that measure.

The user's words are `$ARGUMENTS`.

## Steps

1. Read step 1 of `${CLAUDE_PLUGIN_ROOT}/references/conduct.md`, The frame, and keep it from here
   on.
2. Read `${CLAUDE_PLUGIN_ROOT}/references/record.md` whole, and find the session as its step 1
   says.
3. When the session is not waiting for a sign-off, as record.md's step 7 tells, tell the user what
   the session is doing, from the last decision line, and end, since there is no sign-off to
   answer.
4. Take the feedback from the words given. With none, take every comment the `gh` user wrote on
   the pull request after the stop commit, on a line or on the whole, each with its place and URL:

   ```
   stop=$(git log -1 --grep='^● ' --format=%H)
   since=$(TZ=UTC git log -1 --format=%cd --date=format-local:%Y-%m-%dT%H:%M:%SZ "$stop")
   me=$(gh api user --jq .login)
   n=$(gh pr view "<pr>" --json number --jq .number)
   gh api --paginate "repos/{owner}/{repo}/pulls/$n/comments" --jq ".[] | select(.user.login == \"$me\" and .created_at > \"$since\") | \"\(.path):\(.line // .original_line) \(.html_url)\n\(.body)\n\""
   gh api --paginate "repos/{owner}/{repo}/issues/$n/comments" --jq ".[] | select(.user.login == \"$me\" and .created_at > \"$since\") | \"the whole pull request \(.html_url)\n\(.body)\n\""
   gh api --paginate "repos/{owner}/{repo}/pulls/$n/reviews" --jq ".[] | select(.user.login == \"$me\" and .submitted_at > \"$since\" and .body != \"\") | \"the whole pull request \(.html_url)\n\(.body)\n\""
   ```

5. With neither, ask the user for their feedback, and end.
6. Write the feedback whole, in the user's words, to a `feedback` item in `open/`, named as
   record.md's step 3 says.
7. Commit and push as record.md's step 5 says, with the decision line its step 6 gives after
   `/rn:gm`.
8. Give the user what `git log -1 --format=%b` prints, then
   `Say "go on", or /clear and then /rn:up.`, and end.
9. When the user says to go on, read the rest of `${CLAUDE_PLUGIN_ROOT}/references/conduct.md`,
   from step 2 to the end, and go on as its step 8, Taking up the session, says.
