---
name: plan
version: 1
made_from:
  checklist: 1
  usability: 1
---

# Plan

A plan, the part of `steering.md` from its title to its tasks, in the session's folder
`.rn/<yyyymmdd>-<slug>/`, where rn keeps one piece of work, is read by the user at each sign-off,
where rn waits for their answer, to approve what the finished work will do and why or send it back,
and on the pull request, to see what is left of the work. In every later conversation the
orchestrator, the AI of rn that talks with the user and decides each move, reads it as the map to
the user's purpose: from it and what each move found, it decides what to do next and leads the user
and turn, the plugin that makes each work for rn, there without asking the user again.

A plan serves them by tying each thing made to the user's purpose in links of one kind, each checked
against the one above it. The goal holds that purpose, with why the user wants it; the acceptance
criteria each say one thing the finished work must do for the goal, checked on the finished work at
the deliverable sign-off, where rn last waits for the user's answer, so that a finished work passing
every criterion reaches the goal; and each task's completion criterion says what its result must do
for the criteria it serves, so that results passing every completion criterion pass the criteria
they serve. The tasks are laid backward from the criteria, from what each criterion needs back to
what can be made now; a task is one result, accepted by its completion criterion, and its actions
are only what that result needs. turn makes the plan in a file of its own, and these items judge
it; rn's scripts put it back into the steering, under the front matter they write and above what
comes next and what is open.

## Format

### F-1: Shape

Scope: whole

Does the plan follow this template, headings and IDs included?

```markdown
# <The piece of work, in a few words>

G1: <the user's purpose, with why they want it>

## Acceptance criteria

- AC1: <one thing the finished work must do for the goal>

## Tasks

- T1: <the result it makes>. Serves <G1, or the criteria by ID>.

  Completion criterion: <what its result must do for what it serves, and the check that shows it>

  Test: `<the one command that runs that check>`

  - [ ] 1. <what is found out or settled>. The orchestrator, with the user.
  - [ ] 2. <what is made, from which works before it>, `<its path>` as a <kind> work. turn.
```

The goal and the criteria are there once made, and `## Tasks` while a task is left. A task has as
many actions as its result needs, numbered from 1, each in one of the two forms above: the
orchestrator's, with the user, or turn's, one work at one path, and research or a trial made at a
path in the session's folder as a `research` or `trial` work. The line `Test:` is there where the
check is one command, such as the tests, which rn gives turn with the task's last action of
turn's, the one that makes the result. A task line has no tick; the ticks are rn's scripts' to
write.

Why: rn's scripts refuse a plan out of this form at every keep, as they read the IDs, the forms of
the actions and the ticks by these names, and the user reads the same lines at each sign-off.

## Benefit

### B-1: The user's purpose, with why

Scope: its part

From the goal alone, can whoever reads the plan tell what the user wants the piece of work to
achieve, and why they want it?

Look for: no reason, or a reason that says again what the goal says instead of what the user wants
it for.

Why: the user approves at the plan sign-off a reason they recognize as theirs, and every later
decision, in any conversation, is judged by it; without it later decisions aim at the user's first
words, which can be met while what they want them for is missed.

### B-2: The whole goal, checked on the finished work

Scope: its part

Does a finished work that passes every acceptance criterion, each answered yes or no by using it,
achieve the whole goal, its reason included?

Look for:
- a word whose bar depends on who checks, such as fast or easy;
- a criterion about how the piece of work went rather than what the finished work does;
- a criterion naming a library, a file layout or a way of building that the goal does not ask for;
- a part of the goal, or of its reason, that no criterion gives.

Why: the finished work is made and checked by the criteria alone; a criterion that cannot be checked
on it passes a finished work that misses it, one of how it is built fixes a way before the
architecture is drawn, and a part of the goal no criterion gives is never built, and the user sends
it back at the end.

### B-3: Each task's result accepted in its turn

Scope: its part

Can each task's result, once made, be used as its own user would use it, such as the user reading
the criteria at the plan sign-off, the reader of a document or a user of the finished work trying a
part of it, and accepted by its completion criterion, with nothing it needs left to a later task?

Look for:
- a task that makes one layer for later tasks, such as all the tests or a part shared by several
  features, with nothing to use until another task is done;
- a task holding several results that could be accepted apart, such as two documents, or two things
  a user could try apart;
- a completion criterion that names no check, or a check made on something other than the task's
  result, such as how the task went;
- a check that is one command, such as the tests, with no `Test:` line giving it, or a `Test:` line
  whose command runs another check than the one the completion criterion names;
- a task placed before one it builds on.

Why: each task's result is made and accepted before the next task starts, so a slip shows while only
that slice is made; a task that makes much at once, or builds on what is not there yet, is made
again, and a result accepted on a guess carries its slip into the tasks after it.

### B-4: Each action done by what it says

Scope: its part

Can whoever does each of a task's actions tell from it who does it and what to do toward that
task's completion criterion?

Look for:
- an action that holds only the template's words, the same in every task;
- an action that names no one to do it, or one of turn's that names no path or kind of the work it
  makes, which turn's call is made on;
- two actions of turn's on the same work, such as one designing a part and one making it;
- an action the result does not need, such as one set in every task alike or research whose
  finding would change nothing the task makes, or one whose content does nothing toward the
  completion criterion;
- a work an action says to make that only its maker uses on the way, such as a survey or a map to
  reach the result, rather than one the user or the maker of a later work uses, as they use a
  research or trial result handed to them.

Why: each action is done and ticked by what it says, and the task's result waits until the actions
before it are ticked; one that says only the template's words is ticked unseen, one with no doer is
left or done twice, and two calls on one work make it twice; one the result does not need, or what
only its maker reads, takes the time the result needed, drifts from the purpose, and is left for no
one to keep.

### B-5: Each task made on checked ground

Scope: its part

Does each task settle what its result rests on before the action that makes it: what is the user's
to decide confirmed with them, and what no one in the session yet knows found out by research or by
a small trial, its result handed to each action that rests on it?

Look for:
- an action of turn's left to choose what is the user's to decide;
- a fact, a library or a way the result rests on that the session has not checked, with no
  research or trial before the making, such as a tool's current version or whether two parts work
  together;
- a research or trial result that no later action names as what it makes its work from.

Why: a task begun on a gap fills it with a guess, which the user sends back once the whole is built;
a fact checked or a way tried before anything is built on it shows a wrong guess while it is small;
and a finding not handed on is guessed again by the maker who needed it.

### B-6: Each result made to a check made first

Scope: its part

Where the check a task's completion criterion names is made in the session, such as tests or a set
of cases with the answers they must give, does an action before the one making the result make it
and see it fail on what is there?

Look for:
- the check made in the same action as the result, or after it;
- a check named that no action makes, left to whoever makes the result;
- no action seeing the check fail before the result is made;
- the check made as a task of its own, apart from the result it checks;
- an action of turn's after the one that makes the result, which the command that runs the check
  would be given to in its place.

Why: a check made with or after the result is fitted to what the result does, not to what it must
do, and passes whatever was made; one seen failing first is shown to tell a result that meets the
criterion from one that does not, and made in the same task it is accepted with that result; rn
gives the command that runs it to the task's last action of turn's, so a work made after the result
is checked in the result's place. A check that is not made, such as a checklist read by turn's first
user, is there before the result already.

### B-7: The tasks give what their stage needs

Scope: whole

Do the completion criteria of the stage's tasks, all passed, give what that stage needs, as the
acceptance criteria all passed reach the goal: in the plan stage, criteria for the whole goal; in
the design stage, each document the purpose needs; in the build stage, every acceptance criterion
passed?

Look for:
- in the build stage, a criterion, or a case it names, that no completion criterion gives;
- in the design stage, a document the purpose needs with no task, or a task for a document it does
  not need;
- an ID named by a task whose completion criterion, passed, would leave it exactly as unmet as
  before;
- a task whose result neither a criterion nor a later task needs;
- a task for a stage the session has not reached, such as one that builds the finished work while
  the criteria are made;
- what a done task found, such as a research or trial result handed to the plan, showing a need
  that no task meets, or a task no longer needed that is still there.

Why: turn makes each task's result for what it names, and the orchestrator accepts it by its
completion criterion, so an ID named by a task that does nothing for it is counted as served while
nothing builds it, one no task gives is never built, and the finished work misses what the user
approved; a task made for a later stage rests on guesses about what the stages before it settle,
and one kept after a finding showed it needless is made for nothing.

### B-8: Each line used by its readers

Scope: whole

Does each line give the user at a sign-off or on the pull request, or the orchestrator in a later
conversation, something they would lose without it?

Look for:
- how a point was reached or confirmed, which the commit messages keep;
- a decision of one work, such as a library a task's result uses, which the call to turn that makes
  that work keeps;
- a task whose actions are all done, whose result the repository and its call to turn keep;
- a learning, which `learnings.md` in the session's folder keeps;
- where the session stands, such as what is next or open, written in the goal, a criterion or a
  task, which the ticks, Next and Open hold;
- one thing said in two places, such as a task saying again what a criterion it serves says.

Why: the plan is read in every conversation, so each line beyond what its readers use costs them a
reading each time, and a thing said in two places comes to say two things as one of them changes.

### B-9: Each line taken as meant

Scope: whole

Does each reader take each line as the plan means it, the same in every conversation?

Look for:
- a term of the subject, or a plain word in a sense of its own, that the user may not know and no
  line shows the meaning of;
- one thing under two names, or one name for two things;
- an ID naming another thing than in the plan's earlier versions on the session's branch: the goal
  other than `G1`, a changed criterion or task under a new ID, a removed one's ID given to another,
  or a new task under a number no higher than every task ID the plan has held;
- a task serving an ID the plan does not hold;
- two lines that cannot both hold, such as a task's completion criterion asking otherwise than a
  criterion it serves.

Why: a line read another way than meant is approved by the user, or built by turn, the other way;
later messages, commit messages, each call to turn and what rn shows at each sign-off name the goal,
the criteria and the tasks by their IDs, so an ID given to a second thing points to two, and one
that names nothing points nowhere.
