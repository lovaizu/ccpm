---
name: prompt
version: 0.2.0
---

# Prompt

A prompt, a skill or an agent, is read by an AI. From it alone, the AI can judge for itself, and
achieves the same purpose however often it is run. What only the user can decide, it hands back to
the user.

The AI already reasons well and knows common practice, so a prompt gives it only what it would not
know or do without it: the role expected of it and why, and the steps whose doing or order it would
otherwise vary. How exactly a step is set down follows how easily it breaks: what a script, a hook
or another step reads is written exactly, and what nothing reads is left to the AI's judgment. What
must come out the same is done by a script, its form is kept in a form file, and a step a hook
holds is told again by that hook; the prompt names each of these files and does not say what they
hold again.

Each item of `usability.md` applies to a prompt with the AI's work as its subject. Its B-9 is
answered by the `description`, and its B-16 by the Steps. Its B-19 is answered against what the AI
already knows: a sentence it would follow without being told fails. Its B-7 is answered across the
prompt and the files it names: a step held by a hook says the hook's sentence as its own words, once.

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

### F-2: Form of what goes in and out

Scope: its part

Is the form of what each step takes in and hands on set, in the step or in a form file the step
names?

Why: whoever receives the work, the next step or a script, reads it by its form; a form the AI
chooses afresh on each run breaks them.

## Benefit

### B-22: When it is used

Scope: its part

From the `description`, can Claude Code tell the runs the skill or agent is for?

Look at: the description says what the prompt achieves and the situations it is used in, in the
words a request for it would carry.

Why: Claude Code chooses a skill or an agent by its description alone; one that does not say when
is not chosen where it is needed, or is chosen where it is not.

### B-1: What is expected

Scope: its part

From the Role, can the AI tell what is expected of it?

Why: what is expected is what the AI spends its judgment on and checks its work against; without it,
the AI spends that judgment working out what the prompt is for.

### B-2: Why it is needed

Scope: its part

From the Role, can the AI tell why its work is needed?

Why: an AI that knows why chooses, where the steps run out, the action that fits the purpose; given
only what to do, it stops at the end of the steps or goes on by guessing.

### B-3: Everything that must happen every time

Scope: its part

Is each thing that must happen on every run, and that the AI would not always do unasked, a step?

Look for: what the AI reads, what it writes and where, and each thing it must do in full, given only
as a rule or as advice.

Why: what is left out of the steps is done on some runs and not on others; a rule says what must
hold, not what to do, so the AI judges when it applies and keeps it on some runs only.

### B-7: Done in the order it must be

Scope: its part

Does the AI do each step in the order the work needs?

Look at: an input read before the step that uses it, and a thing done only when an earlier step
calls for it coming after that step.

Why: a thing done before what it rests on is done on a guess.

### B-8: What breaks, set down exactly

Scope: its part

Is each part that something reads, such as a command, a path, a field name or a hook's sentence,
written exactly, in the prompt or in the file it names?

Why: a part read by a script, a hook or another step, left for the AI to phrase, comes out
differently on some run and breaks what reads it.

### B-4: Its own judgment within a step

Scope: its part

Is the AI left to decide how to do each step where nothing reads how it was done?

Look for: a step set out as how to reason or which way to go about it, where nothing that follows
breaks if the AI does it another way.

Why: the AI often does better than a plan written for it, so a step set down in more detail than
its work needs narrows the AI where it would have done better.

### B-17: Scripts for what must come out the same

Scope: its part

Is each operation that must give the same result on every run done by a script the AI runs?

Why: a script gives the same result every time and spends no attention; the same operation worked
out by the AI varies from run to run.

### B-5: Checked before handed back

Scope: its part

Does the AI check what it hands back against what it should be, and fix what falls short, before
handing it back?

Why: a slip caught then is cheap to fix; one handed back goes on to whoever receives it.

### B-19: What the user must see, shown by a tool

Scope: its part

Is each thing the user must see while the AI is still at work shown by a script or a hook?

Why: the AI writes words between its tool calls on some runs and not on others, so what rests on
them reaches the user only sometimes.

### B-18: Each field used by someone

Scope: its part

Is each field of what the AI takes in and hands back used toward the purpose, by the AI or by whoever
receives its work?

Why: a field nobody uses is still read and filled on every run, and drifts from what the work is,
since nothing checks it.

### B-23: When a place is written

Scope: its part

Does the prompt write each place of a form the AI may fill or leave on the condition its reader
takes a written place to mean?

Look for: a place the prompt has written on a looser condition, such as part of what is asked.

Why: a place written on a looser condition than its reader counts on is read as what it is not,
such as a note that nothing was found read as a find.

### B-6: The user's decisions handed back

Scope: whole

When the AI meets something only the user decides, does the prompt have it hand that to the user?

Why: an AI that decides for the user leaves its guess to be taken as the user's choice.

### B-10: An action hard to undo, asked first

Scope: whole

Does the prompt have the AI ask the user before an action hard to undo, such as deleting, merging
or sending?

Why: an action hard to undo cannot be taken back once the user sees it.

### B-21: The scope of its inputs

Scope: whole

Does the prompt name the whole of what the AI reads, works on and consults?

Why: what the AI reads outside a set scope shapes its work without anyone having chosen it; what it
is meant to consult, left unnamed, is found on some runs and missed on others.

### B-13: Details read only when needed

Scope: whole

Is each detail needed only on some runs kept in a file of its own, which the prompt says when to
read?

Why: a detail read on every run costs attention on the runs that do not need it.

### B-14: Detail files named in the prompt

Scope: whole

Is each file of details named directly in the prompt?

Why: a file reached only through another file is often read in part.

### B-12: What to do

Scope: whole

Does each instruction say the action to take, rather than what to avoid?

Why: an instruction that names what to avoid leaves the right action to be guessed, and puts what
to avoid in the AI's attention.

### B-15: Examples close to the real work

Scope: whole

Does each example have the same kind of input and result as the work the AI is actually given?

Why: the AI copies examples closely, and one far from the real work steers it away from that work.

### B-16: Examples alike only on purpose

Scope: whole

Is each thing all the examples share, such as their length, subject or order, something the prompt
asks?

Why: the AI takes what its examples share as part of what is asked, so a likeness left by chance is
copied too.

### B-26: Each step's bounds held by a hook

Scope: whole

Is each bound the steps set that shows in the AI's tool calls, such as the inputs it reads, the
places it writes and an action hard to undo, held by a hook?

Why: what an AI does outside its steps on some run, such as reading a file it was not given, shapes
the work unseen; a hook stops it on every run, and told the step's sentence, the AI goes back to it.

### B-25: Each step seen done by a hook

Scope: whole

Is each step of B-3 that shows in the AI's tool calls, such as an input read whole, a command run or
a place written, checked by a hook while the AI can still do it?

What shows in no tool call, such as what the AI weighs, stays with the step and its reason.

Why: an AI given a clear step and its reason still leaves it out on some runs, and the result looks
right; a hook sees it on every run, while the step can still be done.
