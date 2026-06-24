# rn — Right Now

Start by naming a goal, and pick up right where you left off after any break. One task at a time, with quality built in as you go.

## Install

`rn` ships from the `ccpm` marketplace. In Claude Code, add the marketplace once, then install the plugin:

```console
> /plugin marketplace add lovaizu/ccpm
> /plugin install rn@ccpm
```

That makes `/rn:on`, `/rn:dn`, and `/rn:up` available.

## How it works

```mermaid
flowchart TD
  G([Your goal]) --> P[Reviewed plan on a PR<br/>one task at a time]
  P --> W[Assistant runs a task]
  W -->|heavy work, kept out of sight| X[Expert does it<br/>reviewers try to break it]
  X -->|only the finished change| Y([You approve])
  Y -->|added to the same PR| W
```

One assistant stays with you the whole time; the experts and reviewers work behind the scenes, so the trial-and-error never crowds the conversation. What reaches you is the finished change — and nothing lands until you approve.

## Getting started

Say you want to push through "fix the bug in the payment screen."

### 1. Start — `/rn:on`

Tell it your goal. It restates the goal as it understands it, breaks it into verifiable tasks, and opens a draft PR with the full plan for you to review — too much to read comfortably in the console.

```console
> /rn:on fix the bug in the payment screen

● Captured your goal as I understand it:
    "Fix the bug on the payment screen so payments complete successfully"

  Location: .rn/payment-fix/steering.md
    □ #1  Write a test that reproduces the payment failure
    □ #2  Find the root cause and fix it
    □ #3  Check for regressions

  Opened a draft PR with the full plan: https://github.com/you/repo/pull/42
  Review the steering there and approve to start #1.
```

Read the plan on the PR, approve, and the assistant begins the first task — from here it's the loop above, one task at a time, each approved task added to the same PR.

### 2. Step away — `/rn:dn`

Context is full, or you're done for the day. Run it and your work is committed / pushed, with a note left for next time.

```console
> /rn:dn

● Committed and pushed — "test: add reproduction test for payment failure"
  Last completed: #1 reproduction test
  Up next:        #2 find the root cause and fix it

  Run /clear, then start a fresh conversation with /rn:up.
```

### 3. Come back — `/rn:up`

Run it in a fresh conversation. It finds where you stopped from git and resumes from there.

```console
> /rn:up

● Found a suspended session: payment-fix
  Reconciled with the git log — #1 is done.

● Resuming from #2: find the root cause and fix it
```

---

`on` is just once, at the very start. After that, each break is just **`dn` → `/clear` → `up`**, and your work stays unbroken until the goal is met.

> Run `/clear` yourself after `/rn:dn` — a plugin can't clear the context for you.

## Why on / dn / up?

They're a two-letter power set — on / down / up — easy to keep straight because they track the session's own state:

- **`on`** — *power on.* You sit down and start a session.
- **`dn`** — *down.* You take the session down for now — a pause, not quitting. ("down" trimmed to two letters to match.)
- **`up`** — *up.* You bring the session back up and pick up where you left off.
