---
name: on
description: Start an rn session. Work out with the user what they really want, write the plan on a draft pull request, and stop for their Plan sign-off. It writes files, commits, pushes, and opens a pull request, so run it only on an explicit /rn:on.
disable-model-invocation: true
---

# /rn:on — Start a session

## Purpose

Every piece of work and every decision in the session rests on the goal set here, so the goal must
be what the user really wants, not their first words: a plan built on the words achieves the wrong
thing, however well it is carried out, and the user finds out only at the end.

## Steps

1. Work out the plan with the user from `$ARGUMENTS` and the repository, as in
   `${CLAUDE_PLUGIN_ROOT}/references/conduct.md`.
2. Work on the current branch when it is not the default branch, otherwise on a new branch from the
   default branch, in `.rn/{yyyymmdd}-{slug}/`, the slug naming what the work produces.
3. Write `steering.md` there as in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`, in the language of
   the repository's documents, with `rn` from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`.
4. Commit and push. Link `steering.md` on the branch, and the issue it serves when there is one, from
   the body of the branch's pull request, opening a draft one when it has none, and write its URL in
   `pr`.
5. Go on as in `${CLAUDE_PLUGIN_ROOT}/references/conduct.md`: the plan is evaluated and settled, and
   the session stops at the Plan sign-off.
