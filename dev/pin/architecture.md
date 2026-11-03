# pin architecture

pin gives its users a design tree, a JSON file that holds a plan's goal, the questions that must
hold for the goal, and the decisions that make each question hold. The pinner, the AI that follows
the skill `pin:down`, builds the tree from the goal down and settles each decision: a subagent
finds each fact, and the person decides what is theirs, one question at a time. The pinner is the
main conversation when the person runs `/pin:down`, or a role of Turn or rn that takes the skill.
One script, `pin-check`,
checks after each answer that the tree holds together. What this gives the person, Turn and rn is in
[pin's UX](ux.md).

## Principles

pin follows all nine principles of [how a plugin works](../architecture.md#principles). Under
Principle 5, the person reads the design first, as they read it in full to confirm it. The
principles below are what pin adds.

### Facts are found, decisions are asked

The pinner finds each fact through a subagent, and asks the person only a
decision that is theirs. It settles itself a decision that follows from the goal and the decisions
before it, and shows it in the design with what settled it.

A question about a fact spends the person's time on what the AI could look up, and a decision taken
for the person is a guess they never saw (KR1.1, KR1.2). The split is that of Matt Pocock's
[grilling](https://github.com/mattpocock/skills/blob/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/productivity/grilling/SKILL.md):
"Finding _facts_ is your job, never the user's", and "The _decisions_ are the user's: put each to
them and wait."

### One question at a time

The pinner puts one decision to the person in each message, with a recommendation worded so that
"yes" takes it, and waits for the answer before the next.

grilling asks a whole round of questions at once, but its own documentation says that "it can put
two questions in one round and only later find that one answer should have changed the other". One
at a time, each answer is weighed before the next question is chosen. The same page offers this
way as "a supported setting, not a workaround". Each question costs a message more, so the lead
time is kept down by the next principle and by asking only what is the person's (KR1.2).

### Research runs beside the questions

The pinner starts each subagent that finds a fact in the background, and meanwhile asks the
decisions that do not build on that fact. Only the decisions that build on it wait for it.

A question that waits for research it does not need adds the research's time to the lead time, with
nothing gained (KR1.2, KR2.2).

### The tree is the only record

Every decision and answer is written into `design-tree.json` before the next question. The pinner
asks a decision only once each decision it builds on is decided, and it reads which decisions those
are from the tree, not from the conversation.

A conversation can end, be cleared or be compacted, so a plan kept only in it is lost
([Where the course is kept](../architecture.md#where-the-course-is-kept)). A tree in a file is
read the same way by `pin-check`, by a new conversation and by the AI that makes the work.

### Every decision reaches the goal

Each decision is joined by `contributes_to` to the questions or decisions it serves, and through
them to the goal. A decision that reaches no question is cut, and a question that no decision
serves is a gap. `pin-check` finds both, and a decision decided before one it builds on.

A decision that serves nothing costs the person a question for nothing, and a gap is a point the
work will guess (KR1.1, KR2.1).

### pin knows no caller

No line of pin names a plugin that uses it. A caller gives `pin:down` the goal, the questions the
work must answer and the path of the tree, and the decisions it has already settled; pin fills the
rest. A caller may add keys of its own to the tree, and `pin-check` leaves them.

Turn and rn each take pin in as it is, and a change for one of them would reach the other unseen.

### The script is a command on the PATH

`pin-check` lies in pin's `bin/`, and is run by its name alone, as `pin-check <design tree>`.

A plugin's `bin/` is on the PATH of the Bash tool while the plugin is enabled, so a role of any
plugin that depends on pin runs the same command
([plugin components](https://code.claude.com/docs/en/plugins/components#executables)). The path of
pin's folder cannot be written in the caller's steps: `${CLAUDE_PLUGIN_ROOT}` in a caller's prompt
is the caller's own folder, and the Bash tool's environment does not hold it
([plugins reference](https://code.claude.com/docs/en/plugins-reference#where-each-variable-resolves)).
The check that ccpm's plugins lay on a role, holding it to the commands its steps name, matches each
command whole, so it holds `pin-check` only where the steps can write the command whole.

Tried on Claude Code 2.1.317 on 2026-11-03, with a plugin A that declared pin in `dependencies` and
both loaded by `--plugin-dir`:

- A's subagent ran `pin-check tree.json`, and the shell found pin's `bin/pin-check`. A's hook was
  given the command as `pin-check tree.json`, and A's check of the commands its steps name let it
  through.
- The same subagent, told to run `python3 pin/scripts/check.py tree.json`, was stopped by that
  check, and then ran `pin-check tree.json`.
- A subagent of A that preloaded `pin:down` read pin's `${CLAUDE_PLUGIN_ROOT}` as pin's folder,
  and A's own as A's folder; in its Bash tool, `$CLAUDE_PLUGIN_ROOT` was empty. A's hook was given
  A's folder alone, so it could not have matched a command naming pin's folder.

The cost: claude.ai and Cowork do not install a plugin with a `bin/` folder, so pin, and every
plugin that depends on it, runs in Claude Code alone.

## User stories

- As the person, I want to run `/pin:down` with my plan in rough words, be asked only what is mine,
  one question at a time, and confirm the design at the end. Carries O1 from the request to the
  confirmed design tree.
- As Turn or rn, I want to give my role `pin:down` with a work's goal, its questions, what I have
  settled and the path of the tree, and get back the confirmed design tree. Carries O2 from the
  call to the design tree.
- As Turn or rn, I want my role to run `pin-check <design tree>` and learn whether the tree holds
  together, or what is wrong. Carries each check step of O2; in O1 the pinner runs it within the
  first story.
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
  CK["pin-check<br>#lt;command line · Python 3.9#gt;"]
  TR[("design-tree.json<br>#lt;JSON file#gt;")]
  SRC[["the project's files and public pages"]]
  P -- "1 the plan, then each answer and the confirmation" --> MC
  MC -- "2 the plan, or a Caller's settled points (Goal, Question, Decision)" --> PN
  PN -- "3 a fact to find" --> RS
  RS -- "4 reads" --> SRC
  RS -- "5 the fact, with its Ground" --> PN
  PN -- "6 writes Decision" --> TR
  PN -- "7 runs on the path" --> CK
  CK -- "8 reads Design tree" --> TR
  CK -- "9 Check result" --> PN
  PN -- "10 one Decision to make, with a recommendation, then the design" --> MC
  MC -- "11 puts it" --> P
```

Legend: a rounded box is a person; a box is an AI or a script, with its kind and what it is made
with in angle brackets; a cylinder is a file; a box with double sides lies outside pin. Each
arrow says what one does to another, with the data it hands on named as in the data model, and its
number gives the order.

- Where the pinner is the main conversation, arrows 2, 10 and 11 are the main conversation's own.
- The pinner alone decides which decision to settle next, who settles it, and what to recommend.
  It alone writes the tree.
- The researcher finds one fact and nothing else. It is a subagent that Claude Code ships, such as
  Explore, so pin holds no agent of its own.
- `pin-check` alone decides whether the tree holds together. It reads the tree and writes nothing.
- A pinner that is a caller's role asks the person through the main conversation, as
  [Where the orchestrator runs](../architecture.md#where-the-orchestrator-runs) says.
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

### Sequences

The person runs `/pin:down`, O1 of the UX:

```mermaid
sequenceDiagram
  participant P as person
  participant M as main conversation (pinner)
  participant R as researcher
  participant C as pin-check
  participant T as design-tree.json
  P->>M: /pin:down with the plan
  M->>R: in the background, a fact to find
  M->>T: writes the Goal to confirm, and the Questions under it
  M->>P: the Goal, with a recommendation
  P->>M: the answer
  M->>T: writes the Goal confirmed
  R-->>M: the fact, with its Ground
  M->>T: writes the Decision it settles
  M->>C: runs on the path
  C->>T: reads the Design tree
  C-->>M: Check result
  loop until no Decision is left open
    M->>P: one Decision to make, with a recommendation
    P->>M: the answer
    M->>T: writes the Decision, with the person's words as its Ground
    M->>C: runs on the path
    C->>T: reads the Design tree
    C-->>M: Check result
  end
  M->>P: the design, each Decision in a short line, with what settled it
  P->>M: confirms it
  M-->>P: the path of the Design tree
```

Turn's designer has a work's design pinned down, O2 of the UX:

```mermaid
sequenceDiagram
  participant D as designer (pinner)
  participant R as researcher
  participant C as pin-check
  participant T as design-tree.json
  participant M as main conversation
  participant P as person
  D->>T: writes Turn's settled points: the Goal, the Questions, the Decisions it has
  D->>R: in the background, a fact to find
  R-->>D: the fact, with its Ground
  D->>T: writes the Decision it settles
  D->>C: runs on the path
  C->>T: reads the Design tree
  C-->>D: Check result
  loop until no Decision is left open
    D->>M: one Decision to make, with a recommendation
    M->>P: puts it
    P->>M: the answer
    M->>D: the answer
    D->>T: writes the Decision
    D->>C: runs on the path
    C-->>D: Check result
  end
  D->>M: the design
  M->>P: puts it
  P->>M: confirms it
  M->>D: the confirmation
```

A decision reopened takes the same loop: the pinner marks it and each decision that builds on it
open again in the tree, and settles them in order.

## Physical view

### Deployment

```mermaid
flowchart TB
  subgraph PC["the person's computer"]
    subgraph CCP["Claude Code process #lt;Claude Code 2.1.317 or later#gt;"]
      MC2["main conversation, or the caller's role: the pinner"]
      RS2["researcher"]
    end
    CKP["pin-check process #lt;python3 3.9 or later#gt;"]
    REPO[("the repository: .pin/#lt;yyyymmdd#gt;-#lt;name#gt;/design-tree.json,<br>or the path the caller names")]
  end
  API[["Anthropic's API, which Claude Code uses"]]
  CCP -- "runs pin-check by its name, through the Bash tool" --> CKP
  CCP -- "reads and writes" --> REPO
  CKP -- "reads" --> REPO
  CCP -- "the model's turns" --> API
```

- The person installs pin as [the README](../../plugins/pin/README.md#installation) says. A plugin
  that uses pin lists it in its `dependencies`, and installing that plugin installs pin.
- The person starts pin with `/pin:down`. A caller's role starts it by taking the skill.
- `pin-check` uses Python 3.9 and its standard library only, as
  [Python 3.9 and the standard library](../architecture.md#python-39-and-the-standard-library)
  says.
- A person's tree is kept in `.pin/<yyyymmdd>-<name>/` at the root of the repository, as
  [Where a plugin writes its files](../architecture.md#where-a-plugin-writes-its-files) says. A
  caller's tree is kept where the caller names.

### Directory structure

`pin-check` lies in `bin/`, not in `scripts/` as
[Entries pass the job to their parts](../architecture.md#entries-pass-the-job-to-their-parts) has
it, so that it is on the PATH, as [The script is a command on the PATH](#the-script-is-a-command-on-the-path)
says.

```text
plugins/pin/
├── .claude-plugin/plugin.json      pin's manifest and version <JSON>
├── skills/down/SKILL.md            pin:down's entry, which links the pinner's part <Markdown>
├── bin/pin-check                   pin-check's entry <command line · Python 3.9>
├── core/domain/tree.py             pin-check: the Design tree and its Check result <module · Python 3.9>
├── core/roles/pinner.md            the pinner's flow <Markdown>
├── LICENSE-grilling                Matt Pocock's copyright and permission notice for grilling <text>
└── README.md, CHANGELOG.md         for users <Markdown>

dev/pin/
├── ux.md, architecture.md, README.md   for builders <Markdown>
├── cosmic-ray.toml                 the mutation testing <TOML>
└── tests/
    ├── unit/core/domain/           unit and property tests of tree.py <Python 3>
    ├── integration/                bin/pin-check on real files <Python 3>
    └── e2e/                        the E2E tests and the prompt tests, and their plugin <Python 3>

.pin/<yyyymmdd>-<name>/design-tree.json   a person's Design tree
```

`LICENSE-grilling` lies in pin's folder, as installing copies only that folder, and the MIT
License asks that its notice go with each copy of a substantial portion.

## Test

pin is tested as [Test](../architecture.md#test) says. What follows is what pin adds.

| Deployment unit | Unit | Integration | End-to-end |
|---|---|---|---|
| pin-check process [python3 3.9 or later] | unittest, Cosmic Ray, Hypothesis · ●●● · each of the three checks, and the tree's form | unittest, real files · ●●○ · the exit and its message | E2E tests · ●●○ · run by the pinner on each answer |
| Claude Code process: the pinner [Claude Code 2.1.317 or later] | prompt tests · ●●○ · `pin:down` alone, with the person and the researcher stood in for | empty: the pinner's only parts are itself, the researcher Claude Code ships, and `pin-check`, whose meeting with the pinner the E2E tests run | E2E tests · ●●● · O1 by `/pin:down`, and O2 by a caller's role that takes `pin:down` |

The researcher has no row of its own: Claude Code ships it, and pin gives it only a prompt, tested
with the pinner's.

- A prompt test runs `pin:down` alone as [Unit: prompts](../architecture.md#unit-prompts) says,
  with Opus. A script stands in for the person, answering each question from a set of answers, and
  a stand-in researcher gives set facts. It passes in three runs of three: each message to the
  person holds one decision, each decision asked is one the person decides, no fact is asked, and
  the tree passes `pin-check`.
- An E2E test runs Claude Code with Opus on a copy of pin and of a plugin standing in for a caller,
  as [End-to-end: user stories](../architecture.md#end-to-end-user-stories) says. The person's
  answers are given by resuming the session with each next answer. It passes in three runs of three:
  what the prompt test asks, and the person asked to confirm before the run ends; in O2, also no
  point the caller settled is asked again, and the caller's check of the commands its steps name
  lets `pin-check` through.
- `pin-check` weighs ●●● in unit tests, as a tree it passes wrongly sends a gap into the work
  unseen. The pinner weighs ●●● in E2E tests, as a question that is not the person's, or a decision
  taken for them, is what pin is there to stop.
- Integration tests and the prompt tests weigh ●●○: the unit tests hold every behavior of
  `pin-check`, and the E2E tests run the pinner whole.
