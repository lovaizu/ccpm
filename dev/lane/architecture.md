# Lane architecture

## User stories

- S1: the user wants to read what Lane would hold before any change, so that nothing holds their
  plugin unread.
- S2: the user wants to approve the proposal or ask a change, so that Lane lays only what they
  approved.
- S3: the user, as an AI, wants to approve by its own act, so that it waits for no person.
- S4: the user wants the checks to follow their changed steps, so that the checks match the steps
  as written.
- S5: the user wants their plugin's subagents to start in the order they designed, so that results
  move the run.
- S6: the user wants each subagent held to its steps, so that one that leaves a step goes back.
- S7: the user wants a stopped run to go on where it stopped, so that its subagents don't start
  over.

## Solution strategy

Lane turns the user's steps into checks once, and holds every run by them. up proposes them,
`lay.py` lays them on approval, and the laid guard gives each run its step or start due. Lane builds
on [the plugin guide](../plugin-development-guide.md), and every view keeps these rules.

### The steps are the one source

up proposes from the steps alone, without the text the Laid names, and writes each asked change into
the steps.

*Why*: a rule kept apart from the steps is unseen there, and the next `/lane:up` loses it, which
raises KR1.1.

### One type gives the sentence, the check, and the steps it suits

up, `lay.py`, and the guard take each rule's sentence, check, and suited steps from its lane type
alone.

*Why*: a sentence and check made apart drift, so the check stops a role that keeps the sentence,
raising KR1.1.

### Laid only on the caller's own act

`lay.py write` lays only the Proposal its caller approved by their own act, while the steps read as
shown.

*Why*: unread rules stop moves the user meant to allow, raising KR1.1, and an AI kept waiting adds
to KR1.2.

### Lane's part replaced whole

`lay.py write` replaces at once everything the Laid names, and leaves every other part of the plugin
as it stands.

*Why*: a stale rule stops an allowed move, and a lost user hook entry leaves a step unheld,
raising KR1.1.

### A result only from the result script

The guard moves a Run only on a Result that its Start's subagent gave by `result.py`, never by
reply.

*Why*: a reply read as a result starts a role the order doesn't name, which raises KR1.1.

### What no hook shows only from Lane's scripts

The guard checks what hooks show from the calls, and takes the rest only from Lane's scripts.

*Why*: a reply taken for a read or a Step done lets a skipped Step pass, raising KR1.1.

### Only the main conversation starts the roles

The guard lets a start of a role through only from the main conversation, as a Start due.

*Why*: a subagent that starts roles of its own starts roles the order doesn't name, which raises
KR1.1.

### A stop gives the step back

Each stop gives the sentence broken and what to do, or why the guard can't check, and who fixes it.

*Why*: a role that meets only a refusal finds another way to do the step, which raises KR1.1.

### The run kept in a file

Each Run's state comes from the run record and the kept results, worked out by the guard's code
alone.

*Why*: a compacted or new conversation forgets the run, and two parts working it out drift apart,
raising KR1.1.

### The guard checks only the run

The guard checks calls only within a Run, and none during another plugin's run that a move called.

*Why*: a check that reaches the user's work or another plugin's run stops a move no step
forbids, raising KR1.1.

### The laid plugin runs alone

The guard, `result.py`, and lane types need only Python 3.9's standard library and the plugin's
folder, and name no plugin.

*Why*: whoever runs the plugin may lack Lane or have another version, stopping or changing the run,
raising KR1.1.

## Components

![Lane's components](images/components.svg)

- user\
  Writes each step, reads the proposal, and approves it or asks a change.
- up\
  Proposes each step's lane type, each skill's routes, and each missing result's name from the steps.
- lay.py\
  Checks a Proposal, shows how the steps read once laid, and lays it into the plugin.
- lane types\
  Give each rule's sentence, the steps it suits, what it allows, and its check of a call or an end.
- guard\
  Places each hook event in its Run, and gives each start due, each stop, and each approval.
- result.py\
  Takes a result given as a command of its own, only where a Run lets its role give it.
- step.py\
  Gives a Step's Mark as a command of its own, which the guard checks at its call.
- item.py\
  Gives an Item's Mark as a command of its own, which the guard checks at its call.
- adapter\
  Gives each start's text, a Step's Items, and kept results in Lane's form, and names what a call
  picks up.

Strategies:

- A proposal from the steps' sense, by up\
  Only a reading of their sense gives routes to a step that names no subagent, keeping KR1.1 low.
- The approval held by a guard laid on up\
  The main conversation can't approve for a person who typed `/lane:up`, keeping KR1.1 low.
- Each skill as one role whose steps lie in several files\
  No hook event marks where a command's steps end, so only the skill's lanes hold them all, keeping
  KR1.1 low.
- `lay.py print` refusing a Proposal the plugin's files can't carry\
  Route commands the model calls, unnamed adapters, shared steps files, and foreground subagents
  break runs, raising KR1.1.
- An end held to the plugin's own command, which Lane runs\
  A role that leaves its steps skips the checking step too, and only the plugin knows its measure,
  raising KR1.1.
- A sentence left out of a step that already says it\
  A rule said twice takes the role's attention from its step, so the step says each once, keeping KR1.1 low.
- A call kept where one Lane of each lane type allows it, and Lane's scripts by every type\
  Else one Lane stops what another of its type allows, or a role's Result or Mark, raising KR1.1.
- A Step's Mark held only by its own Lanes of reads_whole and keeps_items, laid only with keeps_steps\
  The Marks alone bound a Step, so only there does a Lane see its reads and Items, keeping KR1.1
  low.
- Each Mark checked by the guard at its script's call, which names the subagent\
  The script's environment names no subagent, so only the call's agent_id tells whose Step is due,
  keeping KR1.1 low.
- A Step's Items given by the plugin's adapter, from the role, the Step, and the run values\
  Only the plugin knows each Step's checklist, and Lane names no plugin, keeping KR1.1 low.
- Each event placed by `session_id` and `agent_id`, a Start tied at its Agent call's PostToolUse\
  Only this placing holds each call to its own Start, as [Claude Code's states](claude-code-states.md)
  shows, keeping KR1.1 low.
- The runs of several skills side by side, each held to its own routes\
  A person types another command while a subagent of the first runs, and leaving it unheld raises
  KR1.1.
- Each Result and Mark added by the guard at the PostToolUse of a run of Lane's scripts that gave 0\
  A Bash command carries no `agent_id`, so only the hook event ties each to its subagent, keeping
  KR1.1 low.
- The adapter naming the work a call picks up, from the words typed after the command\
  Only the adapter, run before the guard answers, separates a new request from a pick-up, keeping KR1.1
  low.
- Subagents in the background\
  A foreground subagent's PostToolUse comes only once it ends, so the guard couldn't hold its calls,
  raising KR1.1.
- The guard standing aside while another plugin's called skill runs\
  The other plugin's guard holds the main conversation there, and two guards would stop each other's
  moves, raising KR1.1.

## Data model

![Lane's data](images/data-model.svg)

- Step\
  One item under `## Steps` of a skill or a subagent, or of the file its body names.
- Lane\
  A rule of one lane type on one step, which the README calls a rule.
- Route\
  The moves of one skill after its start, a Result, a typed command, or another plugin's run it
  called.
- Laid\
  What Lane added to the plugin, kept in a form that a later Lane separates from the user's text.
- Approval\
  The caller's own act that approves one Proposal: a person's reply, or an AI's run of
  `lay.py write`.
- Start\
  One start or resume of a role, made due by a Route, that holds its text and its run values.
- Call\
  One tool call of a role, checked as it comes, and kept only as a Read that reads_whole needs.
- Item\
  One item of a Step's checklist, by the ID that the plugin's adapter gives.
- Mark\
  A role's report of a Step or an Item done, each Mark of Step 1 beginning a new pass.
- Run\
  One run of one skill in one conversation, with each prompt typed in it, until a route starts no
  more.
- Kept results\
  The results of a run that the user's plugin keeps in its own records.

Strategies:

- An append-only run record of only what no later payload gives again\
  Parallel hooks run at once, so a Run written whole loses another's line, raising KR1.1.
- The form of Lanes and Routes, in `lanes.json` and a Proposal, decided by the guard's code\
  A laid plugin runs without `lay.py`, so the laid copy alone decides the form, keeping KR1.1 low.

## Sequences

### S1: a proposal

```mermaid
sequenceDiagram
  actor U as user
  participant CC as Claude Code
  participant G as Lane's guard on up
  participant RS as run record
  participant UP as up
  participant L as lay.py
  participant P as proposal
  participant T as lane types
  participant ST as steps
  participant LS as laid set
  U->>CC: /lane:up <plugin>
  CC->>G: the skill's call, typed by a person
  G->>RS: adds the call of up's Run, by a person
  UP->>L: types
  L->>T: each type
  L-->>UP: the types, and the form of a Proposal
  UP->>L: steps <plugin>
  L->>ST: reads each Step
  L->>LS: reads the Laid
  L-->>UP: each Step without the text that the Laid names
  UP->>UP: writes the Lanes and the Routes (Proposal)
  loop until the Proposal can stand
    UP->>L: print (Proposal)
    L->>T: checks each Lane, and makes its sentence
    L->>ST: checks the Proposal against the plugin's files
    alt the Proposal can't stand
      L-->>UP: what's wrong
      UP->>UP: mends the Proposal
    else a file of the plugin can't carry it
      L-->>UP: what's wrong in the file
      UP-->>U: what to fix in their plugin, and stops
    end
  end
  L->>P: keeps the Proposal by its ID
  L-->>UP: the Routes, each Step as it'll read, and the ID
  CC->>G: the PostToolUse of lay.py print
  G->>RS: adds what it showed, with the Proposal's ID, to up's Run
  UP-->>U: what lay.py print showed, and asks for yes or a change
```

### S2: a person approves or asks a change

```mermaid
sequenceDiagram
  actor U as user, a person
  participant CC as Claude Code
  participant G as Lane's guard on up
  participant RS as run record
  participant T as lane types
  participant UP as up
  participant L as lay.py
  participant P as proposal
  participant ST as steps
  participant LS as laid set
  participant HL as hooks/lane/, in the plugin
  UP->>CC: ends its turn
  CC->>G: the stop, with its last message
  G->>T: checks the end by each Lane of up
  alt up didn't give what lay.py print showed, word for word
    G-->>UP: stops it, with what lay.py print showed
  end
  U->>CC: replies (Approval)
  CC->>G: the prompt
  G->>RS: adds the prompt, to up's Run
  alt a change
    UP->>ST: writes the change into its Step
    Note over U,ST: up proposes again, as S1 draws.
  else neither a change nor yes
    UP->>CC: result.py up left
    CC->>G: the PostToolUse, with no agent_id
    G->>RS: adds up's Result, which ends up's Run with no lay.py write
  else yes
    UP->>CC: runs lay.py write <plugin> <ID>
    CC->>G: the call
    G->>T: checks the Call by each Lane of the Run of up that showed that ID
    alt no person's prompt since that Run showed it
      G-->>UP: stops it: lay only after the person's reply
    else
      G-->>CC: lets it through
      UP->>L: write <plugin> <ID>
      L->>P: reads the Proposal by its ID
      L->>G: asks where up's Run stands
      G->>RS: reads the lines
      alt no such Proposal, its Run no longer waits, or the Steps changed
        L-->>UP: refused, with why
      else
        L->>ST: writes each Lane's sentence in place of the Laid's
        L->>LS: replaces Lane's hook entries, as the guard's code names them
        L->>HL: copies Lane's code
        L->>G: writes lanes.json through the guard's code
        L->>CC: claude plugin validate <plugin>
        alt it fails
          L->>ST: puts back each file it changed
          L-->>UP: what failed
        else it passes
          L-->>UP: each file written, and to type /reload-plugins
          UP->>CC: result.py up laid
          CC->>G: the PostToolUse, with no agent_id
          G->>RS: adds up's Result, which ends up's Run
          UP-->>U: what Lane wrote, and to type /reload-plugins
          U->>CC: /reload-plugins
        end
      end
    end
  end
```

### S3: an AI approves by its own act

```mermaid
sequenceDiagram
  actor A as user, an AI in the main conversation
  participant CC as Claude Code
  participant G as Lane's guard on up
  participant RS as run record
  participant ST as steps
  actor D as whoever gives the conversation its prompts
  A->>CC: calls up by the Skill tool
  CC->>G: the Skill tool call
  G->>RS: adds the call of up's Run, by an AI
  opt a person's Proposal waits for their reply
    G->>RS: keeps the person's Run, whose lay.py write still waits for their reply, as S2 draws
  end
  loop until the Proposal holds what it means
    Note over A,ST: up proposes, as S1 draws.
    opt it falls short
      A->>ST: writes the change into its Step
    end
  end
  A->>CC: runs lay.py write <plugin> <ID> (Approval)
  CC->>G: the call
  G-->>CC: lets it through
  Note over A,ST: lay.py lays the Proposal, as S2 draws.
  A->>D: asks for /reload-plugins
  D->>CC: /reload-plugins
```

### S4: proposed again after the steps or Lane change

```mermaid
sequenceDiagram
  actor U as user
  participant UP as up
  participant L as lay.py
  participant ST as steps
  participant LS as laid set
  U->>ST: changes the Steps, or updates Lane
  U->>UP: /lane:up <plugin>
  UP->>L: steps <plugin>
  L->>LS: reads the Laid by the guard's code in its hooks/lane/, the form of the Lane that laid it
  L->>ST: reads each Step
  loop each sentence that the Laid added
    alt the Step still holds it word for word
      L->>L: takes it out
    else the user changed it
      L->>L: keeps it as the user's words, and notes it
    end
  end
  L-->>UP: each Step that remains, with the notes
  Note over U,LS: up proposes, the caller approves, and lay.py lays with the newest code, as S1 to S3 draw.
```

### S5: a run in the order the user set

```mermaid
sequenceDiagram
  actor U as user
  participant CC as Claude Code
  participant M as the plugin's main conversation
  participant G as guard
  participant RS as run record
  participant A as adapter
  participant T as lane types
  participant PC as the plugin's command
  participant SA as the plugin's subagent
  U->>CC: a command of the plugin's skill
  CC->>G: the skill's call
  G->>RS: adds the call of that skill's Run, or picks it up, as S7 draws
  loop until a move of the Run starts no more
    opt lanes.json names an adapter of a start's text
      G->>A: asks for the text of each start due, with each Start that runs
      alt it gives one
        A-->>G: the text, and the run values
      else it gives none, as no work waits for that start
        A-->>G: why
        G->>G: leaves that start out of the moves due, with why in its place
      else it fails at the skill's call
        A-->>G: why
        G->>G: gives that start with why, and lets the call run
        Note over M,G: The skill's own steps may make what the adapter reads before its first start, so the guard asks again after each later call of the main conversation, and gives the start with its text once the adapter gives it.
      else it fails at any other move
        A-->>G: why
        G-->>M: why and who must fix it, in place of that start
      end
    end
    G-->>M: the moves due, each start with its text
    alt the main conversation starts or resumes a subagent
      M->>CC: the start, with its text
      CC->>G: the start
      G->>T: checks the start by the Lane of the skill's Routes, with the moves due
      alt a start due, with its text
        G->>RS: adds the Start
        G-->>CC: lets it through
        CC->>SA: starts it in the background
        CC->>G: the PostToolUse, with its agent_id
        G->>RS: adds the tie of the Start to that agent_id
        Note over M,G: The start stays due beside each Start of its role that runs, while the adapter gives it a text other than theirs, so the skill's steps may start the role side by side.
      else a resume, where the Routes open none
        G-->>CC: lets it through, and moves no Run
      else any other start
        G-->>M: stops it, with the moves due
      end
    else it calls another plugin's skill that a move names
      M->>CC: the Skill tool call
      CC->>G: the call
      G->>RS: adds it, so the Run stands aside
      Note over M,G: The guard checks none of the main conversation's calls until it makes the move after that call.
    else it makes any other call
      M->>CC: the call (Call)
      CC->>G: the call
      G->>T: checks the Call by each Lane of each Run's skill
      alt it breaks a Lane
        G-->>M: stops it, with each skill's Step sentence
      else
        G-->>CC: lets it through
      end
      Note over M,G: The skill's runs of step.py and item.py, its Reads, and its Marks go as S6 draws, with no agent_id.
    else it ends its turn, where a move waits for the person
      U->>CC: replies, or types the command the move waits for
      CC->>G: the prompt
      G->>RS: adds the command typed
    end
    opt the person types a command that a route goes after
      U->>CC: the command, such as a pause
      CC->>G: the prompt
      G->>RS: adds it, so that route's moves are due in place of those before
    end
    opt a subagent ends unheld, as TaskStop stops it
      CC->>G: its end
      G->>RS: adds the end, with no Result
      G-->>M: that it ended with no Result, and its start due again
    end
    opt a subagent ends, held as S6 draws
      CC->>G: its end, as it reaches the main conversation
      G->>RS: adds the end
      G-->>M: the Result, and the moves of its Route
    end
    opt the main conversation ends its turn
      CC->>G: the stop
      alt a move is due with its text, and no subagent of the Run runs
        G-->>M: stops it, with the moves due
      else
        G->>T: checks the end by each Lane of each Run's skill
        opt a Lane holds the end to a command of the plugin's
          T->>PC: runs it, with the Result filled in
          PC-->>T: its exit code
        end
        alt a Lane is broken
          G-->>M: stops it, with the Lane's sentence
        else
          G-->>CC: lets it stop
        end
      end
    end
  end
  G-->>M: start no more subagents, where the move after a Result starts no more
  M->>CC: result.py <skill> <result>
  CC->>G: the PostToolUse, with no agent_id
  G->>RS: adds the skill's Result, which ends the Run
```

### S6: a subagent held to its steps

```mermaid
sequenceDiagram
  participant SA as the plugin's subagent
  participant CC as Claude Code
  participant G as guard
  participant T as lane types
  participant A as adapter
  participant SP as step.py
  participant IP as item.py
  participant R as result.py
  participant RS as run record
  participant PC as the plugin's command
  loop each call the subagent makes
    SA->>CC: a tool call (Call)
    CC->>G: the call, with its agent_id
    G->>RS: reads the lines, for its Start, its Marks, and its Run
    alt a run of step.py <role> <n>
      alt Step n isn't due in the latest pass of its Start
        G-->>SA: stops it, with the Step due
      else
        opt a Lane of keeps_items lies on Step n
          G->>A: asks for the Step's Items, with the role, Step n, and the Start's run values
          A-->>G: each Item's ID
        end
        G->>T: checks the Mark by each Lane on Step n, with the Reads and Marks since the Step began
        alt the adapter fails
          G-->>SA: stops it, with why and who must fix it
        else a path a Lane of reads_whole names wasn't read whole, or an Item isn't marked
          G-->>SA: stops it, with the Lane's sentence and what the Step lacks
          SA->>SA: goes back to the Step
        else
          G-->>CC: lets it through
          SA->>SP: step.py <role> <n>
          SP-->>SA: exits 0
          CC->>G: the PostToolUse, with its agent_id
          G->>RS: adds the Mark of Step n, for that subagent's Start
        end
      end
    else a run of item.py <role> <id>
      G->>A: asks for the Items of the Step due, with the role and the Start's run values
      A-->>G: each Item's ID
      alt the adapter fails
        G-->>SA: stops it, with why and who must fix it
      else no Item of the Step due
        G-->>SA: stops it, with the Items left
      else
        G-->>CC: lets it through
        SA->>IP: item.py <role> <id>
        IP-->>SA: exits 0
        CC->>G: the PostToolUse, with its agent_id
        G->>RS: adds the Mark of the Item, for that subagent's Start
      end
    else any other call
      G->>T: checks the Call by each Lane of the role, with the Start's run values
      alt it keeps every Lane
        G-->>CC: lets it through
        opt a Read of a path that a Lane of reads_whole names
          CC->>G: the PostToolUse, with the lines it read
          G->>RS: adds the Read (Call), for that subagent's Start
        end
      else it breaks a Lane
        G-->>SA: stops it, with the Step's sentence and what it may do
        SA->>SA: goes back to the Step
      else it starts a role of the plugin
        G-->>SA: stops it, with the sentence of the Lane on its last Step
      else the guard can't check it
        G-->>SA: stops it, with why and who must fix it
      end
    end
  end
  SA->>R: result.py <role> <result>
  R->>G: asks where each Run stands
  alt a Result the role may give
    R-->>SA: exits 0
    CC->>G: the PostToolUse, with its agent_id
    G->>RS: adds the Result, for that subagent's Start
  else
    R-->>SA: refuses it, with the Results it may give
  end
  SA->>CC: ends
  CC->>G: the end
  G->>T: checks the end by each Lane of the role
  alt the Lane on its last Step finds no Result since its Start
    G-->>SA: stops the end, with that Lane's sentence
  else a Lane of keeps_steps finds a Step unmarked in the latest pass
    G-->>SA: stops the end, with that Lane's sentence and the Step due
  else
    opt a Lane holds the end to a command of the plugin's
      T->>PC: runs it, with the run values and the Result filled in
      PC-->>T: its exit code
    end
    alt a Lane is broken
      G-->>SA: stops the end, with the Lane's sentence
    else
      G-->>CC: lets it end
    end
  end
```

### S7: a run picked up

```mermaid
sequenceDiagram
  actor U as user
  participant CC as Claude Code
  participant G as guard
  participant RS as run record
  participant A as adapter
  participant M as the plugin's main conversation
  U->>CC: a command of the plugin's skill, after /compact or in a new conversation
  CC->>G: the skill's call, with the words typed after it
  alt lanes.json names an adapter of the plugin's records
    G->>A: asks for the Kept results, with those words
    alt it gives none, or results that reach a route that starts no more
      G->>RS: adds the call of a new Run
      G-->>M: the first start due
    else results that follow the Routes
      G->>RS: adds the call and each Result, where the record doesn't hold them
      G-->>M: where the run picks up, and the start due
      Note over G,M: A resume due of a role that this conversation never started is due as a start of it, as no subagent of it is here to resume.
    else results that don't follow them, or it fails
      G-->>U: stops the command, with why and who must fix it
    end
  else the record holds the Run, as after /compact
    G-->>M: the start due
  else
    G->>RS: adds the call of a new Run
    G-->>M: the first start due
  end
```

## Deployment

![Lane's deployment](images/deployment.svg)

Claude Code runs the laid guard on each hook event of the plugin, from the session's start or after
`/reload-plugins`.

Strategies:

- The person's `/reload-plugins`, which `lay.py write` asks for\
  Hooks load as a session starts or on that command alone, so building goes on unbroken, keeping
  KR1.2 short.
- Lane's code copied into the user's plugin\
  Whoever runs the plugin needs no Lane, and the guard runs the code Lane's tests ran, keeping KR1.1
  low.
- Lane's code on Python 3.9 and its standard library\
  Whoever runs the plugin installs nothing for Lane, keeping KR1.2 short.
- The proposal and the run record in the system's temporary folder\
  Lane writes nothing that the user's repository must keep or ignore, keeping KR1.2 short.
- The adapter and each command that a Lane runs in the hook event's `cwd`\
  A conversation that enters a worktree moves its `cwd` there, so they read the run's checkout,
  keeping KR1.1 low.
- Each lane's path read from the top of its worktree, beside the root\
  Roles may work in worktrees of their own, so a step's path names the file there, keeping KR1.1 low.

## Directory structure

`plugins/lane/` holds what Claude Code installs for the user. `dev/lane/` holds what only Lane's
developers use. `dev/tests/` holds what the developers of Lane and rn share for their tests. In the
user's plugin, Lane writes only the sentences in the steps and the files under `hooks/`. The
system's temporary folder holds what Lane keeps only for a run.

```text
plugins/lane/
├── skills/up/SKILL.md            /lane:up, which runs up's part
├── domain/up.md                  up's part
├── domain/lay/                   lay.py's code, a module for each of its decisions
├── scripts/lay.py                lay.py types, steps, print, and write
├── hooks/
│   ├── hooks.json                starts Lane's own guard on up
│   ├── lanes.json                the lanes and routes that hold up
│   └── lane/                     Lane's code, copied whole into each plugin
│       ├── hook.py               the guard
│       ├── result.py             the result script
│       ├── step.py               the script by which a role marks a Step done
│       ├── item.py               the script by which a role marks an Item of a Step done
│       └── domain/               the guard's code, the form of lanes.json, and lanes/, the lane types
├── CHANGELOG.md                  the changes in each version
└── README.md                     for Lane's users

dev/lane/
├── product-vision.md, architecture.md, images/
├── claude-code-states.md         each state of Claude Code that the guard meets, with its records
└── tests/                        the test cases, in unit/, properties/, prompts/, integration/, e2e/
    └── released/<version>/       the walkthrough's plugin as each released Lane laid it

dev/tests/
├── claude_code.py                the double of Claude Code, its `claude plugin validate` too
├── fresh_imports.py              keeps the plugins' modules out of a case's process, so each script imports the bench's copy
├── opus.py                       runs a prompt on Opus by `claude -p`, and the judge of its runs
├── repo_files.py                 git, the files a case writes, and a block of the README's text
├── scenario.py                   a key result measured by e2e.py until its mean holds, and a fresh home
├── recorded/                     the records of Claude Code that the double gives from
└── recorder/                     what records a state again, and compare.py

<the user's plugin>/
├── skills/<skill>/SKILL.md       a skill's Steps, with Lane's sentences
├── skills/<command>/SKILL.md     the Steps of a command that a skill's Route waits for or goes after
├── agents/<role>.md              a subagent's Steps, with Lane's sentences
├── <the file a body names>       the Steps of the skill or subagent that names it
└── hooks/
    ├── hooks.json                the guard's hook entries, beside the user's own
    ├── lanes.json                the Lanes, the Routes, the adapters, and the Laid
    ├── lane/                     the copy of Lane's code
    └── adapters/                 each adapter, the user's own

<system temporary folder>/
├── lane/<yyyymmdd>-<plugin>/     each Proposal, by its ID
└── <plugin>/<yyyymmdd>-<id>/     the run record of one conversation
```

Strategies:

- The lane types inside `hooks/lane/`, which `lay.py` imports\
  The sentence `lay.py print` shows and the check the guard runs come from one copy, keeping KR1.1
  low.

## Test strategy

Each test case lies in `dev/lane/tests/`, written as Given, When, and Then before anyone builds a part.
`dev/scripts/trace.py` checks that each names an element or a case one level up.

| Check | Test target | Kind | Exit criteria or measure |
|---|---|---|---|
| Lint | Parts | Quality | ruff: 0 findings. |
| Static analysis | Parts | Quality | pyrefly, and pylint's duplicate-code and cyclic-import checks: 0 findings. |
| Complexity analysis | Parts | Quality | complexipy and ruff: per function, McCabe 10, cognitive 15, 6 returns, 12 branches, 5 arguments, 50 statements at most. |
| Unit testing | Parts | Quality | pytest, with the double of Claude Code: every case passes. |
| Unit testing | Parts that hold a prompt | Benchmark | `claude -p` on Opus: each case's results over several runs, up's Lanes and Routes read by code. Runs per case: added until one more changes no case's count. |
| Code coverage | Parts | Quality | coverage: 100% statement (C0) and branch (C1) coverage. |
| Property-based testing | Parts | Quality | hypothesis: 0 counterexamples in reading Steps and Proposals, each lane type's check, and the guard's reading of events. |
| Mutation testing | Parts | Quality | cosmic-ray: 0 surviving mutants. |
| Data compatibility testing | Parts | Quality | pytest: the newest `lay.py` lays again each plugin in `dev/lane/tests/released/`, leaving no earlier sentence, none doubled. |
| Integration testing | Architecture | Quality | pytest, with the double of Claude Code: every case passes, each handoff giving the data the data model names. |
| Contract testing | Architecture | Quality | `dev/tests/recorder/compare.py` on each new Claude Code: each recorded state gives the double's events, with their fields in order. |
| Traceability | Architecture | Quality | `dev/scripts/trace.py`: every element tested, every case naming one level up, each rule's case failing broken. A review: 0 cases that miss what their element says. |
| Scenario testing | Product | Benchmark | `dev/scripts/e2e.py` on the walkthrough with S3 and S4, judged on Opus: key results KR1.1, then KR1.2, over several runs. Runs: added until one more moves no mean by a step. KR1.1 counts a role off its steps, a wrong stop or start, an early stop, or a step left unheld. |
| Installation testing | Product | Quality | `dev/scripts/e2e.py`: Lane installs by the README's commands in a fresh home's shell, and `/lane:up` answers. |
| Configuration testing | Product | Quality | CI's Tests on Python 3.9 and the newest Python: every case passes on each. |
| Conformance and compliance testing | Product | Quality | `claude plugin validate --strict` on each laid plugin: passes. |
