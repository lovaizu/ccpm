# Bringing an older session to the current form

## Role

You bring a session that an rn before 0.9.0 recorded to the current form, so that it goes on as a
session of this rn. Take the old record as the user's request and what was done so far, and work
the goal out again from it, since an older record may not hold why the user wants the goal.

## Steps

1. Read the old `steering.md` and whatever else the old version left in the session folder.
2. Read the rest of `${CLAUDE_PLUGIN_ROOT}/references/conduct.md`, from step 2 to the end, since
   its steps carry the session from here.
3. Read `${CLAUDE_PLUGIN_ROOT}/checklists/session/plan.md` whole, since the new `steering.md` is written in
   the form it gives.
4. When the old record does not give the two languages, choose them as conduct.md's step 3 says.
5. Write the new `steering.md` in the session folder in the form `plan.md` gives, replacing the old
   one: the two languages; `rn` as
   `jq -r .version "${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json"` prints it; `pr` as the old
   record gives the session's pull request; and the goal as the old record gives it for now.
6. Work out the plan as conduct.md's step 9, Working out the plan, says, with the session's
   branch, pull request and session folder in place of new ones, and the old record as the
   request. Ask the user only what the old record leaves unclear.
7. Write what an old design the user approved settled into the design's decisions as agreed points,
   as conduct.md's step 10 says, and what was done as Facts in Assumptions, each saying where.
8. Remove the other old files with `git rm`; they stay readable in git.
9. Stop at a new Plan sign-off, as conduct.md's step 7 says.
