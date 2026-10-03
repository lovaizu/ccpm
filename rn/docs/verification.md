# rn verification

Run these after any change to `rn` to see whether it still gives what its
[design document](./design.md) promises, criterion by criterion, and whether something that worked
broke.

## Where a run starts

- The practice repository [`lovaizu/rn-try`](https://github.com/lovaizu/rn-try): a small shop backend,
  its cart and checkout in TypeScript and its account helpers in JavaScript. Its default branch
  `main` holds the tree of `c3b5f8e`, which has no `.rn/` directory, and it has no other branch and no
  open pull request, so no earlier session's plan or code is there to be found.
- `rn` from the branch under test, and `writ` from `worktree-writ` at `d3754b1` until it is merged,
  then from the marketplace.
- Claude Code 2.1.285 or later.

## How a run goes

- Each turn runs `claude -p --plugin-dir <rn> --plugin-dir <writ>` in a clone of the practice
  repository, carrying the conversation over with `--resume`. `/clear` is a new `claude -p` without
  `--resume`.
- A stand-in plays the user. It is given only its part below and what `rn` says to it, writes in
  Japanese, and asks back whenever a question does not give it what it needs to decide.
- The account session is one run, its scenes in this order: A1's `/rn:on` and Plan sign-off
  feedback, A2's no-name question, A4's change on `main` at the Design sign-off, A4's pause in the
  second task, and the Deliverable sign-off; A2's and A3's whole-session scenes read the same run. The
  coupon session and the 0.8.0 session are runs of their own.
- A first user is given a scene's input and the run's record: the conversation, `steering.md`,
  `open/`, the commits, the pull request, the product, and the run's output, where each hook that
  stops says why. It reports what happened. The maintainer running the verification sets that
  beside the scene's "Passes when".
- After a run, a revert commit puts back the tree of `c3b5f8e` on `main`, and the run's branches and
  pull requests are closed.

## The stand-in's parts

The account session starts from rough words:

- It starts with `/rn:on move src/account to TypeScript`.
- Why it wants this, said only when asked why: users who signed up with only an email see
  "undefined undefined" as their name, and support keeps getting tickets about it.
- What it knows, said only when asked: in a user record, `nickname`, `firstName`, and `lastName` can
  each be missing, `null`, or `""`.
- What it wants for a user with no name, when asked: something that tells users apart and gives
  away nothing private. It chooses among the ways the question offers by what each gives and costs,
  and asks back when the question offers no ways or leaves out what they cost.
- Whether every record has an email it does not know and cannot find out before the release, and,
  when asked, it says to go on as if every record has one.
- At a sign-off where a scene gives it no words, it approves when the proposal shows nothing against
  its reason and decisions, and otherwise gives `/rn:gm` with what it saw.

The coupon session is made by hand before the run, on its own branch with a draft pull request, in
the form `rn/references/steering.md` gives, and taken up with `/rn:up`:

- Goal: every coupon is a discount, so no coupon makes an order cost more than it would without one.
- Acceptance criteria: A1, a percent coupon over 100% takes the items' total to 0, not below; M1,
  the app builds and its tests pass as before.
- The Plan and Design sign-offs are approved, with a README, design document, and verification
  document saying of coupons only that one over 100% takes the items' total to 0, and tasks planned
  for that.
- Why the stand-in wants this, said only when asked why: a coupon once took an order's total below
  0, and money went back to the customer by mistake.
- What it decides, when asked: a coupon that is not a discount refuses the order.

## Scenes

### A1: The user gets what they really want, though they start from rough words

- The account session's `/rn:on`.

    Passes when `rn` asks the stand-in why it wants the goal, and the goal and Acceptance criteria
    approved at the Plan sign-off hold that no user is shown "undefined" in their name, which the
    first words do not: moved to TypeScript as it is, `${user.firstName}` still type-checks with the
    name missing.

- The account session's Deliverable sign-off.

    Passes when, for user records with `nickname`, `firstName`, and `lastName` each set, missing,
    `null`, or `""` in every combination, wherever A4's change put them, a user with a name is shown
    it as before, the name shown never holds "undefined" or "null", and a user with no name is shown
    what the stand-in chose.

- The account session's first Plan sign-off, where the stand-in gives `/rn:gm a user whose last name
  is null is shown "Ann null"`.

    Passes when the plan next put up covers all three forms an absent name takes, missing, `null`,
    and `""`, for each name field, not `null` alone; or, when the first plan already covered all
    three, `rn` shows the stand-in where it does rather than adding `null` again.

- The coupon session's Deliverable sign-off. `src/cart/cart.ts` also takes `{ percent: -10 }` and
  `{ amount: -300 }`, and either raises the total today.

    Passes when `rn` puts what to do with a coupon that is not a discount to the stand-in, and in
    the deliverable proposed `checkout` refuses an order with either coupon in the way the design
    names, returning no total, as the stand-in decided, while `{ percent: 10 }` still takes 10% off,
    `{ percent: 150 }` takes the items' total to 0, and the app builds and its tests pass.

### A2: The user is called only for decisions that are theirs

- The account session from `/rn:on` to the Deliverable sign-off, the stand-in doing nothing but
  answer each call and go on after each sign-off.

    Passes when each call to the stand-in is for one of these: why it wants the goal, what a user
    with no name is shown, what is done about records that may have no email, what a user record
    holds where a name is absent, and the three sign-offs; each of them reached it, and none twice;
    and the session reached the Deliverable sign-off.

- What a user with no name is shown, put to the stand-in while working out the design.

    Passes when the stand-in answers without asking back, since the question gives the one point,
    the ways, what each gives and costs, and the one `rn` recommends and why; and the approved design
    holds the answer.

### A3: At a sign-off, the user decides from the proposal

- Each of the account session's three sign-offs where the stand-in is given no words. What a user
  with no name is shown rests on every record having an email, which nothing in the session can
  check.

    Passes when the stand-in, reading only the proposal, decides as a second stand-in with the same
    part decides reading the real thing on the pull request; every viewpoint in the proposal has a Good or a More, each holding at its place under the
    criterion ID it names; and the proposals at the Design and Deliverable sign-offs name the email
    shortfall as a More.

### A4: Work that takes days goes on from where it stopped

- In the account session, the run is stopped once the generator of the second task after the Design
  sign-off has edited a file; the stand-in gives `/rn:dn`, then `/clear` and `/rn:up`.

    Passes when it goes on with the same task, the edits the pause committed kept in what follows
    rather than reverted and made again, does not redo
    finished tasks, speaks Japanese, and asks the stand-in nothing it already answered.

- At the account session's Design sign-off, the stand-in clears the conversation without answering.
  A commit is made by hand on `main` that moves the names `displayName` takes under `profile`, with
  its tests, and the stand-in gives `/rn:up`.

    Passes when `/rn:up` brings the branch up to `main`, the design document is changed for the new
    shape, the stand-in is asked nothing it already answered, and the session stops at the Design
    sign-off again with a proposal that names the change. Putting up the first proposal unchanged
    fails.

- `/rn:up` on a session paused under `rn` 0.8.0, made before the scene with `--plugin-dir` on
  `rn/` of a worktree of the tag `rn--v0.8.0`: the stand-in starts it with
  `/rn:on make every coupon a discount`, answers as in the coupon session, approves each sign-off
  0.8.0 puts up, and gives `/rn:dn` once its first task has begun.

    Passes when it goes on from that session's goal and what was done, with `steering.md` in the
    current form, what the old design approved in a `notes` item, a stop at the Plan sign-off, and
    nothing asked again that the old record holds.

## Machine checks

| Check | Command | Criteria | When |
|---|---|---|---|
| Hook checks 1–3: the form of `steering.md`, the names in `open/`, the verification document's form and IDs | the hooks; a stop shows in the run's output | M4 | Every scene |
| Hook checks 4 and 8: a decision line on every conductor commit, every commit pushed | the hooks; a stop shows in the run's output | M2 | Every scene |
| Hook check 5: a settled item whole in its commit | the hooks; a stop shows in the run's output | M3 | Every scene |
| Hook checks 6 and 7: each stop keeps what its kind allows; only the user's `/rn:ty` passes a sign-off | the hooks; a stop shows in the run's output | M5 | Every scene |
| Hook checks 9–11: only the conductor uses git; the first user writes only its report and reads nothing of the maker's account | the hooks; a stop shows in the run's output | M6 | Every scene |
| Hook check 12: the conductor starts no agent in the background | the hooks; a stop shows in the run's output | A2 | Every scene |
| Each hook stops its breaking case and lets its passing case through; the first user's definition skips `CLAUDE.md` and the generator's has no Agent tool | `python3 -m unittest discover -s rn/tests`, running at least one test for each check | M2–M6 | Every change to the hooks or agents |
| `main` of the practice repository has, after a scene, the head it had before it, but for the commit A4's second scene makes | `git ls-remote origin main`, before and after | M1 | After every scene |
| Strict validation | `claude plugin validate rn --strict` and `claude plugin validate . --strict` | M7 | Every change to the plugin |
| Installing `rn` brings `writ` | `claude plugin install rn@ccpm` in a clean configuration | M7 | Before every release |
