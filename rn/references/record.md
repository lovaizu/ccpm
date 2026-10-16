# The record of an rn session

## Role

You keep the record of an rn session, so that a fresh conversation and every later version of rn
go on from it alone: the user may clear the conversation at any stop, and the next conversation
knows only what the record holds. Keep its layout, names and markers exactly as written here,
since rn's commands, scripts and hooks find their way by them.

The record is the session folder `.rn/{yyyymmdd}-{slug}/`, the README, the design document and
the verification document its plan names, and git. The plan is `steering.md` in the session
folder, in the form `${CLAUDE_PLUGIN_ROOT}/checklists/session/plan.md` gives.

## Steps

1. Find the session, in this order:

   - The `steering.md` this conversation has been working on, when there is one.
   - Otherwise, the one the current branch changed whose `status` is not `finished`.

     Run `git fetch origin`; when `git rev-parse --verify --quiet origin/HEAD` prints nothing, run
     `git remote set-head origin --auto`; then list the candidates with
     `git diff --name-only $(git merge-base HEAD origin/HEAD) HEAD -- '.rn/*/steering.md'` and
     read the `status` in each one's front matter.

   - None, and `/rn:up` was given words: `/rn:up` starts a session from them.
   - None, and no words: tell the user there is no session on this branch, and that they can check
     out the session's branch or give `/rn:up` what to do; end.
   - Only sessions whose `status` is `finished`: tell the user the session is finished; end.

   Then read the `rn` field of the session's `steering.md`. At `0.9.0` or later, take the session
   up as it stands. With no `rn` field, or a lower one, an earlier rn started it: `/rn:up` brings
   it to the current form as `${CLAUDE_PLUGIN_ROOT}/references/upgrade.md` says; any other command
   asks the user to run `/rn:up` first, and ends.

2. Keep the session folder in this layout:

   - `steering.md`: the plan.
   - `open/`: what is not yet settled, one file per item.
   - `decisions/`: what each work was asked to say, one file per work.
   - `tasks/`: each task handed to turn and the CCS turn wrote back.

   Commit `decisions/` and `tasks/` with the decision that made them. Leave turn's evidence, under
   `.turn/` at the top of the repository, uncommitted.

3. Name each item in `open/` as `{NN}-{kind}-{about}.md`, since rn's checks find each item by these
   names:

   - `{NN}` is one more than the highest number in `open/`, or `01` when it is empty.
   - `{kind}` is `report`, `feedback` or `notes`.

     A `report` is the report `up.py report` printed for one work; a `feedback` item, the user's
     words from `/rn:gm`, whole, in their own language; a `notes` item, a question being put to
     the user, a proposal being made, or where the session stands on `/rn:dn`.

   - `{about}` is what the item is about: `plan`, `design`, `task-{id}` or `deliverable`,
     `question` for a question and `proposal` for a proposal.

   For example `04-report-task-3.md`.

4. Settle an item in the commit that records what was decided on it, by removing it from `open/`
   with `git rm` in that commit. In that commit's message, copy the item whole under its file name,
   each line indented by four spaces, and write what was decided on each shortfall of a report,
   each on a line of its own:

   ```
   - Good A1: <what the user gains, at path:line>
   - More A1: <what the user will struggle with, at path:line>
     → fixed: <how> | → let go: <why> | → to the user: <the question, or back to the plan or the design>
   ```

   `A1` stands for the ID of the criterion the line is about, and the `→` line takes one of its
   three forms, indented under its More.

5. Write every commit you make with a subject line saying what it records, in the artifact
   language, and end its message with the decision line, then push:

   ```
   git commit -F - <<'EOF'
   rn: settle the report on #3 move src/cart

   <the body, when the commit settles an item or stops for the user>

   ● #3 move src/cart ── decided: purpose fulfilled → #4 Deliverable sign-off
   EOF
   git push
   ```

   The decision line is `● {#id task name | plan | design | deliverable} ── {what was decided} →
   {next move}`, the first in a session being `● plan ── started → working out the plan`. Keep
   `●`, `──`, `→`, `waiting for`, `paused at`, `approved` and `feedback in`, and `Good` and `More`
   with their criterion ID at the start of a line, as written here whatever the artifact language.

6. At each of the session's four kinds of stop, write the decision line and leave `open/` as
   follows:

   - At a sign-off, `● #{id} {sign-off name} ── proposed: {what} → waiting for #{id} {sign-off name}`, with the proposal as the message body and nothing left in `open/`.
   - After `/rn:ty`, `● #{id} {sign-off name} ── approved → {next}`, with nothing left in `open/`.

     `{next}` is `planning the tasks` after the Design sign-off, `finished` after the Deliverable
     sign-off, and otherwise the first task in `steering.md` not yet `[x]`.

   - After `/rn:gm`, `● #{id} {sign-off name} ── feedback in {file} → {next}`, with the `feedback` item left in `open/`.

     `{next}` is `working out the plan again` at the Plan sign-off, `working out the design again`
     at the Design sign-off, and `tasks for it` at the Deliverable sign-off.

   - On a pause by `/rn:dn`, `● {#id task name | plan | design} ── {how far it came} → paused at {#id task name | plan | design}`, with whatever is unsettled and a `notes` item on where the session stands left in `open/`.

7. Read where the session stands from the last decision line on the branch, the last line beginning
   `● ` in the message `git log -1 --grep='^● ' --format=%B` prints:

   - When it ends `→ waiting for #{id} {sign-off name}`, the session is waiting for that sign-off,
     and the commit it ends is the stop commit.
   - Otherwise the session goes on from the next move the line names.
