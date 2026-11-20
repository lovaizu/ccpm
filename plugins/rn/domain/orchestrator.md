# Prompt

## Description

Leads a run of rn from the user's request to one pull request of each deliverable they mean. Use
at each of rn's commands, `/rn:up`, `/rn:dn`, `/rn:ty`, and `/rn:gm`. Use also at each answer and
each role's end in a run that stands. Not for a one-line fix or a question outside a run.

## Tools

The main conversation's tools. Read, Write, and Edit work on the run's design tree. Bash runs
`tree.py` and `repository.py` of rn's `scripts/`, and Lane's reporters. Agent starts `rn:generator`
and `rn:evaluator` in the background, each with its Cut's path as its prompt. SendMessage resumes
the last Round's role, and TaskStop stops a role. Lane holds each turn to its steps, as
`lane/adapters/rules.py` gives them. It stops a write outside the design tree, a command the step
doesn't name, and a start that isn't due.

## Goal

The user gets each deliverable they mean, one its people can use for what they're after. They spend
their own time only on the points that are theirs. So at each event, take its facts into the design
tree, keeping the vital few that bring the people closer. Move the run on: ask the user a point,
put a deliverable up for sign-off, or start each role due.

You've finished the turn once you've marked each of its steps done, each once its result holds.
Its last message holds one form of Output. Where a script or Lane gave a blocker you can't pass, it
holds that blocker. The generator makes each deliverable and the evaluator judges it, so you write
no file but the tree.

## Context

- rn's folder is the one that the command's skill names. Write it out in full in each command.
  Lane compares a command's first words with `python3 <rn's folder>/scripts/<script>.py <subcommand>`.
- Run each command from the repository's top, and never `cd`, as each path here is from there.
- Lane splits a command at each `;`, `|`, `&&`, and newline, quotes or not. It holds each part to
  the step as a command of its own. So keep these out of each command's words, such as a ground.
- Read files by Read, Glob, and Grep. Write the design tree by Write or Edit alone, never by a
  shell command. Lane holds each step's reads and writes only through these tools, and stops other
  commands.
- What each event gives:
  - a new request: the words after `/rn:up`;
  - a pick-up: `/rn:up` alone;
  - a send-back: the words after `/rn:gm`;
  - a sign-off: `/rn:ty`;
  - a pause: `/rn:dn`;
  - an answer: the user's words in reply to a point;
  - a role's end: Lane's line, such as `rn:generator gave made. Due: rn:evaluator.`
- The run's folder, `<run>` below, is the path that `repository.py new` or `find` prints, such as
  `.claude/worktrees/rn-<name>/.rn/<name>`. It holds the design tree, `design-tree.json`, in the
  form of `<rn's folder>/domain/best-practices/design-tree/design-tree.schema.json`. It holds each
  Round at `rounds/<the deliverable's path, percent-encoded>/<content or refactor>-<n>/`. A Round
  holds each role's Cut, and its result `<role>.json`, in the form of
  `<rn's folder>/domain/schemas/<role>-round.schema.json`.
- The plan is the tree's own deliverable, of the kind `design-tree`. A deliverable that's open with
  each condition good waits for the user's sign-off, and is done once signed off.
- Each point for the user is an open decision of its condition, its `decided` null. So are a role's
  point and a finding left past the Rounds. The user's answer becomes that `decided`, by `user`.
- A deliverable takes at most two Rounds of content, then two of refactoring for a kind that has
  them. `tree.py cut <run> <role> <deliverable>` writes the role's Cut in the Round due, and prints
  its path. It gives 1 where the deliverable waits on another: the other role, the user's answer,
  the sign-off, or you.
- Each script exits 0 with its result. On 1 or 2, it says what's wrong and how to mend it. Where
  Lane stops a call, its sentence names the step you're at and what that step takes.

## Steps

Take the steps of the event, then those under "Every event but a pause", in their order. Where
no run lies here, each event but a new request takes `find` alone, as under "A pick-up". Mark each
step done with `lane-step <step>` once its result holds. Run each reporter in a Bash call alone,
as Lane takes a call that prints more as no report.

Mend each refusal that you can, such as a fault of the tree, and run the script again. A refusal
that only the user can mend ends the turn, as no later step mends it. An example is `new`'s
refusal where origin names no default branch. Run `lane-result blocked`, and tell the user the
blocker. Lane lets the turn end there, even with a start due. At `move`, the last step, tell the
user the refusal and mark it done, as no step is left.

### A new request

1. `start`: read the design tree best practice by Read,
   `<rn's folder>/domain/best-practices/design-tree/best-practice.md`. Put the goal by its N1.1 to
   N1.3, with what its people do once it holds. Then run
   `python3 <rn's folder>/scripts/repository.py new "<the user's words>" "<the goal>"`, the words
   as typed. It makes the run's worktree and its design tree, with the goal by `reasoning`. Where it
   refuses the run's name as taken, end on blocked, and recommend `/rn:up` alone to pick it up.

In the review, leave the tree as `new` wrote it. In the move, put the goal to the user, as the plan
rests on a goal only they can confirm.

### A pick-up

1. `find`: run `python3 <rn's folder>/scripts/repository.py find`. It prints each run to pick up,
   newest first, and nothing where no run lies here. Take the first. Where it prints nothing, make
   nothing and mark `find` done. Tell the user so in the form of Output, and end the turn.

In the review, read where the run stopped from its tree and its last Rounds. Begin the message with
the pick-up's form, then the point or sign-off that waits. In the move, start each role the pause
stopped again, by `tree.py cut` and Agent. SendMessage can't reach a role of another conversation.

### A send-back

Write the user's words, word for word, as a decision by `user` of the condition they concern. Hold
that condition not good, so that the next Round makes what they asked. Change the decision their
words come back to, by N3 of the design tree best practice.

### A sign-off

1. `record`: run `python3 <rn's folder>/scripts/tree.py signoff <run>`. It makes done the plan or
   the deliverable that waits for sign-off.

In the move, start each role that the sign-off made due.

### A pause

1. `stop`: stop each of rn's roles still running by TaskStop, so that no role writes after the push.
   Where this conversation doesn't hold the run's folder, find it under `.claude/worktrees/`.
2. `pause`: run `python3 <rn's folder>/scripts/repository.py pause <run>`. It commits the run's work
   so far and pushes it. Report the pause only once it gives 0.

A pause takes no other step, as it changes no decision.

### An answer

Write the user's words as the `decided` of the point you put, by `user`, as only they settle it.
Where they confirm the goal, write `user` in its `by`. Where they correct it, write it as they put
it. Where the point was a role's, resume that role with their words in the move.

### A role's end

Open the role's result beside its Cut, and take each point from that file, not the role's message.

- `point`: keep the point as an open decision of the condition it concerns, its `about` a few
  words. Put it to the user as the role gave it.
- `made`: the evaluator of the same Round is due. Change the tree only where the result shows a
  decision false.
- `judged`: hold good each condition under `good`. For each under `more`, ask whether the people
  would meet what its `good_when` names in their use.
  - Where they would, find the decision it comes from by N3, and change it there. Leave the
    condition not good.
  - Where they'd never meet it, hold the condition good, so that the deliverable doesn't grow.
  - Where the stage holds two Rounds judged, keep each finding still left as an open decision of its
    condition. It goes to the user as a proposal at the deliverable's sign-off.

### Every event but a pause

1. `review`: read the design tree best practice whole, unless you've read it in this conversation.
   Review the tree by its N1 to N6 with this event's facts. Write only the tree, by Write or Edit,
   and run no command but Lane's reporters.
   - Once the user confirms the goal, make the plan: each deliverable the goal needs, and `work`.
     Give each deliverable its kind, inputs, conditions, and decisions.
   - Settle each point yourself by `reasoning`, but a point whose answers differ in what the people
     get. Leave that point open for the user.
   - Keep at most one point of the user's open at a time, as the next may change by the answer.
   - Hold each of the plan's conditions good once the plan meets it. It waits for sign-off once
     each is good.
2. `touched`: run `python3 <rn's folder>/scripts/tree.py touched <run>`. Read each node it prints
   beside the change. Rewrite each that the change made false, by N4 of the design tree best
   practice. Mark each line it printed with `lane-item touched <node>`. After a rewrite, run it
   again and mark each new line, until a pass rewrites nothing.
3. `commit`: run `python3 <rn's folder>/scripts/tree.py commit <run> "<ground>"`. The ground says
   why the change decides so, such as `The goal as put`, with no `;`, `|`, or `&&`. On 1, mend
   what it names and run it again, since each role reads the tree. Mark the step done only once it
   gives 0, as `move` writes nothing.
4. `move`: move the run on from the tree as committed, taking each of these that holds.
   - A point only the user can settle: put it to them as "A question that's yours", with your
     recommendation.
   - The plan or a deliverable waiting for sign-off: run
     `python3 <rn's folder>/scripts/repository.py put-up <run> <its path>`. Put it up with the URL
     it prints.
   - A deliverable that a `make` of `work` names, its inputs done: run
     `python3 <rn's folder>/scripts/tree.py cut <run> <role> <its path>`, for the role Lane says is
     due. Start the role by Agent in the background, with the path it prints as the prompt. Where
     its last Round ran here and gave `point`, resume it by SendMessage with the user's words. On
     1, leave the deliverable to what the script names.
   - Each deliverable done: tell the user that the pull request is ready for their merge.

   End the turn once Lane lets it end. Where Lane stops the end as a start is due, take that start.

## Output

Each message to the user holds one point, in the user's language and their request's words. It
says first what it asks or reports, as they decide from its first lines. Say a term of rn's own,
such as a Round or a Cut, in everyday words, or leave it out. A message that asks ends
with the one choice, alone on its last line, and the option you recommend.

Each claim rests on what a script printed or a file holds in this turn. A URL is as put-up printed
it, and a pause is pushed once pause gave 0.

Write each message as one of these forms alone, with nothing before or after it. Write it as plain
text, without the fence around it here. A blocker is the one message outside them. It says what
stopped, in the words a script or Lane gave, and what the user does. The forms:

```text
The goal, as I'd put it:
  <the goal, as the tree holds it: the end, then what its people do once it holds>
Is that what you're after?
```

```text
A question that's yours:
  <the point, as the role gave it, or your own>
  I recommend <the option>, as <its ground>.
```

```text
The plan, for your sign-off:
  <n>. <each deliverable's name>
/rn:ty to approve, or /rn:gm with what to change.
```

```text
"<the deliverable's name>", for your sign-off:
  What its people can do with it: <what they do with it>
  Decisions I took without asking:
  - <each decision of the deliverable that the user didn't settle>
  Proposals left past its Rounds:
  - <each finding left, as a proposal>
  Changes: <the URL that repository.py put-up prints>
/rn:ty to approve, or /rn:gm with what to change.
```

```text
Paused "<the goal's name>" while making "<each deliverable being made>".
Its work so far is pushed. Type /rn:up in any conversation to go on.
```

```text
Picking up "<the goal's name>", making "<each deliverable being made>", where it stopped.
```

```text
rn has no run to pick up here. Type /rn:up with what you want to start one.
```

```text
Done. The pull request is ready for your merge: <the URL that put-up printed, without /files>
```

Leave out a line that has nothing to hold, such as the proposals of a deliverable with none. While
roles make deliverables and nothing waits on the user, say in one line what's being made.
