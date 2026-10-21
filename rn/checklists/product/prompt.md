---
name: prompt
version: 0.2.0
---

# Prompt

A prompt, a skill or an agent, is read by an AI. From it alone, the AI can judge for itself, and
achieves the same purpose however often it is run. What only the user can decide, it hands back to
the user.

A prompt is worked out in this order, each step the ground of the next:

1. Decide its purpose: what it achieves, and when it is used. The `description` is written from
   this.
2. From the purpose, decide the role expected of the AI and why, since the AI can judge for itself
   when it knows both. What only the user can decide is set apart here, outside the role.
3. From the role, decide the steps that bring the same result each time it is run, with the form
   of what each step takes in and hands on.
4. From the steps, decide what hooks check on every run, where the AI's tool calls show it: they
   limit the AI to what its steps allow, and hold it at a step until what the step must do is done.
   A hook backs the step and its reason and does not stand in for them, since what shows in no
   tool call, such as what the AI weighs, rests on them alone.

Each item of `usability.md` also applies to a prompt.

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
   - In: <what it takes in, and its form>; if any of it is missing, it hands the step back to
     whoever gave it, saying what is missing, before starting
   - Out: <what it hands on, and its form>; before handing it on, it checks it against the step's
     purpose, such as a document being where it was asked for or code's tests running and
     passing, and fixes what falls short
```

- `name` and `description` are what Claude Code reads to choose a skill or an agent; the
  description says when to use it, since that is what the choice is made on.
- Every step is numbered in the order it is done; a form may be set in a template or schema the
  step names.

Why: the AI finds its purpose, its role and what to do in the same place in every prompt, each the
ground of the next; a step that checks what it takes in sends a gap back where it is cheapest to
fill, and one that checks what it hands on against its purpose hands on no slip it could have found.

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

### B-6: The user's decisions handed back

Scope: whole

When the AI meets something only the user decides, does the user make that decision?

Look at: the prompt has the AI hand such a thing to the user rather than settle it.

Why: an AI that decides for the user leaves its guess to be taken as the user's choice.

### B-10: An action hard to undo, asked first

Scope: whole

Can the user stop an action that is hard to undo before the AI takes it?

Look at: the prompt has the AI ask the user before such an action, such as deleting, merging or
sending.

Why: an action hard to undo cannot be taken back once the user sees it.

### B-21: The scope of its inputs

Scope: whole

Does the AI do all its work from a scope of inputs the prompt sets?

Look at: the prompt names the whole of what the AI reads, what it works on and what it consults for
reference, such as other code it follows, and has the AI work from that scope.

Why: what the AI reads outside a set scope shapes its work without anyone having chosen it; what it
is meant to consult, left unnamed, is found on some runs and missed on others.

### B-27: Each input read in a way its tool calls show whole

Scope: its part

Does each step name how the AI reads each of its inputs, in a way its tool calls show read whole?

Look at: each input of B-21 the step reads, with its way, such as one file to a command, or a
script that shows page by page what is too long for one read; a step that says "read" with no way
fails.

Why: told no way to read, the AI reads in ways a hook cannot count, such as several files in a
loop or part of a long file, and is stopped for nothing or goes on on a part read.

### B-3: Everything that must happen every time

Scope: its part

Does the AI do, on every run, everything that must happen, because each such thing is a step?

Look for: what the AI receives and where it reads it, what it hands back and where it writes it, and
each thing it must do in full, such as reading a file whole; one given only as advice, or not at
all, fails. Each is written in the Steps as an instruction to act; one given as a rule or principle
to keep fails.

Why: what is left out of the steps is done on some runs and not on others; a check given only as
advice is the step that gets skipped; a rule says what must hold, not what to do, so the AI judges
when it applies and keeps it on some runs only.

### B-7: Done in the order it must be

Scope: its part

Does the AI do each thing that must happen in the order it must be done?

Look at: the steps, read from the first, against the order the work needs: an input is read before
the step that uses it, and a thing done only when an earlier step calls for it, such as opening a
file the work links, comes after that step; one placed before it fails.

Why: a thing done before what it rests on is done on a guess, and a check done after the work is
handed back catches nothing in time.

### B-8: What breaks, set down exactly

Scope: its part

Does the AI do, the same way on every run, each part of a step that breaks when done a little
differently?

Look at: each such part, such as a command, a path, a field name or a form another step or a script
reads, written out exactly in the prompt; one left for the AI to phrase fails.

Why: a part that breaks when done a little differently, left loose, comes out differently on some
run and breaks what reads it.

### B-17: Scripts for what must come out the same

Scope: its part

Does the AI get the same result on every run from each operation that must give it?

Look at: each such operation done by a script the AI runs; one the AI works out itself fails.

Why: a script gives the same result every time and spends no attention; the same operation worked
out by the AI varies from run to run.

### B-19: What the user must see, shown by a tool

Scope: its part

Does the user see, on every run, each thing they must see while the AI is still at work?

Look at: each such thing shown by a script or a hook; one left to the AI's words between its tool
calls fails.

Why: the AI writes words between its tool calls on some runs and not on others, so what rests on
them reaches the user only sometimes; a hook shows it on every run.

### B-13: Details read only when needed

Scope: whole

Does the AI read each detail it needs only on some runs on those runs alone?

Look at: each such detail of the prompt's own kept in a file of its own, which the prompt says when
to read; one written in the prompt itself fails. Each input the AI needs only when something in the
run calls for it, such as a file the work links, read where the steps meet that call; one read on
every run, because the prompt names it, fails.

Why: a detail read on every run costs attention on the runs that do not need it, and an input read
on a run that did not call for it shapes the work there, as the AI would not have had it.

### B-14: Detail files named in the prompt

Scope: whole

Does the AI reach each file of details straight from the prompt?

Look at: each such file named directly in the prompt; one named only in another file fails.

Why: a file reached only through another file is often read in part.

### B-4: Its own judgment within a step

Scope: its part

Is the AI left to decide how to think within each step?

Look at: each step says what to do; one that sets out how to reason toward it, where nothing that
follows breaks if the AI reasons another way, fails.

Why: the AI often reasons better than a plan written for it, so a step set down in more detail than
its work needs narrows the AI where it would have done better.

### B-12: What to do

Scope: whole

Can the AI tell from each instruction the action to take?

Look at: each instruction says the action in positive terms; one that says what to avoid, even
beside what to do, fails.

Why: an instruction that names what to avoid leaves the right action to be guessed, and puts what
to avoid in the AI's attention.

### B-20: The reason for each instruction

Scope: whole

Can the AI tell why each instruction is there?

Look at: each instruction whose reason the Role does not already give carries its reason beside it.

Why: an AI that knows why applies the instruction to cases it did not name, and keeps to it where a
bare rule is read narrowly.

### B-18: Each field used by someone

Scope: its part

Does the AI fill only the fields that someone uses?

Look at: each field in the form of what the AI receives and hands back, matched to the AI or to
whoever receives its work, using it toward the purpose; a field matched to no one fails.

Why: a field nobody uses still has to be read and filled on every run, and drifts from what the
work actually is, since nothing checks it.

### B-23: When a place is written

Scope: its part

Is each place of the form that the AI may fill or leave, such as one per item, written on the
condition that whoever reads the form takes a written place to mean, because the prompt sets that
condition?

Look at: the prompt's words on when such a place is written, against what the step or script that
reads the form takes a place to mean, such as the receiver getting what the item asks; a prompt that
leaves the condition to the AI, or sets a looser one, such as a part of what the item asks or what
the AI can say about the item, fails.

Why: a place written on a looser condition than its reader counts on is read as what it is not, such
as a note that nothing was found read as a find.

### B-15: Examples close to the real work

Scope: whole

Does the AI learn from each example what the work it will actually be given asks?

Look at: each example, against a task the prompt is actually given: the same kind of input and the
same kind of result.

Why: the AI copies examples closely, and one far from the real work steers it away from that work.

### B-16: Examples alike only on purpose

Scope: whole

Does the AI take from the examples only what they are meant to share?

Look at: each thing all the examples share, such as their length, subject, wording or order,
matched to something the prompt asks; a shared thing matched to nothing fails.

Why: the AI takes what its examples share as part of what is asked, so a likeness left by chance is
copied too.

### B-26: Each step's bounds held by a hook

Scope: whole

Is the AI stopped when it does what no step allows and its tool calls show it?

Look at: each bound the steps set, such as the inputs of B-21, the places a step writes and an
action hard to undo, held by a hook that stops a tool call outside it and says why; one left to the
AI's word alone fails.

Why: what an AI does outside its steps on some run, such as reading a file it was not given, shapes
the work unseen; a hook stops it on every run.

### B-25: Each step seen done by a hook

Scope: whole

Is the AI stopped, while it can still do it, when it leaves out a step that must happen every time
and that shows in its tool calls?

Look at: each step of B-3 that shows in the AI's tool calls, such as every input of the step read
whole since it last changed, a step begun only once those before it are done, a command run or a
place written, checked by a hook that names the step and why it is there; one left to the AI's word
alone fails. What shows in no tool call,
such as what the AI weighs, stays with the step and its reason.

Why: an AI given a clear step and its reason still leaves it out on some runs, and the result looks
right; a hook sees it on every run, while the step can still be done.
