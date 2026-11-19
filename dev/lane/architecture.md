# Lane architecture

## User stories

- S1: the user wants to read what Lane would hold before any change, so that nothing holds their
  plugin unread.
- S2: the user wants to approve the proposal or ask a change, so that Lane lays only what they
  approved.
- S3: the user wants the checks to follow their changed steps, so that the checks match the steps
  as written.
- S4: the user wants a start off their order to get the moves due, so that the role notices.
- S5: the user wants a subagent that leaves a step to get that step, so that it notices at once.
- S6: the user wants a stopped run to go on where it stopped, so that its moves due still follow.

## Solution strategy

### Principles

Lane turns the user's steps into checks once, and judges each hook event by them.

- P1: the steps as the one source
  - P1.1: a proposal comes from the steps alone, and each change asked goes into the steps.
  - P1.2: each rule's sentence, its check, and the steps it suits come from one definition.
- P2: laid only as the user read it
  - P2.1: only a proposal shown is laid, while the steps read as shown.
  - P2.2: what Lane laid is replaced whole, and every other part of the plugin stays as it stands.
- P3: facts, never a role's claim
  - P3.1: a run moves only on a result that its role gave by a script, never by a reply.
  - P3.2: what no hook shows comes only from a script that the role runs.
- P4: the order the user set
  - P4.1: only the main conversation starts the roles, each as a start due.
  - P4.2: each stop gives the step's sentence and what to do, or why it can't check and who fixes
    it.
- P5: nothing lost on a stop
  - P5.1: each run's state comes from files, worked out by one code alone.
- P6: only the plugin's run
  - P6.1: calls are checked only within a run of the plugin's skill.
  - P6.2: the laid plugin needs only its own folder and what each machine running it has, naming
    no plugin.

### Data model

![Lane's data](images/data-model.svg)

- Step\
  One item under `## Steps` of a skill or a subagent, or of the file its body names.
- Lane\
  A rule of one lane type on one step, which the README calls a rule.
- Route\
  The moves of one skill after its start, a Result, or a typed command.
- Laid\
  What Lane added to the plugin, kept in a form that a later Lane separates from the user's text.
- Start\
  One start or resume of a role, that holds its text and its run values.
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

- An append-only run record of only what no later payload gives again. [P5.1]\
  Intent: hooks that run at once lose no line of one another's.
- The form of Lanes and Routes, in `lanes.json` and a Proposal, decided by the guard's code. [P6.2]\
  Intent: a laid plugin runs by its laid copy alone.

### Components

![Lane's components](images/components.svg)

- user (role)\
  Writes each step, reads the proposal, and approves it or asks a change.
- up (skill)\
  Proposes each step's lane type, each skill's routes, and each missing result's name from the steps.
- lay.py (script)\
  Checks a Proposal, shows how the steps read once laid, and lays it into the plugin.
- lane types (modules)\
  Give each rule's sentence, the steps it suits, what it allows, and its check of a call or an end.
- guard (hook script)\
  Places each hook event in its Run, and gives each start due and each stop.
- result.py (script)\
  Takes a result given as a command of its own, only where a Run lets its role give it.
- step.py (script)\
  Gives a Step's Mark as a command of its own, which the guard checks at its call.
- item.py (script)\
  Gives an Item's Mark as a command of its own, which the guard checks at its call.
- adapter (script)\
  Gives each start's text, a Step's Items, and kept results in Lane's form, and names what a call
  picks up.

Strategies:

- A proposal from the steps' sense, by up. [P1.1]\
  Intent: a step that names no subagent still gets its routes.
- Each skill as one role whose steps lie in several files. [S4]\
  Intent: a command's steps hold, though no hook event marks where they end.
- `lay.py print` refusing a Proposal that the plugin's files can't carry. [P2.1]\
  Intent: no file of the plugin that can't carry the Proposal breaks a run.
- An end held to the plugin's own command, which Lane runs. [S5]\
  Intent: a role that leaves its steps still meets the check that only the plugin knows.
- A sentence left out of a step that already says it. [P1.2]\
  Intent: the role reads each rule once, and keeps its attention on its step.
- Each Mark checked by the guard at its script's call, which names the subagent. [P3.2]\
  Intent: each Mark counts for the subagent whose Step is due.
- A Step's Items given by the plugin's adapter, from the role, the Step, and the run values. [P6.2]\
  Intent: each Step's checklist comes from the plugin, which alone knows it.
- Each event placed by `session_id` and `agent_id`, a Start tied at its Agent call's PostToolUse.
  [S5]\
  Intent: each call is held to its own Start, as [Claude Code's states](claude-code-states.md)
  shows.
- Each Result and Mark added by the guard at the PostToolUse of each run of Lane's scripts that
  exits 0. [P3.1]\
  Intent: each Result and Mark counts for the subagent that gave it.
- The adapter naming the work a call picks up, from the words typed after the command. [S6]\
  Intent: a new request is told apart from a pick-up before the guard answers.
- Subagents in the background. [S5]\
  Intent: the guard holds each call of a subagent as it comes.

### Sequences

#### S1: a proposal

```mermaid
sequenceDiagram
  actor U as user
  participant UP as up
  participant L as lay.py
  participant P as proposal
  participant T as lane types
  participant ST as steps
  participant LS as laid set
  U->>UP: /lane:up <plugin> [S1]
  UP->>L: types [P1.2]
  L->>T: each type [P1.2]
  L-->>UP: the types, and the form of a Proposal [P1.2]
  UP->>L: steps <plugin> [P1.1]
  L->>ST: reads each Step (Step) [P1.1]
  L->>LS: reads the Laid (Laid) [P1.1]
  L-->>UP: each Step without the text that the Laid names (Step) [P1.1]
  loop until the Proposal of the Lanes and the Routes that up writes can stand [S1]
    UP->>L: print (Lane, Route) [S1]
    L->>T: checks each Lane, and makes its sentence (Lane) [P1.2]
    L->>ST: checks the Proposal against the plugin's files (Step) [P2.1]
    alt the Proposal can't stand [P2.1]
      L-->>UP: what's wrong, which up mends in the Proposal [P4.2]
    else a file of the plugin can't carry it [P2.1]
      L-->>UP: what's wrong in the file [P4.2]
      UP-->>U: what to fix in their plugin, and stops [P4.2]
    end
  end
  L->>P: keeps the Proposal by its ID, with the Steps as shown (Step) [P2.1]
  L-->>UP: the Routes, each Step as it'll read, and the ID (Route, Step) [S1]
  UP-->>U: what lay.py print showed, and asks for yes or a change [S1]
```

#### S2: the user approves or asks a change

```mermaid
sequenceDiagram
  actor U as user, a person or an AI
  participant CC as Claude Code
  participant UP as up
  participant L as lay.py
  participant P as proposal
  participant ST as steps
  participant LS as laid set
  participant HL as hooks/lane/, in the plugin
  alt a change [S2]
    U->>UP: the change [S2]
    UP->>ST: writes the change into its Step (Step) [P1.1]
    Note over U,ST: up proposes again, as S1 draws.
  else yes [S2]
    U->>UP: yes [S2]
    UP->>L: write <plugin> <ID> [S2]
    L->>P: reads the Proposal by its ID [P2.1]
    alt no such Proposal, or the Steps changed since it was shown [P2.1]
      L-->>UP: refused, with why [P4.2]
      Note over U,ST: up proposes again, as S1 draws.
    else [S2]
      L->>ST: writes each Lane's sentence in place of the Laid's (Lane, Laid) [P2.2]
      L->>LS: replaces Lane's hook entries, as the guard's code names them (Laid) [P2.2]
      L->>HL: copies Lane's code [P6.2]
      L->>LS: writes lanes.json through the guard's code (Lane, Route, Laid) [P6.2]
      L->>CC: claude plugin validate <plugin> [S2]
      alt it fails [P2.2]
        L->>ST: puts back each file it changed [P2.2]
        L-->>UP: what failed [P4.2]
      else it passes [S2]
        L-->>UP: each file written, and to type /reload-plugins [S2]
        UP-->>U: what Lane wrote, and to type /reload-plugins [S2]
      end
    end
  end
```

#### S3: proposed again after the steps or Lane change

```mermaid
sequenceDiagram
  actor U as user
  participant UP as up
  participant L as lay.py
  participant ST as steps
  participant LS as laid set
  U->>ST: changes the Steps, or updates Lane [S3]
  U->>UP: /lane:up <plugin> [S3]
  UP->>L: steps <plugin> [P1.1]
  L->>LS: reads the Laid (Laid) [P1.1]
  L->>ST: reads each Step (Step) [P1.1]
  L-->>UP: each Step without each sentence of the Laid that it still holds word for word, and with a note on each that the user changed, kept as the user's words (Step) [S3]
  Note over U,LS: up proposes, the user approves, and lay.py lays with the newest code, as S1 and S2 draw.
```

#### S4: a run in the order the user set

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
  U->>CC: a command of the plugin's skill [S4]
  CC->>G: the skill's call [P6.1]
  G->>RS: adds the call of that skill's Run, or picks it up, as S6 draws (Run) [P5.1]
  loop until a move of the Run starts no more [S4]
    opt lanes.json names an adapter of a start's text [S4]
      G->>A: asks for the text of each start due, with each Start that runs (Start) [S4]
      alt it gives one [S4]
        A-->>G: the text, and the run values (Start) [S4]
      else it gives none, as no work waits for that start, which the guard leaves out of the moves due, with why in its place [S4]
        A-->>G: why [P4.2]
      else it fails at the skill's call, where the guard gives that start with why, and lets the call run [S4]
        A-->>G: why [P4.2]
      else it fails at any other move [P4.2]
        A-->>G: why [P4.2]
        G-->>M: why and who must fix it, in place of that start [P4.2]
      end
    end
    G-->>M: the moves due, each start with its text (Route, Start) [P4.1]
    alt the main conversation starts or resumes a subagent [P4.1]
      M->>CC: the start, with its text (Start) [P4.1]
      CC->>G: the start (Start) [P4.1]
      G->>T: checks the start by the Lane of the skill's Routes, with the moves due (Lane, Route) [P4.1]
      alt a start due, with its text [P4.1]
        G->>RS: adds the Start (Start) [P5.1]
        G-->>CC: lets it through [P4.1]
        alt the call runs [S4]
          CC->>SA: starts it in the background [S5]
          CC->>G: the PostToolUse, with its agent_id [S5]
          opt a resume whose message is queued, as its subagent still runs [S4]
            G->>RS: holds the Start back until that subagent's SubagentStart, so each end before it is the running Start's (Start) [S4]
          end
          G->>RS: adds the tie of the Start to that agent_id (Start) [S5]
        else the call fails, such as naming no subagent type, or a permission rule denies it [S4]
          CC->>G: the PostToolUseFailure, with the call's tool_use_id [S4]
          G->>RS: drops the Start, so its start is due again (Start) [S4]
        end
      else a resume, where the Routes open none [S4]
        G->>RS: adds the Start again, for its subagent runs again (Start) [S4]
        G-->>CC: lets it through, and moves no Run [S4]
      else a start of a subagent not the plugin's [P6.1]
        G-->>CC: lets it through, and adds no Start [P6.1]
      else any other start [P4.1]
        G-->>M: stops it, with the moves due (Route) [P4.2]
      end
    else it makes any other call [S4]
      M->>CC: the call (Call) [S4]
      CC->>G: the call (Call) [S4]
      G->>T: checks the Call by each Lane of each Run's skill (Call, Lane) [S4]
      alt it breaks a Lane [S4]
        G-->>M: stops it, with each skill's Step sentence (Step) [P4.2]
      else [S4]
        G-->>CC: lets it through [S4]
      end
      Note over M,G: The skill's runs of step.py and item.py, its Reads, and its Marks go as S5 draws, with no agent_id.
    else it ends its turn, where a move waits for the person [S4]
      U->>CC: replies, or types the command the move waits for [S4]
      CC->>G: the prompt [S4]
      G->>RS: adds the command typed (Run) [P5.1]
    end
    opt the person types a command that a route goes after [S4]
      U->>CC: the command, such as a pause [S4]
      CC->>G: the prompt [S4]
      G->>RS: adds it, so that route's moves are due in place of those before (Run) [S4]
    end
    opt a subagent ends unheld, as TaskStop stops it [S4]
      CC->>G: its end [S4]
      G->>RS: adds the end, with no Result (Start) [S4]
      G-->>M: that it ended with no Result, and its start due again (Start) [S4]
    end
    opt a subagent ends, held as S5 draws [S4]
      CC->>G: its end, as it reaches the main conversation, with the call it ends [S4]
      G->>RS: adds the end, of the Start of that call and each before it (Start) [S4]
      G-->>M: the Result, and the moves of its Route (Route) [P3.1]
    end
    opt the main conversation ends its turn [S4]
      CC->>G: the stop [S4]
      G->>RS: drops each Start still untied, as another plugin's hook stopped its call with no event (Start) [S4]
      alt a move is due with its text, and no subagent of the Run runs [P4.1]
        G-->>M: stops it, with the moves due (Route) [P4.2]
      else the move due starts no more, and no subagent of the Run runs [P4.1]
        G-->>M: stops it, with the sentence of the Lane on the skill's last Step (Lane) [P4.2]
      else [S4]
        G->>T: checks the end by each Lane of each Run's skill (Lane) [S4]
        opt a Lane holds the end to a command of the plugin's [S4]
          T->>PC: runs it, with the Result filled in [S4]
          PC-->>T: its exit code [S4]
        end
        alt a Lane is broken [S4]
          G-->>M: stops it, with the Lane's sentence (Lane) [P4.2]
        else [S4]
          G-->>CC: lets it stop [S4]
        end
      end
    end
  end
  G-->>M: start no more subagents, where the move after a Result starts no more (Route) [S4]
  M->>CC: result.py <skill> <result> [P3.1]
  alt a Lane of keeps_steps on the skill finds a Step unmarked in the latest pass [P3.1]
    CC-->>M: result.py refuses it, with that Lane's sentence and the Step due (Lane, Step) [P4.2]
  else [P3.1]
    CC->>G: the PostToolUse, with no agent_id [P3.1]
    G->>RS: adds the skill's Result, which ends the Run (Run) [P5.1]
  end
```

Strategies:

- A start judged by the Lane of the Routes, with the adapter of a start's text. [P4.1]\
  Intent: only a start due goes through, and any other start of a role gets the moves due.
- The adapter of a start's text failing at the skill's call, asked again after each later call.
  [S4]\
  Intent: a right move goes on while the skill's own steps make what the adapter reads.
- A start due beside each Start of its role that runs, while the adapter gives another text. [S4]\
  Intent: the skill's steps start one role for several pieces of work at once.
- A resume let through where the Routes open none, moving no Run, its Start running again. [S4]\
  Intent: a resume to answer leaves the order as it stands.
- A start of a subagent not the plugin's let through with no Start. [P6.1]\
  Intent: a helper, such as Explore, runs unstopped.
- The main conversation's call judged by each Lane of each Run's skill. [S4]\
  Intent: each skill's Steps hold while the person types another command as a subagent of the
  first runs.
- A turn's end stopped by a move due while no subagent runs, before any Lane. [P4.1]\
  Intent: the end keeps the order, and a stop that starts no more names the skill's result script.
- A typed command that a Route goes after, its moves due in place of those before. [S4]\
  Intent: the person's pause or approval changes the order.
- An end that ends the Start of the call it names, and each Start of its subagent before it. [S4]\
  Intent: a resume's Result counts, though it comes before the end of the pass before it.
- A Start dropped at its call's PostToolUseFailure, or untied at the turn's end. [S4]\
  Intent: a call that never ran leaves no Run waiting for good.
- A resume queued to a running subagent, its Start held back until that subagent's SubagentStart.
  [S4]\
  Intent: the end of the pass before the resume counts for the Start that runs.
- A subagent that ends with no Result, its start due again. [S4]\
  Intent: a run goes on after TaskStop ends a subagent outside its steps.
- The skill's Result refused by `result.py` while keeps_steps finds a Step unmarked. [P3.1]\
  Intent: a Step left while a turn waits on a subagent shows at the Result.

#### S5: a subagent held to its steps

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
  loop each call the subagent makes [S5]
    SA->>CC: a tool call (Call) [S5]
    CC->>G: the call, with its agent_id (Call) [S5]
    G->>RS: reads the lines, for its Start, its Marks, and its Run (Start, Mark, Run) [P5.1]
    alt a run of step.py <role> <n> [P3.2]
      alt Step n isn't due in the latest pass of its Start [P3.2]
        G-->>SA: stops it, with the Step due (Step) [P4.2]
      else [P3.2]
        opt a Lane of keeps_items lies on Step n [P3.2]
          G->>A: asks for the Step's Items, with the role, Step n, and the Start's run values (Item) [P6.2]
          A-->>G: each Item's ID (Item) [P6.2]
        end
        G->>T: checks the Mark by each Lane on Step n, with the Reads and Marks since the Step began (Mark, Lane) [P3.2]
        alt the adapter fails [P4.2]
          G-->>SA: stops it, with why and who must fix it [P4.2]
        else a path a Lane of reads_whole names wasn't read whole, or an Item isn't marked [P3.2]
          G-->>SA: stops it, with the Lane's sentence and what the Step lacks (Lane) [P4.2]
        else [P3.2]
          G-->>CC: lets it through [P3.2]
          SA->>SP: step.py <role> <n> [P3.2]
          SP-->>SA: exits 0 [P3.2]
          CC->>G: the PostToolUse, with its agent_id [P3.2]
          G->>RS: adds the Mark of Step n, for that subagent's Start (Mark) [P5.1]
        end
      end
    else a run of item.py <role> <id> [P3.2]
      G->>A: asks for the Items of the Step due, with the role and the Start's run values (Item) [P6.2]
      A-->>G: each Item's ID (Item) [P6.2]
      alt the adapter fails [P4.2]
        G-->>SA: stops it, with why and who must fix it [P4.2]
      else no Item of the Step due [P3.2]
        G-->>SA: stops it, with the Items left (Item) [P4.2]
      else [P3.2]
        G-->>CC: lets it through [P3.2]
        SA->>IP: item.py <role> <id> [P3.2]
        IP-->>SA: exits 0 [P3.2]
        CC->>G: the PostToolUse, with its agent_id [P3.2]
        G->>RS: adds the Mark of the Item, for that subagent's Start (Mark) [P5.1]
      end
    else any other call [S5]
      G->>T: checks the Call by each Lane of the role, with the Start's run values (Call, Lane) [S5]
      alt it keeps every Lane [S5]
        G-->>CC: lets it through [S5]
        opt a Read of a path that a Lane of reads_whole names [P3.2]
          CC->>G: the PostToolUse, with the lines it read [P3.2]
          G->>RS: adds the Read (Call) [P5.1]
        end
      else it breaks a Lane [S5]
        G-->>SA: stops it, with the Step's sentence and what it may do (Step) [P4.2]
      else it starts a role of the plugin [P4.1]
        G-->>SA: stops it, with the sentence of the Lane on its last Step (Lane) [P4.2]
      else the guard can't check it [P4.2]
        G-->>SA: stops it, with why and who must fix it [P4.2]
      end
    end
  end
  SA->>R: result.py <role> <result> [P3.1]
  R->>G: asks where each Run stands (Run) [P5.1]
  alt a Result the role may give [P3.1]
    R-->>SA: exits 0 [P3.1]
    CC->>G: the PostToolUse, with its agent_id [P3.1]
    G->>RS: adds the Result, for that subagent's Start (Start) [P5.1]
  else [P3.1]
    R-->>SA: refuses it, with the Results it may give [P4.2]
  end
  SA->>CC: ends [S5]
  CC->>G: the end [S5]
  G->>T: checks the end by each Lane of the role (Lane) [S5]
  alt the Lane on its last Step finds no Result since its Start [P3.1]
    G-->>SA: stops the end, with that Lane's sentence (Lane) [P4.2]
  else a Lane of keeps_steps finds a Step unmarked in the latest pass [S5]
    G-->>SA: stops the end, with that Lane's sentence and the Step due (Lane, Step) [P4.2]
  else [S5]
    opt a Lane holds the end to a command of the plugin's [S5]
      T->>PC: runs it, with the run values and the Result filled in [S5]
      PC-->>T: its exit code [S5]
    end
    alt a Lane is broken [S5]
      G-->>SA: stops the end, with the Lane's sentence (Lane) [P4.2]
    else [S5]
      G-->>CC: lets it end [S5]
    end
  end
```

Strategies:

- A call kept where one Lane of each lane type allows it, and Lane's scripts by every type. [S5]\
  Intent: no Lane stops what another of its type allows, or a role's Result or Mark.
- A Step's Mark checked for the Step due, then by its Lanes of reads_whole and keeps_items. [P3.2]\
  Intent: a Lane sees a Step's Reads and Items within the bounds that the Marks set.
- An Item's Mark checked by keeps_items against the adapter's Items for the Step due. [P6.2]\
  Intent: each Item marked is one of the Step's checklist, which only the plugin knows.
- A subagent's end checked by ends_by_result first, then keeps_steps, then ends_checked. [P4.2]\
  Intent: a stop names the step left, as the plugin's command runs only once the Result and each
  Step hold.
- A subagent's start of a role stopped by the Lane on its last Step. [P4.1]\
  Intent: the subagent gets its own last step back.

#### S6: a run picked up

```mermaid
sequenceDiagram
  actor U as user
  participant CC as Claude Code
  participant G as guard
  participant RS as run record
  participant A as adapter
  participant M as the plugin's main conversation
  U->>CC: a command of the plugin's skill, after /compact or in a new conversation [S6]
  CC->>G: the skill's call, with the words typed after it [S6]
  alt the record holds the Run, as after /compact [P5.1]
    G-->>M: the start due (Start) [S6]
  else lanes.json names an adapter of the plugin's records [S6]
    G->>A: asks for the Kept results, with those words (Kept results) [P5.1]
    alt it gives none, or results that reach a route that starts no more [S6]
      G->>RS: adds the call of a new Run (Run) [P5.1]
      G-->>M: the first start due (Start) [S6]
    else results that follow the Routes [S6]
      G->>RS: adds the call and each Result (Run) [P5.1]
      G-->>M: where the run picks up, and the start due (Start) [S6]
    else results that don't follow them, or it fails [P4.2]
      G-->>U: stops the command, with why and who must fix it [P4.2]
    end
  else [S6]
    G->>RS: adds the call of a new Run (Run) [P5.1]
    G-->>M: the first start due (Start) [S6]
  end
```

Strategies:

- The skill's call placed by the run record first, then by the adapter of the plugin's records.
  [P5.1]\
  Intent: a run goes on after `/compact`, and in a new conversation.
- A resume due of a role that this conversation never started, given as its start. [S6]\
  Intent: no right start is stopped for a subagent that isn't here to resume.

### Deployment

![Lane's deployment](images/deployment.svg)

Claude Code runs the laid guard on each hook event of the plugin, from the session's start or after
`/reload-plugins`.

Strategies:

- The person's `/reload-plugins`, which `lay.py write` asks for. [S2]\
  Intent: the checks judge from the next prompt.
- Lane's code copied into the user's plugin. [P6.2]\
  Intent: whoever runs the plugin needs no Lane, and the guard runs the code that Lane's tests ran.
- Lane's code on Python 3.9 and its standard library. [P6.2]\
  Intent: the guard, started anew on each hook event, answers fast.
- The adapter and each command that a Lane runs in the hook event's `cwd`. [S4]\
  Intent: each reads the run's checkout, in a worktree too.
- Each lane's path read from the top of its worktree, beside the root. [S5]\
  Intent: a step's path names the file in a role's own worktree.

### Directory structure

```text
plugins/lane/                     what Claude Code installs for the user
├── skills/up/SKILL.md            /lane:up, which runs up's part
├── domain/up.md                  up's part
├── domain/lay/                   lay.py's code, a module for each of its decisions
├── scripts/lay.py                lay.py types, steps, print, and write
├── hooks/lane/                   Lane's code, copied whole into each plugin
│   ├── hook.py                   the guard
│   ├── result.py                 the result script
│   ├── step.py                   the script by which a role marks a Step done
│   ├── item.py                   the script by which a role marks an Item of a Step done
│   └── domain/                   the guard's code, the form of lanes.json, and lanes/, the lane types
├── CHANGELOG.md                  the changes in each version
└── README.md                     for Lane's users

dev/lane/                         what only Lane's developers use
├── claude-code-states.md         each state of Claude Code that the guard meets, with its records
└── tests/                        the test cases, from unit to integration

dev/tests/                        what the developers of Lane and rn share for their tests
├── claude_code.py                the double of Claude Code, its `claude plugin validate` too
├── recorded/                     the records of Claude Code that the double gives from
└── recorder/                     what records a state again, and compare.py

<the user's plugin>/              what Lane writes into, beside the user's own
├── skills/<skill>/SKILL.md       a skill's Steps, with Lane's sentences
├── skills/<command>/SKILL.md     the Steps of a command that a skill's Route waits for or goes after
├── agents/<role>.md              a subagent's Steps, with Lane's sentences
├── <the file a body names>       the Steps of the skill or subagent that names it
└── hooks/
    ├── hooks.json                the guard's hook entries, beside the user's own
    ├── lanes.json                the Lanes, the Routes, the adapters, and the Laid
    ├── lane/                     the copy of Lane's code
    └── adapters/                 each adapter, the user's own

<system temporary folder>/        what Lane keeps only for a run
├── lane/<yyyymmdd>-<plugin>/     each Proposal, by its ID
└── <plugin>/<yyyymmdd>-<id>/     the run record of one conversation
```

Strategies:

- In the user's plugin, only the sentences in the steps and the files under `hooks/` written by
  Lane. [P2.2]\
  Intent: every other part of the plugin stays the user's.
- The lane types inside `hooks/lane/`, which `lay.py` imports. [P1.2]\
  Intent: the sentence that `lay.py print` shows and the check that the guard runs come from one
  copy.

## Test strategy

| Check | Test target | Kind | Exit criteria or measure |
|---|---|---|---|
| Lint | Parts | Quality | 0 findings. |
| Static analysis | Parts | Quality | 0 findings of mismatched types, copied code, or import cycles. |
| Complexity analysis | Parts | Quality | Per function, McCabe 10, cognitive 15, 6 returns, 12 branches, 5 arguments, 50 statements at most. |
| Unit testing | Parts | Quality | Every case passes. |
| Unit testing | Parts that hold a prompt | Benchmark | up's Proposal for each case's steps, each case's results over runs added until one more changes no case's count. |
| Code coverage | Parts | Quality | 100% statement (C0) and branch (C1) coverage. |
| Property-based testing | Parts | Quality | 0 counterexamples in reading Steps and Proposals, each lane type's check, and the guard's reading of events. |
| Mutation testing | Parts | Quality | 0 surviving mutants. |
| Integration testing | Architecture | Quality | Every case passes, each handoff giving its data, with one case for each combination that a sequence's Strategies name. |
| Integration testing | Architecture | Benchmark | KR1.1: the share of the guard's answers that the cases hold right. |
| Contract testing | Architecture | Quality | On each new Claude Code, each recorded state gives the double's events, with their fields in order. |
| Traceability | Architecture | Quality | Every element and every combination tested, every case naming one level up, and each principle's case failing broken. |
| Configuration testing | Product | Quality | Every case passes on Python 3.9 and on the newest Python. |
| Conformance and compliance testing | Product | Quality | Claude Code's strict check of each laid plugin passes. |
| Performance testing | Architecture | Benchmark | KR1.2: each hook event's time to the guard's answer. |
