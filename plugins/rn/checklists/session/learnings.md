# Learnings

The learnings are `learnings.md` in the session's folder `.rn/<yyyymmdd>-<slug>/`, where rn keeps
one piece of work. The user uses them once they approve the finished work, as rn puts each to them
in a message of its own, to decide where it goes: into their checklist for a kind of work,
`.rn/checklists/<kind>.md` in their repository, which their later work of that kind is made with; to
rn's makers as an issue, which makes rn better for everyone; both; or neither. They decide from each
learning alone, without opening the records it was found in.

rn's orchestrator, the AI of rn that talks with the user, writes the learnings once, looking over
the whole session. The session's history on the branch shows where rn fell short: each change the
user sent back, each result made again and each decision an answer replaced, with the commits around
each. The orchestrator's conversations with the user show what led there, such as a message to the
user out of the form rn gives it. A plan written again at a stage's start or after a task is rn's
way of working, not a shortfall. A learning only the user's repository would meet goes to their
checklist; one anyone's work would meet goes to rn's makers.

## Format

```markdown
- L1: <what happened, quoting the words of a commit or a conversation it rests on>; <where it would make later work better: for the user's repository alone, the kind of work and what its checklist would ask, or for everyone's work, what of rn would change>.
```

A session where nothing fell short has no learnings, and the list is left empty. rn's scripts read
each learning by its ID, numbered from `L1`.

## Questions

### Q-1: What happened, in the records' own words

Does each learning show what happened in quoted words of a commit or a conversation, each quote
saying whose words they are and where they were said?

Why: the user decides from the learning alone, so one resting on a guess sends a wrong rule to their
checklists or to rn's makers, which every later piece of work then follows.

### Q-2: A cause the words show

Is each cause a learning names one that its quoted words show?

Why: a cause read from what a commit changed, where only a conversation says why, is a guess the
user takes for a fact.

### Q-3: The change that makes later work better

Can the user tell from each learning what would change so that later work goes better?

Why: a learning with no change leaves later work as it was. A question for a checklist that asks
what the deliverable gives its user, rather than a step of making it, holds for every later piece of
work of that kind.

### Q-4: The right place for it

Does each learning name the place its change belongs: the user's checklist for what only their
repository would meet, or rn for what anyone's work would meet?

Why: rn recommends where each learning goes and the user decides. One sent to the wrong place hands
rn's makers one repository's need, or keeps to one repository what would help everyone.

### Q-5: One thing to decide

Does each learning hold one thing that the user decides with one answer?

Why: each learning comes in a message of its own and takes one answer, so two things in one get one
answer where each needed its own. One cause, such as a change sent back and the result it made
again, is one learning, and a learning said twice is decided twice.

### Q-6: Every shortfall the history shows

Does each place where the session's history or conversations show rn fell short come to the user as
a learning?

Why: a shortfall not learnt is met again in later work, and the user, who saw only what came to
them, cannot add what the history and the conversations alone show. Such places include each change
sent back at a sign-off, each result made again, each decision an answer replaced, each question
asked while a task's result was made that the points put to the user before could have settled, each
step of rn's that did not rest on the facts the step before it brought, and each message to the user
out of rn's form.
