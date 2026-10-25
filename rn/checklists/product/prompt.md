---
name: prompt
version: 1
made_from:
  checklist: 1
  usability: 1
---

# Prompt

A prompt, a skill or an agent, is read by an AI. From it alone, the AI can judge for itself, and
achieves the same purpose however often it is run. What only the user can decide, it hands back to
the user.

The AI already reasons well and knows common practice, so a prompt gives it only what it would not
know or do without it: the role expected of it and why, and the steps whose doing or order it would
otherwise vary. How exactly a step is set down follows how easily it breaks: what a script, a hook
or another step reads is written exactly, and what nothing reads is left to the AI's judgment. What
must come out the same is done by a script, its form is kept in a form file, and a hook tells the
AI a step it holds again when the AI drifts from it; the prompt names each of these files and does
not say what they hold again.

## Format

### F-1: Shape

Scope: whole

Does the prompt follow this template, headings included?

```markdown
---
name: <name>
description: <What it achieves, and when it is used, in the third person>
---

## Role

<The role expected of the AI, and why; what it hands back to the user>

## Steps

1. <What to do>
```

Every step is numbered in the order it is done.

Why: the AI finds its role and what to do in the same place in every prompt, the role the ground of
the steps.

## Benefit

### B-1: Chosen when it is needed

Scope: its part

From the `description`, can Claude Code tell the runs the skill or agent is for?

Look for: what the prompt achieves, or the situations it is used in, missing or not in the words a
request for it would carry.

Why: Claude Code chooses a skill or an agent by its description alone; one that does not say when
is not chosen where it is needed, or is chosen where it is not.

### B-2: What it is for

Scope: its part

From the Role, can the AI tell what is expected of it and why, so that where the steps run out it
chooses the action that fits the purpose?

Look for: a role holding two jobs that need different things given or a different stance, such as
making a work and judging it, where one could be another role's.

Why: what is expected is what the AI spends its judgment on and checks its work against; given only
what to do, it stops at the end of the steps or goes on by guessing; a role holding two jobs judges
each with what it holds for the other.

### B-3: The same result on every run

Scope: its part

Do the Steps give the AI, in the order the work needs, each thing that must happen on every run,
with each part that something reads set exactly?

Look for:
- a thing that must happen every run, such as reading a file whole, given only as a rule or advice;
- a thing done before what it rests on;
- a part a script, a hook or another step reads, such as a command, a path, a field or a hook's
  sentence, left for the AI to phrase, or a form of what a step takes in or hands on set neither in
  the step nor in a form file it names;
- an operation that must give the same result every run worked out by the AI instead of a script;
- what the AI reads, works on and consults not named whole;
- what it hands back not checked against what it should be before it is handed back;
- a bound of the steps or a step that shows in the AI's tool calls, such as the files it reads or
  writes or a command it runs, held by no hook;
- an example unlike the work the AI is actually given, or examples alike in something the prompt
  does not ask.

Why: what is left out of the steps or loose in them is done one way on some runs and another way on
others, and breaks whatever reads it; an AI given a clear step still leaves it out on some run with
a result that looks right, which a hook sees every time.

### B-4: Each sentence gives what the AI lacks

Scope: each part

Does each sentence give the AI something it would not know or do without it?

Look for:
- a sentence the AI would follow unasked;
- what a script, a form or a hook holds said again, such as a hook's sentence beside the step's own
  words for the same thing;
- one thing said in two places;
- how to reason or go about a step where nothing that follows reads how it was done;
- a detail needed only on some runs kept in the prompt, rather than in a file the prompt names and
  says when to read;
- a field of what the AI takes in or hands back that no one uses.

Why: every sentence competes for the AI's attention with the work in front of it; one it does not
need draws attention from those it does, and a thing said twice comes to say two things.

### B-5: Each instruction taken as meant

Scope: whole

Does the AI take each instruction as the prompt means it?

Look for:
- a word used in a sense of its own that no sentence explains;
- one thing under two names, or one name for two things;
- two instructions that cannot both be followed;
- an instruction that names what to avoid instead of the action to take;
- a place of a form the AI may fill or leave, written on a looser condition than its reader takes a
  written place to mean.

Why: an instruction read another way than meant is followed the other way, and the result looks
right to the AI that followed it.

### B-6: What is the user's decided by the user

Scope: whole

Does each thing only the user can decide reach the user before it is acted on?

Look for:
- a choice only the user can make that the prompt has the AI settle;
- an action hard to undo, such as deleting, merging or sending, taken without asking first.

Why: an AI that decides for the user leaves its guess to be taken as the user's choice, and an
action hard to undo cannot be taken back once the user sees it.

### B-7: What the user must see shown to them

Scope: whole

Does each thing the user must see while the AI works reach them on every run?

Look for: what the user must see while the AI works left to the AI's words between its tool calls,
rather than shown by a script or a hook.

Why: words between tool calls are written on some runs only.
