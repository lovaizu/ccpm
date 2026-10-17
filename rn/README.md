# rn

rn is a Claude Code plugin that carries work taking days from your rough words to a pull request
ready to merge, with your time spent only on deciding: what you really want, how it is built, and
whether the result is what you wanted. You never babysit the work or re-read all of it to approve
it, and tomorrow, or a fresh conversation, goes on from where you stopped. It is for anyone who has
Claude Code do work in a git repository on GitHub that takes more than one sitting, such as moving
an app to TypeScript, and who wants to decide rather than watch.

## Example

Your app is written in JavaScript, and you want it moved to TypeScript, work that takes days.

### How a session goes

A session is one goal carried through to the end. It has three sign-offs, each a point where you
look at the work before it goes past: the plan, what you want and how you would know it is reached;
the design, how it is built and how that is checked; and the deliverable, the finished work on the
pull request. At each, rn stops with a proposal, what it gives you to decide from alone, and you
approve with `/rn:ty` or ask for changes with `/rn:gm <feedback>`. Between sign-offs rn calls you
only for a decision that is yours. It works on its own branch and a draft pull request, so your
default branch is untouched until you merge, and keeps the record of how things were decided, your
feedback included, in a `.rn/` directory in your repository.

### Starting: the plan

rn works out the plan with you first. It says how it understands your words and asks why, one
point per message; what the repository, the official documentation or best practice can answer, it
looks up instead of asking. You start it by typing `/rn:up` in your repository with what you want:

```console
> /rn:up move this app to TypeScript

● Here's how I understand it: three of last quarter's production bugs were a value of the wrong
  type, undefined where a number was expected. Is catching those before they ship what you're
  after?

> yes, that's why

● Then the goal is that such a mistake fails the build. Every file ending in .ts is not enough: a
  file moved with loose types would still let it through. Is that right?
```

Knowing why you want it is what shows where your first words would go wrong: every file ending in
.ts would have let the bugs through.

From your answers rn writes the goal and the acceptance criteria, in two kinds: what would make you
choose the result (`A1`...) and what you take for granted (`M1`...), each with an ID that every
later task and check refers to. It also asks which language to write the repository in and which to
talk in, and which issues the work closes.

### The plan sign-off

Once nothing is silently assumed, rn writes the plan, `steering.md` on the pull request. An AI that
did not write it reads it as you would and checks it against a checklist, a list of items each
naming one thing a piece of work must give the person it is for; what falls short is written again
before you see it. Then rn stops with the proposal:

```console
● ── typescript: a wrong type fails the build ──
  👉 #1 Plan sign-off ── read the plan on the PR: /rn:ty to approve, /rn:gm <feedback> to ask for changes
  ⬜ #2 Design sign-off

  Draft PR: https://github.com/you/repo/pull/42

  I propose working out the design on this plan: it says what you want, why, and how you would
  know it is achieved.

  Goal: a wrong type fails the build
  Judged by:
  - A1: Code reproducing each of the three bugs fails the build
  - M1: Every file is .ts
  - M2: The app builds and runs as before

  Toward what you would choose it for:
  - A1: each of the three bugs is named with how its failing build is checked; nothing is built
    yet (first proposal)

  Decided for you
  - Which files count as the app: src/ and test/, since package.json names only those (steering.md:14)

  Plan
  - ✅ P-1 Why you want the goal: steering.md:5-7
  - ✅ P-2 What you would choose the result for: steering.md:11-13
  (every item of the checklist gets a line the same way)

● #1 Plan sign-off ── proposed: work out the design on this plan → waiting for #1 Plan sign-off
```

The map on top heads every message where rn stops: ✅ done, 👉 now, ⬜ ahead. Under it come what rn
proposes to do next and why, the goal and criteria in the plan's own words, how close the work has
come to each thing you would choose it for and what came closer since the last proposal (a first
proposal, marked as here, has no earlier one to compare with), and what rn decided for you with its
ground. Last come the items of the checklist the plan was checked against, each met with the lines
that give it or not met with why. You say yes or no from this, and read the plan itself on the pull
request whenever you want. The last line is what rn records of where it stopped.

### Asking for changes, then approving

Feedback sends rn back to working out, from the mismatch behind your words, until it stops at the
same sign-off again; approving moves on to the next sign-off. Either way rn stops there, so you can
clear the conversation and lose nothing:

```console
> /rn:gm the three bugs were in cart and checkout; account had none

● #1 Plan sign-off ── feedback in 01-feedback-plan.md → working out the plan again

  Say "go on", or /clear and then /rn:up.

> go on

● Then the account files move too, but the checks reproduce only the cart and checkout bugs.
  Is that right?

> yes

● ── typescript: a wrong type fails the build ──
  👉 #1 Plan sign-off ── read the plan on the PR: /rn:ty to approve, /rn:gm <feedback> to ask for changes
  ...

> /rn:ty

● #1 Plan sign-off ── approved → #2 Design sign-off

  Say "go on", or /clear and then /rn:up.
```

`01-feedback-plan.md` is your feedback, kept in the `.rn/` record.

### The design sign-off

rn works out with you how to build it and how you will see that it works, asking only what the
product should be and what trades effort against safety. It offers ways only once you have said what
you want, each with what it gives and costs and the one it recommends:

```console
● The three bugs are in src/cart and src/checkout. For the check, I propose code that
  reproduces each of the three, passing when all three fail the build. Strict checks from the
  start stop all three, but nothing builds until every file is typed; loose first builds sooner,
  but lets all three through until tightened. I propose strict: stopping those three is why you
  are moving. Which weighs more for you?

> strict
```

What you settle goes into your README, design document and verification document, which stay with
your product. The verification document gives, for each thing you would choose the product for, a
scene: how the product will be used as you would use it and what must happen then, so the same
check runs again after any later change. rn stops at the design sign-off with the three documents
made, read and checked as the plan was, and a proposal of the same form.

### Building

You don't babysit it. rn plans the tasks from the design and carries them out. Each task's result
is used by an AI that knows nothing of how it was made, checked item by item against its checklist
and made again where it falls short, before rn sets it beside the task's purpose. Each time rn
decides what to do next, it says so in one line:

```console
● #3 move src/cart ── decided: purpose not fulfilled. It passes only because its types are
  `any`; last quarter's cart bug would still ship → fix
● #3 move src/cart ── decided: purpose fulfilled → #4
```

If a decision only you can make comes up, rn asks you, with what it proposes and why.

### The deliverable sign-off

When the tasks are done, the product is used as you would use it, in each scene of the
verification document, and rn stops with the proposal. On `/rn:ty` the pull request is marked
ready, and the merge is yours:

```console
> /rn:ty

● Approved the deliverable. The pull request is ready: https://github.com/you/repo/pull/42
```

Besides your product, the session leaves only its `.rn/` record, and the pull request links the
issues the work closes.

## Why rn

Asking Claude in a conversation also gets work done. What rn adds:

- What you get is what you meant, not what your first words said.

  Claude alone builds on your first words; rn first asks why you want it, as in Starting: the plan,
  and offers ways only after that, as at the design sign-off.

- Each piece of work is checked by an AI that did not make it before you see it.

  Claude alone judges its own work; rn has the plan, the design and each task's result checked by
  another AI, as at the plan sign-off and in Building.

- You decide each sign-off from the proposal alone.

  With Claude alone, you re-read the work to know where it stands; rn's proposal tells you, as at
  the plan sign-off.

- A fresh conversation, or tomorrow, goes on without you explaining anything again.

  With Claude alone, a fresh conversation starts from nothing; rn pushes each decision as it is
  made, as at the plan sign-off.

## Requirements

- Claude Code.

  rn runs inside it.

- A git repository whose remote is on GitHub.

  rn puts everything you review on a pull request.

- The GitHub CLI `gh`, logged in to an account that can push to the repository.

  rn opens and updates the pull request with it.

- Python 3.9 or later, run as `python3`, and jq, the command-line JSON tool.

  rn has another plugin, [turn](../turn/README.md), make each piece of work and have it read and
  checked by an AI that did not make it, as the plan and each task were in the example; turn and rn
  itself run on Python and jq.

## Installation

In Claude Code, add the marketplace once, then install rn; this also installs turn:

```console
/plugin marketplace add lovaizu/ccpm
/plugin install rn@ccpm
```

Then, in your repository, type `/rn:up` with what you want, as in the example.

## Documentation

- [During a session](during-a-session.md) tells how to pause with `/rn:dn` and resume in a fresh
  conversation with `/rn:up`, how to give feedback in the pull request's comments, and what the
  session leaves in your repository.
- [rn's design document](docs/design.md) says how rn is built.
- [rn's verification document](docs/verification.md) gives the scenes rn itself is checked in.
- [The checklists](checklists/) give what rn checks each kind of work against: the plan, a
  proposal, a README, a design document, a verification document, code and its tests, a prompt,
  and any document.
- [The changelog](CHANGELOG.md) says what changed in each version.

## License

[MIT License](../LICENSE)
