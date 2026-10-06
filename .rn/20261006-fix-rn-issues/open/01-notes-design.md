# Design of rn, from what its README promises

`rn/README.md` as on `main` is what rn should be. Each section below takes one step of it: what the
user gets there, the least rn needs to give it, and what in rn 0.9.0 stands in the way and goes.
Nothing is added that a step of the README does not need.

## Why 0.9.0 does harm

- Every fault met while building 0.9.0 became a step or a hook (steering.md, Facts), and each of them
  now stands between the user and a step of the README: below, under "In the way".
- It was checked scene by scene and never used as the README's story runs, so no check saw the user
  waiting hours, reading 72 lines, or never being heard.
- So this design takes away; it adds only where a step cannot be given without it, and it is checked
  by running the README's story end to end.

## 1. Start: rn hears what you really want

- Gets: from rough words, rn says how it understands them and asks, one point at a time, what the
  user wants, why, and how they would know; ways come with what each gives and costs and the one it
  recommends; facts are looked up.
- Needs: the conductor talks with the user directly. The request, or an issue it names, is where the
  hearing starts, never its answer; what the user wants and why is always theirs.
- In the way: a first user takes up each question before the user sees it, and the turn-end check
  sends the conductor on unless a question file waits in `open/`; the conductor answers itself
  instead (PR #48: it dropped its question and widened the goal on its own judgment).

## 2. A sign-off is decided from the proposal alone

- Gets: the user says yes or no from the proposal, and reads the work on the pull request only when
  they want to.
- Needs: a proposal holds the map, how close each thing the user would choose the work for has come,
  each point that is theirs to decide (a More left, an `Assumption`, something taken away), and the
  next move with why. The goal, the criteria and every Good and More are on the pull request.
- In the way: the proposal repeats the goal, every criterion and every Good and More (72 lines,
  #46), and a first user reads it before the user does.

## 3. The design is worked out with you, and writ writes it once

- Gets: the user settles in talk only the calls that are theirs, such as effort against safety, and
  approves the design and verification documents together before anything is built.
- Needs: the conductor settles every point before `writ` is called, then runs `writ:up` itself in
  its own conversation, once per document, so its result comes back.
- In the way: a first user uses the documents against rn's viewpoints on top of writ's own check;
  `writ` run inside an agent returns before its own agents do; rounds of writing (#39: hours).

## 4. It builds without you watching

- Gets: the user does not watch; each result is used before they see it by an agent that knows
  nothing of how it was made; each decision is one line.
- Needs: a generator per task; a first user per task result and once for the deliverable, and once
  more on a fixed attractive More alone; the conductor waits for its agents by ending its turn, and
  their return wakes it.
- In the way: the turn-end check sends the conductor on while it waits, and the check forbidding
  background agents forbids the only way agents run (#44); its checks stop other sessions in the same
  repository (#43).

## 5. Pause and resume

- Gets: a fresh conversation goes on from where the work stopped, without explaining again.
- Needs: every decision pushed as it is made; `/rn:dn` in the middle of a task; `/rn:up`.
- In the way: nothing found beyond the waiting in step 4.

## 6. Your default branch changes only when you merge

- Gets: the work is on a branch and a draft pull request; the merge is the user's.
- Needs: when the user starts on a branch of their own with no commits and level with the latest
  default branch, such as a fresh worktree, rn works on it (#41); otherwise on its own.
- In the way: `/rn:on` always makes a new branch, apart from the user's worktree (#41).

## Hooks keep only what the steps rest on

- Kept, each acting only in the conversation that runs rn and on the agents it started: the record's
  form and the decision line (step 5), pushed commits (step 5), only the conductor uses git (step 4),
  the first user's reads and writes (step 4), the conversation language, the record read again after
  a summary (step 5), a sign-off passed only by `/rn:ty` (step 2).
- Taken away: the turn-end check, the check forbidding background agents, the checks on questions,
  and the verification coverage check before the design writes the verification document.

## It is checked by running the README's story

- One session on the practice repository, from `/rn:on` to the Design sign-off, run as the README's
  story runs, beside rn 0.9.0's run of the same request. It passes when each step above is given:
  the user was asked why they want it; they were called only for what is theirs; they decided the
  sign-off from the proposal; the conductor waited for its agents with no loop; and the time to the
  Design sign-off and the lines read at each stop are below 0.9.0's.

## The same holds for every plugin, in `.claude/rules/plugin.md`

Decided by the user: written into `.claude/rules/plugin.md` with rn and writ.

- § Results: a short result holds only the view, the points the caller decides, and where the file
  is (#46); a called plugin is called so that its result comes back.
- § Hooks: a plugin's hooks act only in the conversation that runs it and on the agents it started,
  and never stop a conversation from waiting for its agents.
- § Roles: a first user is started only for what use shows and its maker cannot see without use.
