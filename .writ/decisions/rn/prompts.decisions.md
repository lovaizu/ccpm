# What rn's prompts say

The work is rn's three skills, `rn/skills/up/SKILL.md`, `rn/skills/ty/SKILL.md` and
`rn/skills/gm/SKILL.md`, the conductor's steps for each command, as the design (`dev/rn/design.md`)
gives them. This unit builds what the first unit needs, from `/rn:up <what they want>` to the plan
sign-off, approved with `/rn:ty` or sent back with `/rn:gm`, and going on with `/rn:up` in a fresh
conversation; later units add the documents, the tasks, the deliverable and the lessons to the same
skills.

## Each skill

- Each runs only when the user types it (`disable-model-invocation: true`), since each commits and
  pushes; the conductor never commits or pushes on the default branch, never merges, and marks the
  pull request ready only after the lessons (a later unit).
- Each runs rn's script as `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/rn.py" <subcommand>` from the
  top of the repository, uses what it prints as printed, and on a stop does what it says.
- Everything said to the user is in the plan's `conversation-language`, everything written to the
  repository in its `artifact-language`; before the plan has them, the user's own language and
  the repository's (English where it has none).
- Every commit's message says what it records, and holds the options weighed with their reasons
  for a decision, and each feedback with its answer, since the documents keep only what holds now.
  Every decision is committed and pushed before the work that follows it.
- The steps are held by hooks only where the design names a guard, the four in
  `.writ/decisions/rn/hooks.decisions.md`; every other bound and step rests on the step and its
  reason, until a trial shows the conductor skipping one.

## `/rn:up`

- `rn.py session` tells whether the branch holds a session. None and no words: say there is none
  on this branch, and that `/rn:up <what you want>` starts one; end. A session: go on from where
  `state.json` stands, as below, with any words the user gave as what they say now.
- Starting: with uncommitted changes in the working tree, say so without touching them and end.
  Make a branch named by a slug for the request, lowercase words joined by hyphens, from the latest
  default branch; `rn.py start <slug>`; commit and push the folder; open a draft pull request
  titled with the request in a line, its body linking the plan's path, and keep its URL as the
  plan's `pr` in the plan's decisions.
- Asking: find the points to decide from the user's words, the repository and its documentation,
  and confirm each with the user, looked-up ones included, one per message, in the form the README
  shows (`rn/README.md`, "Points to decide"): the list of points, the settled ones with their
  outcome and the current one marked; the conclusion and its grounds; the options, the recommended
  one first, each with its trade-off and whether it can be undone; one question on that point
  alone, answered by a letter or in the user's own words. Answers to the user's own questions, and
  slips rn corrected that leave nothing to decide, come first, apart from the points.
- Each answer goes into `<session>/decisions/plan.decisions.md` as what the plan must say, and is
  committed and pushed with the options weighed before the next point.
- The plan's front matter values are decisions too: `rn` from
  `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`, `pr`, `status: running` and the two
  languages: the conversation's the one the user writes in, the artifact's the one the repository
  is written in, English where it has none.
- When no point is left: `rn.py state stage=plan`; `rn.py ccs plan <session>/steering.md --kind
  plan --receiver <the user at the plan sign-off, and the conductor in any later conversation>
  --use <the goal as the decisions give it> --has . --decisions
  <session>/decisions/plan.decisions.md`, the user at the sign-off having their repository;
  start the `turn:up` agent in the background with the call it printed and wait for it.
- While turn runs: pass each message its agents send on to the user in the conversation language,
  judging nothing and asking nothing; when the user says to stop, stop the run.
- When turn returns: read each Good at its lines; put each question to the user as a point, as
  above, write the answer into the decisions and call turn again; fix by hand what falls short of
  the purpose in a few lines, or, where the decisions must change much, change them and call turn
  again. Commit and push the plan, its CCS and turn's result, which keeps turn's lessons for the
  last unit.
- The plan sign-off: `rn.py state signoff=plan`; commit and push; give the user what `rn.py
  proposal plan` prints, as printed, then `/rn:ty to approve, /rn:gm <feedback> to ask for a
  change.`; end.
- Going on, by what `state.json` holds: at `asking`, the decisions kept so far are settled and the
  next point is asked; at a sign-off with feedback kept, find the point behind the feedback, one rn
  decided wrong or did not ask, confirm it as above, put the answer into the decisions, clear the
  feedback, have the work made again and stop at the same sign-off with what changed; at a sign-off
  with no feedback, give the proposal again and end.

## `/rn:ty`

- `rn.py state`: at no sign-off, say what the session is doing and end.
- At the plan sign-off: `rn.py state signoff= stage=documents`; commit and push the approval; then
  go on as `/rn:up` does from where the session stands. In this unit, nothing comes after the plan
  sign-off yet: say the plan is approved and end.

## `/rn:gm <feedback>`

- `rn.py state`: at no sign-off, say what the session is doing and end. No words: ask the user for
  their feedback and end.
- `rn.py state feedback=<their words, whole>`; commit and push with the feedback in the message;
  say `Your feedback is kept. Clear the conversation if you like, then type /rn:up to go on.`; end.
