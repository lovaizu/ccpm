---
name: learnings
version: 1
made_from:
  checklist: 1
  usability: 1
---

# Learnings

The learnings, `learnings.md` in the session's folder `.rn/<yyyymmdd>-<slug>/`, where rn keeps one
piece of work, are used by the user once they approve the finished work, as rn puts each to them one per message,
to decide where it goes: into their checklists, `.rn/checklists/<kind>.md` in their repository,
which their later work is made with; to rn's makers as an issue, which makes rn better for everyone;
both; or neither. They decide from each learning alone, without opening the records it was found in.

A learning serves them by resting on the session's own words, so the user decides on what happened
rather than on a guess. It is found in one stretch of the session, from one sign-off to the next the
user answered, in the stretch's history on the branch, the session's files and the orchestrator's
conversations with the user: the record shows where rn fell short, such as a change the user sent
back or a question turn asked late, and a conversation what was said and done that led there, such
as a message to the user out of the form rn gives it. A learning of the user's repository alone,
such as a question their own work needs asked, goes into their checklist for the kind of work it
concerns; a general one, met in anyone's work, such as a question rn's own checklist does not ask or
a slip of rn's own steps, goes to rn's makers.

## Format

### F-1: Shape

Scope: whole

Do the learnings follow this template?

```markdown
- L1: <what happened, quoting the words of the records it rests on>; <where it would make later work better: for the user's repository alone, the kind of work and what its checklist would ask, or for everyone's work, what of rn would change>.
```

A stretch where nothing fell short adds none, the list left empty. The learnings of one stretch are
numbered from `L1`, and rn's scripts number them on from those kept from the stretches before as
they add them to `learnings.md`.

Why: rn's scripts read each learning by its ID and put it to the user one per message, and the user
reads what happened before where it goes, the order in which they judge it.

## Benefit

### B-1: What happened, in the records' own words

Scope: its part

Can the user tell from each learning what happened in the session, and see it in the quoted words of
the records it rests on, each quote saying whose words they are and at which move, each thing rn's
orchestrator did in turn, such as a point asked or a work handed to turn?

Look for:
- a learning with no quote, or a quote not as the record shows it;
- a cause the quoted words do not show;
- a quote with nothing saying whose words they are and where, such as the user's feedback at the
  plan sign-off, a commit message or a message the orchestrator sent;
- how the learning was found, which the user's decision does not use.

Why: the user decides from the learning alone, so one resting on a guess sends a wrong rule to their
checklists or to rn's makers, which every later work then follows.

### B-2: Where it would make later work better

Scope: its part

Can the user tell from each learning what would change so that later work goes better, and whether
that change is for their repository alone or for everyone's work?

Look for:
- a learning that says what went wrong and no change that would have kept it from happening;
- a learning of the repository alone with no kind of work named, or with no question its checklist
  would ask;
- a question for a checklist that asks for a step of the work rather than what the work gives its
  user;
- a learning called the repository's alone that anyone's work would meet, or one called general that
  rests on what only this repository has.

Why: rn recommends where each learning goes and the user decides; a learning with no change leaves
later work as it was, and one sent to the wrong place either hands rn's makers one repository's need
or keeps to one repository what would help everyone.

### B-3: Each learning one new thing to decide

Scope: whole

Is each learning one thing for the user to decide, apart from the others and from those learnt in
the stretches before?

Look for:
- a learning holding two things that could go to different places;
- two learnings of one cause, or one that rests on another;
- a learning of what happened before the stretch, which a stretch before learnt from.

Why: each learning comes to the user in a message of its own and takes one answer, so two things in
one get one answer where each needed its own, and a learning said twice is decided twice.

### B-4: Every shortfall of the stretch learnt

Scope: whole

Does each place where the stretch's records show rn fell short come to the user as a learning?

Look for:
- a change the user sent back at a sign-off, which the feedback in a commit message shows, that no
  learning takes up;
- a question turn asked while it ran that the points put to the user could have settled, an answer
  added to a work's decisions during the run, that no learning takes up;
- a move that does not rest on the facts of the move before it, that no learning takes up;
- a change to the work that no result of turn's names, that no learning takes up;
- a message to the user out of the form rn gives it, such as one holding more than one point, or the
  recommended option not first, that no learning takes up.

Why: a shortfall not learnt is met again in later work, and the user, who saw only what came to
them, cannot add what the records alone show.

### B-5: Each word known to the user

Scope: whole

Can the user tell what each word of a learning means, without knowing rn's insides?

Look for: a term of rn's insides, such as a script's subcommand, that no line shows the meaning of.

Why: the user decides from the learning alone, and a word they cannot read is decided with a guess.
