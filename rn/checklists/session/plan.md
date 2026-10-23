---
name: plan
version: 0.1.0
---

# Plan

A plan, `steering.md` in the session's record, the folder where rn keeps one piece of work, is read
by the user at the plan sign-off, where rn first waits for their answer, to approve what the
finished work will do and why, or to send it back. In every later conversation the conductor, the
AI of rn that talks with the user and decides each move, and turn, the plugin that makes for rn each
document, each task's result and the finished work, read it to carry each of these to the user's
purpose without asking them again.

A plan serves them by tying each thing made to the user's purpose. The goal holds that purpose,
with why the user wants it; the acceptance criteria each say one thing the finished work must do for
the goal, checked on the finished work, and together give the whole goal; each task, a part a user
of the finished work can try, names the criteria it serves, with a completion criterion checked on
its result and four steps that reach it: the context read and what is lacking confirmed; the part
and its checks designed by turn, then traced on paper by turn's first reader, an AI that did not
design them; and only then the part made, so a slip shows while it is small. The plan holds only
what was decided, each point it rests on kept, with how it was confirmed with the user, in the
plan's decisions, `decisions/plan.decisions.md` beside it. It fills in as the session moves on: the
goal and the criteria before the plan sign-off, the documents the purpose needs after it, and the
tasks after the design sign-off, where rn waits for the user's answer on those documents. The
sign-offs, and where the session stands, are kept in `state.json` beside the plan, outside the
tasks.

Each item of `usability.md` applies to a plan with the user's purpose and what the finished work
must do for it as its subject. Its F-1 is answered inside the template below, with the goal as the
main point under the title. Its B-6 is answered while the session runs: the plan is kept true as
the piece of work moves on, `status` and each box included.

## Format

### F-1: Shape

Scope: whole

Does the plan follow this template, front matter, headings and IDs included?

```markdown
---
rn: <the installed rn version>
pr: <the session's pull request URL>
status: <running; finished once the pull request is marked ready>
artifact-language: <the language of everything rn writes into the repository>
conversation-language: <the language rn speaks to the user in>
---

# <The piece of work, in a few words>

G1: <the user's purpose, with why they want it>

## Acceptance criteria

- AC1: <one thing the finished work must do for the goal>

## Documents

- <the document, such as the architecture>: <its path>

## Tasks

- [ ] T1: <the part of the piece of work>. Serves AC1.

  Completion criterion: <what its result must do for AC1, and the check that shows it>

  - [ ] 1. Read <the context it needs>; confirm <what is lacking>. The conductor, with the user.
  - [ ] 2. Design <the part it makes> and <how that part is checked>. turn, first run.
  - [ ] 3. Trace <the architecture> on paper against <its checks>. That run's first reader.
  - [ ] 4. Make <the part>, checked as it grows, code test first. turn, second run.
```

Why: a check of rn's refuses a plan kept outside this form, and rn's script reads `pr`, `status` and
the two languages by these names, so a plan in another form halts the session.

### F-2: IDs that keep naming one thing

Scope: whole

Compared with the plan's earlier versions on the session's branch, does each ID name one and the
same thing throughout the session: the goal always `G1`, a changed criterion or task under the ID
it had, and a removed criterion's or task's ID given to no other?

Why: later messages, commit messages and what rn shows at each sign-off refer to the goal, the
criteria and the tasks by their IDs, so an ID given to a second thing points to two.

## Benefit

### B-1: Why the user wants the goal

Scope: its part

From the goal alone, can whoever reads the plan tell why the user wants it?

Why: the user approves at the plan sign-off a reason they recognize as theirs, and every later
decision, in any conversation, is judged by it; without it later decisions aim at the user's first
words, which can be met while what they want them for is missed.

### B-2: Each criterion checked on the finished work

Scope: its part

Can each acceptance criterion be answered yes or no by using the finished work?

Look for: a word whose bar depends on who checks, such as fast or easy; a criterion about how the
piece of work went rather than what the finished work does.

Why: the finished work is used for every criterion before the deliverable sign-off, where rn last
waits for the user's answer, on the finished work; a criterion that cannot be checked on it passes a
finished work that misses it.

### B-3: Each criterion a thing done for the goal

Scope: its part

Does each acceptance criterion say what the finished work does for the goal, rather than how it is
built?

Look for: a criterion naming a library, a file layout or a way of building that the goal does not
ask for.

Why: a criterion of how it is built fixes a way before the architecture is drawn, and is met by a
finished work that does nothing for the goal.

### B-4: Each criterion the user's

Scope: its part

For each acceptance criterion, can whoever reads the plan find in the plan's decisions every point
it rests on, confirmed with the user?

Why: a point rn decided for the user sends the piece of work the way rn guessed, and the user meets
it at the deliverable sign-off as a change to send back; a point confirmed is never asked again.

### B-5: Each task serving the criteria it names

Scope: its part

Does each task's part of the piece of work bring about something each acceptance criterion it names
asks?

Look for: a criterion named by a task whose result would leave that criterion exactly as unmet as
before.

Before the tasks are written, it is answered yes.

Why: turn makes each task's result for the criteria it names, and the conductor accepts it by them,
so a criterion named by a task that does nothing for it is counted as served while nothing builds
it.

### B-8: Each task a thin slice tried on its own

Scope: its part

Does each task's result do one thing a user of the finished work can try, through every part that
thing needs?

Look for: a task that makes one layer for later tasks, such as all the tests or a part shared by
several features, with nothing to try until another task is done; a task holding several things a
user could try apart.

Before the tasks are written, it is answered yes.

Why: each task's result is made and accepted before the next task starts, so a slip shows while
only that slice is made; a task that makes much at once shows its slip only once all of it is
made, and all of it is made again.

### B-10: Each completion criterion checked on the task's result

Scope: its part

Can each task's completion criterion be answered yes or no on the task's result, by a check it
names?

Look for: a completion criterion that names no check; a check made on something other than the
task's result, such as how the task went.

Before the tasks are written, it is answered yes.

Why: the conductor accepts each task's result by its completion criterion before the next task
starts; a criterion no named check answers is accepted on a guess, and the tasks after it build on a
result that may miss it.

### B-11: Each step aimed at the completion criterion

Scope: its part

Can whoever reads the plan tell, from each of a task's four steps, what of that task's completion
criterion the step works toward?

Look for: a step that holds only the template's words, the same in every task; a step whose content
does nothing toward the completion criterion.

Before the tasks are written, it is answered yes.

Why: each step is done and ticked by what it says; a step that says only the template's words is
ticked unseen, and one aimed elsewhere is done while the result the task needs is not.

### B-9: Each task making only what is used after

Scope: its part

Does each task, and each thing it says to make on the way, give what someone uses once the piece of
work is done: the user using the finished work, or whoever builds it later?

Look for: something only its maker reads on the way, such as a survey or a map to reach the result.

Before the tasks are written, it is answered yes.

Why: what only its maker reads is made for its own sake: it takes the time the result needed,
drifts from the purpose, and is left for no one to keep.

### B-6: The criteria give the whole goal

Scope: whole

Can whoever reads the plan tell that a finished work doing every acceptance criterion achieves the
whole goal, its reason included?

Why: the finished work is made and checked by the criteria alone, so a part of the goal no
criterion gives is never built, and the user sends it back at the end.

### B-7: Every criterion served by a task

Scope: whole

Is every acceptance criterion named by at least one task?

Before the tasks are written, it is answered yes.

Why: a criterion no task serves is never built, and the finished work misses what the user
approved.

### B-12: Each task after the tasks it builds on

Scope: whole

Does each task come after every task it builds on?

Before the tasks are written, it is answered yes.

Why: each task's result is made and accepted before the next task starts, so a task placed before
one it builds on is made on what is not there yet, and made again once it is.
