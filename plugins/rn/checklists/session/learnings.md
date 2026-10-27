---
name: learnings
version: 1
made_from:
  checklist: 1
  usability: 1
---

# Learnings

The learnings, `learnings.md` in the session's folder `.rn/<yyyymmdd>-<slug>/`, where rn keeps one
piece of work, are used by the user once they approve the finished work, as rn puts each to them one
per message, to decide where it goes: into their checklists, `.rn/checklists/<kind>.md` in their
repository, which their later work is made with; to rn's makers as an issue, which makes rn better
for everyone; both; or neither. They decide from each learning alone, without opening the records it
was found in.

A learning serves them by resting on the session's own words, so the user decides on what happened
rather than on a guess. rn's orchestrator writes the learnings once the finished work is approved,
looking once over the whole session: its history on the branch shows where rn fell short, each
change the user sent back with the proposal that answered it, each work made again and each
decision an answer replaced, with the commits and their messages around each; and the
orchestrator's conversations with the user show what was said and done that led there, such as a
message to the user out of the form rn gives it. A learning of the user's repository alone, such as
a question their own work needs asked, goes into their checklist for the kind of work it concerns;
a general one, met in anyone's work, such as a question rn's own checklist does not ask or a slip
of rn's own steps, goes to rn's makers.

## Format

### F-1: Shape

Scope: whole

Do the learnings follow this template?

```markdown
- L1: <what happened, quoting the words of a commit or a conversation it rests on>; <where it would make later work better: for the user's repository alone, the kind of work and what its checklist would ask, or for everyone's work, what of rn would change>.
```

A session where nothing fell short has none, the list left empty. The learnings are numbered from
`L1`.

Why: rn's scripts read each learning by its ID and put it to the user one per message, and the user
reads what happened before where it goes, the order in which they judge it.

## Benefit

### B-1: What happened, in the records' own words

Scope: its part

Can the user tell from each learning what happened in the session, and see it in the quoted words of
a commit or a conversation it rests on, each quote saying whose words they are and at which move,
each thing rn's orchestrator did in turn, such as a point asked or a work handed to turn?

Tried by: each quote found, as the learning gives it, in the commit it names, with `git show
<commit>`, or in the conversation it names, with `rn.py search "<words>"`.

Signs: the user reads in each learning the words it rests on, as the commit or the conversation
holds them; each cause it names is one the quoted words show, such as a conversation's words
where only a conversation shows why, rather than a cause read from a commit's change; each quote
says whose
words they are and where, such as the user's feedback at the goal sign-off, a commit message or a
message the orchestrator sent; each line is one the user's decision uses, what happened and where
it goes, rather than how the learning was found.

Why: the user decides from the learning alone, so one resting on a guess sends a wrong rule to their
checklists or to rn's makers, which every later work then follows.

### B-2: Where it would make later work better

Scope: its part

Can the user tell from each learning what would change so that later work goes better, and whether
that change is for their repository alone or for everyone's work?

Signs: the user reads in each learning, beside what went wrong, the change that would have kept
it from happening; in a learning of the repository alone, the kind of work and the question its
checklist would ask; in each question for a checklist, what the work gives its user rather than a
step of the work; a learning called the repository's alone is one only this repository would meet,
and one called general one that anyone's work would meet.

Why: rn recommends where each learning goes and the user decides; a learning with no change leaves
later work as it was, and one sent to the wrong place either hands rn's makers one repository's need
or keeps to one repository what would help everyone.

### B-3: Each learning one new thing to decide

Scope: whole

Is each learning one thing for the user to decide, apart from the others?

Signs: the user gives each learning one answer, as it holds one thing, which goes to one place;
each cause comes in one learning, a feedback and the work it made again in the same one, and each
learning stands without another.

Why: each learning comes to the user in a message of its own and takes one answer, so two things in
one get one answer where each needed its own, and a learning said twice is decided twice.

### B-4: What the session's history shows, put to the user

Scope: whole

Can the user make later work better at each place where the session's history shows rn fell short,
as each comes to them as a learning, with its cause where the history or a conversation shows one?

Tried by: `rn.py history` run, and for each feedback, work made again and decision replaced it
prints, the commits read with `git show <commit>` back to the move it rests on; each commit message
of the branch since it left the default branch read; and a cause no commit shows looked for with
`rn.py search "<words>"`.

Signs: the user meets in a learning each change they sent back at a sign-off, which the feedback in
a commit message shows; each work made again, and each decision an answer replaced, as a point asked
again leaves, but the plan written again at a stage's start or after a task, as rn's steps have it;
each question turn asked while it ran that the points put to the user could have settled, an answer
added to a work's decisions during the run; each move that does not rest on the facts of the move
before it; each message to them out of the form rn gives it, such as one holding more than one
point, or the recommended option not first.

Why: a shortfall not learnt is met again in later work, and the user, who saw only what came to
them, cannot add what the history and the conversations alone show.

### B-5: Each word known to the user

Scope: whole

Can the user tell what each word of a learning means, without knowing rn's insides?

Signs: the user reads the meaning of each term of rn's insides, such as a script's subcommand, in
a line that shows it.

Why: the user decides from the learning alone, and a word they cannot read is decided with a guess.
