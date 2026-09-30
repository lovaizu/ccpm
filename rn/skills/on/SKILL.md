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

1. Work on the current branch when it is not the default branch and holds no session, otherwise on a
   new branch from the default branch, in `.rn/{yyyymmdd}-{slug}/`, the slug naming what
   `$ARGUMENTS` asks for.
2. Write `steering.md` there as in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`, in the language of
   the repository's documents, with `rn` from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json` and
   the goal as `$ARGUMENTS` gives it for now.
3. Commit and push. Link `steering.md` on the branch, and the issue it serves when there is one, from
   the body of the branch's pull request, opening a draft one titled with the goal in one line when it
   has none. Write its URL in `pr`, commit, and push. Whenever the goal changes, keep the title to it.
4. Work out the plan with the user from `$ARGUMENTS` and the repository, and go on, as in
   `${CLAUDE_PLUGIN_ROOT}/references/conduct.md`: the session stops at the Plan sign-off.
