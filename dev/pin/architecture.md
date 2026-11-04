# pin architecture

pin gives its users a design tree, a JSON file that holds a plan's goal, the questions that must
hold for the goal, and the decisions that make each question hold. The pinner, the AI that follows
the skill `pin:down`, builds the tree from the goal down and settles each decision: a subagent
finds each fact, and the person confirms each fact and decides what is theirs, one point at a
time. The pinner is the main conversation when the person runs `/pin:down`, or a role of Turn or rn
that takes the skill. One script, `check.py`, checks after each answer that the tree holds
together. What this gives the person, Turn and rn is in [pin's UX](ux.md).

## Principles

pin follows all the principles of [the plugin best practice](../plugin-best-practice.md#principles).
Under [Read by those who did not make it](../plugin-best-practice.md#read-by-those-who-did-not-make-it),
the person reads the design first, as they read it in full to confirm it. The
principles below are what pin adds.

### Facts are found, decisions are asked

The pinner finds each fact itself, never by asking the person. A fact that a search must find
goes to a subagent. A fact in a file the pinner has already read, it quotes directly, after it
sees that the quoted words stand at the line it names. It shows the person each fact as it is
found, alone, to confirm. It asks the person only a decision that is theirs. It
settles itself a decision that follows from the goal and the decisions before it, and shows it in
the design with what settled it.

A question about a fact spends the person's time on what the AI could look up, and a decision taken
for the person is a guess they never saw (KR1.1, KR1.2). A subagent started for what the pinner
already holds adds a start and a wait, with nothing found that it did not have (KR1.2); a quote
not seen at its line may be wrong, as when one listing numbered the lines of several files as one
(trial of 2026-11-03). The split of facts and decisions is that of
Matt Pocock's
[grilling](https://github.com/mattpocock/skills/blob/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/productivity/grilling/SKILL.md):
"Finding _facts_ is your job, never the user's", and "The _decisions_ are the user's: put each to
them and wait." grilling does not show the facts it finds; pin shows each one, as
[Asking until nothing is left to decide](../plugin-best-practice.md#asking-until-nothing-is-left-to-decide)
says, since a fact found but not shown is still a guess made for the person.

### One point at a time

The pinner puts one point to the person in each message, a fact to confirm or a decision with a
recommendation worded so that "yes" takes it, and waits for the answer before the next.

grilling asks a whole round of questions at once, but its own documentation says that "it can put
two questions in one round and only later find that one answer should have changed the other". One
at a time, each answer is weighed before the next point is chosen. The same page offers this
way as "a supported setting, not a workaround". Each point costs a message of its own, so the lead
time is kept down by the next principle and by asking only what is the person's (KR1.2).

### Research runs beside the questions

The pinner starts each subagent that finds a fact in the background, and meanwhile asks the
decisions that do not build on that fact. Only the decisions that build on it wait for it.

A decision that waits for research it does not need adds the research's time to the lead time, with
nothing gained (KR1.2, KR2.2).

### The tree is the only record

Every fact, decision and answer is written into `design-tree.json` before the next point. The pinner
asks a decision only once each decision it builds on is decided, and it reads which decisions those
are from the tree, not from the conversation.

A conversation can end, be cleared or be compacted, so a plan kept only in it is lost
([Where the router keeps the course](../plugin-best-practice.md#where-the-router-keeps-the-course)).
A tree in a file is read the same way by `check.py`, by a new conversation and by the AI that makes
the work.

### Every decision reaches the goal

Each decision is joined by `contributes_to` to the questions or decisions it serves, and through
them to the goal. A decision that reaches no question is cut, and a question that no decision
serves is a gap. `check.py` finds both, and also a decision decided before one it builds on.

A decision that serves nothing costs the person a question for nothing, and a gap is a point the
work will guess (KR1.1, KR2.1).

### pin knows no caller

No line of pin names a plugin that uses it. A caller gives `pin:down` the goal, the questions the
work must answer and the path of the tree, and the decisions it has already settled; pin fills the
rest. A caller may add keys of its own to the tree, and `check.py` leaves them.

Turn and rn each take pin in as it is, and a change for one of them would reach the other unseen.

### The check command keeps one form

`pin:down` names the check as `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/<name>.py <args>`, today
`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/check.py <design tree>`. This form stays the same across
pin's versions; only the folder that Claude Code puts in place of `${CLAUDE_PLUGIN_ROOT}` differs.
Claude Code puts pin's folder there wherever the text of `pin:down` is loaded, in a caller's role
too (tried on Claude Code 2.1.317, 2026-11-03). The Bash tool's environment holds no
`CLAUDE_PLUGIN_ROOT`
([plugins reference](https://code.claude.com/docs/en/plugins-reference#where-each-variable-resolves)),
so the command carries the folder written out.

A caller's role runs the command as `pin:down` writes it, and a check that a caller lays on its
role's commands matches each command as it is written. A command whose form changed would be
stopped, or would go unchecked, in every caller at once.

## User stories

- As the person, I want to run `/pin:down` with my plan in rough words, confirm each fact found
  and decide only what is mine, one point at a time, and confirm the design at the end. Carries O1 from the request to the
  confirmed design tree.
- As Turn or rn, I want to give my role `pin:down` with a work's goal, its questions, what I have
  settled and the path of the tree, and get back the confirmed design tree. Carries O2 from the
  call to the design tree.
- As Turn or rn, I want my role to run the check command as `pin:down` writes it, and learn whether the tree holds together, or what is wrong.
  Carries each check step of O2; in O1 the pinner runs it within the first story.
- As Turn or rn, I want to reopen one decision with `pin:down`, and have it and each decision that
  builds on it decided again. Off the main path, serves KR2.1.
- As the person, I want to go on with a stopped run in a new conversation, from the tree it kept.
  Off the main path, serves KR1.2.

## Logical view

### Components

```mermaid
flowchart LR
  P(["person<br>#lt;person#gt;"])
  MC["main conversation<br>#lt;AI · Claude Code#gt;"]
  PN["pinner<br>#lt;AI · Claude Code, following pin:down#gt;"]
  RS["researcher<br>#lt;AI · Claude Code subagent#gt;"]
  CK["check.py<br>#lt;command line · Python 3.9#gt;"]
  TR[("design-tree.json<br>#lt;JSON file#gt;")]
  SRC[["the project's files and public pages"]]
  P -- "1 the plan, then each answer and the confirmation" --> MC
  MC -- "2 the plan, or a Caller's settled points (Goal, Question, Decision)" --> PN
  PN -- "3 a fact to find" --> RS
  RS -- "4 reads" --> SRC
  RS -- "5 the fact, with its Ground" --> PN
  PN -- "6 writes Decision" --> TR
  PN -- "7 runs scripts/check.py on the tree's path" --> CK
  CK -- "8 reads Design tree" --> TR
  CK -- "9 Check result" --> PN
  PN -- "10 one fact to confirm, or one Decision to make with a recommendation, and at the end the design" --> MC
  MC -- "11 puts it" --> P
```

Legend: a rounded box is a person; a box is an AI or a script, with its kind and what it is made
with in angle brackets; a cylinder is a file; a box with double sides lies outside pin. Each
arrow says what one does to another, with the data it hands on named as in the data model, and its
number gives the order.

- Where the pinner is the main conversation, arrows 2, 10 and 11 are the main conversation's own.
- The pinner alone decides which decision to settle next, who settles it, and what to recommend.
  It alone writes the tree.
- The researcher finds one fact that a search must find, and nothing else, as
  [Facts are found, decisions are asked](#facts-are-found-decisions-are-asked) says. It is a
  subagent that Claude Code ships, such as Explore, so pin holds no agent of its own.
- `check.py` alone decides whether the tree holds together. It reads the tree and writes nothing.
- pin has no roles of its own, so a caller starts no orchestrator of pin's, as
  [A plugin that uses another](../plugin-best-practice.md#a-plugin-that-uses-another) would have it: the
  caller's role takes `pin:down` and runs its steps itself.
- A pinner that is a caller's role asks the person through the main conversation, as
  [Where the orchestrator runs](../plugin-best-practice.md#where-the-orchestrator-runs) says. The caller
  resumes it with the person's answer under the line `The person's answer, word for word:`, the
  one form the pinner takes as the person's words: Claude Code hands a resuming message on as the
  coordinator's, and a pinner left to guess who speaks asked again what the person had answered,
  in pin's trial of a caller and in Turn's, until the caller gave it in that form.
- `pin:down` is a skill that the AI may call: a caller's role takes it by the `skills` field of its
  frontmatter or by the Skill tool, and Claude Code preloads only a skill the AI may call
  ([subagents](https://code.claude.com/docs/en/sub-agents#preload-skills-into-subagents)).

### Data model

```mermaid
erDiagram
  DESIGN_TREE ||--|| GOAL : "has at its root"
  DESIGN_TREE ||--|{ QUESTION : holds
  DESIGN_TREE ||--o{ DECISION : holds
  GOAL ||--|{ QUESTION : "is served by"
  QUESTION }|--|{ DECISION : "is served by (contributes_to)"
  DECISION }o--o{ DECISION : "serves (contributes_to)"
  DECISION }o--o{ DECISION : "builds on (builds_on)"
  GOAL ||--o{ GROUND : "rests on"
  DECISION ||--o{ GROUND : "rests on"
  CHECK_RESULT }o--|| DESIGN_TREE : "is of"
```

- A Caller's settled points are a Goal, Questions and Decisions already decided, in the tree's own
  form, so a caller hands them over by writing the first tree.
- A Decision is settled by the person, by research or by reasoning, and each settled one rests on at
  least one Ground: the person's words, a source quoted, or the goal and decisions it follows from.
  A fact found is a source quoted, and the person's confirmation of it is their words.

### Sequences

The person runs `/pin:down`, O1 of the UX, and goes on with a stopped run the same way:

```mermaid
sequenceDiagram
  participant P as person
  participant M as main conversation (pinner)
  participant R as researcher
  participant C as check.py
  participant T as design-tree.json
  P->>M: /pin:down with the plan
  alt a tree for the plan already lies in .pin/, left by a stopped run
    M->>T: reads the Design tree
    Note over M,T: Goes on from the loop below, asking nothing answered before.
  else no tree lies there
    M->>T: writes the Goal to confirm, the Questions under it, every Decision open
    loop until the Check result says the tree holds
      M->>C: runs on the path
      C->>T: reads the Design tree
      C-->>M: Check result
      opt it names a question no decision serves, or a decision that serves none
        M->>T: mends the Design tree
      end
    end
    M->>R: in the background, a fact to find
    M->>P: the Goal, with a recommendation
    P->>M: the answer
    M->>T: writes the Goal confirmed, the person's words as its Ground
  end
  loop until no Decision is left open, or the person asks to wrap up
    alt the researcher has given a fact
      R-->>M: the fact, with its Ground
      M->>P: the fact, alone, to confirm
      alt the person confirms it
        P->>M: right
        M->>T: writes the fact and the confirmation into the Grounds of the Decision it settles
      else the person corrects it
        P->>M: the correction
        M->>T: writes the correction into the Grounds of that Decision
      end
    else a Decision open now is the pinner's to settle
      M->>T: writes the Decision, by research where a fact confirmed settles it, by the person where their correction changed it, else by reasoning, with what favors it
    else a Decision open now rests on a fact only the person knows
      M->>P: that fact, alone, to tell
      P->>M: the answer
      M->>T: writes it into the Decision's Grounds
    else a Decision open now is the person's
      M->>P: one Decision to make, with a recommendation
      alt the person decides it
        P->>M: the answer
        M->>T: writes the Decision, by the person
      else the person leaves it to the pinner
        P->>M: you decide
        M->>T: writes the Decision, by reasoning, saying so
      end
    end
    opt the answer raises a point not in the tree
      M->>T: adds an open Decision, joined to what it serves and builds on
    end
    M->>C: runs on the path
    C->>T: reads the Design tree
    C-->>M: Check result
  end
  M->>P: the design, each Decision in a short line, with what settled it, and each left open
  alt the person changes something
    P->>M: the change
    M->>T: opens that Decision again, with each that builds on it
    Note over P,T: Back to the loop above.
  else the person confirms it
    P->>M: confirms it
    M->>C: runs on the path
    C-->>M: Check result
    M-->>P: the path of the Design tree, and what the check printed
  end
```

Turn's designer has a work's design pinned down, O2 of the UX. Each step that the first sequence
draws between the pinner and the person goes here through the main conversation:

```mermaid
sequenceDiagram
  participant D as designer (pinner)
  participant R as researcher
  participant C as check.py
  participant T as design-tree.json
  participant M as main conversation
  participant P as person
  D->>T: writes Turn's settled points: the Goal, the Questions, the Decisions it has
  loop until the Check result says the tree holds
    D->>C: runs on the path
    C-->>D: Check result
    opt it names a problem
      D->>T: mends the Design tree, Turn's points kept as given
    end
  end
  D->>R: in the background, a fact to find
  loop until no Decision is left open, or the person asks to wrap up
    alt a point is the person's: a fact to confirm, a fact only they know, or a Decision
      D->>M: ends with the point, headed `For the person:`
      M->>P: puts it
      alt the person answers it
        P->>M: the answer
        M->>D: resumes it, under `The person's answer, word for word:`
        D->>T: writes it, the person's words as its Ground
      else the person asks to wrap up
        P->>M: wrap up
        M->>D: resumes it, under `The person's answer, word for word:`
        D->>T: leaves each open Decision open, and asks no more
      end
    else a Decision open now is the pinner's to settle
      D->>T: writes the Decision, by reasoning
    end
    D->>C: runs on the path
    C->>T: reads the Design tree
    C-->>D: Check result
  end
  D->>M: ends with the design, headed `For the person:`
  M->>P: puts it
  alt the person changes something
    P->>M: the change
    M->>D: resumes it with the change
    D->>T: opens that Decision again, with each that builds on it
    Note over D,P: Back to the loop above.
  else the person confirms it
    P->>M: confirms it
    M->>D: resumes it with the confirmation
    D->>C: runs on the path
    C-->>D: Check result
    D-->>D: ends with the path of the Design tree
  end
```

Turn or rn reopens a decision:

```mermaid
sequenceDiagram
  participant D as caller's role (pinner)
  participant C as check.py
  participant T as design-tree.json
  D->>T: reads the Design tree, every Decision settled
  alt the point is held by a Decision
    D->>T: opens it again, with each Decision that builds on it, the person's words kept in its Grounds
  else no Decision holds the point
    D->>T: adds an open Decision, joined to what it serves and builds on
  end
  D->>C: runs on the path
  C-->>D: Check result, the open Decisions named
  Note over D,T: Then as the loop of O2, from the first open Decision.
```

## Physical view

### Deployment

```mermaid
flowchart TB
  subgraph PC["the person's computer"]
    subgraph CCP["Claude Code process #lt;Claude Code 2.1.317 or later#gt;"]
      MC2["main conversation, or the caller's role: the pinner"]
      RS2["researcher"]
    end
    CKP["check.py process #lt;python3 3.9 or later#gt;"]
    REPO[("the repository: .pin/#lt;yyyymmdd#gt;-#lt;name#gt;/design-tree.json,<br>or the path the caller names")]
  end
  API[["Anthropic's API, which Claude Code uses"]]
  CCP -- "runs python3 on scripts/check.py, through the Bash tool" --> CKP
  CCP -- "reads and writes" --> REPO
  CKP -- "reads" --> REPO
  CCP -- "the model's turns" --> API
```

- The person installs pin as [the README](../../plugins/pin/README.md#installation) says. A plugin
  that uses pin lists it in its `dependencies`, and installing that plugin installs pin.
- The person starts pin with `/pin:down`. A caller's role starts it by taking the skill.
- `check.py` uses Python 3.9 and its standard library only, as
  [Python 3.9 and the standard library](../plugin-best-practice.md#python-39-and-the-standard-library)
  says.
- A person's tree is kept in `.pin/<yyyymmdd>-<name>/` at the root of the repository, as
  [Where a plugin writes its files](../plugin-best-practice.md#where-a-plugin-writes-its-files) says. A
  caller's tree is kept where the caller names.

### Directory structure

```text
plugins/pin/
├── .claude-plugin/plugin.json      pin's manifest and version <JSON>
├── skills/down/SKILL.md            pin:down's entry, which links the pinner's part <Markdown>
├── scripts/check.py                check.py's entry <command line · Python 3.9>
├── core/domain/tree.py             check.py: the Design tree and its Check result <module · Python 3.9>
├── core/roles/pinner.md            the pinner's flow <Markdown>
├── LICENSE-grilling                Matt Pocock's copyright and permission notice for grilling <text>
└── README.md, CHANGELOG.md         for users <Markdown>

dev/pin/
├── ux.md, architecture.md, README.md   for developers <Markdown>
├── cosmic-ray.toml                 the mutation testing <TOML>
└── tests/
    ├── unit/core/domain/           unit and property tests of tree.py <Python 3>
    ├── unit/core/roles/            the pinner's trials, trial_*.py <Python 3>
    ├── architecture/               scripts/check.py on each tree of the sequences, and pin:down's entry <Python 3>
    └── ux/                         the trials of O1 and O2, trial_*.py, and the plugin standing in for a caller <Python 3>

.pin/<yyyymmdd>-<name>/design-tree.json   a person's Design tree
```

`LICENSE-grilling` lies in pin's folder, as installing copies only that folder, and the MIT
License asks that its notice go with each copy of a substantial portion.

## Test

pin is tested as [Test](../plugin-best-practice.md#test) says. What follows is what pin adds.

| Deployment unit | unit | architecture | ux |
|---|---|---|---|
| check.py process [python3 3.9 or later] | unittest, Cosmic Ray, Hypothesis · ●●● · each of the three checks, the tree's form, and the exit and its message | unittest, check.py and the tree on disk real, the pinner as a double · ●●● · each path of O1, O2 and a reopen, check.py run by the command as `pin:down` writes it on each tree the double writes | trials on Opus · ●○○ · run by the pinner on each answer |
| Claude Code process: the pinner [Claude Code 2.1.317 or later] | trials on Opus · ●●● · `pin:down` alone, one input for each class of point and each step of its flow, with the person and the researcher stood in for | unittest · ●●○ · `pin:down`'s entry as Claude Code takes it: the AI may call it, it links the pinner's part, and it names the check in its one form | trials on Opus · ●○○ · O1 by `/pin:down`, and O2 by a caller's role that takes `pin:down` |

The researcher has no row of its own: Claude Code ships it, and pin gives it only a prompt, tried
with the pinner's.

pin lays no lanes. Its only role, the pinner, runs in the main conversation, where a hook is not
told which skill runs, or inside a caller's role, which the caller's own lanes hold
([The guard tells each role its steps again](../plugin-best-practice.md#the-guard-tells-each-role-its-steps-again)).
So pin's steps are held by the check and by these tests.

- **unit, the pinner**: a trial runs `pin:down` alone, as
  [Unit: prompts](../plugin-best-practice.md#unit-prompts) says. Its classes are the kinds of point in
  [Facts are found, decisions are asked](#facts-are-found-decisions-are-asked): a fact a search
  finds, a fact in a file already read, a fact only the person knows, a decision the pinner
  settles, and a decision that is the person's. Each is tried where the pinner must ask and where it
  must not. Its flow adds a tree a caller settled part of, a tree left by a stopped run, a decision
  reopened, and a design the person changes. A script stands in for the person, answering "Yes."
  to every message, or an AI answers from an intent where a case needs the person's own answer,
  such as a correction. A project subagent named Explore, which Claude Code takes in place of its
  own, stands in for the researcher with set facts. A plugin made for the test stands in for a
  caller whose role takes `pin:down`. An AI given the person's intent judges each message. A trial
  passes where each message to the person holds one point, a fact found is shown to the person
  before the design, no decision asked is one the pinner could settle or one the caller settled,
  and the tree passes `check.py` with no decision open, or with only those the person left open.
- **architecture**: what joins pin's parts runs real: `check.py`, run by the command that
  `pin:down` names, on the tree on disk. The pinner is a role an AI runs, so a double stands in for
  it, and runs one path of [Sequences](#sequences) each. At each step of the path, the double writes the tree the step
  calls for, and runs `check.py` by the command that `pin:down` names, with pin's folder put in,
  from the folder the pinner works in. The test checks that `check.py` reads that tree and gives
  the `Check result` the step calls for: that the tree holds, or the problem it names, such as a
  question no decision serves or the decisions open to decide now. The paths:

  | Sequence | Paths |
  |---|---|
  | O1 | the main flow: a new tree, the goal confirmed, a fact confirmed, a decision the pinner settles, a decision the person makes, the design confirmed; a tree mended after the check names a problem; a fact corrected; a fact only the person knows; a decision left to the pinner; a point an answer raises; a wrap-up with decisions left open; the design changed, and its decisions settled again; a tree left by a stopped run, gone on from |
  | O2 | the main flow, from the caller's settled points, with keys of the caller's own; a tree mended, the caller's points kept; a wrap-up the person asks for through the main conversation, with decisions left open; the design changed, and its decisions settled again |
  | a reopen | a decision reopened with each that builds on it; a point no decision holds, added |

  Each tree the double writes holds the form that `check.py`'s unit tests hold the tree to, so a
  change to that form fails the double too. A tree that breaks the form is a class of `check.py`'s
  unit tests, as no path of the pinner writes one. A second test reads `skills/down/SKILL.md` as Claude
  Code takes it, as [The check command keeps one form](#the-check-command-keeps-one-form) promises.
- **ux**: a trial runs Claude Code on Opus on a copy of pin and of a plugin standing in for a
  caller, as [ux: the plugin in real use](../plugin-best-practice.md#ux-the-plugin-in-real-use) says, on the
  notes app's `--json` option, a plan of several decisions that build on one another. There is one
  for O1 by `/pin:down`, and one for O2 by a caller's role. An AI stands in for the person with an
  intent never shown pin, and a run passes where the confirmed tree holds what that intent wants,
  the person's own decisions settled by them, with no decision open, which is what O1 and O2 say.
  For KR1.1 and KR2.1 the trial measures the share of the intent's decisions that the tree does not
  hold as the person holds them, and the share of messages that ask a fact or a settled point. For
  KR1.2 and KR2.2 it measures the time from the request to the confirmed tree. Lower and shorter
  are better.
- `check.py` weighs ●●● in unit and architecture tests, as a tree it passes wrongly sends a gap into
  the work unseen. The pinner weighs ●●● in its unit trials, as a question that is not the
  person's, or a decision taken for them, is what pin is there to stop, and those trials try each
  of its cases.
- The test of `pin:down`'s entry weighs ●●○: the trials run the entry too, and the test only finds
  sooner an entry that Claude Code would not load as pin needs.
- The ux trials weigh ●○○. They only confirm, in real use, what the lower levels have checked.
