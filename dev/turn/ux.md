# turn UX

turn makes the work a plugin's step asks for and returns it with each item of the step's checklists
judged by a reader that did not make it. Build and change every part of turn so that the AI calling
it gets that on every run.

## Users and goals

- G1: The calling AI, the AI that runs a step of a plugin and calls turn from it, wants the work
  that step makes to come back meeting the step's checklists on every run.

  A checklist lists what the receiver, the one the work is for, should get from the work, one item
  each, asked as a question. An item's Good is the judgment that the receiver gets from the work
  what the item asks, with the lines of the work that give it.

## Key results

They stand from the highest priority: time is never saved by leaving the calling AI more to fix,
since a work it must fix costs the user, the person using the plugin the calling AI runs a step
of, the fixing as well as the wait.

- KR1.1: The items of the step's checklists the calling AI judges the work, when it comes back,
  to meet; more is better, and every item once the goal is reached.

  The calling AI judges each item from its own check of each Good at its lines, not from turn's
  judgment of itself, so an item turn says it meets and does not is not counted.
- KR1.2: The time from calling turn to the work coming back, for a work the size of one README;
  shorter is better.

  The calling AI cannot go on with its step while it waits, so the user waits as long.

## Scenes

The user, the calling AI and turn take part.

A CCS is the JSON file in which the calling AI keeps its task, in the shape
[ACC](https://arxiv.org/abs/2601.11653) gives it: parts, each a list of entries, each entry a kind
and its value, every name the calling AI's own. It holds what is decided, where the work goes, the
checklists, the receiver, what they use the work for and what they have with it; the call names the
kinds the calling AI uses in it for each of these. The result holds each item's Good with its lines,
and the lessons from the run, what fell short in it and why, for the calling AI to put to the user.

### From a step that needs a work to the step's end

```mermaid
sequenceDiagram
  participant U as user<br/>#lt;person#gt;
  participant C as calling AI<br/>#lt;AI#gt;
  participant T as turn<br/>#lt;plugin#gt;
  C->>U: asks what the checklists' items need
  U->>C: answers
  Note over C: writes a CCS
  C->>T: calls it with the CCS's path, its kinds, where to write the result, and the command that checks the work or none
  T-->>C: the work where it goes, and the result
  Note over C: checks each Good against its lines, ends its step
```

### While turn runs

```mermaid
sequenceDiagram
  participant U as user<br/>#lt;person#gt;
  participant C as calling AI<br/>#lt;AI#gt;
  participant T as turn<br/>#lt;plugin#gt;
  loop each of turn's agents
    T-->>U: in the main conversation, what it will do, how far and how, then what is done and what comes next
  end
  opt a run going a slow or wrong way
    U->>C: stops it
  end
```

- A run going a slow or wrong way shows before its time is spent, not after the work comes back.
- Where the calling AI is an agent, the lines reach the main conversation above it, which alone
  talks with the user.

### A point only the user can decide

```mermaid
sequenceDiagram
  participant U as user<br/>#lt;person#gt;
  participant C as calling AI<br/>#lt;AI#gt;
  participant T as turn<br/>#lt;plugin#gt;
  T->>C: the question, before the work that rests on it is made
  C->>U: puts it to the user
  U->>C: answer
  C->>T: the answer
  Note over T: goes on from there
```

- turn asks where the CCS lacks what the run needs, making the work meets a point only the user
  can decide, or an item is still without Good after the readings turn allows.

### Stopped, and gone on

```mermaid
sequenceDiagram
  participant C as calling AI<br/>#lt;AI#gt;
  participant T as turn<br/>#lt;plugin#gt;
  Note over C,T: the run stopped anywhere, by the user or by a conversation that ended
  C->>T: calls it again with the same call
  Note over T: goes on from where it stopped
```

## Benefits

- The calling AI gets the work already read by a reader that did not make it, in the receiver's
  place, and made again where that reading found no Good, so it does not judge an item on its own
  assumption.
- Each Good comes with the lines it rests on, so the calling AI checks it by reading those lines.
- The work is made from the CCS and the files it names alone, so it does not stray from what was
  decided.
