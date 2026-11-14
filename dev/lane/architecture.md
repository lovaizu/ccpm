# Lane architecture

This document says how the parts of Lane give what [its README](../../plugins/lane/README.md)
promises. Lane turns the user's steps into checks once, and holds every run by them. up proposes
the rules and the routes from the steps, each rule of a lane type that gives both the sentence a
role reads and its check, and `lay.py` lays them into the plugin once the caller approves. On each
hook event of a run, the laid guard works out where the run stands from the starts and results that
it or the plugin keeps, and gives a role that leaves a step that step's sentence, and the main
conversation the start that the routes name after each result.

## User stories

- S1: the user wants to type `/lane:up <plugin>` and read the proposal, so that they see each step
  as it'll read with its rules, and the order, before anything holds their plugin. It carries the
  walkthrough's `/lane:up changelog`, the routes and lanes shown, the `commands` line, the note
  beside a step that names a command its subagent may not run, and the result `written` that Lane
  names where the steps name none.
- S2: the user wants to reply `yes`, or say what to change, so that Lane lays only what they
  approved, and holds their plugin's next run. It carries the reply `yes`, each `Wrote` line,
  `claude plugin validate passed`, the line that asks for `/reload-plugins`, the person's
  `/reload-plugins`, and `you say what to change, and Lane proposes again`.
- S3: the user, where an AI builds the plugin, wants to call `/lane:up` itself, read the proposal,
  and approve it by its own act, so that it lays the rules without waiting for a person's reply,
  and reaches the plugin's first held run once whoever gives the conversation its prompts types
  `/reload-plugins`, which it asks for. It carries `it reads the proposal and approves it in the
  same way, with no person's reply`, and `asks whoever gives the conversation its prompts`.
- S4: the user wants to run `/lane:up <plugin>` again after they change the steps or update Lane, so
  that the checks hold the steps as they now read, with Lane's newest code. It carries `Lane
  proposes from the steps as they now read, in place of what it laid before` and How it works'
  `After an update of Lane, /lane:up brings them to the new version`.
- S5: the user wants to type their plugin's command and have each subagent start in the order they
  set, so that the run goes from result to result with no code of theirs. It carries
  `/changelog:write`, each `Start` line, each `gave` line, a start with only the text the plugin
  gives, starts side by side, each with a text other than those of its role that run, the route
  that waits for a command the person types, the route after a command they type at any moment,
  the moves that a route lists for the skill's steps to choose among, the command of another skill
  of the plugin typed while a run goes on, which starts that skill's run beside it,
  `Start no more subagents`, and the work after it that Lane doesn't check. It carries, besides,
  the move that calls another plugin's skill, as the plugin guide's
  [A plugin that uses another](../plugin-development-guide.md#a-plugin-that-uses-another) says.
- S6: the user wants each subagent held to its steps on every call, so that a subagent that leaves a
  step goes back to it. It carries the calls that Lane lets through, the stopped `git -C <repo> log --oneline`, and
  the step's sentence and the commands that `writer` may run.
- S7: the user wants a run that stopped to go on where it stopped, after `/compact` or in a new
  conversation, so that its subagents don't start over. It carries How it works' `A run that stops
  starts over`, and the adapter that gives the plugin's records in Lane's form.

## Components

![Lane's components](images/components.svg)

What each decides alone:

- user\
  What each step says, whether the proposal holds what they meant, what to change in it, and
  whether to approve.
- up\
  Which lane type each step takes and what it takes, the routes of each skill from its step and the
  results that the steps name, the result named where a subagent's steps name none, and how a
  change the user asks for reads in its step.
- lay.py\
  Which text of a step Lane laid before, read from the laid set in the form that the released Lane
  that laid it wrote, and so how each step reads without it for up, whether a
  proposal can stand against the lane types, the steps, and the plugin's files, how each step reads
  once laid, whether a proposal can still be laid, as the steps it came from still read as they did
  and the Run of up that showed it still waits for its reply, as the guard works that Run out, and
  which files laying writes or replaces, as one change.
- lane types\
  For each type, such as `run_only` or `write_only`, what it takes, such as the paths that
  `read_never` keeps unread, the steps it suits, the sentence that the role reads in its step,
  whether a step's own words already say that sentence, what it keeps of a call's result for a
  later check, and the check of a call or of an end against it, such as, for `ends_checked`, a
  subagent's end or the skill's turn's end by a command of the plugin's own, which it runs as the
  guard checks the end, with the role's run values and its result filled in.
- guard\
  The form of the laid set, `lanes.json`, with its Lanes, Routes, adapters, and Laid, which
  `lay.py write` writes through the guard's code, which Run, Start, and role each hook event
  belongs to, among the Runs of the plugin's skills
  that go on side by side in a conversation, which facts of an event the run record keeps, where
  each Run stands, worked out from the record's lines on each event for itself, `result.py`, and
  `lay.py`, when a run starts, ends, and stands aside while the main conversation follows another
  plugin's run, whether each call, start, and end passes, which Result a run of the result script
  gave, which start the routes make due, what a stopped role reads, what the main conversation
  reads, whether up gave the person the proposal word for word, and whether the act that lays it is
  the caller's own.
- result.py\
  Whether a result is one that the role may give, in a Run of the conversation as the guard works
  it out.
- adapter\
  How the plugin's own form of its records, or of a start's text, reads in Lane's form, and, from
  the words typed after the skill's command, which of the plugin's kept work the call picks up,
  none for a new request.

The choices made, and why:

- A proposal that up, an AI, makes from the sense of the steps over one that code makes from their
  words\
  The skill's step `Have the entries written and reviewed.` names no subagent, so only a reading of
  its sense gives the routes that the walkthrough shows, and code would leave such a step unheld,
  which raises KR1.1. `lay.py print` checks each proposal against the lane types and the steps, so
  a rule that no check holds never stands. The cost: two runs of `/lane:up` on the same steps may
  word a proposal apart, and the user reads each one.
- Each change the user asks for made in the steps over a change kept beside them\
  The next `/lane:up` reads the change from the steps, so it never drops a change the user made,
  which keeps KR1.1 low. The cost: what the user says to change goes into their step's sentence, and
  they see it there.
- The approval held by a guard that Lane lays on its own up over the instruction in up alone\
  The guard lets `lay.py write` through only after the caller's own act, so the main conversation
  can't approve for a person who typed `/lane:up`, on every run, which keeps KR1.1 low. The cost:
  the guard rests on Claude Code telling a typed `/lane:up` from a call of the Skill tool, which a
  recorded run must show.
- Each skill as one role whose Steps lie in several files over a role for each command that the
  person types\
  The main conversation runs the steps of every command in one conversation, and no hook event
  marks where a command's steps end and the skill's go on, so the guard holds it to every Lane of
  the skill on each call, and no command's step goes unheld, which keeps KR1.1 low. The cost: a
  Lane on a command's step holds the main conversation from the Run's start, before the person
  types the command.
- A proposal refused by `lay.py print` where it doesn't fit the plugin's files over one laid as it
  stands\
  A command that a Route waits for or goes after and that the model may call, as its `SKILL.md`
  doesn't set `disable-model-invocation: true`, lets the main conversation make a move in the
  person's place. A program in `hooks/adapters/` that the Proposal doesn't name leaves each start
  without the text that the plugin gives. A file of Steps that two Roles share takes the sentences
  of both, so a role reads another's rule. Each would leave a run that breaks the steps or the
  order, so refusing them keeps KR1.1 low. The cost: before Lane proposes, up mends the Proposal,
  such as by naming the program, or the user mends their file.
- An end held to a command of the plugin's own that Lane runs at the end over a step that has the
  role run it\
  A role that leaves its steps skips the step that checks its work too, and only the plugin knows
  its own measure, such as whether a record holds each step, so the guard has the `ends_checked`
  lane type run the plugin's command on every end, with the run values of the role's Start and the
  Result it gave, and holds the end until it gives 0, which keeps KR1.1 low. The cost: the command
  runs at each end, and at each end of the skill's turn in a Run, so it must be quick and must hold
  at any of them, and a name in braces that no Start fills, as on the skill, makes `lay.py print`
  refuse the lane.
- A role that reads nothing of a path still running the commands that its steps name over its
  result's alone\
  The plugin's maker names each such command word for word, and approves it in the proposal, so a
  role that must not read its maker's records can still keep one of its own, which keeps KR1.1 low.
  The cost: a command that a step names may read what `read_never` keeps unread, as the proposal
  shows the maker.
- A sentence left out of a step that already says it over each sentence added to the step it suits\
  A step that holds a sentence word for word, or that names each command of its `ends_checked`
  lane, gives the role the rule already, in the maker's words with its reason, and the sentence
  said again takes the role's attention from the step, so `lay.py` adds it there no more, and the
  role reads each rule once, which keeps KR1.1 low. The cost: a step that says a rule in other
  words, such as `Write nothing outside`, still takes the sentence, as code can't tell that the two
  say one rule, and its maker writes the sentence into the step to say it once. A step that names
  the check for the role to run takes no sentence either, so the role learns that the guard holds
  its end only where the guard stops it.
- Each hook event placed by its `session_id` and `agent_id` over its `prompt_id` or its
  `transcript_path`, with each Start tied to its subagent at the PostToolUse of its Agent call over
  the SubagentStart\
  The guard places an event on the Runs of its `session_id`, on the main conversation where it
  carries no `agent_id`, and else on the Start whose Agent call's PostToolUse named that `agent_id`,
  and on that Start's Run.
  A `prompt_id` changes as the person types while a subagent runs, a `transcript_path` moves as the
  conversation enters a worktree, and a SubagentStart may come before or after that PostToolUse and
  names no Agent call, as [Claude Code's states](claude-code-states.md) shows each with its records,
  so the guard holds each call to the lanes and the run values of its own Start, in each state that
  the README's main use and rn bring about, which keeps KR1.1 low. The cost: a state that no record
  shows may place an event apart from its Start, so each rare state gets one line there that names
  what Lane does, never holding a call to the rules of another Run, and the compatibility test of
  Test strategy checks the states on each new version of Claude Code.
- The runs of several skills of one plugin side by side in one conversation, each held to its own
  skill's Routes, over one run at a time\
  A person types another command of the plugin while a subagent of the first runs in the
  background, as a recorded run shows, and a plugin whose second command Lane refuses or leaves
  unheld doesn't run as its maker designed, which raises KR1.1. So each Start keeps the skill whose
  Run made it due, a subagent's events go to its Start's Run by its `agent_id`, a Result of the
  main conversation goes to the Run of the skill that its command names, a command that the person
  types goes to each Run whose Route waits for it or goes after it, and a start of the main
  conversation goes to the Run whose moves open it. The cost: where the moves of two Runs open the
  same start, of one role with one text, the start goes to the Run that began first, and the other
  Run's start stays due.
- The main conversation held to the Lanes of the skill of each Run that goes on, joined as the
  Lanes of one role's Steps, over the Lanes of one skill\
  No hook event says which skill's step a call of the main conversation serves, so the guard checks
  the call by the Lanes of each skill whose Run goes on, joined as each lane type joins the Lanes of
  one role, such as the commands of each `run_only` lane, so that a call one skill's steps allow
  passes and no skill's step goes unheld, which keeps KR1.1 low. The cost: a Lane that keeps a
  path unread in one skill holds the main conversation while the other skill's run goes on too.
- The run record kept as lines that each hook adds and never rewrites, holding only the facts that
  no later payload gives again, over a Run written whole\
  The hooks of subagents that run side by side run at once, so a Run written whole by one hook loses
  the line that another added, and a value worked out and kept, such as the moves due, goes stale
  once another line comes. So the record keeps each Start with its skill, its tie to an `agent_id`,
  each Result, and each other fact that one event alone tells, such as a subagent's end or a
  command that the person typed, and the guard works out where each Run stands from those lines on
  each event, and reads from the payload what it carries each time, such as the `session_id`, the
  `agent_type`, and the skill that a result names, which keeps KR1.1 low. The cost: the guard reads
  the conversation's whole record on each event, so a long run makes each hook slower.
- Each Result added by the guard at the PostToolUse of a run of `result.py` that gave 0, with the
  `agent_id` of that payload, over `result.py` adding it\
  Claude Code gives a Bash command no `agent_id`, only `CLAUDE_CODE_SESSION_ID`, as a recorded run
  shows, so only the hook of the call ties a Result to the subagent that gave it, even where two
  subagents of one role give results at once, which keeps KR1.1 low. The cost: a Result counts only
  once its PostToolUse comes, and `result.py` only checks the result and refuses one that the role
  may not give.
- The adapter of the plugin's records given the words typed after the skill's command, or the
  Skill tool's arguments, to name which kept work the call picks up, over the guard deciding it
  from the run record alone\
  A plugin whose command takes a request, such as `/rn:up <request>`, must tell a new request from
  a pause to pick up, and no part of the plugin runs before the guard answers the call, so only the
  adapter, given the words that the hook event of the call carries, can, which keeps KR1.1 low.
  The guard then starts the Run anew where the results it gives are none, or picks it up from
  them. The cost: where `lanes.json` names that adapter, it runs at each call of the skill, even
  where the conversation's record holds the skill's Run, so an adapter that gives no results there
  starts the Run anew, and the Run before ends.
- Subagents in the background over subagents in the foreground\
  The end of a subagent in the background reaches the main conversation as an event of its own, and
  the PostToolUse of its Agent call names the subagent once it starts, so the guard ties each
  subagent to its Start, counts the Start once its subagent ends, and gives the next start beside
  that end. A subagent in the foreground would lose that tie: the PostToolUse that names it comes
  only once it ends, as [Claude Code's states](claude-code-states.md#rare-states) shows, so while
  it works the guard could hold none of its calls to its Start's lanes and run values, and would
  either let them through unheld or stop each one, which raises KR1.1. The cost: each subagent's
  file sets `background: true`, as the README's Requirements names, and `lay.py print` refuses a
  proposal whose subagent's file doesn't.
- The guard standing aside from a call of another plugin's skill that a Route's move names, until
  the main conversation makes a move of the Route after it, over holding the main conversation to
  the skill's own Lanes meanwhile\
  The main conversation follows the other plugin's steps in the same conversation, as the plugin
  guide's [A plugin that uses another](../plugin-development-guide.md#a-plugin-that-uses-another)
  says, and the other plugin's guard holds it there, so two guards holding one conversation at once
  would each stop the other's moves, which raises KR1.1. The cost: the main conversation's calls in
  between rest on the other plugin's guard alone, and a subagent of the skill that runs stays held
  by its own Start.
- The form of `lanes.json` decided by the guard's code, which `lay.py write` writes through, over
  `lay.py` deciding it as the part that writes it\
  The guard reads `lanes.json` on each hook event of a plugin that runs with no `lay.py`, so the
  form that `lay.py write` writes and the form that the guard reads come from the one copy laid, and
  a change to the form made for one is the change the other reads, which keeps KR1.1 low. The
  cost: `lay.py` reads apart each form that a released Lane wrote, to take that Lane's sentences
  out of the steps.

## Data model

![Lane's data](images/data-model.svg)

- Step\
  One item of the numbered list under `## Steps` of a skill or a subagent, or of the file in the
  plugin's folder that its body names by `${CLAUDE_PLUGIN_ROOT}/`, as the user wrote it. A
  skill's Steps lie in its own file and that file both, and in the `SKILL.md` of each command that
  its Route waits for or goes after, as the main conversation runs them all.
- Proposal\
  The lanes and the routes proposed from the steps as they read at one time, with its ID, kept for
  the Run of up that showed it, if any: until the caller approves it, the steps change, or that Run
  ends without its approval.
- Lane\
  A rule on one step of one role, in the file that holds the step, of one lane type. It holds the
  role on every call and every end of the Run, as its type checks them. The README calls it a rule.
- Route\
  The moves of one skill after the start of its run, a role's result, a command the person types,
  or the end of another plugin's run that a move called: one move, or several among which the
  skill's steps choose by their own judgment. A move starts a role, resumes a role's subagent by
  SendMessage, calls another plugin's skill, starts no more, or ends the turn for the person's reply
  with no start due, and each but that wait may wait for a command that the person types. A Run
  holds the moves of the Route after each Result at once, until the skill's steps make them, so
  that they can start side by side the work that rests on none waiting.
- Laid\
  The sentences that Lane added to the steps, and the hook entries that are Lane's, in the form of
  the Lane that laid them, so that the next `/lane:up`, of that Lane or of a newer one, can take
  Lane's text apart from the user's.
- Approval\
  The caller's own act that approves one Proposal: a person's reply, or an AI's own run of `lay.py
  write`.
- Start\
  One start of a role that a Route makes due, with the skill whose Run made it due, and its text:
  what the adapter gives for the role, such as its run values, or else Lane's words `Carry out your
  steps`, with the words that the person typed after the plugin's command, or that an AI's call of
  the skill by the Skill tool gives as its arguments. The text names no command, as a role given the
  plugin's command runs it and starts roles of its own. The main conversation passes the text word
  for word, so a role gets nothing of the talk that started it. Where the adapter gives the role's
  run values beside its text, the Start keeps them, and each name in braces of the role's lanes that
  they name stands for that value alone, so that the role is held to what it was started for, such
  as one deliverable. A name they don't give stands for any value, as in a plugin with no adapter,
  or in a lane of the skill, whose run no adapter starts. A Start runs beside each other Start that
  runs until its end reaches the main conversation, and the PostToolUse of its Agent call names the
  subagent it started, which holds that subagent to the Start's run values while others of its role
  run. A Start of a role with the text of one of its role that runs isn't due, as it would start
  that work again, so the adapter, asked again after each Start and given each Start that runs,
  decides which work of the role waits, as only Lane knows which Starts run. A resume that a Route
  lists counts as a Start of the subagent it resumes, which keeps the run values of its first Start,
  and the Result that the subagent gives after it moves the Run as a Start's does. Where no Route
  lists a resume, a resume is the main conversation's talk with a subagent, which moves no Run, so
  that a plugin whose routes give one start each runs as before.
- Call\
  One tool call of a role, which the guard checks as it comes, and which the run record doesn't
  keep, as no later move rests on it. A subagent's Call lies in its Start's Run, and the main
  conversation's in each Run that goes on.
- Run\
  One run of one skill of the plugin in one conversation, from its call to the route that starts no
  more, with each Start, each Result, and each Call that lies in it. The runs of the plugin's skills
  go on side by side, one Run for each skill. No Run is written whole: the guard works each out on
  each event from the lines of the conversation's run record, which keeps only what no later payload
  gives again, each Run's call, each Start, its tie to a subagent, each Result, and each other fact
  that one event alone tells and a later move rests on, as Sequences draws each. A Run stands aside
  from a call of another plugin's skill that a move names until the main conversation makes a move
  of the Route after it. A call of the skill that starts its run anew ends the Run before. A run of
  up ends instead once `lay.py write` lays a Proposal, or once the turn on the person's prompt after
  a Proposal shown ends with no `lay.py write` and no new `lay.py print`, as a Proposal waits for
  one reply.
- Kept results\
  The results of a run that the user's plugin keeps in its own records, which the adapter gives.

## Principles

Lane builds on [the plugin guide](../plugin-development-guide.md), and adds these rules, which every
part keeps.

### The steps are the one source

up proposes the lanes and the routes from the steps alone, as `lay.py steps` gives them without
the text that the Laid names, and puts each change that the user asks for into the steps, never into the proposal or into
`lanes.json`.

*Why*: a rule kept apart from the steps is one the user can't see in them, and the next `/lane:up`
loses it or holds a role to what its steps no longer say, which raises KR1.1.

### One type gives the sentence, the check, and the steps it suits

up, `lay.py`, and the guard take a rule's sentence, its check, and the steps it suits from its lane
type, and from no other place.

*Why*: a sentence and a check made apart drift, so the role keeps the sentence and the check stops
it, and up proposing from a list kept apart would propose a rule that no check holds, which raises
KR1.1.

### Laid only on the caller's own act

`lay.py write` lays only the Proposal that its caller approved by their own act, and only while the
steps read as they did when `lay.py print` showed it. Where a person typed `/lane:up`, the act is
the person's reply after the proposal, and the guard holds the end of up's turn until up gives them
what `lay.py print` showed, word for word. Where an AI called up by the Skill tool, the act is its
own run of `lay.py write`.

*Why*: rules laid that the user never read stop moves they meant to allow, which raises KR1.1, and
an approval that waits for a person's reply leaves an AI unable to lay the rules it read until a
person reads them too, which adds to KR1.2.

### Lane's part replaced whole

`lay.py write` replaces at once everything the Laid names, the sentences in the steps, Lane's hook
entries, `lanes.json`, and `hooks/lane/`, and leaves every other part of the plugin as it stands.

*Why*: a rule left from before the steps changed stops a move that the steps now allow, and a hook
entry of the user's own that Lane removed would leave their step unheld, which raises KR1.1.

### A result only from the result script

The guard goes on by the routes only on a Result that a run of `result.py` gave for the role that
ran it, from the subagent that the Start started, never on what a role wrote in its reply.

*Why*: a reply such as `No more entries` read as `more` starts a role that the order doesn't name,
and a result of another subagent of the same role, read as the Start's, moves the run on a result
that the started role never gave, which raises KR1.1.

### Only the main conversation starts the roles

In a run, the guard lets a start of a role of the plugin through only from the main conversation,
as the Start due. It stops a subagent's start of a role by the Agent tool, and its call of the
plugin's skill by the Skill tool, and gives the subagent the sentence of its last step.

*Why*: a subagent that starts roles of its own starts roles that the order doesn't name, and the
run then holds results that no Start of the routes made, which raises KR1.1.

### A stop gives the step back

Each stop the guard makes gives the role, or the main conversation, the sentence of the step or
the route it breaks, and what it may do instead, such as the commands it may run. Where the guard
can't check a call, it stops it, and says why and who must fix it.

*Why*: a role that meets only a refusal finds another way to do the step, and a call let through
unchecked could break it, which raises KR1.1.

### The run kept in a file

The guard keeps each run's starts and results in the run record, and decides each move from that
record and the plugin's kept results, never from the conversation. `result.py` and `lay.py` take
where a Run stands from the guard's code, never from the conversation.

*Why*: a compacted or new conversation forgets where the run stood, so the run stops while the order
names a move, which raises KR1.1.

### The guard checks only the run

The guard checks a call only between the call of a skill of the plugin and the end of that
skill's Run, and only for the role whose lanes name it. While the main conversation follows another
plugin's run that a move called, the guard checks none of the main conversation's calls and holds
none of its stops, until it makes a move of the Route after that call.

*Why*: a check that reaches the user's own work, or the run of another plugin that its own guard
holds, stops a move that no step forbids, which raises KR1.1.

### The laid plugin runs alone

The laid guard, `result.py`, and the lane types need only Python 3.9, its standard library, and the
plugin's own folder, and no line of Lane's code names a plugin.

*Why*: whoever runs the plugin may have no Lane, or another version of it, and the run would then
stop, or meet checks other than those laid, which raises KR1.1.

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
  participant F as the plugin's files
  U->>CC: /lane:up <plugin>
  CC->>G: the skill's call, typed by a person
  G->>RS: adds the call of up's Run, by a person
  Note over U,UP: Claude Code runs up's steps in the main conversation. An AI's call of up by the Skill tool adds the call by an AI, as S3 draws.
  UP->>L: types
  L->>T: each type's sentence, what it takes, and the steps it suits
  L-->>UP: the types
  UP->>L: steps <plugin>
  L->>F: reads each Role, each Step, and the Laid
  L-->>UP: each Role and each Step without the text that the Laid names
  UP->>UP: writes the Lanes, the Routes, and each Result named where none is (Proposal)
  loop until the proposal can stand
    UP->>L: print (Proposal)
    L->>T: checks each Lane, and makes its sentence where its Step doesn't say it already
    L->>L: checks that the Routes reach each Result and each Role
    L->>F: checks that each subagent's file sets background: true
    L->>F: checks that each command a Route waits for or goes after sets disable-model-invocation: true
    L->>F: checks that the Proposal names each program in hooks/adapters/
    L->>F: checks that no two Roles take their Steps from one file
    alt the Proposal can't stand, such as with a program in hooks/adapters/ left out
      L-->>UP: what's wrong, and exits 1
      UP->>UP: mends the Proposal
    else a file of the plugin can't carry it, such as a subagent's file without background: true
      L-->>UP: what's wrong in the file, and exits 1
      UP-->>U: what to fix in their plugin, and stops
    end
  end
  L->>P: keeps the Proposal by its ID
  L-->>UP: the Routes, each Step as it'll read, the commands each role may run, the notes, and the ID
  CC->>G: the PostToolUse of lay.py print, with what it printed
  G->>RS: adds what lay.py print showed, to up's Run
  UP-->>U: what lay.py print showed, and asks for yes or what to change
```

### S2: a person approves or asks a change

```mermaid
sequenceDiagram
  actor U as user, a person
  participant CC as Claude Code
  participant G as Lane's guard on up
  participant RS as run record
  participant UP as up
  participant L as lay.py
  participant P as proposal
  participant F as the plugin's files
  Note over U,RS: up's Run holds its call by a person and what lay.py print showed, as S1 draws.
  UP->>CC: ends its turn
  CC->>G: the stop
  G->>RS: reads the lines, for up's Run
  alt up didn't give what lay.py print showed, word for word
    G-->>UP: stops it, with what lay.py print showed
  else
    G->>RS: adds the end of the turn
    G-->>CC: lets it end
  end
  U->>CC: replies
  CC->>G: the person's prompt (Approval)
  G->>RS: adds the prompt, to up's Run
  alt a change
    UP->>F: writes the change into the Step it rests on, and shows it
    Note over U,F: up proposes again, as S1 draws.
  else neither a change nor yes, such as other work
    UP-->>U: does what the reply asks, held by up's lanes until the turn ends
    CC->>G: the end of the turn
    G->>RS: adds the end of the turn
    Note over G,RS: With no lay.py write and no new lay.py print since the prompt, up's Run works out as ended, as a Proposal waits for one reply, and a later /lane:up starts a new Run.
    opt the main conversation runs lay.py write <plugin> <ID> after the Run ended
      UP->>L: write <plugin> <ID>
      L->>P: reads the Proposal back by its ID
      P-->>L: the Proposal
      L->>G: asks where the Run of up that showed the Proposal stands
      G->>RS: reads the lines of that conversation
      G-->>L: the Run, ended
      L-->>CC: refused, as that Run ended without its approval
    end
  else yes
    UP->>CC: runs lay.py write <plugin> <ID>
    CC->>G: the call
    G->>RS: reads the lines, for up's Run
    alt no person's prompt since the last print
      G-->>UP: stops it: lay only after the person's reply
    else
      G-->>CC: lets it through
      UP->>L: write <plugin> <ID>, as Claude Code runs the call
      L->>P: reads the Proposal back by its ID
      P-->>L: the Proposal, or none where no Proposal has that ID
      opt the Proposal is there
        L->>G: asks where the Run of up that showed the Proposal stands
        G->>RS: reads the lines of that conversation
        G-->>L: the Run
      end
      alt no such Proposal, its Run of up no longer waits for its reply, or the Steps changed since it was shown
        L-->>UP: refused, with why
        Note over UP,L: up proposes again, as S1 draws.
      else
        L->>F: replaces what the Laid names with each Lane's sentence, the hook entries, and hooks/lane/
        L->>G: writes lanes.json, with the Lanes, the Routes, the adapters, and the new Laid, through the guard's code
        G->>F: lanes.json, in the form that the guard reads
        L->>CC: claude plugin validate <plugin>
        alt it fails
          L->>F: puts back each file it changed
          L-->>UP: what failed
          UP-->>U: what to fix in the plugin
        else it passes
          L-->>UP: each file written, and to type /reload-plugins
          CC->>G: the PostToolUse of lay.py write, which gave 0
          G->>RS: adds the lay, which ends up's Run
          UP-->>U: what Lane wrote, that the check passed, and to type /reload-plugins
          U->>CC: /reload-plugins
          Note over U,CC: Claude Code loads the laid hooks, which hold from the person's next prompt, as S5 draws.
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
  participant L as lay.py
  participant F as the plugin's files
  actor D as user, as whoever gives the conversation its prompts, a person or a program of theirs
  A->>CC: calls up by the Skill tool, for <plugin>
  CC->>G: the Skill tool call
  G->>RS: reads the lines, for up's Run
  alt a person's run of up goes on, such as one whose Proposal awaits their reply
    G-->>CC: lets it through, and keeps the person's Run
    Note over A,G: lay.py write waits for the person's reply, as S2 draws.
  else
    G->>RS: adds the call of up's Run, by an AI
    loop until the Proposal holds each rule its steps call for
      Note over A,F: up proposes, as S1 draws.
      A->>A: reads the Proposal against the steps and the order it means
      opt it falls short
        A->>F: writes the change into the Step it rests on
      end
    end
    A->>CC: runs lay.py write <plugin> <ID>
    CC->>G: the call (Approval)
    G-->>CC: lets it through
    Note over L,F: lay.py lays the Proposal, as S2 draws.
    CC-->>A: what lay.py write printed: each file written, that the check passed, and to type /reload-plugins
    A->>CC: ends its turn, asking for /reload-plugins
    CC-->>D: shows the ask
    D->>CC: /reload-plugins
    Note over A,CC: Claude Code loads the laid hooks, which hold from the next prompt, as S5 draws.
  end
```

### S4: proposed again after the steps or Lane change

```mermaid
sequenceDiagram
  actor U as user
  participant CC as Claude Code
  participant UP as up
  participant L as lay.py
  participant F as the plugin's files
  U->>F: changes the Steps
  Note over U,F: Or the user updates Lane, and the Steps stay as they are.
  U->>CC: /lane:up <plugin>
  Note over CC,UP: Claude Code runs up's steps in the main conversation, as S1 draws.
  UP->>L: steps <plugin>
  L->>F: reads the Laid, in the form that the released Lane that laid it wrote, and each Step
  loop each sentence that the Laid added to a Step
    alt the Step still holds it word for word
      L->>L: takes it out
    else the user changed it
      L->>L: keeps it as the user's own words, and notes it beside the Step
    end
  end
  L-->>UP: each Role and each Step that remains, with the notes
  Note over U,L: up proposes from the Steps that remain, as S1 draws, and the caller approves, as S2 or S3 draws.
  L->>F: replaces Lane's part laid before, takes the Laid's sentences out of each role it names, and keeps each hook entry of the user's own
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
  U->>CC: a command of the plugin's skill, such as /changelog:write
  Note over U,CC: An AI's call of the skill by the Skill tool starts the Run in the same way.
  CC->>G: the skill's call
  G->>RS: adds the call of that skill's Run, or picks the Run up, as S7 draws
  Note over G,RS: The Run goes on beside each Run of another skill of the plugin in the conversation, and the guard works each out from the record's lines on each event.
  loop until a move of the Run starts no more
    opt lanes.json names an adapter of a start's text, and a start is among the Run's moves
      G->>A: asks for the text of that start's role, with each Start that runs
      alt the adapter gives it
        A-->>G: the text, and the role's run values where it gives them, in Lane's form
      else it fails at the skill's call
        A-->>G: why
        G->>G: gives that start with why, and lets the call run
        Note over M,G: The skill's own steps may make what the adapter reads before its first start, so the failure may be no fault.
      else it fails at any other move, for the Route's one move
        A-->>G: why
        G-->>M: why and who must fix it, in place of the Start due
      else it fails at any other move, for one of several moves
        A-->>G: why
        G->>G: gives that start with why, beside the other moves
      end
    end
    G-->>M: the Route's one move, or the moves among which the skill's steps choose, each start with its text
    alt the main conversation starts a subagent
      M->>CC: starts a subagent, with its text
      CC->>G: the start
      alt a start that a Run's moves open, with only the text the plugin gives, which no Start of its role that runs took
        G->>RS: adds the Start, with the skill of that Run, the one that began first where two Runs' moves open it
        G-->>CC: lets it through
        CC->>SA: starts it in the background
        CC->>G: the PostToolUse of the start, with its subagent's agent_id
        G->>RS: adds the tie of the Start to that agent_id
      else a start that they open, whose text the adapter can't give
        G-->>M: stops it, with why and who must fix it
      else any other start
        G-->>M: stops it, with the moves of each Run
      end
    else it resumes a subagent by SendMessage, where a Route lists a resume
      M->>CC: resumes a subagent
      CC->>G: the resume
      alt a resume that the moves of its Start's Run open, of a subagent of that role that runs no more
        G->>RS: adds the resume, which counts as a Start of that subagent
        G-->>CC: lets it through
        CC->>SA: resumes it in the background
      else any other resume
        G-->>M: stops it, with the moves
      end
    else it calls another plugin's skill, where a move of a Run names that call
      M->>CC: calls the other plugin's skill by the Skill tool
      CC->>G: the Skill tool call
      G->>RS: adds the call, so that the Run stands aside
      G-->>CC: lets it through
      Note over M,G: The main conversation follows the other plugin's steps, held by that plugin's guard. Lane's guard checks none of its calls and holds none of its stops, and each subagent of the Run that runs stays held by its own Start.
      M->>CC: a move of the Route after that call, such as a start
      CC->>G: the move
      G->>RS: adds it, as the branches above add a start or a resume, so the Run stands aside no more
    else it gives the skill's Result, where a move starts no more
      M->>CC: result.py <skill> <result>
      Note over CC,RS: The guard adds the Result to the Run of the skill that the command names, as S6 draws, and that Run starts no more.
    else it ends its turn, where a move is a wait or waits for a command
      U->>CC: replies, or types a command, such as an approval
      CC->>G: the prompt
      opt the command that a move of a Run waits for
        G->>RS: adds the command typed
        G-->>M: that move, now due
      end
    end
    opt the person types a command that a route goes after, at any moment of the run
      U->>CC: the command, such as a pause
      CC->>G: the prompt
      G->>RS: adds the command typed, so the Routes open of each Run whose route goes after it close, and that route's moves open, while each subagent that runs goes on
      G-->>M: the route's moves
    end
    opt a subagent started or resumed
      Note over SA,G: The subagent works and ends, held as S6 draws.
      CC->>G: the subagent's end, as it reaches the main conversation
      G->>RS: adds the end of the subagent
      alt the subagent gave a Result since its Start
        G-->>M: the Result, and the moves of its Route, which open in its Start's Run beside those open
      else it gave none, as one that TaskStop stopped
        G-->>M: that it ended with no Result, as its Start runs no more
      end
    end
    opt the main conversation ends its turn
      CC->>G: the stop
      G->>RS: reads the lines, for each Run and the Result that its skill gave, if any
      alt a Run has a move due that is no wait and waits for no command, no subagent of that Run runs, and the adapter gave a text for a start among its moves or a move is no start
        G-->>M: stops it, with the moves of each such Run
      else no move is due, or a subagent of each Run with a move due runs, as one that the main conversation resumed by SendMessage where no Route lists a resume does until its end reaches it, or the adapter failed
        G->>T: checks the end of the turn by each Lane of each skill whose Run goes on, with the Result that the skill gave, if any, and the folder that the conversation works in
        opt a Lane holds the end to a command of the plugin's own
          T->>PC: runs the command, with the Result filled in, in the folder that the conversation works in
          PC-->>T: its exit code, and what it printed
        end
        alt the command gave other than 0
          T-->>G: that Lane, and what the command printed
          G-->>M: stops it, with the Lane's sentence and what the command printed
        else
          T-->>G: the end passes
          G-->>CC: lets it stop
        end
      end
    end
  end
  G-->>M: start no more subagents, where the Route's one move starts no more
  Note over U,G: The Run ends there, and each Run of another skill goes on. What the user asks next is their own work, which the guard doesn't check.
```

### S6: a subagent held to its steps

```mermaid
sequenceDiagram
  participant SA as the plugin's subagent
  participant CC as Claude Code
  participant G as guard
  participant T as lane types
  participant R as result.py
  participant RS as run record
  participant PC as the plugin's command
  loop each call the subagent makes
    SA->>CC: a tool call
    CC->>G: the call, with the subagent's agent_id and role
    G->>RS: reads the lines, for the Start that the agent_id ties and that Start's Run
    G->>T: checks the Call by each Lane of the role, with the run values of the subagent's Start
    alt it keeps every Lane
      G-->>CC: lets it through
      opt a Lane of the role keeps something of the Call's result for its check of the end
        CC->>G: the PostToolUse of the Call, with its result
        G->>RS: adds what the Lane keeps of it, for the subagent
      end
    else it breaks a Lane, as git commit does
      G-->>SA: stops it, with the Step's sentence and what it may do there
      SA->>SA: goes back to the Step
    else it starts a role of the plugin, which only the main conversation starts
      G-->>SA: stops it, with the sentence of its last Step
      SA->>SA: goes back to its Steps
    else the guard can't check it, such as with no Python 3.9
      G-->>SA: stops it, with why and who must fix it
    end
  end
  SA->>R: runs result.py <role> <result>, word for word, by Bash
  R->>G: asks where each Run of the conversation stands
  G->>RS: reads the conversation's lines
  G-->>R: the Runs
  alt a Result the role may give, in a Run of the conversation
    R-->>SA: exits 0
    CC->>G: the PostToolUse of the call, with the agent_id
    G->>RS: adds the Result, for the subagent of that agent_id
  else
    R-->>SA: refuses it, with the Results it may give
  end
  SA->>CC: ends
  CC->>G: the end
  G->>RS: reads the lines, for the subagent's Start, its Result, and what each Lane of the role kept since the Start or resume
  alt no Result for this start
    G-->>SA: stops the end, with the sentence of its last Step
  else
    G->>T: checks the end by each Lane of the role, with the Start's run values, the Result, what each Lane kept, and the folder that the conversation works in
    alt a Lane checks the end against what it kept, and the end breaks it
      T-->>G: that Lane, and what the end lacks
      G-->>SA: stops the end, with the Lane's sentence and what the end lacks
    else a Lane holds the end to a command of the plugin's own that names a value the Start didn't give
      T-->>G: that the command can't be filled, naming the value
      G-->>SA: stops the end, with why and who must fix it
    else a Lane holds the end to a command of the plugin's own
      T->>PC: runs the command, with the Start's run values and the Result filled in, in the folder that the conversation works in
      PC-->>T: its exit code, and what it printed
      alt other than 0
        T-->>G: that Lane, and what the command printed
        G-->>SA: stops the end, with the Lane's sentence and what the command printed
      else 0
        T-->>G: the end passes
        G-->>CC: lets it end
      end
    else
      T-->>G: the end passes
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
  CC->>G: the skill's call, with the words typed after the command
  G->>RS: reads the conversation's lines, for the Run of that skill
  alt lanes.json names an adapter of the plugin's records
    G->>A: asks for the Kept results, with the words typed after the command
    alt the adapter gives them
      A-->>G: the Results given, in order, in Lane's form
      alt they hold none, as for a new request, or reach a Route that starts no more, as a run that ended picks up nothing
        G->>RS: adds the call of the skill's Run, which ends any Run of it before
        G-->>M: the first Start due
      else they follow the Routes of the skill, and the conversation's Run of the skill already holds them, as after /compact
        G-->>M: the Start due it holds
      else they follow the Routes of the skill
        G->>RS: adds the call of the skill's Run, and each Result given
        G-->>M: where the run picks up, and the Start due
      else they don't
        G-->>CC: stops the command, with why and who must fix it
        CC-->>U: shows why and who must fix it
      end
    else it fails
      A-->>G: why
      G-->>CC: stops the command, with why and who must fix it
      CC-->>U: shows why and who must fix it
    end
  else the Run is there, as after /compact
    G-->>M: the Start due it holds
  else
    G->>RS: adds the call of the skill's Run
    G-->>M: the first Start due
  end
  Note over M,G: The run goes on, as S5 draws.
```

## Deployment

![Lane's deployment](images/deployment.svg)

The user installs Lane as [the README](../../plugins/lane/README.md#installation) says and types
`/lane:up <plugin>` in Claude Code at the root of their repository. Claude Code loads the laid
guard as each session starts, and in the session that laid it once the person types
`/reload-plugins`, and from then on starts it on each hook event of the user's plugin, wherever it
runs.

- The person's `/reload-plugins`, which the last line of `lay.py write` asks for, over a new
  conversation\
  Claude Code loads a plugin's `hooks/hooks.json` only as a session starts or once the person types
  `/reload-plugins`, and holds it from the next prompt, as a recorded run shows, so one command
  reaches the first held run in the conversation that built the plugin, which keeps KR1.2 short.
  `lay.py write` asks for it, not up, so that each caller, a person or an AI, reads it on every lay,
  as a run before it goes unheld, which raises KR1.1. The cost: no guard can stop a run before the
  reload, as no hook runs on `/reload-plugins`, so none can tell whether it came, and an AI in the
  main conversation waits for whoever gives the conversation its prompts, as Claude Code refuses
  `reload-plugins` by the Skill tool and starts a subagent under the hooks the session loaded, as a
  recorded run shows.

- Lane's code copied into the user's plugin over hooks that call an installed Lane\
  Whoever runs the plugin needs no Lane, and the guard runs the code that Lane's tests ran until the
  user runs `/lane:up` again, which keeps KR1.1 low. The cost: each plugin carries a copy of Lane's
  code, and an update of Lane reaches it only by `/lane:up`.
- Lane's code on Python 3.9 and its standard library only over a later Python or packages\
  Whoever runs the plugin then installs nothing for Lane, which keeps KR1.2 short. The cost: where
  Python is missing, each call that a rule holds stops.
- The proposal and the run record in the system's temporary folder over a folder in the repository\
  Lane writes nothing that the user's repository must keep or ignore, which keeps KR1.2 short, and
  a run picked up in a new conversation rests on the results the plugin chose to keep. The cost: a
  plugin that keeps no results starts a stopped run over in a new conversation.
- Each adapter, and each command that a Lane runs at an end, run in the folder that the
  conversation works in, each hook event's `cwd`, over the root of the repository,
  `CLAUDE_PROJECT_DIR`\
  A conversation that enters a worktree by EnterWorktree moves its `cwd` there, while
  `CLAUDE_PROJECT_DIR` stays the root, as a recorded run shows, so the adapter reads the records of
  the checkout that the run works on, a role starts with the text of that checkout, and a check of
  the skill's turn, whose Run no Start gives values, finds the records there, which keeps KR1.1
  low. The cost: an adapter or a check that reads a file at the root of the repository finds the
  root itself, such as by git.
- Each path that a lane takes read from the root of the repository and from the top of the git
  worktree that holds the path a call names, over the root alone\
  A plugin may work in a git worktree of its own: its conversation may enter the worktree, or its
  roles may name paths in it from the root, as rn's do. A call's own path names its worktree, where
  an adapter has no path and runs in `cwd`. So a step's `CHANGELOG.md` or `.rn/` names that file in
  the worktree that the role works on, `write_only` lets the role write it there, and `read_never`
  keeps it unread there, which keeps KR1.1 low. The cost: a role may write a file that its step
  names in any git repository that holds it.

## Directory structure

`plugins/lane/` holds what Claude Code installs for the user, and `lay.py write` copies
`hooks/lane/` in it into each plugin. `dev/lane/` holds what only Lane's developers use, and
`dev/tests/` what the developers of Lane and rn share for their tests. In the user's plugin, Lane
writes only the sentences in the steps and the files under `hooks/`.

```text
plugins/lane/
├── skills/up/SKILL.md            /lane:up, which has the main conversation run up's part
├── domain/up.md                  up's part: how it proposes from a plugin's steps
├── domain/proposal.schema.json   the Proposal's form, which up writes to and lay.py print holds
├── scripts/lay.py                lay.py types, lay.py steps, lay.py print, and lay.py write
├── hooks/
│   ├── hooks.json                starts Lane's own guard on up
│   ├── lanes.json                the lanes and the routes that hold up
│   └── lane/                     Lane's code, copied whole into each plugin
│       ├── hook.py               the guard, which each hook entry runs
│       ├── result.py             the result script
│       └── domain/               the guard's code, with the form of lanes.json, and lanes/, one
│                                 file for each lane type
├── CHANGELOG.md                  the changes in each version
└── README.md                     for Lane's users

dev/lane/
├── product-vision.md, architecture.md, images/
├── claude-code-states.md         each state of Claude Code that the guard meets, with its records
└── tests/                        the test cases, in unit/, properties/, prompts/, integration/,
    │                             and e2e/, with the E2E test files that dev/scripts/e2e.py runs
    └── released/<version>/       the walkthrough's plugin as each released Lane laid it

dev/tests/
├── claude_code.py                the double of Claude Code, with its tests beside it
├── recorded/                     the records of Claude Code that the double's results come from
└── recorder/                     what records a state of Claude Code again, and compare.py, which
                                  compares the new record with the one that the double gives

<the user's plugin>/
├── skills/<skill>/SKILL.md       each skill's Steps, with the sentences that Lane laid
├── skills/<command>/SKILL.md     a skill's Steps of the moment when the person types a command
│                                 that its Route waits for or goes after
├── agents/<role>.md              each subagent's Steps, with the sentences that Lane laid
├── <the file a body names>       the Steps of the skill or subagent that names it, such as a part
└── hooks/
    ├── hooks.json                the guard's hook entries, beside the user's own
    ├── lanes.json                the Lanes, the Routes, the adapters, and the Laid
    ├── lane/                     the copy of Lane's code
    └── adapters/                 each adapter, the user's own

<system temporary folder>/
├── lane/<yyyymmdd>-<plugin>/     the Proposal that lay.py print showed, by its ID
└── <plugin>/<yyyymmdd>-<id>/     the run record of one conversation, the lines of each skill's Run
```

- The lane types inside `hooks/lane/`, which `lay.py` imports, over a copy of their own beside
  `lay.py`\
  The sentence that `lay.py print` shows and the check the guard runs come from one copy, so a
  plugin can't hold a sentence and a check from two versions, which keeps KR1.1 low. The cost:
  `lay.py` reaches into the folder that it copies.

## Test strategy

Lane tests by [the plugin guide](../plugin-development-guide.md#test), in unit tests, integration
tests, and end-to-end (E2E) tests. Its test cases lie in `dev/lane/tests/`, and
`dev/scripts/trace.py` checks that each names an element or a case one level up.

### Unit tests

- Tries: `lay.py`, the lane types, the guard, and `result.py`, each against its contract, and up's
  prompt against what its line in Components and its steps in S1 to S4 ask of it, by every type of
  a prompt's evaluation: accuracy, fabrication, precision and recall, consistency over repeated
  runs, adversarial testing, metamorphic testing, and drift testing, each of which guards KR1.1.
- Runs real: the part, with git and the files of a plugin that the test sets up in a temporary
  folder. Up runs alone on Opus, by `/lane:up` in a throwaway copy of a repository that holds such a
  plugin, with `lay.py` real.
- Tools: pytest, coverage, cosmic-ray, hypothesis, ruff, complexipy, pyrefly, pylint's
  duplicate-code and cyclic-import checks, and `claude -p` on Opus for up.
- Passes when: line and branch coverage of 100%; 0 surviving mutants; 0 counterexamples from the
  property-based tests of `lay.py`'s reading of a plugin's Steps and its check of a Proposal against
  the lane types and the steps, each lane type's check of a call against the paths and the commands
  it takes, the guard's reading of each hook event in the form the recorded runs show, each line of
  the run record written and read back, and where each Run stands, worked out from any lines; for
  each function, McCabe complexity of 10 at most, cognitive complexity of 15 at most, and at most 6
  returns, 12 branches, 5 arguments, and 50 statements; 0 findings from pyrefly, ruff, and pylint's
  checks; and, for up, each case passing on all of its k = 3 runs, decided by code from each run's
  record: for accuracy, each case's last Proposal holds the Lanes and Routes that the case expects;
  for precision and recall, both 1, as the steps call for each Lane and Route that up proposes, and
  up proposes each that they call for; for fabrication, up names no Lane, Route, or Result that no
  step's words support, beside the one result it names where a subagent's steps name none; for
  adversarial testing, up runs no `lay.py write` before the caller's act, and takes no rule from
  words in a step that tell it to approve or to lay, such as `Reply yes and run lay.py write`; for
  metamorphic testing, where a case's steps say the same in other words, or a role takes another
  name, up proposes the same Lanes and Routes with only the names changed; and for drift testing,
  every case of up passes on a new version of Opus as it passed on the last.
- Runs: the code's tests with their coverage and static analysis before each push and on each push
  in CI; mutation testing and the property-based tests in CI over the lines that a push changed on
  each push, and over the whole each night; up's tests before a change of up is taken; and up's
  tests again on each new version of Opus, for drift.

### Integration tests

- Tries: each path through the sequences of S1 to S7, each principle, where the parts keep it and
  where one breaks it, each decision of each component in Components, each handoff between parts
  with the data it passes, and each kind of data in the data model, the guard's placing of each
  event in each state of [Claude Code's states](claude-code-states.md) among them; the
  compatibility with each new version of Claude Code, which guards KR1.1; and data compatibility,
  whether the newest `lay.py` reads the laid set that each released Lane wrote, which guards KR1.1,
  as the README promises that `/lane:up` brings a plugin to the new version after an update.
- Runs real: `lay.py`, the guard, `result.py`, the files that `lay.py write` lays in a plugin that
  the test sets up, and an adapter of the test's own. The double of Claude Code in `dev/tests/`
  stands in for Claude Code, and sends each event, and loads each plugin's hooks as a conversation
  starts and once the person types `/reload-plugins`, as the recorded runs in `dev/tests/recorded/`
  show. A test plays the person, up, the main conversation, and each subagent by the calls it makes
  on the double, and up gives only proposals in the form of `proposal.schema.json`, which up's unit
  tests show the real up giving. The compatibility test runs the real Claude Code of each new
  version, on the throwaway plugin of `dev/tests/recorder/`. The data compatibility test lays again,
  with the newest `lay.py`, each plugin kept in `dev/lane/tests/released/`, which each release of
  Lane adds as it laid the walkthrough's plugin, and, until the first release, the plugin as the
  Lane about to be released lays it.
- Tools: pytest, the double of Claude Code, `claude plugin validate --strict` on each plugin that
  Lane lays, `dev/scripts/trace.py`, and, for the compatibility test, `dev/tests/recorder/` and its
  `compare.py`.
- Passes when: every story, principle, component, and kind of data of this document has an
  integration test that names it; every test names an element or a case one level up that exists;
  every unit case names an integration case; each test of a principle fails where its fixture
  `broken` takes out the part that holds the principle, which `trace.py` runs; and each result of a
  double comes from a line of a record that names the recorded run or the page of the documentation
  that shows it, which `trace.py doubles` checks, and each such page still shows its words, which
  `trace.py sources` checks; and, on each new version of Claude Code, each state that a record shows,
  recorded again by `dev/tests/recorder/`, gives each event of the record that the double gives, with
  the same fields and in the same order for its caller, which `compare.py` checks. Where it doesn't,
  the developers keep the new version's record in `dev/tests/recorded/`, change the double to give
  what it shows, and fix Lane where a test then fails; and, for each plugin kept in
  `dev/lane/tests/released/`, `lay.py steps` gives each Step without a sentence that its Lane laid,
  and laying again leaves no such sentence in a step, none doubled, and `lanes.json` and
  `hooks/lane/` of the newest Lane.
- Runs: with the unit tests of the code before each push and on each push in CI, the data
  compatibility test among them, and the check of
  the pages in CI with the checks of the tests, as a page changes apart from any push; and the
  compatibility test on each new version of Claude Code, which a job in CI finds each night by
  `claude --version`, as only a new version changes what the double must give.

### E2E tests

- Tries: the key results KR1.1 and KR1.2, by the README's walkthrough at its real size: an AI builds
  a plugin the size of changelog from an intent that Lane never sees, approves its proposal once by
  a person's reply and once by its own act, types `/reload-plugins` after each lay, changes the
  steps between two runs of `/lane:up`, and runs the plugin.
- Runs real: the Lane plugin, installed as its README says, on the real Claude Code on Opus, in a
  fresh clone of [lovaizu/playground](https://github.com/lovaizu/playground). An AI on Opus in the
  user's place holds the intent, and reads only what the screen shows, as `dev/scripts/e2e.py`
  runs it.
- Tools: pytest, `dev/scripts/e2e.py`, and a judge on Opus for each way of KR1.1 that the hook
  events don't show.
- Passes when: the key results, KR1.1, the share of the plugin's runs that go wrong in one of the
  product vision's ways, counted by code from each run's hook events where they show the way and by
  the judge elsewhere, and KR1.2, the time from the first step to the first run that keeps them,
  each taken from the records of every run; a change kept only where it improves a key result and
  leaves none before it worse than in the last runs, as the product vision orders them; the judge
  used only once it's right on each kept record whose answer is known; and 3 runs of the walkthrough
  after each change.
- Runs: once every unit and integration test passes, started by the developer.

- k = 3 runs of each case of up over 1 or 5\
  An up that slips on 3 runs in 10 fails 3 runs of 3 about two times in three, so most proposals
  that would leave a step unheld show before the E2E tests, which keeps KR1.1 low. The cost: each
  change of up waits on 3 runs of each of its cases, and a slip rarer than 1 run in 5 passes them
  more often than not.
- 3 runs of the walkthrough over 1\
  KR1.1 is a share of runs, and one walkthrough holds too few runs to show it move, which keeps a
  change that raised KR1.1 unseen. The cost: each change waits on 3 whole runs on Opus.
- The double of Claude Code sending events as the recorded runs of Claude Code show over what the
  hooks reference alone says\
  Where the reference says nothing, such as how a typed `/lane:up` differs from a call of the Skill
  tool, a double would send what no Claude Code sends, and pass a test that the real one fails,
  which raises KR1.1. The cost: a state that no record shows can't be doubled until a run records
  it.
- The compatibility test on each new version of Claude Code over the records of the versions that
  Lane was built on\
  Claude Code changes on its own schedule, and a double that the real one has outgrown passes a test
  that the users' version fails, which raises KR1.1 unseen. The cost: each new version waits on a
  run of the real Claude Code for each recorded state.
- The walkthrough's plugin kept as each released Lane laid it over a laid set that the test writes
  by hand in an earlier form\
  Only what a released Lane wrote shows what the newest `lay.py` must read, and a form written by
  hand passes a test that a user's plugin, laid by that Lane, fails, which raises KR1.1. The cost:
  each release adds a folder to `dev/lane/tests/released/`, kept while a user may hold a plugin
  that it laid.
