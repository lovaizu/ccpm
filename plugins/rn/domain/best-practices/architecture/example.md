# `rn` architecture

This document says how the parts of rn give [its product vision](../../../../../dev/rn/product-vision.md). rn keeps the
work as a design tree in the user's repository, which only the code of `tree.py` reads and writes.
The main conversation settles each point of the design with the user, one at a time, and starts the
planner with it. The planner has `tree.py` write the point into the tree, and lays out the plan back
from the goal. Once the main conversation has settled a deliverable's points, a turn makes it from
them and its kind's best practice, round after round. The generator makes the deliverable whole
from the design and answers each intent as its people would, and fresh evaluators, reading as those
people, say where it meets each intent or what they still lack. A shortfall goes back to the
decision that serves it, and the next round starts from the design, bringing the deliverable in
line with the decisions. A point that only the user can settle, or a remark the user makes during a
turn, goes back to the main conversation. Lane, the plugin that holds a
plugin's roles to their steps, holds each role to the steps of the practices it carries out and the
main conversation to the routes, and lets a role start only with the text that `tree.py` cut for
it. `tree.py` commits each change on the work's branch and keeps one draft pull request for the user
to merge.

## Principles

rn builds on [the plugin best practice](../plugin/best-practice.md).
It takes as they stand the practices from
[Q1](../plugin/best-practice.md#q1) to
[Q4](../plugin/best-practice.md#q4),
[Q6](../plugin/best-practice.md#q6) to
[Q16](../plugin/best-practice.md#q16),
[Q18](../plugin/best-practice.md#q18) to
[Q20](../plugin/best-practice.md#q20), and
[Q22](../plugin/best-practice.md#q22) to
[Q25](../plugin/best-practice.md#q25). Lane is its guard, as
[Q9](../plugin/best-practice.md#q9) says, and rn names Lane in
its dependencies, as
[Q15](../plugin/best-practice.md#q15) says, since the
generator runs Lane's `lay.py` when a deliverable is a plugin.

rn differs from three of them:

- **[Q5](../plugin/best-practice.md#q5) and
  [Q17](../plugin/best-practice.md#q17)**: the main conversation
  settles the points of the design, which the practice leaves to a role, and puts each point to the
  user itself, which [Q17](../plugin/best-practice.md#q17) leaves
  to a role. *Why*: the design is the user's intent, so rn settles it where the user talks. No role
  stands between a point and the user, and nothing carries a point back and forth. The main
  conversation still makes and judges nothing of a deliverable, and the planner writes each point,
  so Lane holds every change to the tree.
- **[Q21](../plugin/best-practice.md#q21)**: rn takes in no lesson
  once a run ends. *Why*: no step of the product vision follows the work once the user has the
  draft pull request, and a step there would ask the user more, which KR1.2 counts. The cost: a
  lesson that one run meets can come back in a later run.

rn adds these. Each why says how a run goes wrong for the user without the rule.

### Planned back from the goal

The planner lays out every deliverable the goal needs, with the order they need one another in,
before any turn makes one, by [the plan best practice](../plan/best-practice.md).
`tree.py` orders the deliverables from each one's inputs and preconditions. A kind with no best
practice gets a meta deliverable before its first deliverable, made by the meta best practice.

*Why*: a deliverable left out shows only when the work reaches it, and one made before what it
takes needs making again. The people it's for then can't use it as handed over, as KR1.1 counts,
and the user waits longer, which KR1.3 measures.

### One round makes a deliverable whole

The planner makes each deliverable one that a generator makes whole in a round and an evaluator
reads whole. A larger work, such as a plugin's code, splits into a deliverable for each component of
its architecture, each after the components it takes from. The deliverable of the plugin as a whole
comes after them, and checks how they join by the architecture tests.

*Why*: a deliverable larger than a round comes out in pieces that no one design holds together, and
an evaluator that reads only part of it answers an intent on lines it never read. Its people then
meet what no one read whole, as KR1.1 counts.

### The main conversation settles, the planner writes

The main conversation settles each point of the design, in the user's conversation, one at a time.
It settles a point itself where the purpose or a best practice settles it, and puts the rest to
the user with a recommendation. A point the user answers by leaving it to rn counts as theirs.
Only the planner changes the tree, by handing `tree.py` a tree edit. After each edit it answers
each node that `tree.py` lists as touched, and where a node no longer holds, it leaves that point
open for the main conversation. A role never settles a point of the design.

*Why*: a point settled outside the user's conversation comes back as rework, or asks the user what
the purpose settles, which KR1.2 counts. Lane holds a role's calls and never the main
conversation's own, so a change written by the main conversation would go unheld, and the nodes
around it would go on saying what held before. A deliverable built on them then fails its people, as KR1.1 counts.

### Each role gets only its cut

`tree.py` cuts each role's part of the tree, and the main conversation starts the role with that
text alone. No one adds a fix, a hint, or a remark of the user's to a start on the way, or to a
message to a role that runs. No role, and not the main conversation, reads the design tree itself.

*Why*: a role that reads the whole tree takes up decisions that aren't its own, and an evaluator
that reads it judges whether the deliverable follows the design, not what its people get. A
deliverable its people can't use then passes, as KR1.1 counts. A fix or a remark added to a start
reaches the deliverable beside the design, as [Good from the root](#good-from-the-root) rules out.

### The evaluator has only what the deliverable's people have

An evaluator gets the intents of its group, the deliverable, the deliverables it takes its
content from, and the record of the deliverable tried. It never gets the design, the practices,
or the generator's record. Where the user kept a decision knowing what it costs an intent, the
evaluator gets that lack too, in the people's terms, as an accepted shortfall.

*Why*: the people a deliverable is for never see what its maker meant. An evaluator that has the
design or the practices checks how its maker made the deliverable, not what it gives them, as
KR1.1 counts. An evaluator that isn't told of an accepted shortfall sends it back every round,
and the turn never ends, which KR1.3 measures.

### A turn makes a deliverable until every intent is good

A turn is a unit inside `/rn:up`, with no skill of its own, and Lane holds its flow by the routes.

- **It starts from** the decisions the main conversation settled for the deliverable, as `tree.py`
  cuts them, and the best practice of the deliverable's kind. It starts once the planner gives
  `ready`.
- **Its phases** come in order. The first makes what the deliverable says, by its kind's best
  practice. The second makes how it reads, by `refactor-doc` for a document or `refactor-code` for
  code, and changes nothing it says.
- **Each phase goes round after round**: in each round, the generator brings the deliverable in
  line with the design and the evaluators answer each intent of the phase, until every intent is
  good.
- **It ends** once every intent of both phases is good, which the planner writes into the tree as
  it commits the deliverable. Or it stops at a point that only the user can settle, as
  [A point found open goes back to the main conversation](#a-point-found-open-goes-back-to-the-main-conversation)
  says.
- **Its rounds' records** lie in the run's folder, under `turns/`, as
  [Directory structure](#directory-structure) shows.

*Why*: a deliverable handed over with an intent not met fails its people, as KR1.1 counts. A
sentence polished before what it says holds needs polishing again, which KR1.3 measures.

### Good from the root

A shortfall goes back to the decisions that serve its intent, and the next round starts from the
design. `tree.py` cuts the next round's generator start with the deliverable's decisions and each
shortfall beside the intent it falls short of, and with nothing else. The generator brings the
deliverable in line with the decisions, so that each part of it rests on one, and keeps each part
that already does. It lays no fix on the deliverable beside the design. The generator judges
whether the decisions meet a shortfall, as only the generator makes the deliverable from them:

- Where the decisions meet the shortfall, they stand, and the round brings the deliverable in line
  with them.
- Where only a changed decision would meet it, the generator gives `open` and names that decision.
  The main conversation settles it, the planner writes it, and the turn goes on from the changed
  design, as
  [A point found open goes back to the main conversation](#a-point-found-open-goes-back-to-the-main-conversation)
  says.

*Why*: a fix laid on the deliverable beside the design is a part that no decision holds. The next
round loses it, or keeps it though no one settled it, and a fix for one evaluator's finding breaks
an intent that another found met. A part made anew though a decision already held it can lose what
an evaluator found met. A decision that a role changes is one that no one settled, and an evaluator
can't tell the two cases apart, as it never gets the design. The people then get a deliverable no
design holds, as KR1.1 counts.

### The maker checks first

Before it gives `made`, the generator answers each intent of the phase the way the evaluators do,
as the deliverable's people, with the lines that meet it or what they still lack. Where it would
answer one not met, it brings the deliverable in line with the design again. Where only a changed
decision would meet an intent, it gives `open` with that decision named instead of `made`, as
[Good from the root](#good-from-the-root) says. Only the evaluators' answers make an intent good.

*Why*: a lack that the maker could have seen otherwise costs a round of evaluators to find, and the
user waits longer, which KR1.3 measures. The maker reads what it meant, not only what it wrote, so
its own answer making an intent good would let a deliverable its people can't use pass, as KR1.1
counts.

### The evaluator seeks the good

An evaluator reads as the deliverable's people. For each intent, it says where the deliverable
meets it, or what the people still lack to reach good. It hunts no defect that the people would
never meet.

*Why*: a finding that the people never meet sends the deliverable back for a change that gives them
nothing, and the turn runs longer, which KR1.3 measures. A fix for it can break what they do meet,
as KR1.1 counts.

### A point found open goes back to the main conversation

Where the generator finds a point the design leaves open or names a decision that must change, or
an evaluator finds a point only the user can settle, the run stops there. The main conversation
settles the point, the planner writes it, and the turn goes on from the design as changed. Where
only a change to a decision the user settled would meet a shortfall, rn takes it to the user only
with a fact their answer didn't weigh. Otherwise it stays an accepted shortfall.

*Why*: a role that settles such a point itself makes a part that the design doesn't hold, which
[Good from the root](#good-from-the-root) rules out for a fix. Asking the user again what they settled
spends their time and gives them nothing to weigh, as KR1.2 counts.

### A remark during a turn is a point

A remark the user makes while a turn runs is a point. The main conversation first stops each role
of the turn that still runs, with `TaskStop`. The remark is a prompt of the user's, so Lane lets the
stop through, as
[its principle on how long the guard holds the main conversation](../../../../../dev/lane/architecture.md#the-guard-holds-the-main-conversation-only-while-its-run-lasts)
says. Right after the stop, the main conversation calls `/rn:up` with the remark, which ends the
turn's run and begins another. It hands the planner the remark settled, where the purpose or a best
practice settles it, or else as a point open. The planner writes it into the tree. A remark settled
lets the turn go on from the design as changed. For a point open, the planner gives `asks`, the run
ends with no start due, and the main conversation puts the point to the user as it puts any point.
No one adds the remark to a running role's start or messages.

*Why*: a role that runs on makes or judges a deliverable by a design about to change, and its
result costs the user a round, as KR1.3 measures. A turn that went on in the run that the remark
broke would start its next role from a cut made before the remark. A remark passed to a role
reaches the deliverable beside the design, as [Good from the root](#good-from-the-root) rules out,
and the next round loses it, so the user says it again, as KR1.2 counts.

### Tried in a throwaway copy

The commands that try a deliverable, its install steps among them, run only in a throwaway copy of
the repository, with a throwaway home.

*Why*: a command run as the people run it, such as `tidy` on a Downloads folder, would otherwise
change the user's own files, which can't be undone.

### Every step on every run

Lane holds each role to the steps of the practices it carries out, read from the best practice
itself at the steps port, a best practice made on the run among them. It holds the main
conversation to the routes, and each start to the text that `tree.py` gave.

*Why*: an AI that skipped a step once skips it again on another run, and the deliverable misses
what the step was there to make sound, as KR1.1 counts.

### The repository holds the work

`tree.py` commits every change to the tree on the work's own branch as the planner writes it, with
its grounds in the commit message. It commits a deliverable once its turn ends good, and keeps
one draft pull request for the work. The user merges it, and rn never does. A run's files lie in
`.rn/<yyyymmdd>-<goal>/`, and `/rn:up` alone goes on from them.

*Why*: a conversation can end at any point, and work kept only in it goes with it, so the
user answers again, as KR1.2 counts. The merge is the user's, as
[Q16](../plugin/best-practice.md#q16) says.

## User stories

- **S1**: the user wants to type `/rn:up` with what they want, in their own words, and confirm the
  goal rn reads in it. It carries the walkthrough's first `/rn:up` and the goal put to the user.
- **S2**: the user wants to answer each point rn puts to them, one at a time, in their own words.
  It carries the plan shown with its first point, the answer `each file`, each point that comes up
  while rn makes a deliverable, and each remark the user makes meanwhile.
- **S3**: the user wants to type `/rn:up` alone in a new conversation, and have rn go on where it
  stopped, asked nothing again. It carries the walkthrough's second `/rn:up` and `Picking up`.
- **S4**: the user wants each deliverable committed on a branch, one draft pull request to merge,
  and the decisions rn took without asking them. It carries the walkthrough's `Done`, and the
  user's merge.

## Components

![rn's components](images/components.svg)

What each decides alone:

- **user**: what's theirs: the goal, each point the purpose and the best practices leave open, and
  whether to merge.
- **main conversation**: whether a point is the user's or settled by the purpose or a best
  practice, how it's settled, the words it's put in, when a deliverable has no point left, and
  which roles of a turn to stop when the user makes a remark.
- **planner**: the goal as drafted from the request, the plan, each deliverable's kind, inputs and
  preconditions, each deliverable's size, so that a round makes it whole, whether each node a
  change touches still holds, and each status and intent made good from the evaluators' answers.
- **generator**: the deliverable, each small point of making it, such as a phrase, its own answer
  to each intent before it gives `made`, the points the design leaves open, and whether the
  decisions meet a shortfall or only a changed decision does.
- **evaluator**: where the deliverable meets each intent of its group for its people, or what they
  still lack, and the points only the user can settle.
- **tree.py**: the form of the design tree and of a change, the order of the deliverables, each
  role's cut, the nodes an edit touches, each turn's phase, round and groups, the points open for the
  main conversation, each commit, the branch, and the draft pull request, and the report of each
  decision taken without asking, read from the run's commits.
- **throwaway.py**: where a deliverable's commands run, and what of them the try record keeps.
- **steps adapter**, **items adapter**: how rn's best practices and design tree read in the forms
  of Lane's steps and items ports.
- **guard**: whether a role's call keeps its lanes, which start is due, whether a start's text
  is the one `tree.py` gave, and whether a stop of a role or a call of `/rn:up` during a run follows
  a prompt of the user's, as [Lane's architecture](../../../../../dev/lane/architecture.md) says.

These choices in the components are ones a developer would question:

- **The main conversation calling `/rn:up` again once it settles a point, or with a remark,** over
  resuming the role that stopped: the point comes from the main conversation, not from the user's
  words alone, and Lane lets a resume carry the user's words and nothing else. A new call of the
  skill begins a run, whose first start is the planner with the text `tree.py` cut from the change.
  During a run, Lane lets such a call through only once the user has written a prompt, and it then
  ends that run. The cost: the main conversation reads the skill's part again on each call.
- **One point a user settles in each change** over the points of a deliverable written at once: each
  answer is in the tree before the next point goes out, so a conversation that ends loses none,
  as KR1.2 counts. The cost: a run of the planner for each such point.
- **The planner started fresh for each change** over one planner kept for the run: each start
  keeps to its own cut, and a fresh planner carries no decision of an earlier change into this
  one, as KR1.1 counts. The cost: the planner reads its cut again on each start.
- **The generator running `throwaway.py` once it has made the deliverable** over each evaluator
  running it: the evaluators of a round run at once, and one try record for the round lets them
  judge the same run of the commands. The cost: an evaluator can't try a command that the try
  record doesn't hold, and names it as a lack instead.
- **`tree.py` committing and keeping the draft pull request** over a script of its own: each commit
  holds a tree edit, and the edit's grounds make its message, which only `tree.py` reads in the
  form the planner writes. The cost: `tree.py` needs git, and `gh` for the pull request.

## Data model

![rn's data](images/data-model.svg)

- **Request**: the user's words after `/rn:up`, as they typed them.
- **Change**: what one start of the planner writes: the request, the decisions the main
  conversation settled, a remark as a point open, or a turn's answers.
- **Tree edit**: what the planner hands `tree.py` to write: each node it changes, the grounds, and
  its answer to each node touched: it holds, or the planner leaves it open.
- **Cut**: the text `tree.py` gives a role to start with: its run values and its part of the tree.
- **Point**: a decision the main conversation settles, whether the tree holds it open, a turn
  found it, or the user remarked it during a turn.
- **Turn**: the making of one deliverable from its settled decisions, through both phases.
- **Round**: one making of the deliverable in a phase, and the evaluators' answers to it.
- **Making record**: the generator's record of a round, `generator.json`: what it made, each small
  point it decided, its own answer to each intent, and each point it found open.
- **Answers**: an evaluator's record of a round, `evaluator-<group>.json`: each intent met with the
  lines that meet it, or not met with what the people still lack.
- **Try record**: the commands that try a deliverable and what each gave, `throwaway.txt`.
- **Accepted shortfall**: a decision of the user's, under the intent it costs, that says what the
  people lack by it.
- **Port JSON**: a best practice's steps or a tree's items in the forms of Lane's ports.

## Sequences

Each story's steps follow in order. The participants carry their names in
[Components](#components), and the data in brackets those in [Data model](#data-model). Each start
of a role goes through the guard, which lets it through only with the cut `tree.py` last gave for
that role, as [Lane's architecture](../../../../../dev/lane/architecture.md) draws.

### S1: a request

```mermaid
sequenceDiagram
  actor U as user
  participant M as main conversation
  participant T as tree.py
  participant P as planner
  participant R as run's folder
  U->>M: /rn:up with what they want (Request)
  M->>T: start, for the planner (Request)
  T->>R: makes .rn/yyyymmdd-goal/
  T-->>M: the planner's cut (Cut)
  M->>P: starts it (Cut)
  P->>T: write, with the goal drafted (Tree edit)
  T->>R: writes it (Design tree)
  P->>T: commit (Tree edit)
  T->>R: commits on the work's branch, made here
  P-->>M: gives asks
  M->>T: points (Design tree)
  T-->>M: the goal, to confirm (Point)
  M->>U: the goal, is that what you're after? (Point)
  U->>M: answers
  Note over U,M: The goal is the user's, so the main conversation settles it with them, as S2 draws.
```

- **The planner drafting the goal** over the main conversation asking for it outright: the user
  confirms a goal written to the plan best practice faster than they write one, which shortens
  what KR1.3 measures. The cost: a run of the planner before the user's first point.

### S2: a point settled

```mermaid
sequenceDiagram
  actor U as user
  participant M as main conversation
  participant T as tree.py
  participant P as planner
  participant R as run's folder
  M->>T: points (Design tree)
  T-->>M: the points open of the deliverable at hand, with its intents and inputs (Point)
  loop each point open
    alt the purpose or a best practice settles it
      M->>M: settles it, by reasoning or research
    else it's the user's
      M->>U: one point, with a recommendation (Point)
      U->>M: answers, in their own words
    end
  end
  Note over M,T: Once a point is settled by the user, or none is left, the main conversation calls /rn:up.
  M->>M: calls /rn:up
  M->>T: start, for the planner, with the decisions settled (Change)
  alt the change is out of form
    T-->>M: what's wrong
  else it's in form
    T-->>M: the planner's cut (Cut)
    M->>P: starts it (Cut)
    opt the goal is newly the user's
      Note over P: lays out the deliverables back from the goal, each one a round makes whole, a meta deliverable before the first of a kind with no best practice
    end
    loop until the tree holds and each node touched is answered
      P->>T: write, with each decision (Tree edit)
      alt the edit breaks the tree, such as an order out of place
        T-->>P: what's wrong
      else it holds
        T->>R: writes it (Design tree)
        T-->>P: each node the edit touches
        P->>P: answers each, as holding or left open (Tree edit)
      end
    end
    P->>T: commit (Tree edit)
    T->>R: commits on the work's branch, the grounds as its message
    alt a point is open
      P-->>M: gives asks
      Note over M,T: The main conversation shows the plan where it's new, and goes on with the points.
    else the deliverable at hand has none left, which the change says
      P-->>M: gives ready
      Note over M,P: A turn starts, as the next section draws.
    end
  end
```

- **The run ending at `asks`, a route with neither a next start nor a wait,** over a route that
  waits for the user: such a route has the main conversation resume the planner with the user's
  words alone, while the main conversation settles points by reasoning too. The cost: the start of
  a role started by mistake between two runs goes unheld, though Lane still holds its calls.

### S2 and S3: a deliverable made in its turn

```mermaid
sequenceDiagram
  participant M as main conversation
  participant T as tree.py
  participant G as generator
  participant W as throwaway.py
  participant E as evaluator
  participant P as planner
  participant R as run's folder and the deliverable
  M->>T: start, for the generator
  T->>R: makes the next round's folder (Round)
  T-->>M: the generator's cut: the deliverable's decisions, its kind, its phase, and each of last round's shortfalls beside its intent (Cut)
  M->>G: starts it (Cut)
  loop until it would answer each intent met, or finds a point open
    G->>R: brings the deliverable in line with the design, by its phase's practices, keeping each part that rests on a decision
    G->>W: runs it
    W->>R: copies the repository, runs the deliverable's commands there, and writes what they gave (Try record)
    G->>R: answers each intent as the deliverable's people, and writes its record (Making record)
  end
  alt the design leaves a point open, or only a changed decision meets an intent
    G-->>M: gives open, naming the point or the decision
    Note over M,G: The run ends, and the main conversation settles the point, as S2 draws.
  else every intent is met by its own answers
    G-->>M: gives made
    M->>T: start, for each evaluator
    T-->>M: a cut for each group of the phase's intents (Cut)
    par one for each group, at once
      M->>E: starts it (Cut)
      E->>R: reads the deliverable, its inputs, and the try record, as its people
      E->>R: writes where it meets each intent, or what its people still lack (Answers)
      E-->>M: gives open, more, or good
    end
    Note over M,E: Of the evaluators' results, the guard takes open, then more, then good.
    alt an evaluator gave open
      Note over M,E: The run ends, and the main conversation settles the point, as S2 draws.
    else one gave more
      Note over M,G: The next round starts from the design, each shortfall beside its intent.
    else every one gave good
      M->>T: start, for the planner, with the turn's answers (Change)
      T-->>M: the planner's cut (Cut)
      M->>P: starts it (Cut)
      P->>T: write, with each intent good (Tree edit)
      T->>R: writes it (Design tree)
      alt the phase was of what the deliverable says
        P->>T: commit (Tree edit)
        P-->>M: gives ready
        Note over M,G: The phase of how it reads, by refactor-doc or refactor-code.
      else the phase was of how it reads
        P->>T: write, with the deliverable done (Tree edit)
        P->>T: commit, with the deliverable, and push (Tree edit)
        Note over P,T: S4 draws the commit and the pull request.
        alt the next deliverable has a point open
          P-->>M: gives asks
        else its points are settled
          P-->>M: gives ready
        else every deliverable is done
          P-->>M: gives done, with the report (Message)
        end
      end
    end
  end
```

- **A turn inside `/rn:up`, with no skill of its own,** over a skill for a turn: the user types
  only `/rn:up`, as the walkthrough does, and the routes of one skill take the work from the
  planner's `ready` through the rounds and back to the planner with no call between them. The cost:
  `/rn:up`'s routes carry the results of every role.
- **The generator bringing the deliverable in line with the design in each round, keeping each
  part that rests on a decision,** over mending the lines that last round found short, or making
  the whole deliverable anew: each round's deliverable holds only what the design holds, and keeps
  what an evaluator found met. The cost: the generator reads each part against the decisions,
  however small the shortfall.
- **The generator answering each intent before it gives `made`** over leaving every answer to the
  evaluators: a lack it can see costs no round of evaluators. The cost: the generator reads the
  deliverable again as its people in each round.
- **The rounds without a limit** over a turn that stops after a set number: a shortfall that only
  a changed decision meets goes back as a point open, so a turn goes on only while the generator can meet what
  the evaluators find. The cost: a turn runs long while its evaluators keep finding new shortfalls.
- **One evaluator for each group of intents, all at once,** over one for every intent: each is fresh
  on fewer intents, as KR1.1 asks, and they run side by side, as KR1.3 asks. The cost: each evaluator
  reads the whole deliverable.

### S2: a remark during a turn

```mermaid
sequenceDiagram
  actor U as user
  participant M as main conversation
  participant T as tree.py
  participant G as generator
  participant E as evaluator
  participant P as planner
  Note over M,P: A turn runs, as the last section draws.
  U->>M: a remark, in their own words (Point)
  Note over U,M: The remark is a prompt of the user's, so the guard lets each stop through.
  opt a role of the turn still runs
    M->>G: stops it [TaskStop]
    M->>E: stops each [TaskStop]
    M->>P: stops it [TaskStop]
  end
  opt the purpose or a best practice settles the remark
    M->>M: settles it, by reasoning or research
  end
  M->>M: calls /rn:up with the remark
  Note over M,P: The guard ends the turn's run and begins another, as Lane's S3 a run the person redirects draws.
  M->>T: start, for the planner, with the remark settled or as a point open (Change)
  Note over M,P: The planner writes it into the tree, as S2 draws.
  alt the remark was settled, and the deliverable has no point left
    P-->>M: gives ready
    Note over M,P: The turn goes on from the design as changed, as the last section draws.
  else a point is open
    P-->>M: gives asks
    Note over U,M: The run ends with no start due, and the main conversation puts the point to the user, as S2 draws.
  end
```

- **Each role that still runs stopped with `TaskStop`** over letting it end, or sending it the
  remark: a role let end gives a result made by a design about to change, and a remark sent to it
  reaches the deliverable beside the design. Claude Code's subagents reference documents
  `TaskStop`. The cost: the stopped round gives no result, so its work goes unused.
- **A call of `/rn:up` right after the stop, with the remark settled or as a point open,** over
  starting the stopped role again in the same run, or putting the remark to the user first: the
  new run's first start is the planner, which writes the remark before any role starts, and Lane
  ends the old run on such a call once the user has written a prompt. The stopped run still has a
  start due, which Lane has the main conversation take before its turn ends, so the user would get
  the point only after a role ran by the old design. The cost: the planner runs twice for a remark
  that's the user's. It first writes the remark open, and later the user's answer.

### S3: picking up

```mermaid
sequenceDiagram
  actor U as user
  participant M as main conversation
  participant T as tree.py
  participant P as planner
  participant R as run's folder
  U->>M: /rn:up, alone, in a new conversation
  M->>T: start, for the planner
  T->>R: reads each run under .rn/
  T-->>M: the planner's cut, with the work left (Cut)
  M->>P: starts it (Cut)
  alt no work is left
    P-->>M: gives done, with none to pick up
    M->>U: says so
  else more than one is left
    P-->>M: gives asks, with each by its goal
    M->>U: which one? (Point)
    U->>M: answers
    Note over U,M: The main conversation calls /rn:up with the run's folder, and the run picks up from it.
  else one is left
    M->>T: status
    T-->>M: where the work stands
    M->>U: Picking up, at the deliverable not yet done
    alt the deliverable at hand has a point open
      P-->>M: gives asks
      Note over M,P: The main conversation goes on with the points, as S2 draws.
    else it's doing
      P-->>M: gives ready
      Note over M,P: The turn goes on from its last round, as the last section draws.
    end
  end
```

### S4: the work handed over

```mermaid
sequenceDiagram
  actor U as user
  participant M as main conversation
  participant P as planner
  participant T as tree.py
  participant GH as GitHub
  P->>T: commit, with the deliverable, and push (Tree edit)
  T->>T: commits the deliverable and the tree on the work's branch
  alt git or gh can't push, such as with no login
    T-->>P: what's missing, the commit kept on the branch
    P-->>M: names it in its message, and gives its result as the rest of the work goes on
    M->>U: asks for what's missing
  else the work has no pull request yet
    T->>GH: pushes the branch, opens a draft pull request [gh]
  else it has one
    T->>GH: pushes the branch [git]
  end
  opt every deliverable is done
    P->>T: report
    T-->>P: each decision taken without asking, with its grounds, from the run's commits
    P-->>M: gives done, with the report
    M->>U: Done, the deliverables, and the decisions taken without asking
    U->>GH: reads the draft pull request, and merges it
  end
```

## Deployment

![rn's deployment](images/deployment.svg)

The user installs rn as [the README](../../../README.md#installation) says, which installs
Lane with it, and types `/rn:up` in Claude Code at the root of their repository.

- **macOS and Linux** over Windows as well: `python3` and the symbolic link of `hooks/lane/` work
  there as rn needs them, and the README names Windows as not yet tried. The cost: a user on
  Windows has no tried way.
- **Python 3.9 and its standard library only, for `tree.py`, `throwaway.py`, and the adapters,**
  over a later Python or packages, as
  [Q13](../plugin/best-practice.md#q13) says: the user installs
  nothing for rn. The cost: the code goes without what later versions give.
- **A run's files in `.rn/<yyyymmdd>-<goal>/` of the repository, committed on the work's branch,**
  over the system's temporary folder, as
  [Q12](../plugin/best-practice.md#q12) says for what the user
  may keep: a run picks up from them in any conversation, and each round's records stay for the
  user to read. A user who keeps `.rn/` out by `.gitignore` still gets each commit, with its
  grounds in the message. The cost: a folder in the user's repository, which the draft pull request
  shows.
- **A best practice made on a run in the run's `best-practices/`** over rn's own folder: rn's folder
  changes with each update, and a later run of the repository finds it there. `tree.py` looks for a
  kind in the run's folder, then in rn's own, then in the repository's earlier runs. The cost: a
  later run may take a best practice made for an earlier run's work.
- **The throwaway copy and home in the system's temporary folder** over a folder in the repository:
  the copy means nothing once the round ends, and a command run there can't reach the user's own
  files. The cost: a command that needs a file outside the repository, such as one in the
  user's Downloads folder, gets a made-up one in the throwaway home.

## Directory structure

```text
plugins/rn/
├── .claude-plugin/plugin.json       rn's manifest, naming Lane in its dependencies
├── skills/up/SKILL.md               the main conversation's entry, /rn:up
├── agents/<role>.md                 the entries of the planner, the generator, and the evaluator
├── domain/up.md                     the main conversation's part
├── domain/<role>.md                 the parts of the planner, the generator, and the evaluator
├── domain/forms/                    the JSON Schemas of each role's in and out, Change, Tree
│                                    edit, Making record, and Answers
├── domain/best-practices/<kind>/    every kind's best practice: plan, plugin, and those of each
│                                    deliverable, meta among them
├── domain/                          the code of tree.py and throwaway.py
├── scripts/tree.py, throwaway.py    tree.py and throwaway.py
├── hooks/hooks.json, lanes.json     the guard's hook entries, and rn's lanes and routes as laid
├── hooks/lane/                      the guard, a link to Lane's code
├── hooks/adapters/                  the steps adapter and the items adapter, with their cases
└── README.md, CHANGELOG.md, images/   for rn's users

dev/rn/
├── product-vision.md, architecture.md, images/   rn's product vision and architecture
├── README.md                        for rn's developers
├── cosmic-ray.toml                  the mutation testing
└── tests/
    ├── unit/                        unit tests, at the path of what each tests
    ├── architecture/                a test for each path of each sequence
    └── product-vision/              the trials of O1, and the repository tidy that they work in

.rn/<yyyymmdd>-<goal>/               Design tree, as design-tree.json
.rn/<yyyymmdd>-<goal>/best-practices/<kind>/   a best practice made on the run
.rn/<yyyymmdd>-<goal>/turns/<nn>-<deliverable>/<round>/   Making record, Answers, and Try record
                                     of each Round, the rounds of both phases in order
<the paths the plan gives>           each deliverable
<temporary folder>/rn/<yyyymmdd>-<goal>/   the throwaway copy and home, and each Tree edit until
                                     tree.py commits it
```

- **The parts in `domain/`, with the best practices and the code beside them,** as
  [Q1](../plugin/best-practice.md#q1) says, over Turn's
  `core/roles/` and `core/domain/`: rn now holds Turn, so it keeps one folder of its own
  knowledge, where Lane finds each part. The cost: moving every file of Turn's.
- **No progress file** over a file that says where the run stands: the design tree's statuses and
  the rounds' records already hold it, and a second record of it drifts from them. The cost:
  `tree.py` reads the rounds' folders to tell which round is due.

## Tests

rn tests by [the architecture best practice](best-practice.md#q12)
and [the plugin best practice](../plugin/best-practice.md#q22),
and differs from them where this section says.

![rn's tests](images/tests.svg)

- **The `tree.py` process tried `FULL` at unit and at architecture** over `HAPPY`: a fault there
  writes the tree wrong, hands a role another's cut, or hands the evaluator the design, and no
  higher level checks every case. The cost: the most tests to keep up as the tree's form changes.
- **Lane's double of Claude Code and its trial driver, taken from `dev/lane/`,** over a double of
  rn's own, as [Q14](../plugin/best-practice.md#q14) says: one
  double sends the events that a recorded Claude Code sent, for both plugins. The cost: a change to
  Lane's double reaches rn's tests.
- **`claude plugin eval` left out of the trials** over a suite of eval cases: an eval case runs one
  prompt in an empty workspace and never stops for an answer, while the walkthrough types `/rn:up`
  twice, answers two points, and goes on in a new conversation. An eval run leaves `gh` real, so it
  would open a real pull request, and a case run on one prompt tries a skill alone, which
  [Q22](../plugin/best-practice.md#q22) rules out. The cost: the
  trials need their own driver, which Lane's already is.
- **The trials `HAPPY` for the Claude Code process, and `SMOKE` for the rest,** over every row
  alike: only the trials run the prompts, while the other rows only confirm what lower levels
  checked. The cost: a fault in a prompt shows only once every lower level passes.
- **The trial's `tidy` holding each fact a deliverable needs, such as where it's hosted,** over a
  placeholder: no way of making a README can give a real clone command from a placeholder, so a
  trial would fail on the fixture and not on rn. The cost: keeping the fixture's facts true.
