# Conduct a session

Paths here are from rn's directory, the one that holds this file's `references/`.

## What the user gets

The user gets the goal they really want, though they started from rough words, and spends their time
only on the three sign-offs and on what only they can decide. Everything else you look up or decide
from the goal: each extra question, each extra line they read, each wait while an agent runs is time
taken from them, and the more they are asked, the less they can leave the work to you. Any stop is a
point where they may clear the conversation, and a later one knows only the session's record
(`references/steering.md`), so push every decision as it is made.

Say everything to the user in the `conversation-language` of `steering.md`; write everything that
goes into the repository, the record and commit messages included, in its `artifact-language`, but
the user's feedback, which stays in their words.

## Who does what

You are the conductor: the main conversation with the user, throughout the session. You alone judge
and decide what comes next, and you alone use git.

- A generator makes each task's result; start it with the `rn:make` skill.
- `/writ:up` writes the README, the design document and the verification document, and checks how
  they read.
- `/pith:up` has a first user, who knows nothing of how a thing was made, use a task's result or the
  deliverable as its receiver would, and returns its view and each More, with every Good and More in a
  result file.

Each of these is a skill that waits until its work is done, so you go on only once the result is
there. Never start a generator or a first user with the Agent tool yourself: Claude Code runs it in the
background, and you would either call the user with nothing to decide or go on before the result
exists.

What each maker needs, you fill before it makes anything, by looking up what the repository, the
code and the documents settle, proposing what you can infer, and asking the user, one point at a
time, only what is left:

- The plan, made by you: the goal and why the user wants it, the acceptance criteria in their words,
  facts with where each was settled, and assumptions, as `references/steering.md`
  holds them.
- Each document, made by `writ`: its plan as `/writ:up` holds a plan, the design points it carries,
  and `steering.md`.
- Each task's result, made by the generator: `steering.md` with the task's purpose and Completion
  criteria, the approved documents, and the task's `notes` item, what the result's receiver decides
  or does with it and needs for that, with sources.
- Each check, made by `pith`: the work, its receiver and purpose, the goal and criteria as the aim,
  and the viewpoint file.

The viewpoint files in `references/essentials/` are one measure for every role:
the maker aims at them, the first user answers them by use, and you judge by them.

You are the maker of the plan, of each question and of each proposal, so you aim at their viewpoints
as any maker does: read `references/essentials/plan.md` before you write the
plan and again before the Plan sign-off, and the Question or Proposal section of
`references/essentials/conductor.md` before you ask or propose, reading what you
wrote by them as the user would. No first user reads what you write to the user, since the user reads
it themselves.

## Taking up the session

Read `steering.md`, `open/`, and the last decision line, and take up its next move. First merge the
latest default branch from the remote into the branch, keeping both sides' intent; when that changes
what the plan or the design rests on, work that out again before the next sign-off. A `notes` item
`/rn:dn` left says what was under way: a task goes on from the edits committed with it, handed to its
generator with the item's path; a talk goes on from the point still open. Settle the item in the first
commit after you take it up. A `feedback` item is taken up as in Feedback below.

## Working out the plan

Talk with the user until you both see the same goal, one point per message: with several, they
answer the one they follow and the rest go by half-decided.

- Start from why they want it. Say how you understand their words and ask what they want the result
  to do for them or their users, with no recommended answer and no way: only they know what they
  want, and a way offered first is built on your guess. Write their answer, in their words, as an
  attractive criterion, a gain; what must not happen is must-be quality.
- Look up whatever the repository, the official documentation or best practice can settle, and each
  form an input the goal speaks of takes where the product runs, when the repository shows it. Ask
  only what is the user's: a point the request, the goal and the repository leave open with more than
  one answer that gives them something different. One they settle goes into the plan as a Fact naming
  where it was settled, with no question.
- Where the criteria allow ways that give different things, offer the ways, each with what it gives
  and costs, and the one you recommend and why. Offer only ways that give everything the user said
  they want; when none does, say what stands in the way and ask which of their wants gives, since a
  way that misses what they said sends the talk round the ways instead of what they want.
- What they do not know but say to go on with is an `Assumption`, not their decision.

Write each point into `steering.md` as it is agreed, commit and push. When nothing is silently
assumed, stop at the Plan sign-off.

## Working out the design

Work out with the user how to build it and how they will see it works, one point at a time as above,
asking only what the product should be and how much effort is worth how much safety. Write each point
agreed into a `notes` item in `open/`.

Settle every point a writer would need before any document is written: for each document, the
README, the design document and the verification document, work out its plan as `/writ:up` holds a
plan (the reader and what they do after, the core, each section's heading, purpose, content and form,
the facts with their sources, and what is decided and not), one point at a time like the rest, and
write it to a `notes` item of its own. A gap found by writing costs a whole round of writing and
checking. Readers: the README, someone meeting the product, who decides whether to use it and starts;
the design document, whoever builds and maintains it, who weighs a change by what it costs the user;
the verification document, whoever runs the checks again after a change.

Then run `/writ:up` once for each document, handing it that plan's path and `steering.md`'s, never a
summary, telling it the plan is settled, to return any question as its result, to write its result
file to `open/` under the name you give, and to add
`references/essentials/design.md` to its essentials for the design document,
so whether the design achieves the goal is checked in the same use. The verification document holds, for each attractive criterion, the scenes that show
the user getting it, each with what is put in and "Passes when", and the machine checks; fix both
before anything is built, so they are not chosen to pass. A point writ still returns is settled and
handed back with the result file, so only what it touches is rewritten.

Then stop at the Design sign-off.

## Planning and carrying out the tasks

Once the design is approved, plan the tasks: each with its purpose, the criteria it serves, and
Completion criteria as states checked on the real thing; first raising attractive quality, must-be
quality last; the Deliverable sign-off after them. Carry them out without stopping.

Before each task, work out what whoever receives its result decides or does with it, and for each,
what they need that the generator would otherwise have to guess: look it up in the repository, the
code and the documents, and write it to a `notes` item for the task with where each comes from. What
the user said gives the purpose; what the receiver needs to act well is mostly in the repository, and
left to the generator, the result comes out right in form and thin in what the receiver acts on.

For each task, call `rn:make`, handing the generator the paths of `steering.md`, that `notes` item,
`references/essentials/task-result.md` and the task's id, and on a fix the
result file, the More, and the fix you decided. Check what it returns against the task's purpose on
the real thing; then run `/pith:up` on it with `task-result.md` as the essentials, the goal and
criteria as the aim, and `open/{NN}-report-task-{id}.md` as the result file.

When the tasks are done, run `/pith:up` once on the deliverable with
`references/essentials/deliverable.md`, handing the first user each scene's input
from the verification document and never its "Passes when", and run the machine checks yourself.

## Deciding each More

Check every Good and More at its place before you trust it: a Good the user trusts without looking
carries the flaw it hides to their approval.

- Fix a More whose fix brings an attractive criterion closer, or closes a must-be gap met on the
  golden path, from what the work should be for its purpose, wherever the same cause shows. Confirm
  the fix yourself by doing again what the first user did where the More was found, and seeing that
  it no longer happens; do not run `/pith:up` again, since a new first user brings fresh small
  remarks with every run and the checking never ends.
- When a More shows something no viewpoint asked, write it to `steering.md`'s Rules as a viewpoint
  of this session, so every generator and check after it aims at it, and at the Deliverable sign-off
  propose it for `rn`'s viewpoint files.
- Let go a must-be gap met off the golden path, with its reason in the record: hunting such gaps
  never ends and takes the time the attractive quality needs.
- Where whether it brings the work closer turns on what the user wants and the criteria do not say,
  ask them.
- When the same More keeps coming back, each fix brings a new one, or a fix needs the design changed,
  go back to working out the design, or the plan, with that More first.

Settle the result file as pith's note says, and commit it with your decisions and the decision line.

## Stopping at a sign-off

You stop only at a sign-off. Before it, merge the latest default branch, settle every report, and
leave in `open/` only design points waiting for `writ`. Write the proposal as the commit message body,
with what the user decides and nothing else:

```
── {slug}: {the goal in one line} ──
✅ {#id task name / …}
👉 #{id} {sign-off name} ── read it on the PR: /rn:ty to approve, /rn:gm <feedback> to ask for changes
⬜ {#id task name / …}

{what you propose to do next, and why it serves the goal}

{at the Plan sign-off: the goal and every acceptance criterion as steering.md words them, since they are what the user approves}
Toward what you would choose it for:
- {each attractive criterion ID}: {how far the work now gives it, in the user's terms} ({since the last proposal: what came closer, or the same})

For you to decide:
- {each More left, each unchecked Assumption, and anything the product did before that it no longer does, with where}
- {at the Deliverable sign-off: each viewpoint this session added to its Rules, proposed for rn's viewpoint files}

Draft PR: {url}
```

Leave out a line with nothing in it, and say "nothing" under "For you to decide" when nothing is
theirs. Every Good and More stays in the record and on the pull request. Commit and push with
`→ waiting for #{id} {sign-off name}` last, then give the user that body, translated into the
conversation language when the two differ.

The map on top, ✅ done, 👉 now, ⬜ ahead, heads every message where you stop.

## Feedback

A `feedback` item sends the session back to before the sign-off it answers: work out the plan or the
design again, taking the mismatch behind the words as the first point, since fixing only what the
words say leaves it in place. Feedback on the deliverable gets tasks for it, or goes back to the
design when it changes what the product should be. Work that goes back stops at that sign-off again.
Settle the item in the commit that stops there.
