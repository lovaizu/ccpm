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
and turn, the plugin that makes each work for rn but the plan and the learnings, there without
asking the user again.

A plan serves them by tying each thing made to the user's purpose in links of one kind, each checked
against the one above it. The goal holds that purpose, with why the user wants it; the acceptance
criteria each say one thing the finished work must do for the goal, checked on the finished work at
the deliverable sign-off, where rn last waits for the user's answer, so that a finished work passing
every criterion reaches the goal; and each task's completion criterion says what its result must do
for the criteria it serves, so that results passing every completion criterion pass the criteria
they serve. The tasks are laid backward from the criteria, from what each criterion needs back to
what can be made now; a task is one result, accepted by its completion criterion, and its actions
are only what that result needs. The orchestrator writes the plan in a file of its own with these
items open and checks it against them; rn's scripts put it back into the steering, under the front
matter they write and above what comes next and what is open.

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

Signs: the reader reads the reason, what the user wants the goal for, beyond what the goal says.

Why: the user approves at the goal sign-off a reason they recognize as theirs, and every later
decision, in any conversation, is judged by it; without it later decisions aim at the user's first
words, which can be met while what they want them for is missed.

### B-2: The whole goal, checked on the finished work

Scope: its part

Does a finished work that passes every acceptance criterion, each answered yes or no by using it,
achieve the whole goal, its reason included?

Signs: each criterion is answered the same by whoever checks, its bar said by what is looked at
rather than by a word such as fast or easy; each says what the finished work does, rather than how
the piece of work went; each library, file layout or way of building a criterion names is one the
goal asks for; each part of the goal, and of its reason, is given by a criterion.

Why: the finished work is made and checked by the criteria alone; a criterion that cannot be checked
on it passes a finished work that misses it, one of how it is built fixes a way before the
architecture is drawn, and a part of the goal no criterion gives is never built, and the user sends
it back at the end.

### B-3: Each task's result accepted in its turn

Scope: its part

Can each task's result, once made, be used as its own user would use it, such as the user reading
the criteria at the goal sign-off, the reader of a document or a user of the finished work trying a
part of it, and accepted by its completion criterion, with nothing it needs left to a later task?

Signs: each task's result is used once that task is done, rather than one layer for later tasks,
such as all the tests or a part shared by several features; each task holds one result, rather than
several that could be accepted apart, such as two documents, or two things a user could try apart;
each completion criterion names a check made on the task's result, rather than on how the task
went; a check that is one command, such as the tests, is given by a `Test:` line whose command runs
the check the completion criterion names; where the result is code, that command runs the
project's formatter, linter and type checker with the check, set up by an action before the one
that makes the result where the project has none yet; each task stands after those it builds on.

Why: each task's result is made and accepted before the next task starts, so a slip shows while only
that slice is made; a task that makes much at once, or builds on what is not there yet, is made
again, and a result accepted on a guess carries its slip into the tasks after it.

### B-4: Each action done by what it says

Scope: its part

Can whoever does each of a task's actions tell from it who does it and what to do toward that
task's completion criterion?

Signs: whoever does each action reads in it what that task needs done, beyond the template's
words, the same in every task; each work has one action of turn's, rather than one designing a part
and one making it; each action is one the result needs, its content toward the completion
criterion, rather than one set in every task alike or research whose finding would change nothing
the task makes; each work an action says to make is one the user or the maker of a later work
uses, as they use a research or trial result handed to them, rather than one only its maker uses on
the way, such as a survey or a map to reach the result.

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

Signs: each point that is the user's to decide is confirmed with them in an action of the
orchestrator's, rather than left to an action of turn's to choose; each fact, library or way the
result rests on, such as a tool's current version or whether two parts work together, is checked
in the session or found out by research or a trial before the making; each research or trial result
is named by a later action as what it makes its work from.

Why: a task begun on a gap fills it with a guess, which the user sends back once the whole is built;
a fact checked or a way tried before anything is built on it shows a wrong guess while it is small;
and a finding not handed on is guessed again by the maker who needed it.

### B-6: Each result made to a check made first

Scope: its part

Where the check a task's completion criterion names is made in the session, such as tests or a set
of cases with the answers they must give, does an action before the one making the result make it
and see it fail on what is there?

Signs: the check is made by an action before the one that makes the result, rather than in the
same action or after it; each check named is made by an action, rather than left to whoever makes
the result; an action sees the check fail before the result is made; the check is made in the same
task as the result it checks; the action that makes the result is the task's last of turn's, the
command that runs the check given in place of any after it.

Why: a check made with or after the result is fitted to what the result does, not to what it must
do, and passes whatever was made; one seen failing first is shown to tell a result that meets the
criterion from one that does not, and made in the same task it is accepted with that result; rn
gives the command that runs it to the task's last action of turn's, so a work made after the result
is checked in the result's place. A check that is not made, such as a checklist read by turn's first
user, is there before the result already.

### B-7: The tasks give what their stage needs

Scope: whole

Do the completion criteria of the stage's tasks, all passed, give what that stage needs, as the
acceptance criteria all passed reach the goal: in the goal stage, criteria for the whole goal; in
the ux and the architecture stage, each document of the stage the user decided to make; in the
build stage, every acceptance criterion passed?

Signs: in the build stage, each criterion, and each case it names, is given by a completion
criterion, and each document made before it whose checklists hold an item judged on the built
product is made again by a task once the product is built, its receiver the product's users with the
built work; in the ux and the architecture stage, each document the user decided to make in that
stage has a task, and each task is for one of them, or for research one rests on; each ID a task
names is brought nearer to met by its completion criterion passed; each task's result is needed by a
criterion or a later task; each task is for a stage the session has reached, the finished work built
only once the criteria are made; each need a done task found, such as a research or trial result
handed to the plan, is met by a task, and each task it showed no longer needed is gone.

Why: turn makes each task's result for what it names, and the orchestrator accepts it by its
completion criterion, so an ID named by a task that does nothing for it is counted as served while
nothing builds it, one no task gives is never built, and the finished work misses what the user
approved; a document made before the build was judged without the items only the built product
answers, so one not made again promises what no one checked against the product; a task made for a
later stage rests on guesses about what the stages before it settle, and one kept after a finding
showed it needless is made for nothing.

### B-8: Each line used by its readers

Scope: whole

Does each line give the user at a sign-off or on the pull request, or the orchestrator in a later
conversation, something they would lose without it?

Signs: each line is one its readers use, with what is kept elsewhere left there: how a point was
reached or confirmed in the commit messages; a decision of one work, such as a library a task's
result uses, in the call to turn that makes that work; a learning in `learnings.md` in the
session's folder; where the session stands, such as what is next or open, in the ticks, Next and
Open, rather than in the goal, a criterion or a task; each thing is said in one place, a task
naming the criterion it serves rather than saying again what it says.

Why: the plan is read in every conversation, so each line beyond what its readers use costs them a
reading each time, and a thing said in two places comes to say two things as one of them changes.

### B-9: Each line taken as meant

Scope: whole

Does each reader take each line as the plan means it, the same in every conversation?

Tried by: the plan read, and its criteria and tasks set beside those of each earlier version of
`steering.md` on the session's branch, as `git log -p` of it since the branch left the default
branch shows them.

Signs: the user reads the meaning of each term of the subject, or plain word in a sense of its own,
that they may not know, in a line that shows it; each thing has one name, and each name one thing;
each ID names the thing it named in the plan's earlier versions on the session's branch, a changed
criterion or task under the ID it had, and a removed criterion's ID given to no other; every two
lines hold together, such as a task's completion criterion asking as a criterion it serves asks.

Why: a line read another way than meant is approved by the user, or built by turn, the other way;
later messages, commit messages, each call and what rn shows at each sign-off name the goal, the
criteria and the tasks by their IDs, so an ID given to a second thing points to two, and one that
names nothing points nowhere.
