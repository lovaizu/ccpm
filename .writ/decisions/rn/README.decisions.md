# What rn's README says

## readme

### B-1: What they gain
- rn is a Claude Code plugin that carries work taking days, from your rough words to a pull request
  ready to merge, with your time spent only on deciding: what you really want, how it is built, and
  whether the result is what you wanted. You never babysit the work and never re-read all of it to
  approve it, and tomorrow, or a fresh conversation, goes on from where you stopped.

### B-2: Who it is for
- Anyone who has Claude Code do work in a git repository on GitHub that takes more than one sitting,
  such as moving an app to TypeScript, and wants to decide rather than watch.

### B-3: Why this one
- Asking Claude in a conversation also gets work done. What rn adds:
- Claude alone builds on your first words. rn asks why you want it and what the result should do
  for you, one point at a time, looks up what the repository and the documentation can tell instead
  of asking, and offers ways only after you have said what you want, each with what it gives and
  costs and the one it recommends; so what you get is what you meant.
- Claude alone judges its own work. Every piece of rn's work, the plan, the design and each result,
  is read or used by an AI that did not make it, as the person it is for would, and checked item by
  item against a checklist of what such work must give; what falls short is made again before you
  see it.
- You decide each sign-off from the proposal alone: how close the work has come to each thing you
  would choose it for, what changed since your last approval, and for each item what is good and
  what falls short, with where; the work itself is on the pull request whenever you want it.
- Every decision is pushed as it is made, so a fresh conversation, or tomorrow, goes on without you
  explaining anything again.

### B-4: Using it on their own work
- The situation: your app is written in JavaScript and you want it moved to TypeScript, work that
  takes days.
- A session is one goal carried through to the end. It has three sign-offs, the plan, the design
  and the deliverable: at each, rn stops with a proposal, and you approve with `/rn:ty` or ask for
  changes with `/rn:gm <feedback>`. Between sign-offs rn calls you only for a decision that is
  yours. It works on its own branch and a draft pull request, so your default branch is untouched
  until you merge.
- What you type to start, in your repository: `/rn:up move this app to TypeScript`.
- What rn does first: works out the plan with you. It says how it understands your words and asks
  why, one point per message; from the answers it writes the goal and the acceptance criteria, in
  two kinds: what would make you choose the result (`A1`...) and what you take for granted
  (`M1`...), each with an ID that every later task and check refers to. What the repository, the
  official documentation or best practice can answer, it looks up. It also asks which language to
  write the repository in and which to talk in, and which issues the work closes.
- The console at the start:
  ```console
  > /rn:up move this app to TypeScript

  ● Here's how I understand it: three of last quarter's production bugs were a value of the wrong
    type, undefined where a number was expected. Is catching those before they ship what you're
    after?

  > yes, that's why

  ● Then the goal is that such a mistake fails the build. Every file ending in .ts is not enough: a
    file moved with loose types would still let it through. Is that right?
  ```
- Knowing why you want it is what shows where your first words would go wrong: every file ending
  in .ts would have let the bugs through.
- The plan sign-off: once nothing is silently assumed, rn has the plan, `steering.md` on the pull
  request, made and read as you would read it, and stops with the proposal:
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
- The map on top heads every message where rn stops: ✅ done, 👉 now, ⬜ ahead. Under it, what rn
  proposes to do next and why, the goal and criteria in the plan's own words, how close the work has
  come to each thing you would choose it for and what came closer since the last proposal, what rn
  decided for you with its ground, and each item of the checklist the plan was checked against,
  met with the lines that give it or not met with why. You say yes or no from this, and read the
  plan itself on the pull request whenever you want. The last line is what rn records of where it
  stopped, so a fresh conversation goes on from the same place.
- Approving and giving feedback:
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
- Feedback sends rn back to working out, from the mismatch behind your words, and it stops at the
  same sign-off again; either command stops there, so you can clear the conversation and lose
  nothing.
- The design sign-off: rn works out with you how to build it and how you will see that it works,
  asking only what the product should be and what trades effort against safety:
  ```console
  ● The three bugs are in src/cart and src/checkout. For the check, I propose code that
    reproduces each of the three, passing when all three fail the build. Strict checks from the
    start stop all three, but nothing builds until every file is typed; loose first builds sooner,
    but lets all three through until tightened. I propose strict: stopping those three is why you
    are moving. Which weighs more for you?

  > strict
  ```
- What you settle goes into your README, design document and verification document, which stay
  with your product; the verification document says, for each thing you would choose the product
  for, how it will be used as you would use it and what must happen then, so the same check runs
  again after any later change. rn stops at the Design sign-off with the three documents made and
  read as their readers would, and the same proposal form.
- Building: you don't babysit it. rn plans the tasks from the design and carries them out. Each
  task's result is made to pass its checklist, used by an AI that knows nothing of how it was made,
  and checked item by item, before rn sets it beside the task's purpose; each time rn decides what
  to do next, it says so in one line:
  ```console
  ● #3 move src/cart ── decided: purpose not fulfilled. It passes only because its types are
    `any`; last quarter's cart bug would still ship → fix
  ● #3 move src/cart ── decided: purpose fulfilled → #4
  ```
- If a decision only you can make comes up, rn asks you, with what it proposes and why.
- The deliverable sign-off: when the tasks are done, the product is used as you would use it, in
  each scene of the verification document, and rn stops with the proposal. On `/rn:ty` the pull
  request is marked ready, and the merge is yours:
  ```console
  > /rn:ty

  ● Approved the deliverable. The pull request is ready: https://github.com/you/repo/pull/42
  ```
- Besides your product, the session leaves only its `.rn/` directory, the record of how things
  were decided, and the pull request links the issues the work closes.

### B-5: Started from the README alone
- Installing: in Claude Code, add the marketplace once with `/plugin marketplace add
  lovaizu/ccpm`, then install rn with `/plugin install rn@ccpm`. This also installs turn.
- Then, in your repository, type `/rn:up` with what you want, as in the example.

### B-7: Terms of use
- MIT License (`../LICENSE`).

### B-9: Why each requirement is needed
- Claude Code: rn runs inside it.
- A git repository with its remote on GitHub: rn puts everything you review on a pull request.
- The GitHub CLI `gh`, logged in with push access: rn opens and updates the pull request with it.
- Python 3.9 or later as `python3`, and jq: rn has another plugin, turn (`../turn/README.md`), make
  every piece of work, read it as its reader and check it, and turn and rn's own checks on the
  record run on them.

### F-1: Under Documentation
- During a session (`during-a-session.md`): pausing with `/rn:dn`, resuming in a fresh conversation
  with `/rn:up`, feedback from the pull request's comments, and what the session leaves in your
  repository.
- How it is built (`docs/design.md`) and how rn itself is checked (`docs/verification.md`).
- The checklists rn makes and checks its work by (`checklists/`): the plan, a proposal, a README,
  a design document, a verification document, code and its tests, a prompt, and any document.
- The changelog (`CHANGELOG.md`): what changed in each version.

## readme: Usability

### U-1: Nothing to learn of the product's inside
- The only part named is turn, the plugin rn installs with and has make, read and check each
  piece of work; the reader sees it installed.

## doc

### B-12: Every term known
- A session: one goal carried through to the end.
- A sign-off: where you look at the work before it goes past that point, and approve or give
  feedback.
- A checklist: a list of items, each one thing a piece of work must give the person it is for.
- The proposal: what rn gives you at a sign-off, to decide from alone.

### B-13: One name for each thing
- "rn" names the plugin; "the work" names what rn makes in a session; "the plan", "the design" and
  "the deliverable" name the three things you sign off; "turn" names the plugin that makes, reads
  and checks each piece of work; "the proposal" names what rn stops with at a sign-off.
