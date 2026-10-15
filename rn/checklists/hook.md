---
name: hook
version: 0.1.0
---

# Hook

A hook is run by Claude Code at an event of a session, and is read by its maintainer, who changes
it with confidence, and by whoever its stop reaches, who then knows what went wrong and what to
do. It keeps the AI to the steps its prompts set: a step begun before the steps ahead of it are
done, a step left out, an input not read or an output not written where its step says, each
stopped as it happens. Each item of `code.md` applies to a hook and its tests, with what the hook
stops and lets through as its behavior.

## Benefit

### B-1: Each stop names its step

When a hook stops a call, can whoever is stopped tell which step of the prompts it concerns?

Why: a stop that names no step is a rule out of nowhere, and the AI guesses what to do instead of
doing the step.

### B-2: Each stop says why and what to do

When a hook stops a call, can whoever is stopped tell what the step needs and why, in one
sentence, so that their next move is the step itself?

Why: a stop that says only what was wrong leaves the right move to be guessed, and a stop with no
why is kept narrowly.

### B-3: Nothing stopped outside its session

Can a user whose repository, or whose session, the hook does not concern work without meeting it,
because the hook does nothing where no session of its plugin is open, and nothing when its tools
are missing there?

Look at: a test with no session open, and one with the tool the hook runs on missing, each
letting the call through.

Why: a plugin's hooks run in every session where it is installed, and a stop in a session that is
not the plugin's breaks work the plugin has nothing to do with.

### B-4: Only the call it judges

Can the maintainer tell, from the hook's matcher and its first lines, exactly which event and
which tool calls it judges, with every other call let through?

Why: a hook that reads more calls than it judges costs every call its time, and a call stopped by
a hook not meant for it cannot be traced to a step.

### B-5: The process, not the content

Can the maintainer tell that each check judges whether a step happened, in its order, with its
inputs read and its outputs written, and never whether the work is good?

Why: whether the work serves its purpose is for the reader in its receiver's place; a hook that
judges content stops good work and lets bad through on the shape alone.

### B-6: One check per file

Can the maintainer read, fix and test each check on its own, because each is in a file of its own,
with one entry file per event that runs them?

Why: a check mixed with others is changed with them, and a slip in one is found in the others'
tests.

### B-7: A stop never holds the AI in a loop

When a hook sends the AI back to a step, can the maintainer tell that a second pass through the
same stop lets the AI go on, or that the step can always be done?

Why: a stop the AI cannot satisfy holds it forever, and the user waits on work no one carries on.

## Usability

None: each thing that makes a hook easy to keep or to meet is one its maintainer or the one it
stops gets from it, so its item is in Benefit.

## Format

### F-1: Shape

Does the hook follow this shape?

- `hooks/hooks.json` names each event with its matcher and the one entry file it runs, with a
  guard so that a missing runtime does nothing outside a session.
- `hooks/<event>.py` is the entry file for the event: it reads the event's JSON from standard
  input, runs each check, and on a stop writes the checks' sentences to standard error and exits
  with 2; otherwise 0.
- `hooks/checks/<what it holds>.py` holds one check, a function `check(data)` returning the
  sentences of a stop, or an empty list.

Why: Claude Code reads the hook by this form, and the maintainer finds each check where the form
puts it.
