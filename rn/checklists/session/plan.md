---
name: plan
version: 1
made_from:
  checklist: 1
  usability: 1
---

# Plan

A plan, `steering.md` in the session's record, the folder where rn keeps one piece of work, is read
by the user at the plan sign-off, where rn first waits for their answer, to approve what the
finished work will do and why, or to send it back. In every later conversation the conductor, the
AI of rn that talks with the user and decides each move, and turn, the plugin that makes for rn each
document, each task's result and the finished work, read it to carry each of these to the user's
purpose without asking them again.

A plan serves them by tying each thing made to the user's purpose, each link checked against the
one before it. The goal holds that purpose, with why the user wants it; the acceptance criteria each
say one thing the finished work must do for the goal, checked on the finished work at the
deliverable sign-off, where rn last waits for the user's answer, and together give the whole goal;
each task, a part a user of the finished work can try, names the criteria it serves, with a
completion criterion checked on its result and four steps that reach it: the context read and what
is lacking confirmed; the part and its checks designed by turn, then traced on paper by turn's first
reader, an AI that did not design them; and only then the part made, so a slip shows while it is
small. The plan holds only what was decided: how each point was reached is kept in the plan's
decisions, `decisions/plan.decisions.md`, and where the session stands in `state.json`, both beside
it. It fills in as the session moves on: the goal and the criteria before the plan sign-off, the
documents the purpose needs after it, and the tasks after the design sign-off, where rn waits for
the user's answer on those documents; an item on the tasks passes a plan that has none yet.

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

Can each task's result, once made, be tried as a user of the finished work would try it and
accepted by its completion criterion, with nothing it needs left to a later task?

Look for:
- a task that makes one layer for later tasks, such as all the tests or a part shared by several
  features, with nothing to try until another task is done;
- a task holding several things a user could try apart;
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
done while the result the task needs is not, and what only its maker reads takes the time the
result needed, drifts from the purpose, and is left for no one to keep.

### B-5: The tasks build what the criteria ask

Scope: whole

Do the tasks together build every acceptance criterion, each task's result bringing about something
of each criterion it names?

Look for: a criterion no task names; a criterion named by a task whose result would leave it exactly
as unmet as before.

Why: turn makes each task's result for the criteria it names, and the conductor accepts it by them,
so a criterion named by a task that does nothing for it is counted as served while nothing builds
it, and one no task names is never built, and the finished work misses what the user approved.

### B-6: Each line used by its readers

Scope: whole

Does each line give the user at the plan sign-off, or the conductor and turn later, something they
would lose without it?

Look for:
- how a point was reached or confirmed, which the plan's decisions keep;
- where the session stands, which `state.json` keeps;
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
- two lines that cannot both hold, such as a task's completion criterion asking otherwise than a
  criterion it serves.

Why: a line read another way than meant is approved by the user, or built by turn, the other way;
later messages, commit messages and what rn shows at each sign-off name the goal, the criteria and
the tasks by their IDs, so an ID given to a second thing points to two.
