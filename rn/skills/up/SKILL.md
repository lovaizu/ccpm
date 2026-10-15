---
name: up
description: Start an rn session from what the user asks for, or take up the session on the branch where it stopped, and carry the work to the next sign-off. It writes files, commits, pushes, and on a start opens a pull request, so run it only on an explicit /rn:up.
disable-model-invocation: true
---

# /rn:up — Start or go on

## Role

Every piece of work and every decision in a session rests on the goal set at its start, so the
goal must be what the user really wants, not their first words; and the user can clear the
conversation at any stop and come back without explaining anything again, since the session goes
on from where they left it by what its record says. One command serves both, since the record
tells whether a session is there.

## Steps

What the user gave:

$ARGUMENTS

1. Run `sh "${CLAUDE_PLUGIN_ROOT}/scripts/tools.sh"`; if it exits with 1, show what it printed and
   end, since rn and turn run on python3, jq and gh.
2. Read `${CLAUDE_PLUGIN_ROOT}/references/record.md` whole, and find the session as it says. A
   session there → go to step 6. None, and no words were given → say so as it says, and end.
3. Start a session: when the working tree has uncommitted changes, say so without touching them,
   and end. Work on a new branch from the latest default branch, pushed to a branch of the same
   name on the remote, in `.rn/{yyyymmdd}-{slug}/`, the slug naming what the words ask for.
4. Ask the user, as one point, the languages: one to write everything that goes into the
   repository in, and one to talk in, proposing what the repository and the user's instructions
   already set, or else English for the repository, which reaches the most readers later, and the
   one they write in for the talk, so a single yes settles both. Write `steering.md` in the form
   `${CLAUDE_PLUGIN_ROOT}/checklists/plan.md` gives, with what they chose, `rn` from
   `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`, and the goal as the words give it for now.
5. Commit and push, in the chosen artifact language as every commit from here on, with the subject
   and the decision line record.md gives, and open a draft pull request titled with the goal in one
   line, its body linking `steering.md`. Write its URL in `pr`, commit and push with
   `● plan ── pull request opened → working out the plan`, and go on as
   `${CLAUDE_PLUGIN_ROOT}/references/conduct.md` says from Working out the plan: the session stops
   at the Plan sign-off.
6. Take up the session: when an older rn started it, bring it to the current form as record.md
   says instead. Say where it resumes, in the `conversation-language` of `steering.md`:

   ```
   ● {resuming {slug} at #{id}: {task name}, or at the next move of the last decision line}
   ```

7. When the last decision line ends `waiting for #{id} {sign-off name}`, and the branch is level
   with the latest default branch, give the proposal again as that commit's message body prints it,
   the decision line included, translated into the conversation language when the two differ,
   adding nothing and leaving nothing out, and end. Otherwise take up the session as conduct.md
   says from Taking up the session, with any words the user gave as what they say to you.
