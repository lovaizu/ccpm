---
name: gm
description: Ask rn to revise what it last presented — /rn:gm <feedback> takes the feedback as written, plain /rn:gm takes it from the review left on the session PR — record it in steering.md, and stop so /rn:up revises in a fresh conversation. Has side effects (commits, pushes) — run only on explicit /rn:gm.
disable-model-invocation: true
---

# /rn:gm — Revise

Records the user's request for a revision where a fresh conversation will find it, so the revision
starts from the feedback and not from a summary of it.

## Steps

1. **Enter the session** as in Entering a session in
   `${CLAUDE_PLUGIN_ROOT}/references/steering.md`.
2. **Take the feedback.** `$ARGUMENTS`, trimmed, not empty → that text, word for word. Empty → the
   review the user left on the session PR since the branch's latest commit: review threads that
   are unresolved and whose last comment does not open with `<!-- rn -->` (`gh api graphql` on
   `reviewThreads`, paginated), and review summaries submitted after that commit — each word for
   word, a thread with its id so the reply finds it. rn replies from the same account the user
   reviews from, so the marker, not the author, tells them apart. With no PR or nothing there, ask
   for the feedback as `/rn:gm <feedback>` and stop.
3. **Hand off** as in Handing off to a fresh conversation in
   `${CLAUDE_PLUGIN_ROOT}/references/conductor.md`, with that feedback as `Feedback`.
