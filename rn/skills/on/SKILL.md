---
name: on
description: Start an rn session. Work out with the user what they really want, write the plan on a draft pull request as it is agreed, and stop for their Plan sign-off. It writes files, commits, pushes, and opens a pull request, so run it only on an explicit /rn:on.
disable-model-invocation: true
---

# /rn:on — Start a session

## Purpose

Every piece of work and every decision in the session rests on the goal set here, so the goal must
be what the user really wants, not their first words: a plan built on the words achieves the wrong
thing, however well it is carried out, and the user finds out only at the end.

## Steps

1. Check that `python3` runs, since `pith`'s check of each result needs it; when it does not,
   say so and how to install it, and stop. When the working tree has uncommitted changes, say so
   without touching them, and stop.
2. Work in `.rn/{yyyymmdd}-{slug}/`, the slug naming what `$ARGUMENTS` asks for, on the branch the
   user is on when it is not the default branch, has no commits of its own, and is at the latest
   default branch, such as a fresh worktree's; otherwise on a new branch from the latest default
   branch. Make it in the folder this conversation runs in, never in another worktree: the next
   conversation and rn's reminder after a summary find the session there. Push it to a branch of the
   same name on the remote. When `$ARGUMENTS` says nothing, ask what they want to achieve, alone,
   since everything after rests on it.
3. Ask the user, as one point, the languages: one to write everything that goes into the repository
   in, and one to talk in, proposing what the repository and the user's instructions already set,
   or else English for the repository, which reaches the most readers later, and the one they write
   in for the talk, so a single yes settles both. Write
   `steering.md` as in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`, with what they choose, `rn`
   from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`, and the goal as `$ARGUMENTS` gives it for
   now.
4. Commit and push, in the chosen `artifact-language` as every commit from here on, with the subject
   and decision line `steering.md`'s reference gives, and open a draft pull request titled with the
   goal in one line, its body linking `steering.md` by its full URL on GitHub, since a relative link
   in a pull request body does not reach the file. Write its URL in `pr`, then commit and push with
   `● plan ── pull request opened → working out the plan`.
5. Work out the plan with the user and go on, as in `${CLAUDE_PLUGIN_ROOT}/references/conduct.md`:
   the session stops at the Plan sign-off.
