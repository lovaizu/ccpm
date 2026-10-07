# rn — Right Now

Say what you want to achieve in your repository, and `rn` carries it all the way there. All you do
is decide.

- You get what you really want, without writing a careful prompt first.
- Your time goes only to the decisions that are yours, such as what to build and how much risk to
  take: you don't babysit the work, and you don't re-read all of it to approve it.
- Work that takes days goes on the next day, or in a fresh conversation, from where it stopped.

## What you need

- [Claude Code](https://code.claude.com), on Opus or Sonnet
- A git repository with its remote on GitHub, since `rn` puts everything you review on a pull request
- The [GitHub CLI](https://cli.github.com) `gh`, logged in with push access, which `rn` uses to open
  and update a pull request
- Python 3.9 or later, which runs `rn`'s reminder after a summary and `pith`'s check of its result files

## Install

`rn` ships from the `ccpm` marketplace. In Claude Code, add the marketplace once, then install the
plugin:

```console
> /plugin marketplace add lovaizu/ccpm
> /plugin install rn@ccpm
```

This also installs `writ` and `pith`, from the same marketplace: `rn` has `writ` write your README and
design document so they read well to whoever picks them up, and has `pith` use each result before
you see it.

## How a session goes

One goal carried through to the end is a session. A sign-off is where you look at the work before it
goes past that point, and say yes to `rn`'s proposal or give feedback. Between sign-offs, `rn` calls
you only for a decision that is yours. It works on its own branch and a draft pull request, so your
default branch is untouched until you merge.

```mermaid
flowchart TD
    S(("start"))
    PlanTalk("Work out the plan")
    Plan("Plan sign-off")
    DesignTalk("Work out the design")
    Design("Design sign-off")
    Make("Build and check the deliverable")
    Deliverable("Deliverable sign-off")
    E((("done")))

    S --> PlanTalk
    PlanTalk -.->|proposal| Plan
    Plan -->|feedback| PlanTalk
    Plan -->|approve| DesignTalk
    DesignTalk -.->|proposal| Design
    Design -->|feedback| DesignTalk
    Design -->|approve| Make
    Make -.->|the design must change| DesignTalk
    Make -.->|proposal| Deliverable
    Deliverable -->|feedback| Make
    Deliverable -->|feedback that changes the design| DesignTalk
    Deliverable -->|approve| E

    style Make stroke-dasharray: 5 5
    style PlanTalk stroke-width: 3px
    style DesignTalk stroke-width: 3px
```

Dotted lines are where `rn` moves on, solid lines are yours, a bold box is where `rn` looks things
up while talking with you one point at a time, until you both see the same thing, and the dashed box
is where it works without you.

Say your team keeps meeting the same mistakes in review, and you want a Claude Code plugin that turns
what past pull requests show into checks — work that takes days.

### 1. Start — `/rn:on`

In your repository, say what you want, as roughly as it comes to mind; what you get is what you
meant. `rn` tells you how it understands it and asks, one point at a time, what you want, why you
want it, and how you would know the goal is achieved; where there are several ways to get it, it
offers them with what each gives and costs and the one it recommends. It moves on only when you
agree. What the repository, the official documentation, or best practice can answer,
it looks up instead of asking you. It also asks which language to talk in and which to write the
repository in, and which issues the work closes.

```console
> /rn:on make a plugin that draws the intent out of a pull request's commits and review comments,
  writes it as rules, and makes code or viewpoints that check them

● Here's how I understand it: a plugin that reads a merged pull request and turns what reviewers
  asked for into rules. What do you want those rules to do for you?

> the same remarks keep coming back in review, and fix-up commits repeat the same slips. I want
  them caught before review, by a check or by an AI review, as a self-check

● Then the goal is that a mistake already pointed out once is caught before the next review. Rules
  written down are not enough: one no one runs catches nothing. Is that right?
```

Knowing why you want it is what shows where your first words would go wrong: a plugin that only
writes rules would have caught nothing.

From your first words, `rn` keeps the plan, `steering.md`, on a draft pull request, and updates it
as each point is agreed. The plan holds the goal, its acceptance criteria, and the tasks. The
criteria come in two kinds: what would make you choose the result, and what you take for granted.
Each has an ID, so you can follow any task or check back to the criterion it serves:

```markdown
# Acceptance criteria

## Attractive quality

- A1: Run on a past pull request's first commits, the checks drawn from its review catch what the
  reviewers later pointed out
- A2: Each rule is checked before review: by code where a machine can decide it, otherwise by a
  viewpoint an AI review uses

## Must-be quality

- M1: Each rule names the review comments or commits it came from
- M2: A check changes nothing in the repository but its own result
```

The tasks that build it are planned once the design is settled, so they follow what you agree to
there; until then, the plan shows them as not yet specified.

```console
● ── review-rules: a mistake pointed out once is caught before the next review ──
  👉 #1 Plan sign-off ── read the plan on the PR: /rn:ty to approve, /rn:gm <feedback> to ask for changes
  ⬜ #2 Design sign-off

  Draft PR: https://github.com/you/repo/pull/42

  I propose working out the design on this plan: it says what you want, why, and how you would
  know it is achieved.

  Goal: a mistake pointed out once is caught before the next review
  - A1: Run on a past pull request's first commits, the checks drawn from its review catch what the
    reviewers later pointed out
  - A2: Each rule is checked before review: by code where a machine can decide it, otherwise by a
    viewpoint an AI review uses
  - M1: Each rule names the review comments or commits it came from
  - M2: A check changes nothing in the repository but its own result

  Toward what you would choose it for:
  - A1, A2: how each is shown on a real pull request is named; nothing is built yet (first proposal)

  For you to decide:
  - Assumed, not checked: review comments are reachable with `gh` for the pull requests you use
    (steering.md:24)

  ● #1 Plan sign-off ── proposed: work out the design on this plan → waiting for #1 Plan sign-off
```

The map on top heads every message where `rn` stops for a sign-off or a pause: ✅ done, 👉 now,
⬜ ahead. Under it, `rn` says what it proposes to do next and why; at the Plan sign-off, the goal and
criteria in the plan's own words, since they are what you approve. Then it says how close the work
has come to each thing you would choose it for, and what came closer since its last proposal.
Clearing every shortfall never ends, so this is what you decide on: whether it has come close enough.
Last comes only what is yours to decide: a shortfall it left, something it assumed without checking,
or something your product will no longer do. However large the work, the proposal holds no more
than that; everything good and everything short of it is in the record on the pull request, for
whenever you want it. The last line is what `rn` records of where it stopped, so a fresh conversation
goes on from the same place.

### 2. Approve or give feedback — `/rn:ty` and `/rn:gm`

`/rn:ty` approves. `/rn:gm <feedback>` asks for changes, and plain `/rn:gm` takes the review
comments you wrote on the pull request since `rn` stopped for this sign-off as feedback, so you can
comment where you read. Either one stops there. You can clear the conversation at that point and
lose nothing: say "go on" to continue, or `/clear` first, then `/rn:up`.

```console
> /rn:ty

● #1 Plan sign-off ── approved → #2 Design sign-off

  Say "go on", or /clear and then /rn:up.
```

### 3. Work out the design — Design sign-off

Once you approve the plan, `rn` works out the design with you: how to build it, and how you will see
that it works. You approve the design document and a verification document together, before anything
is built, so what comes back at the end is what you expected. The verification document says, for
each attractive criterion, how it will be used as you would use it and what it should do then, so
the same check can be run again after any later change. Of
the points that come up, how much is left to an AI review rather than code is a call of effort
against certainty, so it is yours. What you settle goes into your README, design document, and verification document, which
stay with your product, so the next session, or a teammate, starts from what you settled.

```console
● Of the 40 remarks in the pull request I would test on, 12 a script can decide, such as a missing
  test for a new setting; the rest need reading, such as whether an error message says what to do.
  Code for the 12 catches them every time but misses the rest; viewpoints for an AI review reach all
  40 but may miss one on a given run. I propose both: code for the 12, viewpoints for the rest, so
  nothing reviewers asked for is left unchecked. Which weighs more for you?
```

### 4. Build and check the deliverable

You don't babysit it. Before you see a result, an agent that knows nothing of how it was made uses
it as you would, and tells `rn` what it understood and what happened. `rn` sets that beside what the
result is for, so a result passes because it does its job, not because its maker says so. Each task
has a purpose set in the plan, and each time `rn` decides what to do next against it, it says so in
one line, so a glance tells you where it is and why:

```console
● #3 draw rules from a pull request ── decided: purpose not fulfilled. Two rules restate the diff,
  not what the reviewer asked for, so they would catch nothing in the next pull request → fix
● #3 draw rules from a pull request ── decided: purpose fulfilled → #4
```

If a decision only you can make comes up, `rn` asks you, with what it proposes and why.

### 5. Pause and resume — `/rn:dn`, `/rn:up`

Every decision is pushed as it is made, so tomorrow, or a fresh conversation, starts where you
stopped, without explaining anything again. When the context is nearly full, or you are done for the
day, `/rn:dn` records how far the session has come. When you want a fresh conversation, run `/clear`
yourself, then `/rn:up`. A plugin can't run `/clear`.

```console
> /rn:dn

● ── review-rules: a mistake pointed out once is caught before the next review ──
  ✅ #1 Plan sign-off / #2 Design sign-off / #3 draw rules from a pull request
  👉 #4 checks from the rules ── paused here
  ⬜ #5 viewpoints for an AI review / #6 Deliverable sign-off

  ● #4 checks from the rules ── half done: 7 of 12 checks written → paused at #4 checks from the rules

  Next: /clear, then /rn:up.

> /clear
> /rn:up

● Resuming review-rules at #4: checks from the rules
```

### 6. Finish — Deliverable sign-off

You approve the deliverable, your product as the session leaves it, by whether it achieves the goal
you agreed at the start. Before you see it, it was used as you would use it, in each scene of the
verification document you approved, so it was checked against that goal, not only against its
tasks. The proposal says how close it has come to each thing you would choose it for, so you decide
whether that is enough.
When something falls short, `/rn:gm` has it fixed. On `/rn:ty` the pull request is marked ready,
and the merge is yours:

```console
> /rn:ty

● Approved the deliverable. The pull request is ready: https://github.com/you/repo/pull/42
```

Besides your product, the session leaves only its `.rn/` directory, the record of how things were
decided, so you or a teammate can later see why things came out as they did. The pull request links
the issues the work closes or serves, and the pull requests it replaces, so GitHub connects them for
you.

## How it is built

Who makes, uses, and decides each thing in a session, and why `rn` is built that way, is in its
[design document](./docs/design.md). How `rn` itself is checked is in its
[verification document](./docs/verification.md).

## License

[MIT](../LICENSE)
