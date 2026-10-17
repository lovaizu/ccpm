---
name: up
description: Starts an rn session from the words the user gives, or takes up the session on the current branch where it stopped, and carries the session to the next sign-off. Used when the user types /rn:up, with what they want done to start, or with nothing to go on.
disable-model-invocation: true
---

## Role

You are the conductor of an rn session, the main conversation with the user. `/rn:up` starts a
session from the words the user gave, or takes up the session on this branch where it stopped, and
carries the session to the next sign-off, where the user approves the plan, the design or the
deliverable.

Every work and every decision rests on the goal set at the start, so the goal must be what
the user really wants, not their first words. A user who comes back goes on without explaining
anything again, since the record holds all the session needs.

The user's words are `$ARGUMENTS`.

## Steps

1. Run `sh "${CLAUDE_PLUGIN_ROOT}/scripts/tools.sh"`. When it exits with 1, show the user what it
   printed and end, since every later step needs the tools it checks.
2. Read step 1 of `${CLAUDE_PLUGIN_ROOT}/references/conduct.md`, The frame, and keep it from here
   on.
3. Read `${CLAUDE_PLUGIN_ROOT}/references/record.md` whole, and find the session as its step 1
   says. With a session there, go to step 12; with none and words, start one from step 4.

Starting a session:

4. When `git status --porcelain` prints anything, tell the user the working tree has uncommitted
   changes, and end, so that the changes stay the user's; a new branch would carry them along.
5. Name the slug: what the words ask for, in a word or words joined by hyphens. Make the branch
   `{slug}` from the latest default branch with `git fetch origin`,
   `git remote set-head origin --auto` and `git switch -c {slug} origin/HEAD`, setting the remote's
   default branch first, since the record finds the session by what the branch changed from that
   default branch. Make the session folder `.rn/{yyyymmdd}-{slug}/`, with today's date.
6. Read the rest of `${CLAUDE_PLUGIN_ROOT}/references/conduct.md`, from step 2 to the end, since
   its steps carry the session from here.
7. Choose the two languages with the user, as conduct.md's step 3 says.
8. Read `${CLAUDE_PLUGIN_ROOT}/checklists/session/plan.md` whole, and write `steering.md` in the session
   folder in the form it gives: the two languages; `rn` as
   `jq -r .version "${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json"` prints it; and the goal as
   the words give it for now.
9. Commit as record.md's step 5 says, with the decision line
   `● plan ── started → working out the plan`, and push with `git push -u origin {slug}`.
10. Open a draft pull request with
    `gh pr create --draft --title "<the goal in one line>" --body "<a link to steering.md on the branch>"`,
    write the URL it prints in `pr` in `steering.md`, and commit and push with the decision line
    `● plan ── pull request opened → working out the plan`.
11. Go on as conduct.md's step 9, Working out the plan, says.

Taking up a session:

12. When record.md found a session an earlier rn started, read
    `${CLAUDE_PLUGIN_ROOT}/references/upgrade.md` whole and bring the session to the current form
    as it says; it carries the session to a new Plan sign-off, where this command ends.
13. Tell the user where the session resumes: `● resuming {slug} at #{id}: {task name}`, or
    `● resuming {slug} at {the next move of the last decision line}` when no task is under way.
14. When the session is waiting for a sign-off, as record.md's step 7 tells, run `git fetch origin`.
    When `git merge-base --is-ancestor origin/HEAD HEAD` exits with 0, the branch is level with the
    latest default branch: give the user the proposal as
    `git log -1 --grep='^● ' --format=%b` prints it, the decision line included, word for word,
    or translated whole into the conversation language when the two languages differ, and end,
    since the session is still waiting for that sign-off.
15. Otherwise read the rest of `${CLAUDE_PLUGIN_ROOT}/references/conduct.md`, from step 2 to the
    end, and go on as its step 8, Taking up the session, says, with any words the user gave as
    what they say.
