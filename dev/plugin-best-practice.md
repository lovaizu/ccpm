# Best practice for building a Claude Code plugin

This is the best practice for building a Claude Code plugin. It says how a plugin's roles work
together when the work takes several steps and ends in something made, such as a document or code.
It also says where a plugin's files go, how its code is written, and how it is tested and released.
A plugin takes from it what its requirements call for. It has no UX and no user stories of its own:
each plugin's architecture links this one, names what it takes, and holds its own UX's user stories
and what only that plugin adds.

## Principles

A plugin takes the principles its requirements call for, and its architecture names them. The
reason for each is under Why it is so.

1. The orchestrator holds the whole run and decides each move.
2. The caller decides only what is theirs to decide, and approves it by their own action. The
   plugin does the writing. It makes every other choice itself and reports it.
3. Each job has its own role. The role gets only what the job needs.
4. Nobody relays messages. Whoever needs something asks whoever has it, and goes on with the
   answer.
5. A reader, an AI that did not make a work, uses it first. For each item of the checklist, the
   reader gives the item's Good lines, or its need, and tells the maker directly. Before that, the
   maker checks its own work item by item. The caller reads first a work they read in full to
   approve, such as a plan.
6. A script, a hook or the project's own tools check what a machine can check. They tell the role
   its step again, or stop what would break a rule. An AI reads only for what needs a reader.
7. A run that goes in a fixed loop has its course in a script. Every run that keeps a state writes
   it to a file before each next move, so a stopped run goes on from where it stopped.
8. The purpose comes first, speed second.
9. When the caller approves the finished work, the orchestrator looks once for what fell short and
   why. Lessons for the user's own project go into its checklists or rules. General lessons go to
   the plugin's makers as an issue, only if the user says yes. A plugin called by an AI leaves this
   to its caller.

## Architecture

### Logical view

#### Components

![A plugin's components](images/components.svg)

- The caller talks with the orchestrator, and a role that needs the person's decision asks the
  main conversation directly, as only the main conversation can ask the person
  ([Where the orchestrator runs](#where-the-orchestrator-runs)).
- The maker and the reader pass the work and its needs between them, with no one relaying
  ([Messages](#messages)).
- A plugin has a course script only where its run is a fixed loop that keeps a state
  ([Where the course is kept](#where-the-course-is-kept)).
- The guard is Lane's code laid in the plugin, and tells only subagents their steps again
  ([The guard tells each role its steps again](#the-guard-tells-each-role-its-steps-again)).

#### Data model

![A plugin's data model](images/data-model.svg)

- What agents pass on as data is JSON ([JSON between agents](#json-between-agents)).

#### Sequences

A run, from the orchestrator starting the maker to the reader's reply:

```mermaid
sequenceDiagram
  participant M as main conversation<br/>#lt;AI#gt;
  participant O as orchestrator<br/>#lt;main conversation or subagent#gt;
  participant G as maker<br/>#lt;subagent#gt;
  participant R as reader<br/>#lt;subagent#gt;
  O->>G: prompt
  G->>M: question, only the person can decide
  M->>G: answer
  O->>R: prompt
  R->>G: need
  G->>R: work mended, or a question back
  R-->>O: reply
```

- Each plugin's architecture draws a sequence for each of its own user stories on this one.

### Physical view

#### Deployment

![A plugin's deployment](images/deployment.svg)

- A person starts a plugin by its skill, which makes the main conversation the orchestrator. An AI
  starts a plugin by starting its orchestrator as an agent
  ([Where the orchestrator runs](#where-the-orchestrator-runs)).
- A run keeps its files as [Where a plugin writes its files](#where-a-plugin-writes-its-files)
  says.

#### Directory structure

```text
plugins/<plugin>/                 what runs on users' machines, installed by Claude Code
├── .claude-plugin/plugin.json    the manifest, holding the version <JSON>
├── skills/<command>/SKILL.md     a skill's entry <Markdown>
├── agents/<name>.md              an agent's entry <Markdown>
├── hooks/hooks.json              the hooks' entries <JSON>
├── hooks/lane/                   the guard, laid by Lane <Python 3>
├── scripts/                      what runs as a command and depends on Claude Code <Python 3>
├── core/domain/                  the knowledge and rules of the plugin's work
├── core/roles/                   each role's flow
├── docs/                         fuller use, named by the README's Documentation <Markdown>
├── images/                       the images the README shows
├── README.md                     for the plugin's users <Markdown>
└── CHANGELOG.md                  what changed for users in each version <Markdown>

dev/                              what only the builders need
├── README.md                     the plugins' folders, and how to run the shared checks
├── plugin-best-practice.md       this document
├── images/                       the images this document shows
├── scripts/                      the checks every plugin shares, and the hook before a push <sh, Python>
└── <plugin>/
    ├── README.md                 the way to the plugin's UX, architecture and tests
    ├── ux.md                     the plugin's UX <Markdown>
    ├── architecture.md           the plugin's architecture <Markdown>
    ├── images/                   the images its UX and architecture show
    ├── cosmic-ray.toml           the plugin's mutation testing <TOML>
    └── tests/
        ├── unit/                 each part against its contract, at the path of what each tests
        ├── architecture/         all the parts joined, against the plugin's architecture
        └── ux/                   the plugin in real use, against its UX
```

[Repository structure](#repository-structure) says why each lies where it does.

## Why it is so

### The orchestrator holds the whole and decides

The orchestrator talks with the caller. It keeps everything the run has found. It decides each
move: what to ask, what to have made, and when to change the plan or remake a work.

Each move brings facts that the next move depends on. Only someone who holds the whole run can
weigh them. Because the orchestrator talks with the caller itself, it can answer "why" and change
its proposal when the caller objects. A go-between cannot. Anthropic's
[Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
describes the same pattern: "a central LLM dynamically breaks down tasks, delegates them to worker
LLMs", for "complex tasks where you can’t predict the subtasks needed".

The orchestrator does not report progress while the run goes. Claude Code already shows each role
while it runs, and a message that repeats it is read by no one.

### Where the orchestrator runs

A plugin that a person calls runs its orchestrator in the main conversation, started by a skill. A
plugin that an AI calls, such as one given what to make as JSON, runs its orchestrator as an agent
that the calling AI starts.

Only the main conversation can ask the person; a subagent cannot
([subagents](https://code.claude.com/docs/en/sub-agents#available-tools)). So a role that needs the
person's decision asks the main conversation directly, whoever called the plugin.

### Languages

A plugin that a person calls first proposes two languages: the one it talks in, and the one it
writes into the repository in. It proposes what the repository and the person's instructions set.
Where they set nothing, it proposes the person's own language for talking and English for the
repository. It records the answer.

The plugin writes what goes into the repository in the repository's language. It puts what it shows
the person into the language of the talk, with nothing added and nothing left out. A plugin that an
AI calls writes in the repository's language, and the caller that talks with the person translates.

The person decides from what they read, so a translation that adds or leaves out something changes
what they approve. People who were not in the conversation read the repository later, and English
reaches most of them.

### Asking until nothing is left to decide

The orchestrator asks the caller every point that only they can decide, one at a time, each with a
recommendation. It finds facts itself. It shows the caller each fact the work depends on, one at a
time, to confirm.

A rough request leaves points open. A point settled before the work does not come back later as
rework. A fact that was found but not shown is still a guess made for the caller. The work starts
only after the caller confirms that both understand it the same way
([grilling](https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md),
[Let Claude interview you](https://code.claude.com/docs/en/best-practices#let-claude-interview-you)).

Some choices follow from the purpose and the project's usual practice, such as where a test goes.
These are not the caller's. The role that meets them decides, and reports the choice with the
reason, so the caller can see and change it.

Each question costs the caller time and holds the run until the answer comes. A question about
something the caller does not care about spends their time on the plugin's job. In a trial of Rn on
2026-10-27, most of its 11 questions were of this kind.

### The caller approves what is theirs

What the caller decides goes to the caller to approve. So does what is hard to undo, such as a
merge. A commit or a push can be undone, so it does not go to the caller.

If an AI decides these for the caller, the caller ends up answerable for something they never saw.

An approval counts only when it comes from the caller's own action, such as a skill that the AI
cannot call (`disable-model-invocation: true`). An agent saying it was approved does not count.
cc-sdd's agent sets its own approval flag, so the flag stops nothing.

### One agent for each job

A role made for each job does it, and gets only what the job needs.

A role starts in a fresh context with its own prompt and tools
([subagents](https://code.claude.com/docs/en/sub-agents)), so nothing from other work leads it
astray.

### Messages

The orchestrator starts a role with its prompt, and the role replies at its end, as
[Sequences](#sequences) draws. In between, whoever needs something
sends a message ([SendMessage](https://code.claude.com/docs/en/sub-agents#resume-subagents)) to
whoever has it.

A go-between holds nothing of what passes, and adds a move to every exchange. What the end of the
run needs from an exchange is in the files the roles write, and a script checks it there.

### JSON between agents

What agents pass on as data is JSON, read and changed with `jq`.

An agent then changes only the part it needs, with a tool it already knows, and leaves the rest as
it was.

### A plugin that uses another

A plugin that has another plugin do a job starts that plugin's orchestrator as one of its roles.
When a role of that plugin must ask something, it asks the main conversation, as every role does.

A subagent can start subagents down to three layers below the main conversation
([subagents](https://code.claude.com/docs/en/sub-agents#let-subagents-spawn-their-own-subagents)).

### Asking for what lies outside the work

Sometimes what keeps the work from going on lies outside it, such as a permission not given or a
tool not installed. Then the role does not look for a way round. It asks the main conversation for
what it needs, and goes on with the answer. It goes on with the rest of the work meanwhile.

The person can clear such a cause in a moment; the run cannot. A way round leaves a work checked
under other terms than the purpose set. A run that stops brings nothing back.

### Read by those who did not make it

AIs that did not make a work use it first. They stand in for the receiver, with what the
receiver has, and do what the receiver does with it. Each gives its verdict from its own first
reading.

The maker finds the Good it meant. A reader that did not make the work finds only the Good its
lines give, which is what the receiver gets. A reader shown someone else's verdict finds what it
was told. So two readings add a check only when each is made on its own.

A reader judges an item by whether the receiver can use the work for what they use it for. Where it
finds no Good, it says in one sentence what the receiver would need. It does not say how to make
it. It leaves what a machine can check to the checks that do it (Principle 6).

A reader that hunts for defects finds one in every work. Each is then mended, whether or not the
receiver would ever meet it. The rounds go on, and the work does not get better for its receiver.
In a trial of Rn on 2026-10-27, about 25 works were sent back. About 12 were for defects found by
running the work, 8 for what a linter or a type checker would have shown, and 5 for wording.

The maker holds the sources, so how the work gives each Good is the maker's to decide. The reader
says what the receiver would need, not how to give it. The maker then mends the work for the
receiver's use. When a reader names a fault for the maker to answer, the two end up arguing about
the fault, when both are there for the receiver's use.

When the receiver is the caller, and the caller reads the work in full to approve it as soon as it
is made, such as a plan, the caller reads it first. A reader in their place would add a reading the
caller makes anyway, and its time at every remake.

Once the maker has made the work, it checks it against its checklist item by item. It gives each
item as the lines of the work that give its Good, `<path>:<from>-<to>`, with no words. On a remake
it gives only the items sent back. Each item says what is run and how far, so maker and reader run
the same thing.

Finding the lines makes the maker look at the place. Lines can be checked by a script, a reader or
the caller. A claim in words is read by no one, and costs its writing at every round. In that trial
the maker rewrote such a claim for every item each round, 23,000 characters, and only a form check
read it. Two who run the same check see the same result. So when one of them finds no Good, it is
not because they chose to run different things.

### The guard tells each role its steps again

A role's step that is not sure to hold gets a hook. The hook notices when the role drifts from the
step and tells it the step again. The hooks are in the plugin's `hooks/hooks.json`, and each acts
only in the roles it names.

A hook runs every time, while an instruction is only advice
([best practices](https://code.claude.com/docs/en/best-practices)). Claude Code reads no hooks from
a plugin agent's own file ([subagents](https://code.claude.com/docs/en/sub-agents)). A hook is told
which subagent it runs in, but not which skill runs in the main conversation, and a skill's hooks
last the whole session once it starts
([hooks](https://code.claude.com/docs/en/hooks#hooks-in-skills-and-agents)). So an orchestrator in
the main conversation is held by its own steps, or by the script that keeps its course. GitHub's
branch protection or Claude Code's permission rules hold what is hard to undo.

### What a machine can see of the work

A project whose work is code has a formatter, a linter and a type checker set up, and the command
that checks the work runs them. Makers and readers do not look for what these tools show.

A tool finds the same thing every time, at once. An AI reading for it finds only some, and spends a
round on each. In that trial the project had none of these tools, and 8 of the works sent back were
for what they would have shown.

### Where the course is kept

A plugin whose run is a fixed loop keeps its course in a script of its own.
The script gives the orchestrator each next step, so the orchestrator cannot go on without it. A
plugin whose course changes with what the run finds, such as Rn, keeps its course in its skill's
steps and its plan in a document. A plugin whose run keeps no state, such as Turn, where the maker
and the reader settle the work between them, keeps no course in a script.

The spec-driven tools read on 2026-10-21 (Spec Kit, BMAD-METHOD, OpenSpec, superpowers and cc-sdd)
all keep a fixed course outside the AI, with the plan as a file of tasks that the course walks
through. None of them runs the steps inside a task from code. OpenSpec calls its own steps
"prompt-level behavior contracts, not enforceable checks". A course and its rules kept in code are
followed the same way every time; an AI deciding may not follow them.

A course fixed in code has no move for what it did not foresee, so it does not suit a run whose
findings keep changing the course.

The script gives the orchestrator only the moves that need it, such as starting a role, sending a
message, asking or returning the result. The script does itself what a script can do, such as
checking a reply's form or waiting for a role to end.

Each move of the orchestrator is a turn of the model, which reads the whole conversation. So a move
that the script could make costs time, and adds to what every later move reads.

The run's state is kept in a file in its work folder, placed as
[Where a plugin writes its files](#where-a-plugin-writes-its-files) says. Each decision and answer
is written there before the next move. So a run stopped anywhere goes on from its last move in a new
conversation, and an answer is taken in where the run stands. What is kept is committed and pushed
at the end of a step.

A conversation can end, be cleared or be compacted, and what lives only in it is lost. Going on
after a stop needs the file, not the push. A run started again for an answer would make again what
it had already made.

### Where a plugin writes its files

Besides the work and the files its caller names, a plugin writes two kinds of files. What may be
kept goes in `.<plugin>/<yyyymmdd>-<name>/` at the root of the repository, as Rn keeps
`.rn/<yyyymmdd>-<slug>/`. What is used only while the plugin runs, including its tests' and
trials', goes in `<plugin>/<yyyymmdd>-<name>/` in the system's temporary folder, the one Python's
`tempfile.gettempdir()` gives. A file that an agent reads with its tools goes in the folder that may
be kept, even if it is used only while the plugin runs, and is removed once it is used.

With one folder named after the plugin, the user chooses with one line of `.gitignore` whether git
keeps what is in it. The date at the front sorts the runs and shows the old ones.

What is used only while running needs no step to remove it. A run stopped partway would miss such a
step, but the system clears its temporary folder itself. That folder is the one TMPDIR names where
it is set; macOS and sandboxes set it to a folder of their own, so it is not always `/tmp`.

Claude Code lets an agent read without asking only inside the working folder and the folders added
to it (permissions, Permission system). A file outside it stops an agent that works on its own to
ask.

### The purpose before performance

A change is taken only if it still meets the requirements. Time or cost is cut only after that.

A work that misses the purpose costs the caller the fixing as well as the wait. So time saved by
leaving them more to fix is spent again by them.

### Learning from each run

A plugin takes in what is general, and leaves to the user's project only what is the project's own.
What a user finds missing in the plugin comes back to it as a lesson.

Once the caller approves the finished work, the orchestrator looks once through what the run kept:
each work sent back, each work made again, and each point asked again. It checks each cause it
doubts in the records of the run, so each lesson comes with the words it rests on, quoted. It puts
each lesson to the user.

- A lesson of the user's own project goes into their checklists or rules.
- A general lesson goes to the plugin's makers as an issue. The issue holds the need and its points,
  never the user's source. The orchestrator shows it to the user in full, and opens it only on
  their own yes, as [The caller approves what is theirs](#the-caller-approves-what-is-theirs) says,
  since an issue on a public repository cannot be undone.

Looked for once, the lessons cost the user one reading. Lessons made at every approval would be
weighed again in every session. What the run kept holds every send-back and remake, because each
move is kept before the next (Principle 7). A cause named without its record is a guess.

A plugin called by an AI is one move of its caller's run. So what fell short in it shows in what
that run kept, beside the rest.

A lesson of the project's own improves that project's later work. The plugins are open source, so
a general lesson, met once, improves the plugin for every user. The work and its source are the
user's, so the user chooses what leaves their project.

## Repository structure

### The plugin's folder and dev/

What runs on users' machines is in the plugin's folder, `plugins/<plugin>/`. What only its builders
need, such as its UX, its architecture, its tests and its trials, is in `dev/<plugin>/`.

Installing a plugin copies only its folder, so what only builders need stays off users' machines.
The plugins' folders are kept together in `plugins/`, as the official marketplaces
[anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) and
[anthropics/claude-code](https://github.com/anthropics/claude-code) keep theirs. The root then holds
only what the whole repository needs.

### Entries pass the job to their parts

An entry is a skill, an agent, a hook or a command line: something whose form Claude Code fixes. An
entry holds only what Claude Code fixes, and hands the job to its part, kept in a file of its own
named after that part. The files then show the parts the logical view draws.

- A command line reads its arguments and calls the part's module.
- A hook's script reads the event and calls the part that answers it.
- A skill or an agent is its frontmatter and a body. The body points to its part and says where
  each script, file or folder the part names lies. The part names each of these by its name alone,
  such as `turn.py`, never by where it is installed.

The entries lie where Claude Code looks for them, in `agents/`, `skills/` and `hooks/`. A plugin's
own parts lie in `core/`, as [The core apart from Claude Code](#the-core-apart-from-claude-code)
says. What runs as a command and depends on Claude Code lies in `scripts/`, as the official
plugins keep their scripts. Lane's guard, which every plugin takes in, lies in `hooks/lane/`, where
Lane lays it.

The form of an entry is Claude Code's: a skill's folder is named after its command, and an agent is
called by the name in its frontmatter. The job is the plugin's. A job kept in its entry is found by
the command that calls it, not where the logical view puts it. A second entry to the same job, such
as `/rn:ty` beside `/rn:up`, would come to repeat the first. Cockburn's
[ports and adapters](https://alistair.cockburn.us/hexagonal-architecture/) says the same: "as events
arrive from the outside world at a port, a technology-specific adapter converts it into a usable
procedure call or message and passes it to the application".

An agent's body has the agent read its part in full before anything else, and a lane holds it to
this. Claude Code makes the body the agent's system prompt and takes in no other file
([subagents](https://code.claude.com/docs/en/sub-agents)). A skill's body links its part, as Claude
Code has a skill "reference supporting files from `SKILL.md`"
([skills](https://code.claude.com/docs/en/skills)). In a trial on 2026-10-26 with a plugin made for
it, each of twenty runs read its part first and followed it. After `/compact`, the part a skill
links came back attached in full, while the skill's own body survived only as the summary retold
it.

Claude Code replaces `${CLAUDE_PLUGIN_ROOT}` with the plugin's folder only in what an entry's own
body gives, not in what the Bash tool runs
([plugins reference](https://code.claude.com/docs/en/plugins-reference#environment-variables)). In
a trial of Turn on 2026-10-26, it was not replaced in a part read with Read either: a part naming
`${CLAUDE_PLUGIN_ROOT}/scripts/turn.py` ran `/scripts/turn.py`. A part naming `probe.py`, whose
entry said where it lies, ran it in each of twelve runs, an agent's and a skill's, and in each of
three after `/compact`, where the summary kept where it lies. Where the plugin is installed is
Claude Code's business. The entry adapts to it, as ports and adapters has it, and the part holds
none of it.

### The core apart from Claude Code

A plugin's own logic lies in `core/`, and depends on no agent, such as Claude Code or Codex. It
names no tool of theirs, such as the Agent tool or `AskUserQuestion`; the entries do. Inside it:

- `core/domain/` holds the knowledge and rules of the plugin's work, which every role reads alike.
- `core/roles/` holds each role's flow, which uses the domain.

Each places its prompts, scripts and assets as its parts need.

What the plugin knows then outlives the agent it runs on, as Cockburn's
[ports and adapters](https://alistair.cockburn.us/hexagonal-architecture/) has it: the application
is "developed and tested in isolation from its eventual run-time devices and databases". The
domain changes only when the work's rules change, and a role only when its way of working does, so
each is changed without reading the other.

### Images beside their document

An image lies in `images/` beside the document that shows it, as `dev/images/` for this document.

A folder then shows its documents and parts when it is opened, and an image is found from the
document that shows it.

A figure is an SVG whose style is the one in `dev/images/figures.css`, its colours light by default
and dark under `prefers-color-scheme`, which follows the page's theme. An image shown by `<img>`
reads no file beside it, so each SVG carries a copy: `python3 dev/scripts/figures.py write` puts it in, and
`dev/scripts/check.sh` fails on a copy left behind.

### The READMEs

- `plugins/<plugin>/README.md` is for the plugin's users.
- `dev/<plugin>/README.md` links the plugin's architecture, and says how to run its tests and trials
  once they exist.
- `dev/README.md` lists each plugin's folder, says how to run the checks every plugin shares, and
  links [the order the work goes in](../.claude/rules/dev.md).
- The root `README.md` leads users to each plugin's README and builders to `dev/`.

No README is put deeper.

GitHub shows a folder's README when the folder is opened, so a visitor finds the way by opening
folders. A README further down would repeat its parent's and drift from it.

### The CHANGELOG

Each plugin keeps its `CHANGELOG.md` in its root, `plugins/<plugin>/CHANGELOG.md`, in the form that
Release gives.

A user then finds what changed for them in the same place for every plugin.

## Code

### Python 3.9 and the standard library

What runs on users' machines is Python 3, version 3.9 or later, with the standard library only. The
plugin's README says so. A script that only calls an existing tool may be sh.

python3 is wherever git is, while Node.js may not be, and users run 3.9.

### Code kept once

What the plugins already share is used, not written again. Code that more than one plugin needs,
such as how a hook reads a command, is kept once, in the plugin whose job it is. Its tests are in
that plugin's `dev/<plugin>/tests/`. Each other plugin takes it in through a relative symbolic
link. What the tests share, such as a repository made once and copied for each test, is kept beside
that code's tests, as Lane's `dev/lane/testing.py` is.

Installing copies the target of a link within the marketplace into the plugin
([share files within a marketplace with symlinks](https://code.claude.com/docs/en/plugins/host-marketplace#share-files-within-a-marketplace-with-symlinks)).
So each plugin carries the shared code, while the code is written, tested and fixed in one place.

### No lines copied

No lines are copied between files, except a test's expected value, which is written out again.
`dev/scripts/check.sh` fails when two files share four or more similar lines of Python, not counting
comments, docstrings and imports, as pylint's `duplicate-code` finds them. It does this wherever
pyproject.toml's `test-quality` group is installed. It does not tell a test's expected value apart.

A copy gets fixed in one file and left wrong in the other. A test that takes its expected value
from the code checks the code against itself.

### Checks kept in Lane

A check on what an AI does is a lane of [Lane](../plugins/lane/README.md), laid in each plugin by
Lane's `lay.py`. The assistant adds a check that no lane holds to Lane as a lane of its own, in its
own named file, with one entry file for each hook event, as the official
[`hookify`](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/hookify) plugin
does.

Each check is then written and tested once, in Lane, and each plugin takes Lane's code in through a
link. A check kept in a plugin of its own would read the AI's calls apart from Lane and drift from
it. A check in a file of its own can be read, fixed and tested on its own.

## Test

Each plugin is tested at three levels. Each level is named by what its tests check against:

- **unit** checks one part against its contract: what the part takes, what it gives, and the
  forms its results take.
- **architecture** joins all the parts and checks them against the plugin's architecture. It runs
  every user story's sequence from start to end.
- **ux** checks the plugin in real use against its UX.

A **double** is a stand-in for a part that gives set results. A part made of code is tested by
tests of code, and a part run by an AI by a **trial**: a run of the AI, judged from its records.
Each test is drawn from the one thing its level checks against, not chosen by its writer: unit
from the ways a part's contract divides, architecture from the paths the plugin's sequences draw,
and ux from an objective's scenario. Two builders then draw the same tests, and a failure points to
that one thing. The levels compare as follows; the sections below give each rule's reason.

| | unit | architecture | ux |
|---|---|---|---|
| Runs real | the part alone; a part run by an AI on Opus | what joins the parts: the hooks, the scripts, and the entries, lanes and routes as they are laid | the whole plugin, installed as its user installs it, on Opus |
| Doubles stand in for | the part's neighbours, and Claude Code where the part meets it | each role an AI runs, and each thing outside the plugin, such as Claude Code, so no model is called | nothing of the plugin |
| Stands in for the person | a script with set answers, or an AI given an intent | the double of the main conversation, with set answers | an AI holding an intent written before the run and never shown the plugin |
| Covers | each class, each edge and each rule of the part's contract | every path through each sequence: the main flow, each branch, each send-back and each question | each objective's scenario, on a subject as big as a real request |
| Passes when | code: every test passes, every line and branch run, every mutant caught; a trial: as [Results that vary from run to run](#results-that-vary-from-run-to-run) says | every test passes, with the role and the data checked at each step | the stand-in gets what the objective says, as [Results that vary from run to run](#results-that-vary-from-run-to-run) says |
| Runs | code: before each push and in CI; a trial: as the part is made | before each push and in CI | once every lower level passes, at the end of the whole |
| Is written as | `test_*.py`, or `trial_*.py` for a trial | `test_*.py` | `trial_*.py` |

The tests lie in `dev/<plugin>/tests/`, in a folder for each level: `unit/`, at the path of what
each tests, as `tests/unit/core/domain/`; `architecture/`; and `ux/`. What the tests of more than
one level share lies in `tests/` itself, as `tests/helpers.py`. A file of tests of code is named
`test_*.py`, and the code that runs a trial `trial_*.py`, so `unittest` finds only the tests that
CI runs.

A test is then found from what it tests, and the folders bear the names of the test table's
columns. Each plugin's architecture holds that table, a row for each deployment unit, and its own
test rules give only what differs from these.

### No check passes what it did not check

Every check ends in one of three ways: no problem, a problem found, or could not check, with why.
For each way a check can fail to check, what happens next is decided beforehand and tested.

- A hook whose script fails or times out, or that cannot parse a command, stops the call and says
  so.
- A skipped test is not a passed test.
- A CI job that did not run does not pass.
- A reader whose command did not run gives no Good.

A check that says nothing when it could not check is read as one that found nothing. What it was
there to stop then goes through unseen. A case decided only when it is met is decided in a hurry,
by whoever meets it.

### Unit: code

Each part made of code has unit tests, written with `unittest` in `dev/<plugin>/tests/unit/`.
Each double in them stands in for a neighbour of the part, such as a module it calls or an event
of Claude Code. The tests are drawn from the part's contract:

1. Divide each input and each result the contract names into classes that the part treats alike,
   the ones it refuses among them, and write one test for each class.
2. Where a class ends on an ordered scale, such as a length or a count, write one test at each end
   and one at the nearest value in the next class.
3. Where the result turns on a combination of conditions, write a table with one rule for each
   combination that can occur and the result it gives, and write one test for each rule.

A part treats every input of a class alike, so one test stands for the class, and faults gather at
the edges of a class. A table shows each combination at once, so none is left out unseen.

The unit tests run every line and every branch of the part: C0 and C1 coverage, 100%, counted on
the unit tests alone.

Two more checks confirm that the unit tests are enough.

- Mutation testing with Cosmic Ray: the unit tests must catch every mutant. The only exception is a
  line marked `# pragma: no mutate`, where no input the code takes can tell the mutant apart. The
  plugin's `cosmic-ray.toml` gives the reason once.
- Property tests with Hypothesis, on new inputs each time: they must all pass. The assistant
  adds each input a property test fails on as a unit test.

The unit tests hold every behavior the code must have. A line or branch that none of them runs goes
unnoticed. A line that only an architecture test runs is one whose contract no unit test holds. A
gap the other two checks find is a missing unit test, and the assistant adds it so that every push
catches it again.

What runs when:

- Before each push, `dev/scripts/githooks/pre-push` runs the unit and architecture tests of each plugin the
  push changes, counting lines and branches. It also runs the linter, the formatter, the type
  checker and the manifests' check, and stops the push on a failure.
- On every push, CI runs every plugin's unit and architecture tests, counts the lines and branches
  the unit tests run, and fails on any line or branch not run. It runs the mutation testing and the
  property tests on what changed since the last commit whose run passed, the property tests on many
  inputs, each plugin in its own job, all at once. A push stops the run still going for the push
  before it on the same branch.
- On a push that changes a plugin's version, CI runs both on the whole plugin, before it is
  released.
- Each check runs on Python 3.9 and the newest Python. Cosmic Ray and Hypothesis run on the newest
  only.
- CI's `tests` job runs on every push. It skips the checks when the push changes only what no check
  reads, such as the session records and the documents in `dev/`, and the last commit whose run
  passed is in its history.

The reasons:

- The code must run on 3.9. The two tools need newer versions only to test, not to run.
- A check left to be run by hand gets forgotten, and is found only by CI after the push.
- The tests are designed before the code, and the coverage shows each line and branch run. So the
  property tests and the mutation testing only confirm that design. Run before every push, on many
  inputs or once per mutant, they would make every change wait. A survivor that CI finds goes back
  to the test design that missed it.
- A run stopped or failed confirms nothing, so the next run checks from the last one that passed;
  started from the push before, every push made while a run was going would check the whole
  branch again, and the runs would pile up.
- Checking what a change touches takes minutes; checking the whole takes long. So the whole is
  checked when it reaches users. A test weakened with no line of code changed is among what only
  the whole run finds.
- `main` takes a pull request only after `tests` has passed. So `tests` always runs, and passes
  only what it checked.

A plugin's whole test run takes seconds, and the time each check takes is read on every run.
Mutation testing runs the tests once for each mutant, so a slow test run makes every change wait.

### Unit: prompts

The assistant tries each role, a skill or an agent, on its own, with doubles standing in for its
neighbours and for the researchers, and a stand-in for the person. It names the model in each run:
Opus, the model the maintainer uses. It judges the role from its input, its output and the records
of the run, against its Role and Steps. The trials are made as `prompt.json`'s trials part, its
questions and its practices say: drawn from the role's contract, one case at a time, each part of
a trial checked on a kept record before a run trusts it.

A prompt is known by what the AI does with it, and only the records show where a run went wrong. A
role tried together with what lies around it does not show which of them went wrong. A smaller
model makes different slips from the ones users meet. A model left to the runner's settings changes
with whoever runs the trial.

### Architecture: the parts joined

The architecture tests run real what joins the parts: the hooks, the scripts, and the entries,
lanes and routes as they are laid. They stand in with a double each role an AI runs and each
thing outside the plugin. Each plugin's test rules name what runs real in it. A double of Claude
Code sends the hook events and runs the hooks' commands in `sh`, as
Claude Code does. A double of the main conversation, or of a caller, answers each question with a
set answer. The double of Claude Code is kept once, in Lane's `dev/lane/testing.py`, as
[Code kept once](#code-kept-once) says.

The tests are drawn from the plugin's sequences:

1. For each user story, list the paths through its sequence: the main flow first, then each branch,
   each step that sends work back to an earlier one, and each question put to the caller or the
   person.
2. Add paths until every move from one step to the next lies on some path.
3. Write one test for each path, from its first step to its end. At each step, check the role that
   acts and the data it hands on.

Each plugin's test rules list its paths. A path the sequences draw that no test runs is a gap in
the architecture tests, and a path no sequence draws is a gap in the sequences.

A fault of a sequence lies between parts, where each part's unit tests pass, so what joins them
runs real. With each role an AI runs a double, no model is called. So the tests take seconds and give the same result on each run, and
every push checks every path.

### ux: the plugin in real use

Once every unit and architecture test passes, the assistant tries the whole plugin as its user
uses it, on each objective's scenario, on a subject as big as a real request. The trial confirms
the objective and its key results that no lower level can measure, such as the lead time. It does
not aim to cover every case, as the lower levels cover them.

An AI stands in for the person, answering from an intent written before the run and never shown to
the plugin. A run passes where the stand-in gets what the objective says, judged against that
intent. For each key result, the plugin's test rules say what is measured, such as the lead time
from the request to the result. Each measure is set against the last run's in the direction the UX
gives it, as the UX gives a key result no target value. The assistant then shows the maintainer:

- how close it came to the goal and to each key result of the UX;
- the time and the tokens it took, beside the size of the work;
- what could be improved.

The maintainer decides from these whether the plugin reaches users. The assistant keeps each
run's time and tokens with the trial's records, so runs can be compared.

Each part can pass, and every sequence too, while the user's objective is missed. What reaches
users is the maintainer's decision. No bar for the time and the tokens is known before runs gather,
so each run is set against the last. Runs kept side by side show whether a change made things
better or worse, with the purpose met as fully (Principle 8). A trial takes minutes and calls the
model on each move, so a few trials confirm what the lower levels have already checked.

A plugin made for the test stands in for a plugin that calls the one tried. Each Claude Code a
trial starts, and each stand-in for a person, runs on a configuration folder of its own, made fresh
by `dev/lane/trials/trying.py`, with only the plugins under test, so it reads none of
the developer's CLAUDE.md, settings or memory: a trial shows how a plugin behaves for any user, not
for the one who runs it. A configuration folder holds its own login
([multiple accounts](https://code.claude.com/docs/en/authentication#log-in-with-multiple-accounts)),
so the trial gives the developer's as `CLAUDE_CODE_OAUTH_TOKEN`, read from their own folder and
never written there. Where Claude Code asks the person to allow a call, the stand-in sees what the
screen shows and chooses, as a person would.

A trial that needs a real GitHub repository runs in `lovaizu/playground`, one at a time, on a branch
of its own. When it ends, the trial removes the branch, its pull requests and anything else it made
there. The code that runs a trial, of the whole or of a role, is not counted in the lines and
branches.

CI cannot start Claude Code, so each trial is a check of its own. The pull requests and pushes a
trial makes stay out of every repository people use, and `main` there takes nothing except a
reviewed pull request. Two trials at once, or one left behind, would mix with the next.

### Where a double's results come from

A double is built from the form that the part's contract gives its results, and is set only to
results that form allows, the refusals among them.

- A role's double writes files in the forms the role's part must write, and gives only results
  that a route from the role is on. The architecture test checks each file the double writes by
  the same check that the role's unit test makes of the role's files, such as the JSON Schema of an
  `in_form` lane or a plugin's own check script.
- The double of Claude Code sends the hook events in the fields and the order that Claude Code
  documents. Where its documentation says nothing, the double sends what a try of the real Claude
  Code showed. The plugin's architecture records each such try with the Claude Code version and
  the date, as [Lane's sequences](lane/architecture.md#sequences) do.
- The double of the `claude` command, a script on `PATH`, prints what `claude plugin validate`
  prints.

A pass of unit and architecture then holds for the real parts. A double that gave what the part
never would would pass a test that the real part fails. A double held to the part's contract fails
as soon as the contract changes, as the part's own unit tests do.

### A fault is tested at the level that must catch it

Each fault belongs to the lowest level whose check it breaks:

| The fault | The level that must catch it |
|---|---|
| A part gives what its contract does not allow, or a case of the contract goes wrong | unit |
| A handoff, a route or a result between roles goes wrong, such as a role started that no route names, or a file one role writes that the next cannot read | architecture |
| It shows only in real use at real size, such as the lead time, a work the person would still change, or Claude Code acting otherwise than its double | ux |

Where a higher level finds a fault, the assistant names the case or the path the lower level
missed. It adds that test at the level that must catch it, runs it and sees it fail, and then fixes
the fault there. Where Claude Code acts otherwise than its
double, the assistant first corrects the record of the try and the double, and then sees an
architecture test fail.

A fault found by a higher level is one that a lower level missed. A lower-level test points to the
part or the handoff at fault, runs in seconds, and catches the fault again on every push. A fault
fixed only where a trial found it comes back unseen, as no trial runs on every push.

### Results that vary from run to run

A trial passes where its expectation holds in three runs of three, unless the plugin's test rules
give other counts. A run counts only where it tried what the trial invites, such as a break of a
rule. A run that does not count is no pass.

What an AI does varies from run to run. An AI that keeps a step once may break it the next time,
and a user meets every run. So each run must meet the expectation, not most of them.

## Release

### On the maintainer's word

The assistant releases a plugin only on an explicit instruction from the maintainer, not on a merge
to `main`.
Until then, the changes users would notice wait under the CHANGELOG's `## [Unreleased]`.

Users receive an update only when the version is bumped, so the maintainer decides when it reaches
them.

### The manifests checked

Each plugin passes `claude plugin validate <plugin-path> --strict`, and the marketplace passes
`claude plugin validate <marketplace-root> --strict`.

A malformed manifest fails for every user at install, before any behavior is reached.

### The version

`version` is written in one place only, the plugin's `plugin.json`. It is always set, in semver,
such as `0.1.0`. How far it goes up is decided by the largest change users see:

- major for a breaking change, or minor while the version is `0.x`;
- minor for a new or changed behavior users see;
- patch for no change in behavior.

When both are set, `plugin.json` wins over the marketplace entry, so a second copy means nothing.
`claude plugin validate --strict` fails when `version` is not set.

### The CHANGELOG's form

The CHANGELOG is in [Keep a Changelog](https://keepachangelog.com) form.

- Each release has one `## [x.y.z] - YYYY-MM-DD`, with its changes under `Added`, `Changed`,
  `Fixed` and `Removed` as they apply.
- Every change a user would notice gets one line, written as
  `<what changed> — <why it helps the user>`. Typos, refactors, internal documents and formatting
  get none.
- On a release, `## [Unreleased]` is renamed to the version and date, and no empty
  `## [Unreleased]` is left behind. It is made again when the next change users would notice lands.

A user reads what changed for them and why it helps them.

### The steps of a release

1. The assistant bumps `version` in `plugin.json`, finalizes `CHANGELOG.md`, makes the
   [final check](../.claude/rules/final-check.md), commits and pushes.
2. The assistant asks the maintainer to merge the pull request to `main`. It never merges it itself
   and never uses `--admin`, since `main` is protected and only the maintainer can clear its
   required review.
3. The maintainer merges, and says so.
4. The assistant tags `main` as `<plugin>--v<version>`, such as `rn--v0.2.0`, with
   `claude plugin tag --push` from the plugin's folder. It publishes a GitHub Release for that tag,
   with the CHANGELOG's matching section as its notes.

The tag is in Claude Code's own form. A plugin that depends on another with a version range
resolves the range against these tags, and the prefix lets each plugin number its versions apart
from the others. The command also checks the plugin, and refuses a tag that already exists. When a
plugin was released is read from its tags and Releases, not from merge commits.

### Registering in the marketplace

The assistant registers a plugin on its first release, and again whenever it is renamed or removed.
Registering changes two things together:

- one entry under `plugins` in `.claude-plugin/marketplace.json`, with `name`, `description`,
  `source`, such as `./rn`, and `category`
  ([plugin entries](https://code.claude.com/docs/en/plugins/marketplace-reference#plugin-entries));
- a line in the root `README.md` linking the plugin's README, with a one-line description.

Claude Code installs from the marketplace entry, and people find the plugin from the root README. A
plugin counts as shipped only once both reach it.
