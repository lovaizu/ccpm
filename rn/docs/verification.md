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

- Each scene is run by its trial in `dev/rn/trials/`, from the state just before the moment it checks
  to the first result that shows it. A state partway through a session is a fixture in
  `dev/rn/trials/fixtures/`, committed on its session branch of a fresh clone with a draft pull request.
  Trials run one at a time, since `rn` reads the practice repository's branches and pull requests.
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

- `/rn:on move src/account to TypeScript` on `main`, to `rn`'s first call to the stand-in.

    Passes when `rn` asks why the stand-in wants the goal.

- The account session at its first Plan sign-off (fixture `account-plan`), whose plan treats only a
  missing name as absent: `/rn:gm a user whose last name is null is shown "Ann null"`, to the next
  Plan sign-off.

    Passes when the plan put up covers all three forms an absent name takes, missing, `null`, and
    `""`, for each name field, not `null` alone.

### A2: The user is called only for decisions that are theirs

- A1's first scene, gone on to `rn`'s third call, the stand-in answering each.

    Passes when each call asks what only the stand-in can say, why it wants the goal, what it
    knows, or what it chooses; none asks what the repository or a run could tell, and none asks
    again what was answered. A call to choose is answered without asking back, since it gives the
    one point, the ways, what each gives and costs, and the one `rn` recommends and why.

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

## Machine checks

| Check | Command | Criteria | When |
|---|---|---|---|
| Hook checks 1–3: the form of `steering.md`, the names in `open/`, the verification document's form and IDs | the hooks; a stop shows in the run's output | M4 | Every scene |
| Hook checks 4 and 8: a decision line on every conductor commit, every commit pushed | the hooks; a stop shows in the run's output | M2 | Every scene |
| Hook check 5: a settled item whole in its commit | the hooks; a stop shows in the run's output | M3 | Every scene |
| Hook checks 6 and 7: each stop keeps what its kind allows, and every Good and More of a proposal names its criterion; only the user's `/rn:ty` passes a sign-off | the hooks; a stop shows in the run's output | M5, A3 | Every scene |
| Hook checks 9–11: only the conductor uses git; the first user writes only its report and reads nothing of the maker's account | the hooks; a stop shows in the run's output | M6 | Every scene |
| Hook checks 12–14: the conductor starts no agent in the background, ends its turn only at a stop or a question, and speaks the conversation language | the hooks; a stop shows in the run's output | A2, A3 | Every scene |
| Each hook stops its breaking case and lets its passing case through; the first user's definition skips `CLAUDE.md` and the generator's has no Agent tool | `python3 -m unittest discover -s dev/rn/tests`, running at least one test for each check | M2–M6 | Every change to the hooks or agents |
| `main` of the practice repository has, after a scene, the head it had before it | `git ls-remote origin main`, before and after | M1 | After every scene |
| Each fixture in the current form passes the form checks | `python3 -m unittest discover -s dev/rn/tests` | M4 | Every change to the fixtures or to the form |
| Strict validation | `claude plugin validate rn --strict` and `claude plugin validate . --strict` | M7 | Every change to the plugin |
| Installing `rn` brings `writ` | `claude plugin install rn@ccpm` in a clean configuration | M7 | Before every release |
