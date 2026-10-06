# rn verification

Run these after any change to `rn` to see whether it still gives what its
[design document](./design.md) promises, criterion by criterion, and whether something that worked
broke.

## Where a run starts

- The practice repository [`lovaizu/rn-try`](https://github.com/lovaizu/rn-try): a small shop backend,
  its cart and checkout in TypeScript and its account helpers in JavaScript. Its default branch
  `main` holds the tree of `c3b5f8e`, which has no `.rn/` directory, and it has no other branch and no
  open pull request, so no earlier session's plan or code is there to be found.
- `rn`, `writ` and `pith` from the branch under test, as its marketplace installs them.
- Claude Code 2.1.285 or later.

## How a run goes

- Each scene is run by its trial in `dev/rn/trials/`, from the state just before the moment it checks
  to the first result that shows it. A state partway through a session is a fixture in
  `dev/rn/trials/fixtures/`, committed on its session branch of a fresh clone with a draft pull request.
  Trials run one at a time, since `rn` reads the practice repository's branches and pull requests.
- Each turn runs `claude -p --plugin-dir <rn> --plugin-dir <writ> --plugin-dir <pith>` in that clone, carrying the
  conversation over with `--resume`. `/clear` is a new `claude -p` without `--resume`.
- A stand-in plays the user. It is given only its part below and what `rn` says to it, writes in
  Japanese, and asks back whenever a question does not give it what it needs to decide.
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
  away nothing private. Asked to choose among ways, it chooses by what each gives and costs, and asks
  back when no way gives what it wants or the question leaves out what they cost.
- It does not know whether every record has an email and cannot find out before the release; when
  asked, it says to go on as if every record has one.
- At a sign-off where a scene gives it no words, it approves when the proposal shows nothing against
  its reason and decisions, and otherwise gives `/rn:gm` with what it saw.

The coupon session asks that every coupon be a discount:

- Why the stand-in wants every coupon to be a discount, said only when asked why: a coupon once
  took an order's total below 0, and money went back to the customer by mistake.
- What it decides, when asked: a coupon that is not a discount refuses the order.

## Scenes

### A1: The user gets what they really want, though they start from rough words

- `/rn:on move src/account to TypeScript` on `main`, to `rn`'s first call to the stand-in after the
  languages are settled.

    Passes when `rn` asks why the stand-in wants the goal.

- The account session at its first Plan sign-off (fixture `account-plan`), whose plan treats only a
  missing name as absent: `/rn:gm a user whose last name is null is shown "Ann null"`, to the next
  Plan sign-off.

    Passes when the plan put up covers all three forms an absent name takes, missing, `null`, and
    `""`, for each name field, not `null` alone.

### A2: The user is called only for decisions that are theirs

- The account session with the stand-in's reason recorded and no criterion yet written, paused
  (fixture `account-why`): `/rn:up`, to `rn`'s second call to the stand-in, the stand-in answering
  the first.

    Passes when, before any call asks the stand-in to choose a way, a call asks what it wants the
    result to do for it, and the ways a call then offers each give what it said; none asks what the
    repository or a run could tell. A call to choose gives the ways, what each gives and costs, and
    the one `rn` recommends and why.

### A3: At a sign-off, the user decides from the proposal

- The account session with its plan settled and its proposal not yet drafted, paused (fixture
  `account-ready`): `/rn:up`, to the Plan sign-off, where the stand-in is given no words.

    Passes when the stand-in, reading only the proposal, decides as a second stand-in with the same
    part decides reading the real thing on the pull request; every viewpoint in the proposal has a
    Good or a More, each holding at its place under the criterion ID it names; and the proposal
    names as a More each Assumption the plan rests on.

### A4: Work that takes days goes on from where it stopped

- The coupon session paused in its first build task, its generator's test written and the code not
  yet changed (fixture `coupon-paused`): `/rn:up`, to the first edit or call to the stand-in.

    Passes when it goes on with that task, handing the written test to its generator rather than
    writing it again or asking whose it is, and speaks Japanese.

- The coupon session paused under `rn` 0.8.0 in its first build task (fixture `coupon-0.8.0`):
  `/rn:up`, to the first call to the stand-in.

    Passes when it goes on from that session's goal and what was done, with `steering.md` in the
    current form and what the old design approved in a `notes` item, and asks nothing the old record
    holds.

## The whole story

Before a round's verdict, `dev/rn/trials/story.py` runs the account session from
`/rn:on move src/account to TypeScript` on `main` to the Deliverable sign-off, the stand-in answering
as above, and records in `spent.json` how long the user waited at each call, how many lines they read,
and each time they were called. It is run the same way with `rn` 0.8.0, the last version that runs to
the end.

    Passes when the session reaches its end, each attractive criterion is given at least as well as
    with 0.8.0, and the user waited less, read less at each sign-off, and was called less, with no
    call for what the request, the goal or the repository already settled.

## Machine checks

| Check | Command | Criteria | When |
|---|---|---|---|
| The reminder after a summary reaches only a conversation that typed an rn command, and runs every line | `coverage run -m unittest discover -s dev/rn/tests` | A4 | Every push, in CI |
| `main` of the practice repository has, after a scene, the head it had before it | `git ls-remote origin main`, before and after | M1 | After every scene |
| Strict validation | `claude plugin validate rn --strict` and `claude plugin validate . --strict` | M7 | Every change to the plugin |
| Installing `rn` brings `writ` and `pith` | `claude plugin install rn@ccpm` in a clean configuration | M7 | Before every release |
