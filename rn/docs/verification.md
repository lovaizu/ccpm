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

- Each trial in `rn/trials/` sets up its scene's start, runs `rn` as its user would until the
  scene's end, and leaves the record for the first user. A scene that starts partway through a
  session starts from a fixture in `rn/trials/fixtures/`, committed on a session branch of a fresh
  clone, not reached by running the session up to it. One run serves every scene it reaches.
- Each turn runs `claude -p --plugin-dir <rn> --plugin-dir <writ>` in that clone, carrying the
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
  away nothing private. It chooses among the ways the question offers by what each gives and costs,
  and asks back when the question offers no ways or leaves out what they cost.
- Whether every record has an email it does not know and cannot find out before the release, and,
  when asked, it says to go on as if every record has one.
- At a sign-off where a scene gives it no words, it approves when the proposal shows nothing against
  its reason and decisions, and otherwise gives `/rn:gm` with what it saw.

The coupon session asks that every coupon be a discount:

- Why the stand-in wants every coupon to be a discount, said only when asked why: a coupon once
  took an order's total below 0, and money went back to the customer by mistake.
- What it decides, when asked: a coupon that is not a discount refuses the order.

## Scenes

### A1: The user gets what they really want, though they start from rough words

- The account session from `/rn:on` on `main` to the second Plan sign-off; at the first, the
  stand-in gives `/rn:gm a user whose last name is null is shown "Ann null"`.

    Passes when `rn` asks the stand-in why it wants the goal, and the plan put up holds that no user
    is shown "undefined" in their name, which the first words do not: moved to TypeScript as it is,
    `${user.firstName}` still type-checks with the name missing. The plan put up after the `/rn:gm`
    covers all three forms an absent name takes, missing, `null`, and `""`, for each name field,
    not `null` alone; or, when the first plan already covered all three, `rn` shows the stand-in
    where it does rather than adding `null` again.

### A2: The user is called only for decisions that are theirs

- A1's run.

    Passes when each call to the stand-in asks what only it can say, why it wants the goal, what it
    knows, or what it chooses, or is a Plan sign-off; none asks what the repository or a run could
    tell, and none asks again what was answered. The stand-in answers what a user with no name is
    shown without asking back, since the question gives the one point, the ways, what each gives
    and costs, and the one `rn` recommends and why; and the plan holds the answer.

### A3: At a sign-off, the user decides from the proposal

- The second Plan sign-off of A1's run, where the stand-in is given no words.

    Passes when the stand-in, reading only the proposal, decides as a second stand-in with the same
    part decides reading the real thing on the pull request; every viewpoint in the proposal has a
    Good or a More, each holding at its place under the criterion ID it names; and the proposal
    names as a More what the plan rests on that nothing in the session could check.

### A4: Work that takes days goes on from where it stopped

- The coupon session at its first build task, both sign-offs before it approved (fixture
  `coupon`): the stand-in says "go on", the run is stopped once the generator has edited a file,
  and the stand-in gives `/rn:dn`, then `/clear` and `/rn:up`, until that task is checked off.

    Passes when it goes on with the same task, the edits the pause committed kept in what follows
    rather than reverted and made again, does not redo the sign-offs, speaks Japanese, and asks the
    stand-in nothing the record holds.

- The coupon session paused under `rn` 0.8.0 in its first build task (fixture `coupon-0.8.0`):
  `/rn:up`, until the Plan sign-off.

    Passes when it goes on from that session's goal and what was done, with `steering.md` in the
    current form, what the old design approved in a `notes` item, a stop at the Plan sign-off, and
    nothing asked again that the old record holds.

## Machine checks

| Check | Command | Criteria | When |
|---|---|---|---|
| Hook checks 1–3: the form of `steering.md`, the names in `open/`, the verification document's form and IDs | the hooks; a stop shows in the run's output | M4 | Every scene |
| Hook checks 4 and 8: a decision line on every conductor commit, every commit pushed | the hooks; a stop shows in the run's output | M2 | Every scene |
| Hook check 5: a settled item whole in its commit | the hooks; a stop shows in the run's output | M3 | Every scene |
| Hook checks 6 and 7: each stop keeps what its kind allows, and every Good and More of a proposal names its criterion; only the user's `/rn:ty` passes a sign-off | the hooks; a stop shows in the run's output | M5, A3 | Every scene |
| Hook checks 9–11: only the conductor uses git; the first user writes only its report and reads nothing of the maker's account | the hooks; a stop shows in the run's output | M6 | Every scene |
| Hook checks 12–14: the conductor starts no agent in the background, ends its turn only at a stop or a question, and speaks the conversation language | the hooks; a stop shows in the run's output | A2, A3 | Every scene |
| Each hook stops its breaking case and lets its passing case through; the first user's definition skips `CLAUDE.md` and the generator's has no Agent tool | `python3 -m unittest discover -s rn/tests`, running at least one test for each check | M2–M6 | Every change to the hooks or agents |
| `main` of the practice repository has, after a scene, the head it had before it | `git ls-remote origin main`, before and after | M1 | After every scene |
| Strict validation | `claude plugin validate rn --strict` and `claude plugin validate . --strict` | M7 | Every change to the plugin |
| Installing `rn` brings `writ` | `claude plugin install rn@ccpm` in a clean configuration | M7 | Before every release |
