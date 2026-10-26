# rn UX

rn takes a whole piece of work its user asks for in their own words to their purpose, asking them
only what is theirs to decide. Build and change every part of rn so that its user gets that.

## Users and goals

- G1: Whoever wants to hand a whole piece of work to an agent: they ask for it without preparing
  anything and only answer what they are asked, and their purpose is achieved.

  The purpose is what the user wants the piece of work to achieve. Preparing is anything the user
  would do before asking, such as writing a specification or gathering what the agent needs to know.

## Key results

The key results count what happens at the sign-offs. A sign-off is a stop where rn shows the user a
proposal and waits for their answer. There are up to three, in this order: the plan sign-off, on
the plan, which holds the user's purpose as rn wrote it down and the acceptance criteria, each one
thing the finished work must do for that purpose; the design sign-off, on all the documents the
purpose needs, such as a UX, a README and a design for what the user is building, left out where
the purpose needs none; and the deliverable sign-off, on the finished work.

The key results stand from the highest priority: the changes sent back at the end come before the
user's time. Time saved on a finished work that misses the purpose is lost, since what is sent back
then is made again after all of it is built; so a version saves the user time only without raising
the changes sent back. Neither has a target value: each version is judged by how close it brings
the user to G1.

- KR1.1: The changes the user sends back at the deliverable sign-off; fewer is better, and none once
  G1 is reached.

  Each thing the user's feedback there asks to be different counts as one change. Every one counts,
  since the user agreed the purpose at the plan and design sign-offs, so a change asked at the end
  is where the finished work misses it; changes asked at those two earlier sign-offs do not count,
  as there the user is still deciding what the finished work should be. Each change is effort the
  user spent beyond answering, so fewer shows them closer to G1.

- KR1.2: The time the user spends from asking to their purpose achieved; shorter is better, and once
  G1 is reached only the time spent answering the points to decide is left.

  A point to decide is a choice that changes what is made; it is the user's to decide. The time
  counted is every minute the user spends answering, checking proposals at the sign-offs, sending
  changes back, and doing anything by hand. G1 is asking without preparing and only answering, so
  every minute beyond answering the points to decide is effort rn left to them.

## Scenes

The user and rn take part. `/rn:ty` approves a proposal and `/rn:gm <feedback>` asks for a change. A
task is one part of the piece of work, such as research, a document or a part of the finished work;
rn divides each stage into tasks as it reaches it, and changes them as each task brings its facts.
A learning is what the piece of work taught that would make later work better.

### From asking to the merge

```mermaid
sequenceDiagram
  participant U as user<br/>#lt;person#gt;
  participant R as rn<br/>#lt;plugin#gt;
  U->>R: /rn:up #lt;what they want#gt;
  R->>U: the points to decide, one per message
  R->>U: the plan, at the plan sign-off
  U->>R: /rn:ty
  opt the purpose needs documents
    R->>U: the documents the purpose needs, at the design sign-off
    U->>R: /rn:ty
  end
  Note over R: carries out the tasks
  R->>U: the finished work, at the deliverable sign-off
  U->>R: /rn:ty
  Note over R: looks back once for what fell short
  R->>U: the learnings to decide, one per message
  R-->>U: the pull request marked ready
  Note over U: merges
```

- Languages: rn's first point is the language it talks in and the one it writes into the
  repository, proposed from what the repository and the user's instructions set; all it shows the
  user, the proposals included, is in the first, adding nothing and leaving nothing out.
- The plan: rn gives the goal and each acceptance criterion an ID and puts the plan on a draft pull
  request of its own branch.
- Sign-offs: before the design and the deliverable sign-off, an AI that did not make the work reads
  and uses it in the user's place, the finished work for each acceptance criterion, and rn makes it
  again until that AI finds nothing lacking; the plan, which the user reads at its sign-off as it
  stands, rn checks against its checklist itself. At the design and the deliverable sign-off rn
  shows the link to each work and each choice made in it that the user was not asked, by rn or by
  the AI that made it, each with why, and nothing else: nothing of the user's own answers, which
  the work holds and that AI has checked, no summary of the text, no diff. The user glances at the
  work for its size and diagrams and judges those choices; the text is for that AI and rn to check.
- Records: rn writes in its commit messages what the documents do not keep: the options weighed
  with their reasons, and each feedback with its answer.
- Checklists: each document and the finished work is made with rn's checklist for its kind, which
  says what that kind, such as a README, must give its reader, and with the user's addition to it.

  The addition sits at `.rn/checklists/<kind>.md` in the user's repository and holds only what it
  adds; a kind rn has no checklist for gets one made there. rn's own checklists are not changed in
  place, since they sit outside git on the user's machine and an update of rn replaces them.

### Asked each point, and a change sent back

```mermaid
sequenceDiagram
  participant U as user<br/>#lt;person#gt;
  participant R as rn<br/>#lt;plugin#gt;
  U->>R: /rn:up #lt;what they want#gt;
  loop one message per point
    R->>U: one point to decide, with what rn looked up and the answer it recommends
    U->>R: a letter, or the user's own words
  end
  R->>U: the plan, at the plan sign-off
  U->>R: /rn:gm #lt;feedback#gt;
  R-->>U: feedback kept, rn stops
  U->>R: /rn:up
  R->>U: the point behind the feedback
  U->>R: answer
  R->>U: the plan made again, at the same sign-off, with what changed
  U->>R: /rn:ty
```

- rn confirms each point to decide with the user, even the points it could look up, since a point
  decided unasked is made again when it is wrong.

  Each message shows the points to decide, the settled ones with their outcome and the current one
  marked. For the current one it gives the conclusion, its grounds, and the options, the recommended
  one first, each with its trade-off and whether it can be undone, then one question on that point
  alone, answered by the option's letter or in the user's own words. Answers to the user's own
  questions, and slips rn corrected that leave nothing to decide, come first, apart from the points.
- On `/rn:gm`, rn keeps the feedback and stops, so the conversation can be cleared. The point behind
  the feedback is one rn decided wrong or did not ask. The same goes at every sign-off.

### While the tasks are carried out

```mermaid
sequenceDiagram
  participant U as user<br/>#lt;person#gt;
  participant R as rn<br/>#lt;plugin#gt;
  loop each step of the tasks
    R-->>U: what it will do, how far and how
    R-->>U: what is done and what comes next
    opt a point to decide
      R->>U: the point
      U->>R: answer
    end
  end
  opt a step going a way the user does not want
    U->>R: stops it, and says the way
  end
```

- Each task names the goal or the acceptance criteria it serves and is checked against them; the
  user need not watch. A change to the goal or an acceptance criterion comes to the user as a point
  to decide.

### Stopped, and gone on

```mermaid
sequenceDiagram
  participant U as user<br/>#lt;person#gt;
  participant R as rn<br/>#lt;plugin#gt;
  Note over U,R: the user stops anywhere, or closes Claude Code
  U->>R: /rn:up, in a fresh conversation
  R->>U: goes on from where it stopped
```

### Learnings

```mermaid
sequenceDiagram
  participant U as user<br/>#lt;person#gt;
  participant R as rn<br/>#lt;plugin#gt;
  loop one message per learning
    R->>U: what happened, and where it would make later work better
    U->>R: the user's checklists, an issue to rn's makers, both, or neither
  end
  R-->>U: each issue sent, and the pull request marked ready with the additions taken
```

- Once the user approves the finished work, rn looks back over the whole piece of work, once, for
  each change the user sent back, each work made again and each point asked again, and what each
  taught is a learning; one put to the user mid-way would be a stop in the work.
- A learning for the user's repository alone goes into the user's checklists; one that would help
  everyone's work, such as a question rn's own checklist does not ask or a slip of rn's own steps,
  goes to rn's makers as an issue, since rn is open source and gets better for all its users from
  it. rn recommends where each goes, and the user decides.

## Benefits

What the user gains with rn, each with why it holds; these are why the user chooses rn.

- The user asks without preparing: rough words are enough, and rn finds the points to decide and
  comes to confirm them.
- The user's purpose is achieved by answering alone: each point is confirmed, each task traced to
  the acceptance criteria, and the plan remade from the facts each move brings, so the work does
  not drift from the purpose and making a finished work again becomes rare.
- At each sign-off the user decides from the proposal alone: the plan is the proposal itself, and
  each document and the finished work has been read and used in their place by an AI that did not
  make it, so they need not read it all again; they judge only what was chosen without asking them,
  each with why.
- A piece of work that takes days neither swells nor drifts, and goes on from wherever the user
  stopped: only a short record of where it stands is carried from move to move.
- What was decided, and why, stays, in the documents rn writes into the user's repository and in
  rn's commit messages, so the next piece of work, or a teammate, starts from it.
- What a piece of work taught is confirmed with the user one learning at a time: what they add to
  their checklists makes their later work better, and what they send rn's makers makes rn better
  for them and everyone.
