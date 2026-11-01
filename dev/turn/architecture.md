# turn architecture

turn draws a work's design from its kind's template and the person's answers, and has an AI that
never sees the design use the work as its user would, until that AI finds the work meets the aim
of every question of the template. A kind is a sort of work, such as a press release, and its
template holds the kind's format, the shape of the work, and its questions, each one asking what
the work's user gets from it. Four roles do this: planner, designer, builder and evaluator. The
builder and the evaluator first make what the work says, then better how it says it. The ccpm plugin
[lane](../../plugins/lane/README.md) holds the order the roles go in and the limits of each. The
experience this delivers is in [ux.md](ux.md).

## Principles

turn holds the principles of [how a plugin works](../architecture.md#principles), with the
reasons under its [Why it is so](../architecture.md#why-it-is-so), except where a choice under
Components says it departs from one, and why. In that document's words, turn's builder is the
maker, its evaluator the reader, and a question of a template an item. A role answers each question
**good** or **more**. A good answer says the work meets the question's aim, and names the lines
that meet it. A more answer, called a more, says the work falls short, and says what the work's
user gets once it is good, never how to make it. Good and more are what that document calls an
item's Good and need. The principles below are what turn adds.

### One way for every kind

turn's roles hold no rule of any one kind; all that a kind needs is in its template.

A new kind then needs only a template, and every kind gets the same care. A rule written into a
role for one kind, such as "a press release carries a date", bends the work of every other kind.

### Nothing is needed beforehand

turn asks for what it needs: planner asks the kind, and designer asks this work's purpose. A caller
may give what it has already settled with the person, and turn takes that as decided.

Anyone who wants a work can then ask for it in a sentence. A caller such as rn has often settled
the kind or the purpose already, and asking the person again would spend their time on a point
they have decided.

### The evaluator uses the work as its user would

The evaluator uses the work as its user would, and answers each question by what that user gets.
When the work is a template, the evaluator uses it on the examples it holds: each question's
`fails` and `passes`, which are works of that kind, judged as the question asks.

A judge who reads only the work's words passes a work that meets them and misses its aim. A press
release whose headline names the product passes a reading of the words, while a reporter still
cannot tell from it what is new. The builder answers the questions on its own work the same way, in
a file called its self-check, so it finds first what the evaluator, in its file called the
verification, would find.

### The evaluator never sees the design

The evaluator takes the work and the templates `turn:up` gives it, and never the design tree.

The work's user never sees the design. An evaluator that has it judges whether the work follows the
design, and passes a work that follows a wrong one.

### One asker for each thing the person decides

Planner alone asks the person about the kind and its template. Designer alone asks about this
work's purpose and its design, and alone changes the design.

The work is then always made from one design, and the person is asked each point once. Two roles
that asked would ask the person twice, or keep two answers that drift apart.

### Decided from the purpose down

Designer decides in the order the decisions build on one another, this work's purpose first, and
every decision serves a question of the template. Designer decides what the purpose and the best
practice settle, and asks the person what only they can decide.

Designer keeps the decisions in a design tree: this work's purpose as its goal, the template's
questions under it, and under each question the decisions that make it good. It is read from the
goal down, as a tree is, though one decision may serve several questions and build on several
decisions. A decision made before the one it builds on is made again once that one is made. A
decision that serves no question is made, kept and checked for nothing.

### What the work says before how it says it

The builder and the evaluator make the work in two phases. In the content phase, they answer the
questions of the kind's own template alone, and the builder makes the work from the design tree. In
the refactoring phase, they answer the questions of each template the kind's template includes,
such as `refactor-doc` for every document, alone and with no design tree; only how the work says a
thing changes. A point that would change what the work says goes back to designer, and through the
content phase again.

The builder and the evaluator then keep to what the work says while it is made. Wording polished
before the content is settled is polished again at each new making. A polish that changed what the
work says would pass unchecked by the kind's own questions.

### A more is mended at its decision

Each more of the kind's own questions goes to designer, who traces it to the decisions that serve
its question. Where a decision cannot make its questions good, designer decides it again, with the
decisions that build on it, as it decided it first: asking the person where the fact is theirs. No
role adds onto the work to answer a more.

A more that comes back on a question after its decision was made again, or in the refactoring phase
after the builder mended it, is one the decisions cannot make good. In the refactoring phase the
builder returns it `open`. Designer then brings it to the person with two ways: decide it again
another way, which designer recommends, or change this work's purpose, which changes what the
questions ask of it. Either way the design changes, and the content phase runs again. No count of
how often the work is made again stops the run; a design that can make every question good does.

A fault fixed where it shows is a patch, and patches pile up until the work no longer reads as one
design. Making the decision again changes every part that rests on it. Where the decisions hold and
the work strays from them, designer keeps the decisions, and the builder makes the work to them
again. A loop comes from designer keeping a decision that cannot make its question good, so the
way out is a decision made again, or a purpose only the person can change. A bound on how often
the work is made again would hand the person a work that falls short, with no word of why.

### Each role works from the run's files

Each role starts fresh at each move, and takes what earlier roles made from the run's files: the
design tree, the self-checks and the verifications, kept in a folder of their own for each run.

The template and the run's files hold all a role takes from another, so no role needs another's
conversation. An evaluator started fresh reads the work as for the first time each time it is
made again, as no work is passed by the one who made it, and a run stopped anywhere goes on from
its files.

### `turn:up` tells the phase from the roles' ends

The phase is a fact of the run, not of the run's files. `turn:up` tells it from the role that last
ended, the answer it ended with, and the phase `turn:up` gave it, and gives the builder and the
evaluator that phase's paths; neither role tells its phase itself. The work enters the refactoring
phase when the evaluator of the content phase ends with every question good. It goes back to the
content phase whenever the move goes to designer. A `turn:up` started again begins at move 1, and
so in the content phase.

`turn:up` holds the run, and the phase is turn's own, not lane's. `turn:up` gets each role's end
and answer whether it started the role in the foreground or the background, while lane may not
name the position of a move to a `turn:up` that Claude Code resumes
([lane's flow](../../plugins/lane/docs/flow.md)). The files cannot tell the phase. Say the builder, in the refactoring phase, returns a point that
would change what the work says, and designer keeps its decisions. The files then read as they did
in the refactoring phase, yet the work must go through the content phase again. An evaluator that
told the phase from files would also read files beyond the work, which its user never sees.

### lane holds the order and each role's limits

turn declares the order of its roles and the limits of each role in a proposal to lane, and keeps
no script of its own for either. turn's scripts check only what no lane holds.

lane writes and tests each check once, and tells a role that drifts the sentence of its own step,
so the role goes back to the step. A script of turn's own for the order would read the roles' calls
apart from lane, and drift from it.

### turn knows others only by what they document

turn uses lane only as lane's README and its documents say, and a caller only as
[Calling turn](../../plugins/turn/docs/calling.md) says. It names no file of any caller.

lane and each caller change their own code freely behind what they document. A turn built on what
they do not document breaks when they change, and a turn shaped for one caller stops being one way
for every caller.

## User stories

The stories carry O1, the one scenario of [ux.md](ux.md): a person has turn write a press release.
Each story quotes O1 and names the steps of the README's Walkthrough that show it.

- As the person who wants a work, I want to ask `turn:up` for it in the main conversation, and
  confirm its kind. Carries O1's request, "Write a press release for our new meeting-room booking
  app", and its confirmation, "Is this a release for the press?" (the README's Walkthrough, steps 1
  and 2).
- As that person, I want to approve the format and the checklist turn draws for a kind it has not
  made before, and have them kept for my next work of that kind. Carries O1's research and "Format
  … Approve?" (step 3), and the README's line that the next press release skips step 3.
- As that person, I want to answer what this work is for and each point only I can decide, each
  with the answer turn recommends, and to approve the design. Carries O1 from "What is the release
  for?" to the approved key points (steps 4 and 5).
- As that person, I want the work only once a second AI, using it as its user would, finds every
  question good, both of what the work says and of how it says it. Carries O1's last step, "The
  press release" (step 6), and the README's How it works.
- As a plugin's step, such as rn's, I want to start `turn:up` for a work my step needs, giving what
  my step has already settled with the person, and get the work back. Carries O1 when the person
  reaches turn through such a plugin, and the README's Documentation, "Calling turn".

## Logical view

### Components

![turn's components](components.svg)

- `turn:up` alone holds a run. First it names the run's folder, `.turn/<yyyymmdd>-<name>/`, from
  the request: `<name>` is a few words naming the work asked for, and a run stopped is found again
  by it. It takes each move lane tells it (follow_flow), starts each role, and waits for it to end,
  as lane tells the next move only once the role has ended. It alone tells the phase, from the role
  that last ended and its answer, as the principle above says. It ends once lane tells it the flow
  is done, naming each file of the work, one on each line.
- `turn:up` starts each role with the request and one JSON line after it, whose keys the role's
  lanes read as values given for the run, as [lane's lanes](../../plugins/lane/docs/lanes.md) say.
  A path is from the folder Claude Code runs in; `null` says there is none.
  - planner: `run`, the run's folder; and `kind` where the caller gave one. It ends with one JSON
    line, `{"template": "<path>", "includes": ["<path>", ...]}`.
  - designer: `run`; `template`, the kind's template; `tree`, the design tree; `back`, the
    self-check or the verification of the role whose answer sent the work back, or `null` at first;
    and `purpose` and `decided` where the caller gave them. It ends with one JSON line,
    `{"work": ["<path>", ...]}`.
  - builder: `templates`, the phase's templates; `tree`, the design tree in the content phase and
    `null` in the refactoring phase; `work`; `answers`, the phase's self-check; and
    `verification`, the phase's last verification, or `null` before the first. It ends with `open`
    on a line of its own where it returns a point to designer.
  - evaluator: `templates`; `work`; and `answers`, the phase's verification. It ends with `more`
    on a line of its own while an answer is more.
- turn's proposal to lane declares the flow on `turn:up`, as
  [lane's flow](../../plugins/lane/docs/flow.md#the-flow) gives it. Its order is planner, designer,
  builder, evaluator, builder, evaluator, positions 1 to 6. Positions 3 and 4 are the content
  phase, and 5 and 6 the refactoring phase. The work goes back to designer (2) while the builder
  at 3 or at 5 answers `open`, and while the evaluator at 4 answers `more`. It goes back to the
  builder at 5 while the evaluator at 6 answers `more`.
- Planner alone decides the kind, and takes a kind a caller gave without asking. It gives the
  kind's template: one kept in `.turn/templates/`, else one turn ships, else a new one drawn from
  how good works of the kind are made. It judges a new template on a published work of the kind
  found in its research, before the person sees it. It writes a new template in the run's folder,
  and keeps it in `.turn/templates/` once the person approves it, so no run takes a template the
  person has not approved. lane holds it to write only those two folders (write_only), and to pass
  `check.py`'s template check after changing a template (test_after).
- Designer alone decides each point of the design, such as where the work goes and the language it
  is written in, from the purpose and the best practice or by asking the person. It takes each
  point a caller gave as decided. It alone finds where the cause of each more of the kind's own
  questions lies. It alone decides a point the builder returns, in either phase, as a point of
  what the work says: for a point of the refactoring phase, it finds the kind's own questions the
  point bears on, and the decisions that serve them. It alone brings to the person a more the
  decisions cannot make good. It tells a more that
  came back after its decision was made again from the design tree, where each decision made
  again names the more it answered. lane holds it to read `back` to its end (read_whole), to write
  only the design tree (write_only), in its form (in_form), and to pass `check.py`'s tree check
  after changing the tree (test_after).
- Builder alone decides the small points of making, such as a phrase or a function's name, and in
  the refactoring phase how the work says each thing. It returns a point the design leaves open
  that bears on the work's quality, and in the refactoring phase a point that would change what
  the work says, or a more that came back after it mended it: it writes the question the point
  bears on as a more of its self-check, and ends with `open`. In the refactoring phase it mends
  each more of `verification`. lane holds it to read `tree` to its end (read_whole), to write only
  the work and its self-check (write_only), to run no `git commit` or `git push` (hands_off), to
  write the self-check in its form (in_form), to answer every question of `templates`
  (every_item), and to pass `check.py`'s answers check (test_after).
- Evaluator alone decides each answer, good or more, from its own first reading of the work. lane
  holds it to read only the work and `templates` (read_only), to read the work to its end
  (read_whole), to write only its verification (write_only), in its form (in_form), to answer every
  question of `templates` (every_item), to pass `check.py`'s answers check (test_after), and to end
  only once the verification is made (end_when).
- `check.py` alone checks what no lane holds. A template is in its form, and a question looks at
  every part of its format. In a design tree, a decision serves every question, every decision
  reaches the goal, and the decisions stand in the order they were made, each building only on
  decisions before it. In a self-check or a verification, no question stands both good and more,
  and every line an answer names, by its file and line numbers, is in the work.
- The items adapter alone gives every_item the question IDs of a template, each named with its
  template, such as `readme/Q3`. every_item counts a question answered where its ID stands as a
  word of its own, as [lane's lanes](../../plugins/lane/docs/lanes.md) say. A question
  named with its template is then answered only by its own ID, as `readme/Q3` does not stand in
  `refactor-doc/Q3`.
- An ask is a question or an approval that a role puts to the person. The role sends it with
  SendMessage to `main`, the main conversation, whatever started `turn:up`. Claude Code removes
  AskUserQuestion from every subagent, and a subagent in the background keeps SendMessage
  ([subagents](https://code.claude.com/docs/en/sub-agents#available-tools)). `main` is an address
  any subagent can send to, at any depth below the main conversation, and the message waits until
  the main conversation's current turn ends (Claude Code 2.1.316, trial). Each ask says what it
  waits on and the answer turn recommends.
- The main conversation gets the ask as a turn of its own, headed by the agent ID of the role that
  sent it (Claude Code 2.1.316, trial). A main conversation that knows nothing of turn then puts it
  to the person, and sends their words with SendMessage to that agent ID. Neither `turn:up` nor
  any other role sees the ask or the answer.
- `wait.py` alone holds a role that has asked until the answer comes. The role runs it in the
  foreground, and it returns after a short while, as the answer reaches a running subagent only
  once its current tool call has returned, never during one (Claude Code 2.1.316, trial). The role
  runs it again until the answer has come. It does not end while it waits: lane counts the move at
  a role's end ([lane's flow](../../plugins/lane/docs/flow.md)), so an end would move the flow on
  without the answer.
- Each role runs on the model of the session that starts turn, as no agent of turn names a
  `model`; the person picks it.
- Every file the roles pass between them, other than the work, is JSON, so `check.py` checks one
  against another, such as a template's questions against its parts.

The choices below depart from [how a plugin works](../architecture.md), or would be questioned:

- `turn:up` is a subagent, even when a person calls turn, though
  [Where the orchestrator runs](../architecture.md#where-the-orchestrator-runs) starts such a
  plugin by a skill. lane lays a flow only on a subagent, and one entry then serves the person and a
  plugin's step alike.
- The main conversation starts `turn:up` in the background. It then stays free to put each ask to
  the person while the roles work.
- The main conversation passes each ask to the person and their words back, though principle 4 of
  [how a plugin works](../architecture.md#principles) has nobody relay. Only the main conversation
  can ask the person, as [Where the orchestrator runs](../architecture.md#where-the-orchestrator-runs)
  says. Between the roles nobody relays: each role sends its own ask, and `turn:up` passes no
  answer on.
- The person approves a template and a design by their answer in the main conversation, not by the
  skill of their own that
  [The caller approves what is theirs](../architecture.md#the-caller-approves-what-is-theirs) asks
  for. Neither is hard to undo: a change sends planner or designer back to the decision it touches.
- Principle 9 of [how a plugin works](../architecture.md#principles), lessons drawn once the work
  is approved, is not yet decided for turn.
- `check.py`, not an in_form lane, holds a template to its form. An in_form lane holds a file at a
  path fixed in the step, while a kept template's path names its kind, which planner decides only
  in the run.
- The builder returns an open point as a more of the self-check, not in a file of another form.
  Designer then reads one form, whichever position sent the work back.
- The builder and the evaluator each serve both phases, not a role started for each phase. A role
  splits by what it alone decides, and the builder decides how the work is made in both phases, as
  the evaluator decides what its user gets in both.
- The evaluator's more in the refactoring phase goes back to the builder, not to designer. A more
  of how the work says a thing changes no decision, and designer would only pass it on.

### Data model

![turn's data model](data-model.svg)

### Sequences

Asking `turn:up` for a work and confirming its kind:

```mermaid
sequenceDiagram
  actor P as Person
  participant M as Main conversation
  participant U as turn:up
  participant G as Guard
  participant PL as Planner
  participant WT as wait.py
  P->>M: asks turn:up for a work (request)
  M->>U: starts it in the background (request)
  G-->>U: tells move 1: start planner
  U->>PL: starts (request)
  PL->>M: asks the person to confirm the kind (request)
  Note over M: gets it once its current turn ends
  M->>P: the ask
  loop until the answer has come
    PL->>WT: waits for the answer
    WT-->>PL: returns after a short while
  end
  P->>M: answer
  M-->>PL: answer, sent to its agent ID
  Note over PL: reads it once its current tool call has returned
```

Approving the template of a new kind:

```mermaid
sequenceDiagram
  actor P as Person
  participant M as Main conversation
  participant PL as Planner
  participant W as Internet
  participant R as Run files
  participant C as check.py
  participant WT as wait.py
  participant T as Templates
  participant U as turn:up
  alt .turn/templates/ keeps or turn ships a template of the kind
    T-->>PL: the template (template)
  else no template of the kind
    PL->>W: reads how good works of the kind are made
    W-->>PL: guides and examples
    PL->>R: writes the format and the checklist (template)
    PL->>C: checks it (template)
    PL->>M: asks the person to approve (template)
    M->>P: the ask
    PL->>WT: waits for the answer
    P->>M: approval, or a change
    M-->>PL: approval, or a change, sent to its agent ID
    PL->>T: keeps it (template)
  end
  PL-->>U: ends, naming the template (template)
```

Answering what only the person decides, and approving the design:

```mermaid
sequenceDiagram
  actor P as Person
  participant M as Main conversation
  participant U as turn:up
  participant G as Guard
  participant D as Designer
  participant WT as wait.py
  participant R as Run files
  participant C as check.py
  G-->>U: tells move 2: start designer
  U->>D: starts (request, template)
  Note over D: puts the template's questions under this work's purpose
  D->>M: asks what the work is for (decision)
  M->>P: the ask
  D->>WT: waits for the answer
  P->>M: answer
  M-->>D: answer, sent to its agent ID
  Note over D: decides what the purpose and the best practice settle
  loop each point only the person decides, one at a time
    D->>M: asks, with the answer recommended (decision)
    M->>P: the ask
    D->>WT: waits for the answer
    P->>M: answer
    M-->>D: answer, sent to its agent ID
  end
  D->>R: writes (design tree)
  D->>C: checks it (design tree)
  D->>M: asks the person to approve (design tree)
  M->>P: the ask
  D->>WT: waits for the answer
  P->>M: approval, or a change
  M-->>D: approval, or a change, sent to its agent ID
  D-->>U: ends, naming where the work goes (work)
```

Making what the work says, until every question of the kind's own is good:

```mermaid
sequenceDiagram
  actor P as Person
  participant M as Main conversation
  participant U as turn:up
  participant G as Guard
  participant D as Designer
  participant B as Builder
  participant E as Evaluator
  participant R as Run files
  participant C as check.py
  participant IA as Items adapter
  participant WT as wait.py
  G-->>U: tells move 3: start builder
  Note over U: the content phase, as designer ended last
  U->>B: starts (template, design tree, work, answers)
  B->>R: reads (design tree)
  loop each decision, in the order they build on one another
    Note over B: makes it into the work
  end
  B->>R: writes its answers (answers)
  B->>C: checks them (answers)
  opt a point the design leaves open bears on quality
    B-->>U: ends with open
    G-->>U: tells move 2: start designer
    Note over U,D: designer decides it, then the builder makes the work again
  end
  B-->>U: ends
  G-->>U: tells move 4: start evaluator
  U->>E: starts (template, work, answers)
  Note over E: uses the work as its user would
  E->>R: writes its answers (answers)
  E->>C: checks them (answers)
  G->>IA: asks the question IDs, as the evaluator ends (template)
  IA-->>G: the question IDs
  loop while an answer is more
    E-->>U: ends with more
    G-->>U: tells move 2: start designer
    U->>D: starts (answers)
    D->>R: reads the answers and the design tree (answers, design tree)
    alt the decision behind the more was not yet made again
      D->>R: makes it again (design tree)
    else the more came back after its decision was made again
      D->>M: asks: decide it again another way, or change the purpose (decision)
      M->>P: the ask
      D->>WT: waits for the answer
      P->>M: answer
      M-->>D: answer, sent to its agent ID
      D->>R: makes the decision again, or the purpose and what builds on it (design tree)
    end
    D-->>U: ends, naming where the work goes (work)
    Note over U,E: lane tells moves 3 and 4 again
  end
  E-->>U: ends
```

Bettering how the work says it, once every question of the kind's own is good:

```mermaid
sequenceDiagram
  participant M as Main conversation
  participant U as turn:up
  participant G as Guard
  participant D as Designer
  participant B as Builder
  participant E as Evaluator
  participant R as Run files
  participant C as check.py
  G-->>U: tells move 5: start builder
  Note over U: the refactoring phase, as the evaluator of the content phase ended with every question good
  U->>B: starts (included templates, no design tree, work, answers)
  Note over B: betters how the work says each thing, by the included templates' questions
  B->>R: writes its answers (answers)
  B->>C: checks them (answers)
  opt a point would change what the work says, or a more came back after it was mended
    B-->>U: ends with open
    G-->>U: tells move 2: start designer
    U->>D: starts (answers)
    Note over U,D: designer decides it, or brings it to the person; lane then tells moves 3 and 4, the content phase, again
  end
  B-->>U: ends
  G-->>U: tells move 6: start evaluator
  U->>E: starts (included templates, work, answers)
  Note over E: uses the work as its user would
  E->>R: writes its answers (answers)
  E->>C: checks them (answers)
  loop while an answer is more
    E-->>U: ends with more
    G-->>U: tells move 5: start builder
    U->>B: starts (included templates, no design tree, work, answers)
    B->>R: reads the evaluator's answers and its own last ones, writes its own (answers)
    B-->>U: ends
    Note over U,E: lane tells move 6 again
  end
  E-->>U: ends
  G-->>U: tells that the flow is done
  U-->>M: the work (work)
```

Starting `turn:up` from a plugin's step:

```mermaid
sequenceDiagram
  participant S as A plugin's step
  participant U as turn:up
  participant M as Main conversation
  actor P as Person
  S->>U: starts it, with what it has settled (request)
  Note over U,P: the run goes as above, and each ask reaches the person through the main conversation
  U-->>S: the work (work)
```

- Every ask goes to the main conversation, even when a plugin's step started `turn:up`. Only the
  main conversation can ask the person, as
  [Where the orchestrator runs](../architecture.md#where-the-orchestrator-runs) says.
- A point the builder returns in the refactoring phase goes through the whole content phase again,
  builder and evaluator included. The builder there changes only the parts that rest on a decision
  made again, and keeps the rest of the work, its polish included. The evaluator then checks that
  what the work says still holds before the refactoring phase goes on.


## Physical view

### Deployment

![turn's deployment](deployment.svg)

- The person installs turn as the README's Installation says. They start it by asking the main
  conversation to have `turn:up` make a work, as the README's Walkthrough shows. A plugin's step
  starts the `turn:up` agent itself, as [Calling turn](../../plugins/turn/docs/calling.md) tells
  the step's maker.
- A person who asks `turn:up` again for a work whose run stopped goes on with that run. `turn:up`
  finds the run's folder by the `<name>` it gives the work asked for, and each role takes up what
  the run files already hold. lane counts the moves of each start of `turn:up` anew, so it tells
  the new `turn:up` to start again from move 1. Planner and designer then end soon, as their files
  already hold their work.
- A run's files lie in `.turn/<yyyymmdd>-<name>/` in the folder Claude Code runs in, and the
  templates planner makes lie in `.turn/templates/` there. This departs from
  [Where a plugin writes its files](../architecture.md#where-a-plugin-writes-its-files), which
  places what may be kept at the root of the repository: turn needs no git repository, and the
  folder Claude Code runs in is the one its agents may read and write without asking. The
  templates' folder carries no date, as each template serves every later run.
- Planner keeps the templates it makes in the folder Claude Code runs in, not in turn's installed
  folder, which an update replaces, nor in the person's home folder, which agents cannot read
  without asking. A kept template is taken before a shipped one of the same kind, as the person
  approved it.
- lane's guard lies in turn's own folder, where `lay.py write` lays it. The person then needs no
  lane installed.

### Directory structure

```text
plugins/turn/                       turn, installed by Claude Code
├── .claude-plugin/plugin.json      the manifest <JSON>
├── agents/up.md                    turn:up's entry <subagent · Markdown>
├── agents/<role>.md                Planner's, Designer's, Builder's and Evaluator's entries <subagent · Markdown>
├── prompts/<name>.md               the steps of turn:up and of each role <Markdown>
├── scripts/check.py, <check>.py    check.py and each check it runs <script · Python 3.9 stdlib>
├── scripts/wait.py                 wait.py <script · Python 3.9 stdlib>
├── forms/<file>.json               Forms of the template, the design tree and the answers <JSON Schema>
├── templates/<kind>.json           Templates that turn ships <JSON>
├── hooks/hooks.json, lanes.json    the hooks, the flow and the lanes, laid by lane <JSON>
├── hooks/lane/                     Guard, laid by lane <Python 3.9>
├── hooks/adapters/items-template.*   Items adapter and its cases, laid by lane <script · Python 3.9 stdlib>
├── docs/calling.md                 for the maker of a plugin's step <Markdown>
├── README.md, CHANGELOG.md         for the person <Markdown>
└── how-it-works.svg, idea.svg      the README's figures <SVG>

dev/turn/                           what only turn's builders need
├── README.md                       how to run turn's tests and trials
├── ux.md, architecture.md, *.svg   turn's UX and this document
├── cosmic-ray.toml                 the mutation testing of turn's scripts <TOML>
├── tests/                          unit and property tests of turn's scripts <Python 3>
└── trials/                         trials of each role, of the roles together, and of the whole <Python 3>

<the folder Claude Code runs in>/.turn/
├── templates/<kind>.json           Templates that planner made in this folder <JSON>
└── <yyyymmdd>-<name>/              one run's Run files: a new template before approval, design-tree.json, self-check.json and verification.json for the content phase, and refactor-self-check.json and refactor-verification.json for the refactoring phase <JSON>
```

## Test

turn is tested by the project's shared test rules in [Test](../architecture.md#test). What follows
says only what turn adds to them. A trial is a run of a role, or of the whole of turn, made by the
assistant and judged from its records. A weight, from ●○○ to ●●●, says how heavily a unit is tested.

| Deployment unit | Unit | Integration | End-to-end |
|---|---|---|---|
| turn's agents [Claude Code subagents · Markdown] | a trial of one role, the rest mocked · ●●● · it keeps to its steps, in each phase it serves | a trial of the four roles under lane's flow, the person mocked · ●●○ · the hand-offs through the run files, and each way back in both phases, to every question good | ▨[^1] |
| turn's scripts [process · Python 3.9 stdlib] | unittest, Cosmic Ray, Hypothesis · ●●● · each check of `check.py`, `wait.py`, and the items adapter | unittest with lane's real guard laid from turn's proposal, in a real repository · ●○○ · the lanes run the checks and the adapter, and the flow tells each move | ▨[^1] |
| turn's installed folder [plugin folder] | `check.py` · ●●○ · each shipped template is in its form, and a question looks at every part | ▨[^2] | ▨[^1] |
| turn on the person's computer [Claude Code] | ▨[^3] | ▨[^3] | a trial of each user story, the assistant as the person · ●●○ · the work, and what the person was asked |

[^1]: End-to-end tests run on the whole alone, in the last row.
[^2]: A template has no neighbour to join it to, as nothing runs it; the evaluator judges a real
    work of its kind with it when the template itself is the work.
[^3]: The units it is made of are tested in their own rows.

- lane's guard is lane's code, tested in lane, so it has no row here.
- Unit tests: a trial of one role makes the role real and runs it on Opus, with its lanes laid; it
  mocks every other role and the person, and gives the role the run files it would find. Pass: in
  each of three runs, the role keeps to its steps and its file passes `check.py`. The unit tests of
  `check.py`, `wait.py` and the adapter make them real and fake nothing but the files they read.
  Pass: as the shared rules set for code.
- Integration tests: a trial of the four roles makes them, `turn:up` and lane's guard real, on Opus,
  and mocks the person with set answers. Pass: in each of three runs, the run ends with every
  question good, of the kind's own template and of those it includes, and each more of the kind's
  own was mended at its decision, made again or kept, never by an addition to the work alone.
  The test of the guard with turn's lanes makes lane's guard and a repository real. Pass: all pass.
- End-to-end tests: a trial of each user story makes the whole of turn real in Claude Code, on Opus,
  with the assistant standing in for the person. Pass: in each of three runs, the person is asked
  only what the README's Walkthrough asks of them, and gets a work the evaluator finds good on every
  question; the maintainer then judges it as the shared rules say.
- turn's agents weigh ●●●: a role that strays gives the person a work that misses its purpose, or
  asks them what they need not decide.
- turn's scripts weigh ●●●: a check that passes a missing answer, or a decision that serves
  nothing, hands the person a work before every question is good.
- turn's installed folder weighs ●●○: a part no question looks at goes into every work of the kind
  unchecked, while the evaluator still reads the parts the questions do look at.
- turn on the person's computer weighs ●●○: a story's trial takes many minutes and many tokens, and
  the rows above catch most faults first.
- A trial passes on three runs of three, not on one: what an AI does varies from run to run, and a
  role that keeps its steps once may stray in the next.
