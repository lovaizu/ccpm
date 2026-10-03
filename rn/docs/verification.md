# rn verification

How `rn` is checked against the acceptance criteria in its [design document](./design.md), which
this document refers to by ID.

Attractive quality is checked by using `rn` as its user would, on the golden path: `rn` is run with
`claude -p --plugin-dir` on the practice repository [`lovaizu/rn-try`](https://github.com/lovaizu/rn-try),
which holds a small shop backend, its cart and checkout in TypeScript and its account helpers in
JavaScript, with the real `writ`. A stand-in for the user answers one turn at
a time, carrying the conversation over, and knows only what a real user would. What happened, in the
conversation, `steering.md`, `open/`, the commits, the pull request, and the deliverable, is set
beside what passes. `rn` is made of prompts, so the same input does not behave the same way every
time, and no test can compare it against a fixed answer; using it is what shows whether the user
gets what it is chosen for.

Must-be quality has no scenes of its own. A must-be gap is fixed when it shows up in use, without
another use to check the fix, and what a machine can judge is checked by machine every time.

## Two sessions

The scenes run in two sessions on the practice repository. Everything a scene's pass depends on is
fixed here and in the scene before the run: what the stand-in says, knows, and decides, and what is
put in place for it. Whoever runs a scene after seeing the work could otherwise choose these so that
it passes.

The account session starts from rough words:

- The stand-in starts it with `/rn:on move src/account to TypeScript`.
- Why it wants this, said only when asked why: users who signed up with only an email see
  "undefined undefined" as their name, and support keeps getting tickets about it.
- What it knows, said only when asked: in a user record, `nickname`, `firstName`, and `lastName` can
  each be missing, `null`, or `""`.
- What it decides, when asked: a user with no name is shown the part of their email before "@".
  Whether every record has an email it does not know and cannot find out before the release, and it
  says to go on as if every record has one.
- At a sign-off where a scene gives it no words, it approves when the proposal shows nothing against
  its reason and decisions, and otherwise gives `/rn:gm` with what it saw.

The coupon session is made by hand before the run, on its own branch with a draft pull request, in
the form `rn`'s design gives, and taken up with `/rn:up`:

- Goal: every coupon is a discount, so no coupon makes an order cost more than it would without one.
- Acceptance criteria: A1, a percent coupon over 100% takes the items' total to 0, not below; M1,
  the app builds and its tests pass as before.
- The Plan and Design sign-offs are approved, with the practice repository's README, design
  document, and a verification document saying of coupons only that one over 100% takes the items'
  total to 0, and tasks planned for that.
- Why the stand-in wants this, said only when asked why: a coupon once took an order's total below
  0, and money went back to the customer by mistake.
- What the stand-in decides, when asked: a coupon that is not a discount refuses the order.

## Golden-path scenes

### A1: The user gets what they really want, though they start from rough words

- The account session's `/rn:on`, with the stand-in as above.

    Passes when `rn` asks the stand-in why it wants the goal, and the goal and Acceptance criteria
    approved at the Plan sign-off hold that no user is shown "undefined" in their name, which the
    first words do not: moved to TypeScript as it is, `${user.firstName}` still type-checks with the
    name missing, since a template string takes `undefined` without a type error.

- The account session's first Plan sign-off, where the stand-in gives `/rn:gm a user whose last name
  is null is shown "Ann null"`. The words name one value; the mismatch behind them is that no form
  an absent name takes, missing, `null`, or `""`, may show in a name.

    Passes when the plan next put up for the Plan sign-off covers all three forms for each name
    field, not `null` alone. When the first plan already covered all three, passes when `rn` shows
    the stand-in where it does, rather than adding `null` again.

- The coupon session's Deliverable sign-off. Its criteria name only percent coupons over 100%, while
  `src/cart/cart.ts` also takes a negative percent, `{ percent: -10 }`, or a negative fixed amount,
  `{ amount: -300 }`, and either raises the total today.

    Passes when, in the deliverable proposed at the Deliverable sign-off, no coupon raises the
    total: `checkout` given either coupon returns no total above the one it returns with no coupon,
    or refuses the order.

### A2: The user is called only for decisions that are theirs

- The account session as a whole, from `/rn:on` to the Deliverable sign-off. The decisions only the
  user can make in it are these: why the stand-in wants the goal, what a user with no name is shown,
  what is done about records that may have no email, and each of the three sign-offs. One fact is
  the stand-in's alone, since nothing in the repository shows it: what a user record holds where a
  name is absent.

    Passes when each decision reached the stand-in, as a question or at a sign-off, every time the
    stand-in is called is for one of them or for that fact, and the session reaches the Deliverable
    sign-off though the stand-in does nothing but answer those calls and go on after each sign-off:
    it never looks at the work in between, corrects it, or asks how it is going.

- What a user with no name is shown, put to the stand-in while working out the design.

    Passes when the stand-in decides from the question alone, and the approved design holds its
    answer.

### A3: At a sign-off, the user decides from the proposal

- Each of the account session's three sign-offs where the stand-in is given no words. What a user
  with no name is shown rests on every record having an email, which nothing in the session can
  check: a shortfall the stand-in's answers put in place, and which `rn` cannot fix on its own.

    Passes when a stand-in who reads only the proposal decides yes or no, and, reading the real
    thing, the same decision is right and every Good and More holds at its place, under the
    criterion ID it names; and the proposals at the Design and Deliverable sign-offs name that
    shortfall as a More.

### A4: Work that takes days goes on from where it stopped

- In the account session, the run is stopped once the generator of the first task after the Design
  sign-off has edited a file, and the stand-in gives `/rn:dn` in the same conversation, then
  `/clear` and `/rn:up`.

    Passes when it goes on with the same task from the edits the pause committed, without undoing
    them to start the task again, does not redo finished tasks, speaks the conversation language,
    and asks nothing already decided.

- At the account session's Design sign-off, the stand-in clears the conversation without answering.
  A commit is then made by hand on the practice repository's default branch that moves the names
  `displayName` takes under `profile`, with its tests, and the stand-in gives `/rn:up`. The design
  as first proposed rests on a shape the default branch no longer has, so the right decision on it
  is not yes.

    Passes when `/rn:up` brings the branch up to the default branch, works the design out again
    for the new shape, and stops at the Design sign-off again, with a proposal from which the
    stand-in decides as it would reading the real thing. Putting up the first proposal unchanged,
    or a stand-in approving the design as first proposed, fails the scene.

- `/rn:up` on a session paused under `rn` 0.8.0. Before the scene, that session is made with `rn`
  0.8.0 as released, loaded with `--plugin-dir` from the tag `rn--v0.8.0`: the stand-in starts it
  with `/rn:on make every coupon a discount`, answers as in the coupon session, approves its plan and
  design sign-offs, and, the run stopped once its first task has begun, gives its `/rn:dn`.

    Passes when it goes on from that session's goal and what was done, with `steering.md` in the
    current form, what the old design approved in a `notes` item and not in the design document, and
    a stop at the Plan sign-off.

## Machine checks

| Check | Criteria | When |
|---|---|---|
| Hook checks 1 to 3: the form of `steering.md`, the names in `open/`, and the form of the verification document, and every ID traced | M4 | In every scene, at the points the design names |
| Hook checks 4 and 8: a decision line on every conductor commit, and every commit pushed | M2 | In every scene, at the points the design names |
| Hook check 5: a settled item whole in its commit message | M3 | In every scene, at the points the design names |
| Hook checks 6 and 7: each stop keeps what its kind allows, and only the user's own `/rn:ty` passes a sign-off | M5 | In every scene, at the points the design names |
| Hook checks 9 to 11: only the conductor uses git, and, with Claude Code's file tools, the first user writes only its report and reads nothing of the maker's account | M6 | In every scene, at the points the design names |
| The hooks' tests in `rn/tests/`: each check stops its breaking case and lets its passing case through | M2, M3, M4, M5, M6 | On every change to the hooks |
| `rn/agents/`: `rn:first-user` sets `omitClaudeMd`, and `rn:generator` has no Agent tool | M6 | On every change to the agents |
| The practice repository's default branch has, after a scene, the head it had before it, but for the commit A4's second scene makes there by hand | M1 | After every scene |
| `claude plugin validate --strict` for `rn` and for the marketplace | M7 | On every change to the plugin |
| Installing `rn` from the marketplace, which brings `writ` with it | M7 | Before every release |

Sessions that last days, large repositories, and differences between models are not checked here.
