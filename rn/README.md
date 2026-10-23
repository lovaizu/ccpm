# rn

rn keeps a piece of work aimed at your purpose and its execution straight. Every task traces back
to the purpose, and the plan is remade from the facts each move brings; only a short record of where
the work stands is carried from move to move, so a long piece of work neither swells nor drifts. It
is a Claude Code plugin that takes work asked for in rough words to a pull request while you only
answer what it asks, for anyone who would rather hand over work in their GitHub repository, even
work of days, than prepare and watch it.

## Example

Your app is written in JavaScript, and you want it moved to TypeScript, work that takes days. In
your repository, you type what you want:

```console
> /rn:up move this app to TypeScript
```

rn does not start building on those words. It first finds the points to decide, the choices that
change what is made, and asks you one per message, even those it could look up, with what it looked
up and the answer it recommends:

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

● Points to decide
  ✓ 1. What the move is for: stop type mistakes before they ship
  ▶ 2. What shows the move is done

  2. What shows the move is done
  I propose that such a mistake fails the build. Every file ending in .ts is not enough: a
  file moved with loose types would still let the three bugs through.
  a. A value of the wrong type fails the build (recommended). Each file must be typed
     strictly. Can be changed later.
  b. Every file ends in .ts. Done sooner, but does not stop the bugs. Can be changed
     later.
  What shows the move is done? Answer with a letter or in your own words.

> a
```

From your answers rn writes the plan. It holds the goal, which is your purpose as rn wrote it down,
and the acceptance criteria, each one thing the finished work must do for that purpose; the goal
and every criterion get an ID that later messages refer to. Before showing it to you, another AI
that did not write it reads and uses it in your place, and rn makes it again until that AI finds
nothing lacking. Then rn stops at the plan sign-off, the first of three
stops where it shows you a proposal and waits for your answer:

```console
● Plan sign-off
  The plan is on the draft pull request: https://github.com/you/app/pull/42
  G1: A value of the wrong type fails the build, so mistakes like last quarter's three bugs
      do not ship.
  AC1: Code that repeats each of the three bugs fails the build.
  AC2: The app builds and runs as before.
  AC3: Every file of the app is TypeScript.
  /rn:ty to approve, /rn:gm <feedback> to ask for a change.
```

The account pages had none of the three bugs, and you would rather leave them for later, so you ask
for a change. rn keeps your feedback and stops, so you can clear the conversation, or come back
tomorrow:

```console
> /rn:gm leave the account pages in JavaScript for now

● Your feedback is kept. Clear the conversation if you like, then type /rn:up to go on.
```

In a fresh conversation, `/rn:up` goes on from where you stopped, with the point behind your
feedback, one rn did not ask:

```console
> /rn:up

● Points to decide
  ✓ 1. What the move is for: stop type mistakes before they ship
  ✓ 2. What shows the move is done: a value of the wrong type fails the build
  ▶ 3. Which parts move now

  3. Which parts move now
  I propose moving the cart and the checkout now: all three bugs were there (#81, #87, #93
  touch only src/cart and src/checkout).
  a. The cart and the checkout now, the account pages later (recommended). The account
     pages can still let a wrong type through. Can be changed later.
  b. Every part now. The account pages are covered too, but the move takes longer. Can be
     changed later.
  Which parts move now? Answer with a letter or in your own words.

> a

● Plan sign-off
  The plan is on the draft pull request: https://github.com/you/app/pull/42
  Changed: AC3: Every file of src/cart and src/checkout is TypeScript.
  (G1, AC1 and AC2 as before)
  /rn:ty to approve, /rn:gm <feedback> to ask for a change.

> /rn:ty
```

The same goes for the documents the purpose needs, such as a README or a design for what you are
building, which rn writes into your repository on the pull request; here it is a design for the
move. rn asks their points one at a time, such as how the types are made strict file by file, has
an AI that did not write them use them, and stops at the design sign-off:

```console
● Design sign-off
  The design is on the draft pull request: https://github.com/you/app/pull/42
  - Each file moves with strict type checks on, so a moved file lets no wrong type through.
  - Values from the account pages are checked where they enter the cart and the checkout,
    so the JavaScript left there cannot pass a wrong type in.
  - Each of the three bugs is kept as code that must fail the build, so AC1 is checked on
    every build.
  /rn:ty to approve, /rn:gm <feedback> to ask for a change.

> /rn:ty
```

Then rn divides the work into tasks, such as moving the cart, each checked against the acceptance
criteria it serves, and carries them out in the conversation without you watching. Before each step,
rn tells you in a line what it will do, how far and how, and after it, what is done and what comes
next, so you can stop a step going a way you do not want. If a point to decide comes up, rn asks it
there and waits for your answer; if you close Claude Code meanwhile, `/rn:up` in a fresh
conversation goes on from where it stopped. When the work is finished, an AI that did not make it
uses it for each acceptance criterion, and rn stops at the deliverable sign-off:

```console
● Deliverable sign-off
  The finished work is on the pull request: https://github.com/you/app/pull/42
  AC1: Code that repeats each of the three bugs fails the build.
  AC2: The app builds and runs as before.
  AC3: Every file of src/cart and src/checkout is TypeScript.
  /rn:ty to approve, /rn:gm <feedback> to ask for a change.

> /rn:ty
```

rn makes each document and the finished work with its checklist for that kind, which says what that
kind, such as a README or code, must give its reader. What this piece of work taught, rn offers
you as learnings, one per message, each with what happened and where it would make later work
better: your own checklists, for your repository alone, or rn itself, as an issue to rn's makers,
for everyone's work; you decide each:

```console
● Learnings to decide
  ▶ 1. Values typed any

  1. Values typed any
  A file of src/checkout was first moved with its values typed any, which would let a wrong
  type through; the AI that used it caught it. rn's checklist for code does not ask for it, so
  anyone moving code to typed code could meet the same slip.
  a. Add "No value is typed any" to .rn/checklists/code.md, and send rn's makers an issue
     (recommended). Your later code is made to it, and rn can ask it of everyone's.
  b. Add it to .rn/checklists/code.md alone. Your later code is made to it.
  c. Add nothing. Later work may repeat the slip.
  Where does it go? Answer with a letter or in your own words.

> a

● Issue sent: https://github.com/lovaizu/ccpm/issues/120
● The pull request is ready to merge: https://github.com/you/app/pull/42
```

What you add to your checklists sits in `.rn/checklists/` in your repository and goes into the same
pull request. The merge is yours.

## Why rn

Asking Claude Code for the same work in a conversation also gets it done; what rn gives you beyond
that:

- You ask without preparing anything.

  Claude Code alone builds on your words as they stand, so you write out what you want first; rn
  finds the points to decide behind your rough words and comes to ask them.

- Your purpose is achieved by answering alone, so the finished work is rarely made again.

  Each point is confirmed with you before it is built on, each task is traced to the acceptance
  criteria, and the plan is remade from the facts each move brings, so the finished work does not
  drift from the purpose you agreed.

- At each sign-off you decide from the proposal alone.

  An AI that did not make it has read and used it in your place, so you need not read all of it
  again.

- Work that takes days neither swells nor drifts, and goes on from wherever you stopped.

  A long conversation with Claude Code alone swells, and a fresh one starts from nothing; rn carries
  only a short record of where the work stands, and `/rn:up` goes on from it.

- What was decided, and why, stays with your repository.

  It is kept in the documents rn writes into your repository, such as the design, and in rn's
  commit messages, with the options weighed and each feedback with its answer, so your next piece
  of work, or a teammate, starts from it.

- Every later piece of work gets better.

  Each learning you take goes into your checklists, which rn makes all later work with, and one
  that would help everyone goes to rn's makers as an issue, so rn gets better for you too.

## Requirements

- Claude Code.

  rn runs inside it.

- A git repository whose remote is on GitHub.

  rn puts the plan and the work on a pull request.

- The GitHub command-line tool `gh`, logged in to an account that can push to the repository.

  rn opens and updates the pull request with it.

- Python 3.9 or later, run as `python3`, and jq, the command-line JSON tool.

  The scripts of rn run on them, and so do those of turn, a plugin installed with rn that rn uses to
  make the plan, each document and the finished work, and to have an AI that did not make each use
  it.

- Recommended: Claude Code run in a [Docker Sandbox](https://docs.docker.com/ai/sandboxes/), with
  the permission mode `bypassPermissions`.

  rn hands whole pieces of work to agents that run many commands; in this mode they are not stopped
  to ask at each one, and the sandbox keeps what they do inside it. rn is tried in the same setting.

## Installation

In Claude Code, add the marketplace once, then install rn:

```console
/plugin marketplace add lovaizu/ccpm
/plugin install rn@ccpm
```

Then, in your repository, type `/rn:up` with what you want, as in the example.

## Documentation

- The three commands in the example, `/rn:up`, `/rn:ty` and `/rn:gm`, are all there is to use.
- [The changelog](CHANGELOG.md) says what changed in each version.

## Development

- [rn's development](../dev/rn/README.md) is the entrance for those who build rn.

## License

[MIT License](../LICENSE)
