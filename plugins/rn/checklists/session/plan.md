# Plan

A plan is the part of the steering, kept in the session's folder `.rn/<yyyymmdd>-<slug>/`, that ties
what rn makes to the user's purpose. The user reads it at each sign-off, where rn shows a proposal
and waits for their answer, to approve what the finished work will do and why or to send it back,
and on the pull request, to see what is left. rn's orchestrator, the AI of rn that talks with the
user, reads it in every later conversation as the map to the user's purpose, and decides the next
step from it. rn's AI that writes the call for each task reads it to give turn, the plugin that
makes each task's result, what that task needs.

A plan ties each thing made to the user's purpose in links of one kind, each checked against the one
above it. Each goal holds a purpose of the user's, with why they want it. Each acceptance criterion
says one thing the finished work must do for the goals it serves, checked on the finished work at
the deliverable sign-off, so a finished work passing every criterion reaches every goal. Each task
is one result, made by one call to turn, and its completion criteria say what that result must do
for the acceptance criteria it serves, so results passing every completion
criterion pass the acceptance criteria. A task says what its result must do, never the means or the
inputs: the means are for turn to choose, and the inputs for whoever writes the call. The tasks are
laid backward from the criteria, from what each criterion needs back to what can be made now, and
made a few at a time for the stage at hand, as each stage rests on what the one before it settles.

## Format

```markdown
# <The piece of work, in a few words>

## Goals

- G1: <A purpose of the user's>

  <Why they want it>

## Acceptance criteria

- AC1: <One thing the finished work must do>. Serves <the goals, by ID>.

## Tasks

- T1: <The result it makes>. Builds on <the tasks whose results it uses, by ID, or none>.

  - <What the result must do>. Serves <the acceptance criteria, by ID>.
```

The goals and the criteria are there once made, and Tasks while a task is left. rn's scripts write
it from the steering's JSON.

## Questions

### Q-1: The user's purpose, with why

From each goal, can the reader tell what the user wants the piece of work to achieve, and why they
want it?

Why: the user approves at the goal sign-off a reason they recognize as theirs, and every later
decision is judged by it. Without the reason, later decisions aim at the user's first words, which
can be met while what they wanted them for is missed.

### Q-2: The whole goal reached by the criteria

Does a finished work that passes every acceptance criterion achieve each goal, its reason included?

Why: the finished work is made and checked by the criteria alone, so a part of a goal no criterion
gives is never built, and the user sends it back at the end.

### Q-3: Each criterion checked by using the finished work

Can each acceptance criterion be answered yes or no by using the finished work?

Why: a criterion whose bar is a word such as fast or easy, or one about how the piece of work went,
passes a finished work that misses it.

### Q-4: What the finished work does, not how it is built

Does each acceptance criterion say what the finished work does, naming a library, a file layout or a
way of building only where a goal asks for it?

Why: a criterion of how the finished work is built fixes a means before the architecture is drawn.

### Q-5: Each result used when its task is done

Can each task's result be used as its own user would use it as soon as that task is done, with
nothing it needs left to a later task?

Why: each result is accepted before the next task starts, so a slip shows while only that slice is
made. A task that makes a layer for later tasks, such as all the tests or a part shared by several
features, is accepted on a guess and carries its slip into the tasks after it.

### Q-6: One result for each task

Does each task make one result, made by one call to turn?

Why: two results that could be accepted apart, such as two documents, are accepted together or one
is left unchecked, and a result made in two calls is made twice.

### Q-7: Completion criteria on the result

Does each completion criterion say only what the task's result must do, as seen on the
result itself?

Why: a means or an input fixed in the plan settles before the making what its maker decides, and
can send the user a question about it mid-run. A check of how the task went, rather than of its
result, passes a result that misses it.

### Q-8: What each task builds on

Does each task name every task whose result it uses?

Why: the call for a task is written from the plan, so a result the task uses but does not name is
not given to turn, and turn makes it again or guesses it.

### Q-9: Unknowns found out first

Is each fact or way a task's result rests on that no one in the session yet knows, such as a tool's
current version or whether two parts work together, found out by a research or trial task it builds
on?

Why: a task begun on a gap fills it with a guess, which the user sends back once the whole is built.
A fact checked or a way tried before anything is built on it shows a wrong guess while it is small.

### Q-10: What the stage needs

Do the completion criteria of the tasks, all passed, give what the stage the session is in needs:
in the goal stage, criteria for every goal; in the ux and the architecture stage, each document of
the stage that the user decided to make; in the build stage, every acceptance criterion passed?

Why: a part of the stage no task gives is never made. Each task is for the stage at hand, as a task
for a later stage rests on guesses about what the stages before it settle, and a need a done task
found, such as a research result, changes the tasks left.

### Q-11: Each task needed

Is each task's result needed by an acceptance criterion it serves or by a later task?

Why: an ID named by a task that does nothing for it is counted as served while nothing builds it,
and a task kept after a finding showed it needless is made for nothing.

### Q-12: Documents made again on the built product

In the build stage, is each document made before it, whose checklist asks what only the built
product can answer, made again by a task once the product is built?

Why: a document made before the build was judged without those questions, so one not made again
promises what no one has checked against the product.

### Q-13: Each ID the same thing throughout

Does each ID name the thing it named in the plan's earlier versions on the session's branch, a
removed ID given to no other thing?

Why: messages, commit messages, calls and what rn shows at each sign-off name the goals, the
criteria and the tasks by their IDs, so an ID given to a second thing points to two, and one that
names nothing points nowhere.
