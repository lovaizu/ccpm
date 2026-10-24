---
name: plan
version: 1
made_from:
  checklist: 1
  usability: 1
---

# Plan

A plan, the part of `steering.md` from its title to its tasks, in the session's record, the folder
where rn keeps one piece of work, is read by the user at each sign-off, where rn waits for their
answer, to approve what the finished work will do and why or send it back, and on the pull request,
to see how far the work has come. In every later conversation the orchestrator, the AI of rn that
talks with the user and decides each move, reads it to carry each move on to the user's purpose
without asking them again.

A plan serves them by tying each thing made to the user's purpose, each link checked against the one
before it. The goal holds that purpose, with why the user wants it; the acceptance criteria each say
one thing the finished work must do for the goal, checked on the finished work at the deliverable
sign-off, where rn last waits for the user's answer, and together give the whole goal; each task
names by ID what it serves, the goal while the criteria are made and the criteria after, with a
completion criterion checked on its result and the steps that reach it: a first step that reads what
the task rests on, finds out by research or by trying what it must, and confirms with the user what
is lacking; and, before a part is made, its design and checks traced on paper or tried by an AI that
did not design them, so a slip shows while it is small. The tasks are made for the stage at hand, as
each stage rests on what the one before it settled: in the plan stage those that reach the criteria,
in the design stage one for each document the purpose needs, and in the build stage those that build
the finished work; the tasks of a stage passed stay as they were ticked. turn, the plugin that makes
each work for rn, makes the plan from the title to the tasks in a file of its own, and these items
judge that part; the learnings have a checklist of their own. The plan holds only what was decided
about the work: each decision of one work is kept in the call to turn that makes it, how each point
was reached in the commit messages, and where the session stands, the stage, the sign-off waiting,
Next and Open, is written by rn's scripts.

## Format

### F-1: Shape

Scope: whole

Does the steering the plan is put back into follow this template, front matter, headings and IDs
included?

```markdown
---
rn: <rn's version>
pr: <the pull request's URL>
stage: <plan, design, build, deliverable, learnings or finished>
signoff: <none, plan, design or deliverable>
artifact-language: <the language of everything rn writes into the repository>
conversation-language: <the language rn speaks to the user in>
---

# <The piece of work, in a few words>

G1: <the user's purpose, with why they want it>

## Acceptance criteria

- AC1: <one thing the finished work must do for the goal>

## Tasks

- [ ] T1: <the part of the piece of work>. Serves <G1, or the criteria by ID>.

  Completion criterion: <what its result must do for what it serves, and the check that shows it>

  - [ ] 1. Read <the context it needs>, finding out <what it must>; confirm <what is lacking>. The orchestrator, with the user.
  - [ ] 2. Design <the part it makes> and <how that part is checked>. turn, first run.
  - [ ] 3. Trace <the design> on paper, or try it, against <its checks>. That run's first reader.
  - [ ] 4. Make <the part>, checked as it grows, code test first. turn, second run.

## Learnings

- L1: <what happened, with the words it rests on, and where it would make later work better>

## Next

<the step of /rn:up to take next, by its number, and on what>

## Open

- <what is open>
```

The goal, the criteria, the tasks and the learnings are each there once made; a task has the steps
it needs, numbered from 1, each saying who does it, these four for a part made; `## Open` holds
`None.` where nothing is open. A call to turn makes one part in a file of its own: the plan, from
the title to the tasks, or the learnings; the front matter, the ticks, Next and Open are written by
rn's scripts.

Why: rn's scripts refuse a steering out of this form at every keep, as they read the front matter,
the IDs, the ticks, Next and Open by these names, and the user reads the same file at each sign-off.

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
- a task placed before one it builds on.

Why: each task's result is made and accepted before the next task starts, so a slip shows while only
that slice is made; a task that makes much at once, or builds on what is not there yet, is made
again, and a result accepted on a guess carries its slip into the tasks after it.

### B-4: Each step done by what it says

Scope: its part

Can whoever does each of a task's steps tell from it what to do toward that task's completion
criterion?

Look for:
- a step that holds only the template's words, the same in every task;
- a step whose content does nothing toward the completion criterion;
- a task, or a thing a step says to make, that only its maker reads on the way, such as a survey or
  a map to reach the result, rather than what the user of the finished work, or whoever builds it
  later, uses once the piece of work is done.

Why: each step is done and ticked by what it says, and a task's making waits until the steps before
it are ticked; a step that says only the template's words is ticked unseen, one aimed elsewhere is
done while the result the task needs is not, and what only its maker reads takes the time the result
needed, drifts from the purpose, and is left for no one to keep.

### B-8: Each task made on checked ground

Scope: its part

Does each task settle what its result rests on before making it: a first step that reads what the
task needs, finds out by research or by trying what it must know, and confirms with the user what is
lacking, and, for a part made, a step before the making where one who did not design the part traces
its design on paper, or tries it, against its checks?

Look for:
- a first step that names nothing to read or to find out, or that has the maker choose what is the
  user's to decide;
- a part made with no trace or try of its design before it, or one traced by its own designer, or
  against no checks.

Why: a task begun on a gap fills it with a guess, which the user sends back once the whole is built;
a design and its checks traced or tried before the making show its slips while they are small, and
its designer reads in what they meant rather than what they wrote.

### B-5: The tasks give what their stage needs

Scope: whole

Do the tasks of the stage at hand together give what that stage needs, each task's result bringing
about something of each ID it names: in the plan stage, criteria for the whole goal; in the design
stage, each document the purpose needs; in the build stage, every acceptance criterion?

Look for:
- in the build stage, a criterion no task names;
- in the design stage, a document the purpose needs with no task, or a task for a document it does
  not need;
- an ID named by a task whose result would leave it exactly as unmet as before;
- a task for a stage the session has not reached, such as one that builds the finished work while
  the criteria are made.

Why: turn makes each task's result for what it names, and the orchestrator accepts it by that, so an
ID named by a task that does nothing for it is counted as served while nothing builds it, one no
task names is never built, and the finished work misses what the user approved; a task made for a
later stage rests on guesses about what the stages before it settle.

### B-6: Each line used by its readers

Scope: whole

Does each line give the user at a sign-off or on the pull request, or the orchestrator in a later
conversation, something they would lose without it?

Look for:
- how a point was reached or confirmed, which the commit messages keep;
- a decision of one work, such as a library a task's result uses, which the call to turn that makes
  that work keeps;
- where the session stands, such as what is done, next or open, written in the goal, a criterion or
  a task, which the ticks, Next and Open hold;
- one thing said in two places, such as a task saying again what a criterion it serves says.

Why: the plan is read in every conversation, so each line beyond what its readers use costs them a
reading each time, and a thing said in two places comes to say two things as one of them changes.

### B-7: Each line taken as meant

Scope: whole

Does each reader take each line as the plan means it, the same in every conversation?

Look for:
- a term of the subject, or a plain word in a sense of its own, that the user may not know and no
  line shows the meaning of;
- one thing under two names, or one name for two things;
- an ID naming another thing than in the plan's earlier versions on the session's branch: the goal
  other than `G1`, a changed criterion or task under a new ID, or a removed one's ID given to
  another;
- a task serving an ID the plan does not hold;
- two lines that cannot both hold, such as a task's completion criterion asking otherwise than a
  criterion it serves.

Why: a line read another way than meant is approved by the user, or built by turn, the other way;
later messages, commit messages, each call to turn and what rn shows at each sign-off name the goal,
the criteria and the tasks by their IDs, so an ID given to a second thing points to two, and one
that names nothing points nowhere.
