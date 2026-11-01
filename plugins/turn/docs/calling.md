# Calling turn

How a step of your plugin starts turn, gives it what the step has already settled with the person,
and gets the work back, so you can write the step's text to call it.

## The call

Start the `turn:up` agent with a prompt that says, in plain words, what work to make, such as
"Write the README of this repository". turn needs nothing more: it asks the person the kind of
work and what this work is for.

Where the main conversation starts `turn:up`, it starts it in the background. The main conversation
then stays free to put turn's asks to the person while turn works.

## What you may give

Where your step has already settled a point with the person, add it to the prompt as one JSON line,
so turn does not ask the person again:

```json
{"kind": "readme", "purpose": "<who uses this work, and for what>",
 "decided": [{"what": "<a point settled>", "grounds": "<why, such as the person's words>"}]}
```

- `kind`: the kind of work, such as `readme` or `press-release`. turn takes it without asking the
  person to confirm it.
- `purpose`: this work's purpose. turn puts it at the root of the work's design without asking.
- `decided`: each other point of the work settled, such as where the work goes or the language it
  is written in. turn takes each as decided by the person, and builds the rest of the design on it.

Give each key only where the person has settled it with your step; leave out the rest, and turn
asks for it.

## Asks

What only the person can decide comes to the main conversation as a message from one of turn's
agents, whether the main conversation or one of its agents started `turn:up`. Each message is one
question or one approval, and says the answer turn recommends.

Put it to the person, and send their answer in their own words with SendMessage to the agent that
asked, by the ID shown with its message. turn goes on with that answer.

## What comes back

`turn:up` ends once its second AI finds every question of the kind good, both of what the work says
and of how it says it. Its last reply names each file of the work, by its path from the root of the
repository, one on each line. turn commits, pushes and sends nothing; what happens to the work next
is your step's.

## A run that stopped

You stop a run with TaskStop. Started again for the same work, `turn:up` goes on from what the run
had made, which it keeps in `.turn/` at the root of your repository.
