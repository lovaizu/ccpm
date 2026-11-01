# rn

rn is a Claude Code plugin that takes a piece of work you ask for in rough words to a pull request
that meets your purpose, asking you only what is yours to decide.

rn is for you if you want to hand a whole piece of work in your GitHub repository to an agent, even
work of days, without writing out what you want first. You answer what rn asks, decide at each stop
from what rn shows you there, and get a pull request that meets your purpose.

Claude Code alone builds on your words as they stand, and over days one conversation swells and
drifts. rn first asks you each point behind your words, one per message, with the answer it
recommends, and writes your purpose down as a goal and acceptance criteria that every task serves.
It carries only a short record of the plan from move to move, so the work neither swells nor drifts
and goes on in any conversation. [turn](../turn/README.md), installed with rn, makes each document
and the finished work, and an AI that did not make it uses it in your place before you see it.

**Non-goals**

- rn does not merge: it marks the pull request ready, and the merge is yours.
- rn does not push to your default branch: it works on a branch of its own.
- rn sends nothing to its makers without your yes.
- rn does not change the checklists turn ships: a question you add to the checklist of a kind of
  work goes into `.turn/templates/` in your repository.

## Requirements

- Claude Code.
- A git repository whose remote is on GitHub, with its default branch protected so that it takes a
  change only through a reviewed pull request.
- The GitHub command-line tool `gh`, logged in to an account that can push to the repository.
- Python 3.9 or later, run as `python3`, and `jq`.
- Recommended: Claude Code in a [Docker Sandbox](https://docs.docker.com/ai/sandboxes/) with the
  permission mode `bypassPermissions`, so the agents are not stopped at each command and what they
  do stays inside the sandbox.

## Installation

```console
/plugin marketplace add lovaizu/ccpm
/plugin install rn@ccpm
```

Claude Code installs turn with rn. `claude plugin list` then lists `rn@ccpm` and `turn@ccpm`, each
with `Status: ✔ enabled`.

## Walkthrough

Your app is written in JavaScript, and you want it moved to TypeScript, work that takes days:

```console
> /rn:up move this app to TypeScript
```

rn asks the points to decide, one per message, each with what it looked up and the answer it
recommends:

```console
● Points to decide
  ▶ 1. What the move is for
    2. What shows the move is done

  1. What the move is for
  I take it the move is to stop type mistakes before they ship: three of last quarter's
  production bugs (#81, #87, #93) were a value of the wrong type, undefined where a number
  was expected.
  a. Stop such mistakes before they ship (recommended). Costs more than renaming files, since
     the types must be strict enough to catch them. Can be changed later.
  b. Have the code in TypeScript, however loose its types. Quicker, but the three bugs could
     come back. Can be changed later.
  What is the move for? Answer with a letter or in your own words.

> a
```

From your answers rn writes the goal and the acceptance criteria on a draft pull request, and stops
for your sign-off. `/rn:ty` approves; `/rn:gm <feedback>` asks for a change.

```console
● Goal sign-off
  The goal is on the draft pull request: https://github.com/you/app/pull/42
  G1: A value of the wrong type fails the build. So mistakes like last quarter's three bugs
      do not ship.
  AC1: Code that repeats each of the three bugs fails the build.
  AC2: The app builds and runs as before.
  AC3: Every file of src/cart and src/checkout is TypeScript.
  /rn:ty to approve, /rn:gm <feedback> to ask for a change.

> /rn:ty
```

Where the purpose needs documents, such as an architecture for the move, rn stops for them the same
way. It then carries out the tasks. When you come back another day, `/rn:up` alone, in a new
conversation, brings back the sign-off still waiting, or the next point to decide, and asks nothing
again. rn stops at the finished work with each choice it made without asking you, with why:

```console
● Deliverable sign-off
  The finished work is on the pull request: https://github.com/you/app/pull/42
  deliverable: https://github.com/you/app/blob/typescript/src/cart/bugs.test.ts,
    https://github.com/you/app/blob/typescript/src/cart/cart.ts,
    https://github.com/you/app/blob/typescript/src/checkout/checkout.ts
  - The three bugs are kept as tests in src/cart/bugs.test.ts that must fail to type-check:
    the build already runs the tests, so AC1 is checked on every build.
  /rn:ty to approve, /rn:gm <feedback> to ask for a change.

> /rn:ty
```

Last, rn offers what the work taught, one learning per message, as a question for the checklist of
that kind of work in `.turn/templates/`, or as an issue to rn's makers, and marks the pull request
ready:

```console
● The pull request is ready to merge: https://github.com/you/app/pull/42
```

## How it works

![How rn works](how-it-works.svg)

The orchestrator, rn's AI in your conversation, is the only part that talks with you. rn's scripts
keep the steering, the short record of the plan, on the work's branch, and take an approval only
where Claude Code's record shows you typed it.

## Documentation

- `/rn:up`, `/rn:ty` and `/rn:gm` are all there is to use.
- [The changelog](CHANGELOG.md) says what changed in each version.

## Development

[rn's development folder](../../dev/rn/README.md) holds its UX, its architecture and its tests.

## License

[MIT License](../../LICENSE)
