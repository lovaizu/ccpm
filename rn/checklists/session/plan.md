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

A plan is worked out in this order, each step the ground of the next:

1. Set the front matter rn reads the session by: the installed rn version, the session's pull
   request, `running` as its status, turned to `finished` once the pull request is marked ready,
   and the languages of what is written and of what is said to the user.
2. From the points confirmed with the user, each a choice that changes what is made, write the goal:
   the user's purpose, with why they want it, under a title naming the piece of work in a few
   words. Each point, with how it was confirmed, is kept in the plan's decisions,
   `decisions/plan.decisions.md` beside the plan in the record, and the plan holds only what was
   decided.
3. From the goal, write the acceptance criteria, each one thing the finished work must do for the
   goal, checked on the finished work, together giving the whole goal.
4. After the plan sign-off, write the documents the purpose needs, such as a UX, a README or a
   design, each with its path, as settled with the user.
5. After the design sign-off, where rn waits for the user's answer on those documents, write the
   tasks, the parts the piece of work is divided into, each with the acceptance criteria its result
   serves, and tick each once the conductor accepts its result as serving them. The sign-offs are
   not tasks: they, and where the session stands, are kept in `state.json` beside the plan.

Each item of `usability.md` applies to a plan with the user's purpose and what the finished work
must do for it as its subject. Its F-1 is answered inside the template below, with the goal as the
main point under the title. Its B-6 is answered while the session runs: the plan is kept true as
the piece of work moves on, `status` and each task's box included.

## Format

### F-1: Shape

Scope: whole

Does the plan follow this template, front matter, headings and IDs included?

```markdown
---
rn: <the installed rn version>
pr: <the session's pull request URL>
status: running
artifact-language: <the language of everything rn writes into the repository>
conversation-language: <the language rn speaks to the user in>
---

# <The piece of work, in a few words>

G1: <the user's purpose, with why they want it>

## Acceptance criteria

- AC1: <one thing the finished work must do for the goal>

## Documents

- <the document, such as the design>: <its path>

## Tasks

- [ ] T1: <the part of the piece of work>. Serves AC1.
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

Why: a criterion of how it is built fixes a way before the design is drawn, and is met by a
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
