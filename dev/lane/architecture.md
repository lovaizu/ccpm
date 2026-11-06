# Lane architecture

This document says how Lane is built to give [its product vision](product-vision.md). The user
writes the rules of their plugin's steps and its routes in a proposal, a JSON file. A rule is a
sentence in a step that a subagent must keep. A route names the subagent that starts next after
another ends with a given result, a word such as `more`. `lay.py`, Lane's command, shows each step
as it will read. Once the user approves, it lays into their plugin each rule's sentence in its step
and one check script, the guard, with the result script beside it. On a run, Claude Code runs the
guard on each hook event of the plugin. The guard stops each call of a subagent that breaks a rule,
and shows the subagent the sentence of its step. The routes start from one skill of the plugin,
which runs in the main conversation. A run lasts from the call of that skill to the route that
starts no more. Through a run, the guard also holds the main conversation to the routes. It tells
the first start as the run begins, and each next start as a subagent's end reaches the
conversation, from the result that the subagent gave by running the result script. It stops any
other start, and keeps the conversation going while a start is due.

Lane's code and its user docs, [the lanes](../../plugins/lane/docs/lanes.md) and
[the routes](../../plugins/lane/docs/routes.md), call a rule a lane.

## Principles

Lane builds on these principles of
[the plugin best practice](../plugin-best-practice.md#principles):

- [What a machine can see of the work](../plugin-best-practice.md#what-a-machine-can-see-of-the-work)
- [No check passes what it did not check](../plugin-best-practice.md#no-check-passes-what-it-did-not-check)
- [The guard tells each role its steps again](../plugin-best-practice.md#the-guard-tells-each-role-its-steps-again)
- [Where a plugin writes its files](../plugin-best-practice.md#where-a-plugin-writes-its-files)
- [Asking for what lies outside the work](../plugin-best-practice.md#asking-for-what-lies-outside-the-work),
  in what the guard tells a subagent about a fault
- [The caller approves what is theirs](../plugin-best-practice.md#the-caller-approves-what-is-theirs)
- [Python 3.9 and the standard library](../plugin-best-practice.md#python-39-and-the-standard-library)
- [Code kept once](../plugin-best-practice.md#code-kept-once)

Lane takes none of the principles for a plugin with an orchestrator and roles. It does not take
[An entry points to its part](../plugin-best-practice.md#an-entry-points-to-its-part),
[Languages](../plugin-best-practice.md#languages) or
[Learning from each run](../plugin-best-practice.md#learning-from-each-run) either. Lane has no
role, skill or agent of its own, and it talks with no person: the user runs `lay.py` themselves,
and the guard runs inside the user's plugin. Lane departs from
[The core apart from Claude Code](../plugin-best-practice.md#the-core-apart-from-claude-code) in
where its core lies, as [Directory structure](#directory-structure) says.

Lane adds these.

### The check shows the step again

When the guard stops a tool call or an end, it tells the subagent or the main conversation the
sentence of the step that the call breaks, headed by the plugin's name.

*Why*: a role whose call is only refused looks for another way, which KR1.1 counts as gone wrong.
A role that meets the sentence of its own step goes back to the step.

### One wording for the step and the check

`lanes/` alone makes the sentence of a rule, both for the step that `lay.py` writes and for the
message that the guard gives. Beside each wording, it keeps each earlier wording that Lane laid.
`lay.py write` and `lay.py up` put a sentence that a step says in an earlier wording in the current
one, and leave every other word of the step as it was.

*Why*: the role then meets the same words in its step and in each stop, and no change to one place
can make the two differ (KR1.1). The guard holds a step to the current wording. A plugin laid
before would otherwise be stopped on every call once Lane changed a wording. Only a wording that
Lane laid counts as an earlier one, so the words the user wrote stay as they are.

### What was approved is what runs

`lay.py write` lays only a proposal that `lay.py print` would show as it is. The guard takes its
rules and routes only from what `lay.py write` wrote, and holds them to the checks that
`lay.py print` makes. Where they no longer pass those checks, it stops each call they are about, as
a call that cannot be checked.

*Why*: the user approves their rules and routes, as
[The caller approves what is theirs](../plugin-best-practice.md#the-caller-approves-what-is-theirs)
says. A rule copied or edited by hand would be one that no one approved, and could stop a move the
user's steps allow (KR1.1).

### Lane knows no plugin

Each type of rule is one check for every plugin, and the routes are one way of telling the next
start for every plugin. What differs between plugins reaches the guard only in three ways: as a
rule's values, as a value given for a run, or through an adapter. An adapter is the user's script
that turns their plugin's own text format into Lane's. No line of Lane names another plugin.

*Why*: the user then writes no check and no code for the order. Where Lane cannot hold a step or
the order, the user writes their own, which KR1.1 counts as gone wrong. A new text format needs an
adapter, not a new type of rule.

### The check judges only what Claude Code documents

The guard judges a role only from the fields of the hook input that Claude Code documents, and from
the runs of the result script. It never judges from what a role writes about its work, from a shell
command taken apart, or from Claude Code's record of a session.

*Why*: an AI that says it kept a step may not have kept it. A reading of a shell command misses the
forms that no one foresaw. Claude Code does not document its record, so a reading of the record
breaks when Claude Code changes it. Each of these readings would let a break through, or stop a
call that the rules allow (KR1.1).

### A call that cannot be checked is stopped

When the guard cannot check a tool call or an end, it stops it and says why. It tells a fault of the
plugin or of Claude Code to the role and to whoever runs the plugin, with who must fix it.

*Why*: a call let through unchecked could be the break that the rule is there to stop, as
[No check passes what it did not check](../plugin-best-practice.md#no-check-passes-what-it-did-not-check)
says (KR1.1). The role can mend its own call, but only whoever runs the plugin can have a fault
fixed.

### Claude Code's own means first

Where Claude Code has a documented means for what a rule needs, the guard uses that means and builds
nothing beside it.

*Why*: a means of Lane's own reads again what Claude Code already settles, and drifts from it
(KR1.1). For example, Claude Code's permission prompt puts to the person a command that a rule holds
for approval. A search of the person's messages for a word of approval could only guess at the
answer.

### The plugin needs nothing from Lane

The guard and the result script lie and run in the user's plugin, never in Lane.

*Why*: whoever runs the user's plugin did not choose Lane. A plugin that needed Lane installed would
run without its checks wherever Lane is missing (KR1.1).

### The main conversation is held only while its run lasts

The guard holds the main conversation from the call of the skill the routes name until a route
starts no more. There it checks only the starts of subagents, a message that resumes one, and the
end of a turn.

*Why*: the same conversation holds the user's own work, outside the run and beside it. A stop of
that work is a move the steps allow, stopped, which KR1.1 counts as gone wrong.

## User stories

- **S1**: As the user, I want to run `lay.py print` on my proposal, and see each step as it will
  read, or what is wrong. Carries the walkthrough's two rules for `writer` and its routes, and the
  steps shown as they will read.
- **S2**: As the user, I want to run `lay.py write` on the proposal I approved, and find the
  sentences in my steps and the guard and the result script in my plugin. Carries the walkthrough's
  `lay.py write`.
- **S3**: As the user, I want to run my plugin, by typing its skill's command or by an AI calling
  the skill, and have its subagents keep their rules and the main conversation start them in the
  order of the routes. Carries the walkthrough's run: `/changelog:write` typed, `writer` stopped as
  it tries `git commit` and shown its step's sentence, `reviewer` giving `more`, `writer` again,
  `reviewer` giving `good`, and the run's end. It also carries, as branches, a command held for the
  person's approval, a value given for each run, a result, runs at once, a subagent or skill of a
  dependency, and a subagent resumed to give a later result. Without a branch, the user would hold
  that step or order with code of their own (KR1.1).
- **S4**: As the user, I want to run `lay.py up` on my plugin after Lane is updated, and find my
  plugin's copy of Lane's code at Lane's version, and each sentence in my steps in Lane's current
  wording. Off the walkthrough, serves KR1.1: a fault fixed in Lane reaches a plugin's guard only
  this way, and a step left in an earlier wording would be stopped on every call.

The subagents and the main conversation are not users of Lane. Each is the user's plugin, held for
the user.

## Components

![Lane's components](images/components.svg)

What each decides alone:

- **user**: what is theirs: the rules, the routes and each adapter, and whether to approve the
  steps as they will read.
- **lay.py**: what is written where in the user's plugin. No other component writes there.
  `lay.py up` brings the plugin's copy of Lane's code, its hook entries and the sentences in its
  steps to Lane's version.
- **proposal.py**: whether a proposal can be laid. It holds the proposal to the JSON Schema of
  [the proposal](../../plugins/lane/docs/lanes.md#the-proposal), and checks it against the plugin's
  files.
- **lanes/**: for each type of rule, its sentence, what it is given and what breaks it. Each type
  lies in a module of its own. It also decides whether a rule can be laid at all, a check that
  `proposal.py` makes before laying and `guard.py` makes again on the rules laid.
- **hook.py**: how Claude Code's hook input is read and how the guard's answer is written. No other
  component knows that form. `hook.py` hands on the events of a subagent with rules, and the main
  conversation's events, told apart by carrying no `agent_type` key: the expansion of a typed
  command and the Skill call, which begin a run; the starts of subagents and the messages sent to
  them; a user prompt, a task-notification among them; and the end of a turn. It drops a
  SubagentStop whose `agent_type` is empty, as Claude Code's own prompt-suggestion fork gives it.
- **guard.py**: which checks run on an event, whether a run is on, and what the subagent, the main
  conversation and whoever runs the plugin are told.
- **called.py**: what is kept of each run of the skill and of each subagent: the calls as they come
  back, the results, and the texts each was given. It also decides how the runs of one subagent
  join one another.
- **routes.py**: whether routes can be followed, which start is due from the routes and the results
  kept, and which result runs at once give together. The routes name the skill they start from by
  its name. `proposal.py` and `guard.py` both hold the routes to its check, as with the rules.
- **ports.py**: how a text of the plugin, such as a list of items to answer, is read into the form
  in which a check takes it. It reads Lane's own form, or runs the plugin's adapter.
- **result.py**: whether the result that a subagent gives is one that the subagent may give. It
  keeps nothing, and reads no text through `ports.py`: the guard keeps the result from the hook
  event of the run, and checks the rest of the end before the command runs.

- **The checks as entries of the plugin's `hooks/hooks.json`, acting by the event's `agent_type`,**
  over hooks in a subagent's or the skill's own file: Claude Code ignores hooks in a plugin agent's
  own file, and a SubagentStop hook in a skill's own file did not fire in a trial, as
  [The guard tells each role its steps again](../plugin-best-practice.md#the-guard-tells-each-role-its-steps-again)
  says, so only these entries hold every role (KR1.1). It costs the guard starting on every tool
  call of the plugin, and returning at once for a call it does not hold.
- **Lane's code put into the plugin** over running it from where Lane is installed: the plugin then
  needs nothing from Lane (KR1.1). It costs a fix in Lane reaching a plugin only once the user runs
  `lay.py up` (S4).
- **A command matched whole** over a command taken apart: a reading of the shell's grammar would let
  a rule name a part of a command, but
  [The check judges only what Claude Code documents](#the-check-judges-only-what-claude-code-documents)
  rules it out (KR1.1). It costs a subagent with rules running only the commands its rules name,
  word for word. It reads and writes files with Read, Grep, Write and Edit, whose paths the hook
  input gives.
- **Each plugin's guard keeping its own record of a session** over one record for both: a run of a
  dependency's subagent that the routes name is held by two guards, its own plugin's and the one
  whose routes start it. Each would write what the other reads, and a copy of Lane's code of another
  version could read the other's lines wrongly (KR1.1). It costs the start, the result and the end
  of such a run being kept twice.
- **`called.py` keeping each run's calls itself** over reading Claude Code's record of the session:
  the guard never reads that record, as
  [The check judges only what Claude Code documents](#the-check-judges-only-what-claude-code-documents)
  says, and the hook input of one event does not hold the calls before it (KR1.1). It costs a write
  on each call that comes back, and no call known that the hooks did not see.
- **A result counted only from a run of the result script** over reading the subagent's reply: a
  reply such as "No more entries" could be read as `more` (KR1.1). It costs each subagent that the
  routes name one more tool call as it ends.
- **An adapter as a script that Lane runs** over a module that Lane imports: `lay.py up` then
  replaces Lane's code without touching an adapter, and a fault in an adapter cannot break the guard
  (KR1.1). It costs a process started within the hook's time for each read through an adapter.
- **Each subagent with rules or named by the routes running in the background** over one that
  runs in the foreground: its start comes back at once with the ID of its run, so the guard joins
  each run to its own values by documented fields alone (KR1.1). Its end then reaches the main
  conversation as a task-notification, which carries the next start. It costs the subagent's file
  setting `background: true`, which `lay.py print` asks of it.
- **The steps given to a subagent whole, as context that Claude Code adds as it starts,** over a
  rule that has it read its own steps: a subagent could still skip the read (KR1.1). It costs the
  guard reading the steps on each start of a subagent with rules.
- **A later result of a run taking the place of its earlier one** over a run held to its first
  result: a subagent that ends to wait for an answer, with a result whose route starts no one, then
  moves the routes on once resumed. Otherwise the user would write code for that order (KR1.1). It
  costs the guard keeping each subagent's ID and result for the whole run, not only until its
  start counts.
- **Only the subagents that the routes name in `fan_out` running several at once** over any
  subagent beside itself: a subagent whose steps were not made for it, such as one that writes a
  file that every run writes, would then run so with no one having approved it, as
  [What was approved is what runs](#what-was-approved-is-what-runs) says (KR1.1). It costs the user
  naming each such subagent and ordering its results.
- **A run begun at the expansion of the typed command or at the PostToolUse of the Skill call** over
  a user prompt read for the command's words: these are the two ways Claude Code documents a skill
  begun, as
  [The check judges only what Claude Code documents](#the-check-judges-only-what-claude-code-documents)
  asks, while a prompt that quotes the command would match its words and begin no skill (KR1.1).
  It costs a skill followed without being called, such as its text pasted, being no run, and not
  held.
- **Each start told as context that Claude Code adds** over a message of Lane's own: Claude Code
  puts it beside an event that the conversation reads in any case (KR1.1). The first start is told
  on the event that begins the run. Each next one is told on the UserPromptSubmit that a subagent's
  end brings, on the PostToolUse of each start, and on the PostToolUse of a dependency's result
  script. It costs a start that the conversation may pass over, so a start not due is stopped with
  the one due, and the end of a turn is kept going.
- **The end of a turn kept going once while a start is due and no subagent of the run still runs,
  then let end with the user told whose step to fix,** over a hold until the start is made: a hold
  with no end would need a person to break it, which is no check. It costs a run whose
  conversation passes the start over twice stopping with the start due, which KR1.1 counts as gone
  wrong.
- **A dependency's skill that a route names counted as one move,** begun by its Skill call and ended
  by the PostToolUse of a run of the dependency's result script in the main conversation, with the
  caller's guard checking nothing meanwhile, over both guards holding the conversation: two guards
  on one conversation would each stop the other's moves, as
  [A plugin that uses another](../plugin-best-practice.md#a-plugin-that-uses-another) says
  (KR1.1). It costs a dependency's skill that ends with no result leaving its move open, so the end
  of a turn is kept going once, as for any start due.

## Data model

![Lane's data](images/data-model.svg)

- **Run**: one run of the skill the routes name, from its call to the route that starts no more.
- **Kept call**: one tool call that the guard kept, such as a start of a subagent or a call of one.
- **Run value**: a value given for one run of a subagent, in the prompt that started it or in a
  message sent to it.
- **Port JSON**: a text of the plugin, such as a list of items to answer, read into Lane's form.

The fields of each data lie where the data is built. The user docs give those that the user writes:
[the proposal](../../plugins/lane/docs/lanes.md#the-proposal),
[the routes](../../plugins/lane/docs/routes.md#the-routes) and
[the ports](../../plugins/lane/docs/lanes.md#the-ports).

## Sequences

Each story's steps follow in order. The participants are named as in [Components](#components), and
the data in brackets as in [Data model](#data-model). `changelog` is the walkthrough's plugin: its
skill `write` starts `writer`, and then `reviewer`, which gives `more` or `good`.

### S1: `lay.py print`

```mermaid
sequenceDiagram
  participant U as user
  participant L as lay.py
  participant PS as Proposal
  participant P as proposal.py
  participant LN as lanes/
  participant RT as routes.py
  participant PO as ports.py
  participant AD as Adapter
  participant PF as Plugin files
  U->>L: print (Proposal)
  L->>PS: reads (Proposal)
  L->>PF: reads each step it names (Steps' file, Step)
  L->>P: has it checked (Proposal, Step)
  P->>LN: checks each rule (Rule)
  opt the proposal holds routes
    P->>RT: checks the routes and the skill they name (Route, Order of results)
  end
  opt the proposal names an adapter
    P->>PS: reads its test cases (Test cases)
    P->>PO: runs the adapter on each test case (Test cases)
    PO->>AD: runs it (Port JSON)
    AD-->>PO: Port JSON
  end
  alt the proposal can be laid
    P-->>L: Rule, Route
    L->>LN: makes each sentence (Rule)
    L-->>U: the routes, and each step as it will read
  else it cannot
    P-->>L: what is wrong
    L-->>U: what is wrong, and exits 1
  end
```

### S2: `lay.py write`

```mermaid
sequenceDiagram
  participant U as user
  participant L as lay.py
  participant PS as Proposal
  participant P as proposal.py
  participant PF as Plugin files
  participant CC as Claude Code
  U->>L: write (Proposal)
  L->>PS: reads (Proposal)
  L->>P: has it checked, as in S1 (Proposal, Step)
  alt the proposal cannot be laid
    P-->>L: what is wrong
    L-->>U: what is wrong, nothing written, and exits 1
  else it can
    P-->>L: Rule, Route
    L->>PF: writes Step, Hook entry, Rules laid, Adapter, Test cases, and lays Lane's code
    L->>CC: claude plugin validate
    alt it passed
      CC-->>L: passed
      L->>PS: removes the proposal and its folder
      L-->>U: what it wrote
    else it found the plugin malformed, or claude is not on PATH
      CC-->>L: what it found
      L-->>U: what to fix, the proposal kept to run again, and exits 1
    end
  end
```

### S3: a run, each start told

```mermaid
sequenceDiagram
  participant U as user
  participant M as main conversation
  participant CC as Claude Code
  participant H as hook.py
  participant G as guard.py
  participant C as called.py
  participant RT as routes.py
  participant S as writer, reviewer (subagent)
  U->>CC: types /changelog:write, or an AI calls the skill
  CC->>H: UserPromptExpansion of the command, or PostToolUse of the Skill call (Event)
  H->>G: the main conversation's event (Event)
  G->>RT: is it the skill the routes name (Route)
  alt it is, and no run is on
    G->>C: keeps a new run (Run)
    G->>RT: the first start (Route)
    H-->>CC: context, start writer (Answer)
  else it is not, or a run is on
    H-->>CC: nothing to tell (Answer)
  end
  CC->>M: runs the skill's steps, with the context beside them (Step)
  Note over M,G: Outside a run, the guard tells the main conversation nothing.
  loop until a route starts no more
    M->>CC: starts a subagent [Agent]
    CC->>H: PreToolUse of the start (Event)
    H->>G: checks it (Event)
    G->>RT: is this the start due (Route, Result)
    alt it is
      H-->>CC: nothing to tell, so the start goes on (Answer)
      CC->>S: runs it in the background
      CC->>H: PostToolUse of the start (Event)
      H->>G: the start came back (Event)
      G->>C: keeps the start under the ID of its run (Kept call, Run value)
      H-->>CC: context, wait for it to end (Answer)
      S->>CC: gives its result and ends, as S3 a result draws
      CC->>M: a task-notification of its end, as a user prompt
      CC->>H: UserPromptSubmit of the task-notification (Event)
      H->>G: the end reached the main conversation (Event)
      G->>RT: the start due (Route, Result)
      alt writer gave written, or reviewer gave more
        H-->>CC: context, the result and the start its route names (Answer)
      else reviewer gave good, whose route starts no more
        H-->>CC: context, the result, and start no more subagents (Answer)
        G->>C: ends the run (Run)
      else the subagent ended with no result
        H-->>CC: context, start it again (Answer)
      end
    else the start due is a dependency's skill
      M->>CC: calls the dependency's skill [Skill]
      CC->>H: PostToolUse of the Skill call (Event)
      H->>G: a move begun (Event)
      G->>C: keeps the move begun (Run)
      Note over M,G: The dependency's guard holds its run. This guard checks nothing meanwhile.
      M->>CC: runs the dependency's result script, as its steps say
      CC->>H: PostToolUse of it, in the dependency's folder (Event)
      H->>G: the move ended (Event)
      G->>C: keeps its result, where a route from the skill is on it (Result)
      G->>RT: the start due (Route, Result)
      H-->>CC: context, the result and the start its route names (Answer)
    else it is not
      H-->>CC: deny, with the sentence and the start due (Answer)
      CC-->>M: the plugin's name, the sentence and the start due
    end
  end
  M->>CC: ends its turn
  CC->>H: Stop (Event)
  H->>G: the end of a turn (Event)
  G->>RT: is a start due (Route, Result)
  alt no run is on, none is due, or a subagent of the run still runs
    H-->>CC: nothing to tell, so the turn ends (Answer)
  else one is due, and the turn has not been kept going yet
    H-->>CC: keep it going, with the sentence and the start due (Answer)
  else one is due after the turn was kept going once
    H-->>CC: let it end, with the start left and whose step must be fixed (Answer)
    CC-->>U: the message, headed by the plugin's name
  end
```

### S3: a subagent's call held to its rules

`writer` runs here, started as the last section draws.

```mermaid
sequenceDiagram
  participant U as user
  participant M as main conversation
  participant SA as writer (subagent)
  participant CC as Claude Code
  participant H as hook.py
  participant G as guard.py
  participant C as called.py
  participant LN as lanes/
  participant PO as ports.py
  participant PF as Plugin files
  M->>CC: starts writer with its prompt [Agent]
  CC->>SA: starts it in the background
  CC->>H: PostToolUse of the start (Event)
  H->>G: the start of a subagent with rules (Event)
  G->>C: keeps the start and its prompt (Kept call, Run value)
  CC->>H: SubagentStart of writer (Event)
  H->>G: the start (Event)
  G->>PF: reads the steps of writer (Steps' file, Step)
  H-->>CC: the steps whole as context, where they lie apart from its file (Answer)
  loop each tool call of writer
    SA->>CC: a tool call
    CC->>H: PreToolUse (Event)
    H->>G: checks it (Event)
    G->>PF: reads the rules of writer (Rules laid)
    G->>C: reads the calls before it and the run's values (Kept call, Run value)
    opt a rule reads a text of the plugin
      G->>PO: reads the text (Port JSON)
    end
    G->>LN: runs each check (Rule, Run value, Kept call, Port JSON)
    alt the rules allow the call
      H-->>CC: nothing to tell, so the call goes on (Answer)
      CC->>H: PostToolUse (Event)
      H->>G: the call came back (Event)
      G->>C: keeps the call (Kept call)
    else the call breaks a rule, as git commit does
      H-->>CC: deny, with the sentence of the step (Answer)
      CC-->>SA: the plugin's name and the sentence of its step
    else a rule holds the command for the person's approval
      H-->>CC: ask, with the sentence of the step (Answer)
      CC->>U: the permission prompt, with the sentence
      U-->>CC: yes or no
      CC-->>SA: the command's output, or that it was refused
    else a rule takes a value given for the run, and the call holds another
      H-->>CC: deny, with the sentence of the step and the run's value (Answer)
      CC-->>SA: the plugin's name and the sentence of its step
    else the call cannot be checked
      H-->>CC: deny, with why and who must fix it (Answer)
      CC-->>SA: the plugin's name and why
      CC-->>U: the same message
    end
  end
```

### S3: a result given

`reviewer` gives its result here. `writer` gives `written` the same way.

```mermaid
sequenceDiagram
  participant M as main conversation
  participant SA as reviewer (subagent)
  participant CC as Claude Code
  participant H as hook.py
  participant G as guard.py
  participant C as called.py
  participant LN as lanes/
  participant RT as routes.py
  participant RS as result.py
  participant PF as Plugin files
  SA->>CC: runs the result script with its result
  CC->>H: PreToolUse of the command (Event)
  H->>G: checks it (Event)
  G->>RT: may reviewer give this result (Route, Result)
  G->>C: reads the calls of the run (Kept call)
  G->>LN: runs each check of the end (Rule, Kept call)
  alt no route from reviewer is on the result
    H-->>CC: deny, with the sentence of its last step and the commands it may run (Answer)
    CC-->>SA: the plugin's name, the sentence and the commands it may run
  else a rule about the end is not kept
    H-->>CC: deny, with the sentence of each such rule and what is missing (Answer)
    CC-->>SA: the plugin's name, the sentences and what is missing
  else the result and the work are as the rules ask
    H-->>CC: nothing to tell, so the command goes on (Answer)
    SA->>RS: runs it [Bash] (Result)
    RS->>PF: reads the routes (Route)
    RS-->>SA: exits with no error
    CC->>H: PostToolUse of the command (Event)
    H->>G: the result came back (Event)
    G->>C: keeps the result (Result)
  end
  opt the subagent is a dependency's
    SA->>CC: runs its own plugin's result script with its result
    CC->>H: PostToolUse of it, in the dependency's folder (Event)
    H->>G: the result came back (Event)
    G->>C: keeps it, where a route from the subagent is on it (Result)
  end
  SA->>CC: ends
  CC->>H: SubagentStop of reviewer (Event)
  H->>G: the end (Event)
  G->>C: is a result kept (Result)
  alt a result is kept
    H-->>CC: nothing to tell, so reviewer ends (Answer)
  else none is kept, and reviewer has not been kept going yet
    H-->>CC: keep it going, with the sentence of its last step (Answer)
    CC-->>SA: the plugin's name and the sentence
  else none is kept after reviewer was kept going once
    H-->>CC: nothing to tell, so reviewer ends with no result (Answer)
  end
  opt the main conversation resumes a run [SendMessage]
    M->>CC: sends it a message
    CC->>H: PreToolUse of the message (Event)
    H->>G: checks it (Event)
    G->>C: did the run end with no result (Result)
    alt it ended with no result
      H-->>CC: deny, with the sentence and the start due (Answer)
      CC-->>M: the plugin's name, the sentence and the start due
    else it gave a result
      H-->>CC: nothing to tell, so the message goes on (Answer)
      CC->>H: PostToolUse of the message (Event)
      H->>G: a message to the run (Event)
      G->>C: keeps the message as the run's values (Run value)
      Note over SA,G: The run gives a result again, as above, in place of the earlier one.
    end
  end
```

How a subagent writes its result command, and what it is told, is in
[How a subagent gives its result](../../plugins/lane/docs/routes.md#how-a-subagent-gives-its-result).

### S3: runs at once

The main conversation starts several runs of `reviewer` here, as routes that name `reviewer` in
`fan_out` let it.

```mermaid
sequenceDiagram
  participant U as user
  participant M as main conversation
  participant CC as Claude Code
  participant H as hook.py
  participant G as guard.py
  participant C as called.py
  participant RT as routes.py
  participant S as runs of reviewer (subagent)
  M->>CC: starts a run of reviewer
  CC->>S: runs it in the background, as S3 a run draws
  M->>CC: starts another run while the first still runs
  CC->>H: PreToolUse of the start (Event)
  H->>G: checks it (Event)
  G->>RT: may reviewer run beside itself (Route)
  alt the routes name reviewer in fan_out
    H-->>CC: nothing to tell, so the start goes on (Answer)
    CC->>H: PostToolUse of the start (Event)
    H->>G: the start came back (Event)
    G->>C: keeps the start as joining the first run (Kept call)
  else they do not
    H-->>CC: deny, with the wait for the first run (Answer)
  end
  opt the main conversation starts another subagent before every run has ended
    H-->>CC: deny, with the wait for every run (Answer)
  end
  S->>CC: each run gives its result and ends, as S3 a result draws
  CC->>H: UserPromptSubmit of each task-notification (Event)
  H->>G: an end reached the main conversation (Event)
  G->>C: the results of the runs (Result)
  G->>RT: the start due (Route, Order of results, Result)
  alt a run still runs
    H-->>CC: context, wait for every run to end (Answer)
  else the runs gave one result, or the order of results takes one
    H-->>CC: context, the result of the runs and the start due (Answer)
  else a run ended with no result
    H-->>CC: context, start reviewer again in its place (Answer)
  else no order of results holds the results they gave
    H-->>CC: an error that the maker of the plugin must fix (Answer)
    CC-->>U: the message, headed by the plugin's name
  end
```

How the runs join and how their result is taken is in
[Runs at once](../../plugins/lane/docs/routes.md#runs-at-once).

### S4: `lay.py up`

```mermaid
sequenceDiagram
  participant U as user
  participant L as lay.py
  participant PF as Plugin files
  U->>L: up (the plugin's folder)
  alt the folder holds no plugin's manifest
    L-->>U: what is wrong, nothing brought up, and exits 1
  else it holds one
    L->>PF: reads Lane's code, the Hook entries and the Rules laid
    opt the plugin's copy of Lane's code is older than Lane
      L->>PF: lays Lane's code
    end
    opt the hook entries are in another form than Lane's
      L->>PF: writes each Hook entry
    end
    opt a Step says a sentence in a wording that Lane laid before
      L->>PF: writes the Step, the sentence in the current wording
    end
    L-->>U: what it did, and each rule laid, marked where its step no longer says it
  end
```

## Deployment

![Lane's deployment](images/deployment.svg)

The user installs Lane as [the README](../../plugins/lane/README.md#installation) says, and runs
`python3 <installPath>/scripts/lay.py` on their own computer. Claude Code starts the guard through
the plugin's hook entries, each a command in `sh` that runs `python3`, on the computer of whoever
runs the plugin. After an update of Lane, the user runs `lay.py up` on their plugin.

- **Lane's code on Python 3.9 and its standard library only**, as
  [Python 3.9 and the standard library](../plugin-best-practice.md#python-39-and-the-standard-library)
  says, over a later Python or packages: whoever runs the plugin then installs nothing for Lane
  (KR1.1). Each hook's command checks for `python3` in `sh` first, as the guard cannot even read the
  event without Python. It costs each tool call that a rule is about being stopped where Python is
  missing.
- **The kept calls and the run in the system's temporary folder**, as
  [Where a plugin writes its files](../plugin-best-practice.md#where-a-plugin-writes-its-files)
  says for files used only while a plugin runs, over a folder in the repository: they mean nothing
  once the session ends. It costs a call that needs its kept calls being one that cannot be checked
  where the system clears that folder during a run.
- **A plugin's `hooks/lane/` as a link to Lane's code in this marketplace**, as
  [Code kept once](../plugin-best-practice.md#code-kept-once) says, over a copy: a fix to the guard
  reaches every plugin here (KR1.1). Elsewhere it is a copy that carries Lane's version, which
  `lay.py up` reads, as a link cannot reach across repositories. It costs a copy keeping Lane's
  code of the day it was laid until `lay.py up` runs.

## Directory structure

```text
plugins/lane/
├── .claude-plugin/plugin.json      Lane's manifest and version
├── scripts/lay.py                  lay.py, and its parts beside it
├── hooks/lane/                     Lane's code, laid into each plugin
│   ├── hook.py                     hook.py
│   ├── result.py                   result.py, the result script
│   └── core/domain/
│       ├── proposal.py             proposal.py
│       ├── guard.py                guard.py
│       ├── lanes/                  lanes/, a module for each type of rule
│       ├── called.py               called.py
│       ├── routes.py               routes.py
│       ├── ports.py                ports.py
│       └── rules.py, step.py, template.py, schema.py   code that several components share
└── README.md, docs/, CHANGELOG.md, images/   for Lane's users

dev/lane/
├── product-vision.md, architecture.md, images/   Lane's product vision and architecture
├── README.md, design-tree.md       for Lane's developers
├── cosmic-ray.toml                 the mutation testing
├── testing.py                      the tests' shared code and the double of Claude Code
├── trials/                         the code that runs the ux trials
└── tests/
    ├── unit/                       unit tests, at the path of what each tests
    ├── architecture/               a test for each path of each sequence
    └── ux/                         the trials of O1, and changelog

.lane/<yyyymmdd>-<plugin>/          Proposal, and each Adapter with its Test cases
<temporary folder>/lane/            Run, Kept call, Run value, Result
<the plugin>/skills/                the skill the routes name: a Steps' file, with its Steps
<the plugin>/agents/                each subagent's Steps' file, with its Steps
<the plugin>/hooks/hooks.json       each Hook entry
<the plugin>/hooks/lanes.json       Rules laid: each Rule, Route and Order of results
<the plugin>/hooks/adapters/        each Adapter that runs, and its Test cases
<the plugin>/hooks/lane/            Lane's code
```

- **Code that several components share beside them in `core/domain/`**, each module for one data
  or one form, over a copy in each component: `rules.py` reads and writes the Rules laid, `step.py`
  reads a Step, `template.py` reads a Markdown file's frontmatter and headings, and `schema.py`
  holds JSON to a JSON Schema. A copy would be fixed in one component and left wrong in another, as
  [Code kept once](../plugin-best-practice.md#code-kept-once) says (KR1.1). A module inside one
  component lies in it, as `lanes/` holds the forms of `in_form`. It costs a change to a shared
  module reaching every component that uses it, whose tests must all pass.
- **Lane's core in `hooks/lane/core/domain/`** over `core/` at the plugin's root, where
  [The core apart from Claude Code](../plugin-best-practice.md#the-core-apart-from-claude-code) puts
  it: `lay.py` lays `hooks/lane/` into each plugin whole, by one link or one copy, and a core
  outside it would need a second (KR1.1). It costs Lane's core lying apart from where every other
  plugin keeps its core. Lane has no roles of its own, so it has no `core/roles/`.

## Tests

Lane tests by [Test in the plugin best practice](../plugin-best-practice.md#test), and differs from
it where this section says.

![Lane's tests](images/tests.svg)

- **The lay.py, hook and result script processes tried FULL at unit and at architecture** over
  HAPPY: a fault in any of them writes into a plugin what no one approved, or lets a break through
  (KR1.1). Only these levels check every case on every push. It costs the
  most tests to keep up as the code changes.
- **The trials SMOKE** over HAPPY: they only confirm in real use what the lower levels have checked,
  and each step of a trial costs a run of the model. It costs a fault that only a real run brings
  out showing once every lower level passes.
- **The double of Claude Code sending the main conversation's events as a trial on Claude Code
  2.1.319 recorded them,** beside the double with the version and the date, over what the hooks
  reference alone says: where the reference says nothing, a double would send what no Claude Code
  sends, and pass a test that the real one fails (KR1.1). It costs a try of the real Claude Code
  again where a new version may act otherwise.
- **The ux trial in `claude -p` as well as in an interactive session** over one of them: Claude
  Code 2.1.319 brings a background subagent's end back to the main conversation in both, so a
  plugin may run either way (KR1.1). It costs each trial run twice.
